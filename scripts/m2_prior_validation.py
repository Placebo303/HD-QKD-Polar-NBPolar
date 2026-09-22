#!/usr/bin/env python3
"""M2 prior validation runner — Stage-1 interface for NBPOLAR-M2-PRIOR-REALDATA-VALIDATION.

Stage-1 wiring is REAL (``--freeze-config`` with all 19 keys required,
the ``--authorized`` hard gate, flag/freeze cross-check, the frozen
319/6492 K pin, and the ``workspace/``-confined out-root guard). The G1
held-out NLL body (``--stage-g1-nll``) is implemented decoder-free per
``NBPOLAR-M2-PRIOR-G1-REALDATA-NLL`` / ``g1_freeze.md`` (Phase-0 code;
Phase-A ``--closure-only`` framing pass + Phase-B full G1 science). The
G2 one-shot three-arm decode body (``--stage-g2-decode``) is implemented
per ``NBPOLAR-M2-PRIOR-G2-DECODE`` / ``g2_freeze.md``: stage-keyed routing
(only the G2 packet's own ``g2_freeze_config.json`` at window 200 reaches
the body; any other freeze exits 3 ``STAGE_BODY_PENDING_FREEZE`` with
zero data contact), per-arm CAL priors via the frozen M2/M0 leaves, and
two-layer causal SC through the accepted chunked ``sc_decode``
(chunk_rows=512) by importing and calling the frozen
``operational_f13``/P17 procedures (deferred production-only loader;
tests pass an explicit fake chain and never enter it). M2 is a
CANDIDATE, never the baseline.
Science constants are window-keyed contracts: the G1 legacy contract at
w=500 is preserved verbatim, and the G1R2 successor at w=200 (delta
item 8, NBPOLAR-M2-PRIOR-G1R2-W200-CIRCULAR) reuses the same mechanics.
Selection uses the freeze ``pairing_window_primary`` only, never data.

Wiring verifiable via ``--selfcheck`` (pure logic; touches no data).

Importing this module reads no files, constructs no model, and opens no
data. All non-stdlib/non-numpy imports (YAML, TimeTagger shim targets,
``src.qkd_io``, frozen prior leaves) are deferred inside functions.

Frozen prior leaves (``formal_ir/prior_m2.py``,
``formal_ir/nbpolar/prior.py``) are loaded read-only by file location
inside functions: the mandated execution venv has no pandas, and the
``formal_ir`` package ``__init__`` requires it, so the package import
path is unusable there. Both leaves are NumPy+stdlib-only with no
relative imports (enforced by a runtime AST check before loading); they
are NEVER modified.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from typing import NoReturn

import numpy as np

# Repo-root insertion: `python scripts/m2_prior_validation.py` puts scripts/
# (not the repo root) on sys.path, so Stage-1 `src....` imports would fail
# without it. This block must stay BEFORE any TimeTagger shim or `src.qkd_io`
# import. It reads no files and has no other side effects.
_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

STAGE1_PACKET = (
    ".workbuddy/queue/NBPOLAR-M2-PRIOR-REALDATA-VALIDATION/TASK_PACKET.md"
)
STAGE1_STATUS = (
    ".workbuddy/queue/NBPOLAR-M2-PRIOR-REALDATA-VALIDATION/STATUS.yaml"
)

# Frozen CLI spellings (packet §5/§6 commands). Used for add_argument and for
# user-facing messages so the literal appears once.
FLAG_G1 = "--stage-g1-nll"
FLAG_G2 = "--stage-g2-decode"

# Frozen G2 one-shot K pair (packet §6): G2 decodes frozen K1=319/K2=6492
# regardless; any re-split belongs to a separate later freeze.
FROZEN_K1 = 319
FROZEN_K2 = 6492

# CLI-flag -> freeze-config-key cross-check (packet Spec 5). A provided
# flag whose normalized value differs from the freeze value is a hard
# error, never a silent override. --k1/--k2 have no freeze key; they are
# pinned to FROZEN_K1/FROZEN_K2 instead. --acq-id/--out-root are runtime
# selectors with no freeze key.
FLAG_FREEZE_KEYS = {
    "window_primary": "pairing_window_primary",
    "window_sensitivity": "pairing_window_sensitivity",
    "skip": "skip_frames",
    "mod": "mod_boundary",
    "char_pairs": "char_sample_pairs",
    "blocks": "g2_blocks",
    "tag_master": "tag_master",
    "arms": "g2_arms",
}

# The 19 STATUS.yaml to_freeze keys (sorted). Authoritative source of values
# is the --freeze-config file; a missing or null key is a hard error.
REQUIRED_FREEZE_KEYS = (
    "B_tail",
    "a1_cal_ids",
    "block_formation_fallback",
    "cal_frame_ids",
    "cal_split_rule",
    "char_sample_pairs",
    "delta_min",
    "disjointness_matrix",
    "g2_arms",
    "g2_blocks",
    "g2_fail_rule",
    "g2_inconclusive_rule",
    "g2_success_rule",
    "heldout_frame_ids",
    "mod_boundary",
    "pairing_window_primary",
    "pairing_window_sensitivity",
    "skip_frames",
    "tag_master",
)


def _fail(msg: str, code: int = 2) -> NoReturn:
    print(f"ERROR: {msg}", file=sys.stderr)
    raise SystemExit(code)


def _ensure_timetagger_shim() -> str:
    """Make the bare ``TimeTagger`` name importable (Stage-1 helper).

    Tries the bare top-level name first; otherwise aliases the official
    ``Swabian.TimeTagger`` into ``sys.modules``. Stage 1 MUST call this
    BEFORE any ``src.qkd_io`` import (``src/qkd_io/ttbin_pipeline.py`` does
    ``from TimeTagger import FileReader``). Deferred into a function so
    module import stays pure. Returns which path resolved.
    """
    try:
        import TimeTagger  # type: ignore  # noqa: F401

        return "bare-toplevel-TimeTagger"
    except Exception:
        pass
    try:
        from Swabian import TimeTagger as _TT  # type: ignore
    except Exception as exc:
        _fail(f"neither TimeTagger nor Swabian.TimeTagger is importable: {exc}")
    sys.modules.setdefault("TimeTagger", _TT)
    return "swabian-shim"


def _missing_freeze_keys(cfg: dict) -> list[str]:
    """Sorted required keys absent or null in an already-loaded mapping.

    Pure: no I/O. Only absence and explicit null count as missing (0, false
    and empty containers count as present per the packet's null/absent rule).
    """
    if not isinstance(cfg, dict):
        _fail("freeze-config top level must be a JSON/YAML mapping/object")
    return sorted(k for k in REQUIRED_FREEZE_KEYS if cfg.get(k) is None)


def load_freeze_config(path: Path | str) -> dict:
    """Load ``--freeze-config`` and require ALL 19 keys.

    Accepts ``.json`` natively and ``.yaml``/``.yml`` only when PyYAML
    imports. Any missing or null key prints the sorted missing list and
    exits 2. NEVER substitutes a default.
    """
    p = Path(path)
    if not p.is_file():
        _fail(f"freeze-config not found: {p} (run from repo root; no defaults substituted)")
    suffix = p.suffix.lower()
    if suffix == ".json":
        try:
            cfg = json.loads(p.read_text(encoding="utf-8"))
        except Exception as exc:
            _fail(f"freeze-config {p} is not valid JSON: {exc}")
    elif suffix in (".yaml", ".yml"):
        try:
            import yaml  # deferred: PyYAML is optional, never imported at module level
        except Exception:
            _fail(
                f"freeze-config {p} needs YAML but PyYAML is not installed; "
                "use a .json freeze-config instead"
            )
        try:
            cfg = yaml.safe_load(p.read_text(encoding="utf-8"))
        except Exception as exc:
            _fail(f"freeze-config {p} is not valid YAML: {exc}")
    else:
        _fail(f"freeze-config {p} has unknown suffix {suffix!r}; use .json or .yaml/.yml")
    missing = _missing_freeze_keys(cfg)
    if missing:
        _fail(
            f"freeze-config {p} missing/null {len(missing)} required key(s): "
            + ", ".join(missing)
            + " (sorted; refusing to substitute defaults)"
        )
    return cfg


# Forbidden-tree guard: additive to the Spec-5 workspace/ confinement enforced by _out_root_workspace_refusal.
def _out_root_refusal(out_root: Path | str) -> str | None:
    """None when ``--out-root`` is an allowed target, else the refusal text.

    Pure: resolves paths but never creates anything. Refuses any target at
    or under ``results/`` or ``comparison_bench/outputs_comparison/``.
    """
    r = Path(out_root).expanduser()
    if not r.is_absolute():
        r = Path.cwd() / r
    try:
        r = r.resolve()
    except Exception as exc:
        return f"cannot resolve --out-root {out_root!s}: {exc}"
    for forbidden in (
        _REPO_ROOT / "results",
        _REPO_ROOT / "comparison_bench" / "outputs_comparison",
    ):
        try:
            f = forbidden.resolve()
        except Exception:
            f = forbidden
        if r == f or f in r.parents:
            return (
                f"refusing --out-root {r}: inside forbidden tree {f}; "
                "M2 outputs are additive under workspace/m2_prior_validation/ only"
            )
    return None


def _require_authorized(authorized: bool) -> None:
    """Hard gate: stage modes run ONLY with ``--authorized``.

    No file access here; the caller must invoke this before any
    freeze-config parsing or data access.
    """
    if not authorized:
        print(
            "ERROR: stage execution requires --authorized "
            "(refusing implicit production run)",
            file=sys.stderr,
        )
        raise SystemExit(2)


def _out_root_workspace_refusal(out_root: Path | str) -> str | None:
    """None when ``--out-root`` resolves under repo ``workspace/``, else text.

    Pure: resolves paths but never creates anything. Stage-1 M2 outputs
    (when later freezes allow them) are additive under ``workspace/``
    only; anything else exits 2.
    """
    r = Path(out_root).expanduser()
    if not r.is_absolute():
        r = Path.cwd() / r
    try:
        r = r.resolve()
    except Exception as exc:
        return f"cannot resolve --out-root {out_root!s}: {exc}"
    anchor = _REPO_ROOT / "workspace"
    try:
        anchor_resolved = anchor.resolve()
    except Exception:
        anchor_resolved = anchor
    if r == anchor_resolved or anchor_resolved in r.parents:
        return None
    return (
        f"refusing --out-root {r}: outside workspace/ ({anchor_resolved}); "
        "M2 outputs are additive under workspace/m2_prior_validation/ only"
    )


def _norm_crosscheck(value) -> str:
    """Normalize one side of a flag/freeze comparison (whitespace-blind).

    Freeze lists (e.g. ``g2_arms: [A1, A2, B]``) compare as comma-joined
    against the CLI spelling (``--arms A1,A2,B``).
    """
    if isinstance(value, (list, tuple)):
        text = ",".join(str(v) for v in value)
    else:
        text = str(value)
    return "".join(text.split())


def _cross_check_mismatches(options: dict, freeze: dict) -> list[str]:
    """Flag values (when provided) that disagree with the freeze file.

    Pure: no I/O. The freeze file is authoritative; a provided CLI flag
    that contradicts it is a hard error, never an override.
    """
    out: list[str] = []
    for flag, key in FLAG_FREEZE_KEYS.items():
        opt = options.get(flag)
        if opt is None:
            continue
        frozen = freeze.get(key)
        if _norm_crosscheck(opt) != _norm_crosscheck(frozen):
            out.append(f"--{flag.replace('_', '-')}={opt!r} != freeze {key}={frozen!r}")
    return out


def _check_k_pin(k1, k2) -> None:
    """Pin ``--k1/--k2`` to the frozen G2 pair (no I/O; exits 2 on violation)."""
    for label, value, want in (("k1", k1, FROZEN_K1), ("k2", k2, FROZEN_K2)):
        if value is None:
            continue
        try:
            got = int(str(value).strip())
        except (TypeError, ValueError):
            got = None
        if got != want:
            _fail(
                f"--{label} must equal frozen {want}, got {value!r} "
                "(G2 decodes frozen K1=319/K2=6492 regardless; "
                "re-split needs its own freeze)"
            )


# ---------------------------------------------------------------------------
# G1 body (decoder-free; Phase-0 implementation for
# NBPOLAR-M2-PRIOR-G1-REALDATA-NLL, freeze g1_freeze.md).
#
# Boundaries (hard): NEVER call a decoder here (no sc_decode / genie /
# SCL anywhere in this file); NEVER read SHG `_2` (production reader
# refuses it); NEVER write outside the passed ``out_root`` (workspace-
# confined by the Stage-1 guard) except the single Phase-A packet-dir
# freeze-config emission. Remainder science takes caller-supplied pair
# arrays only (no alignment, no char sample — exempt per freeze §1.2);
# the production remainder pairs binding belongs to the Phase-B
# dispatch and is refused loudly, never invented.
# ---------------------------------------------------------------------------

# Frozen (N)-pairing constants, vendored literally from the 2026-09-21
# census implementation `workspace/dual_rule_census_20260921.py`
# (`frozen` block + `_count_nearest` + symbol map `(b_A % 1024,
# b_B % 1024)`, `b = t // 200`, `tA_aligned = tA_raw + offset`).
G1_D = 1024
G1_BIN_WIDTH_PS = 200
G1_PERIOD_PS = 204800
G1_FRAME_PAIRS = 256
G1_GATE_PS = 200  # frozen design-gate provenance (census frozen block)
G1_THRESHOLD_PS = 40000  # frozen threshold provenance (same block)
G1_SCAN_RANGE_PS = 409600
G1_BIN_PS_ALIGN = 100
G1_PEAK_TO_BG_MIN = 10.0

# Phase-A reproduction gate (g1_freeze.md §2/§6; observed values in
# `workspace/census_20260921/20260113_SHG_Type2PPLN_3s/dual_rule_census.json`).
REPRO_GATE = {
    "peak_center_ps": 50,
    "peak_sigma_ps": 112.45189572400645,
    "status": "ok",
    "n_pairs": 1269268,
    "n_frames": 4958,
}

# Segment layout (g1_freeze.md §4): 0-based post-skip complete frames.
SEG_RANGES = (
    ("a1_cal", 0, 1023),
    ("cal32", 1024, 1055),
    ("char", 1056, 1837),
    ("heldout", 1838, 2397),
    ("eval", 2398, 4189),
)
SEG_RESERVE = ("reserve", 4190, 4255)
ALLOCATED_FRAMES = 4190  # frames 0..4189 must exist (freeze §4 fallback)

REMAINDER_ACQ_ID = "remainder_101f"
REMAINDER_N_FRAMES = 101
REMAINDER_CAL_FRAMES = 32

G1_PACKET_DIR = _REPO_ROOT / ".workbuddy" / "queue" / "NBPOLAR-M2-PRIOR-G1-REALDATA-NLL"
G1_CONFIG_NAME = "g1_freeze_config.json"

# G1R2 successor contract (delta item 8, NBPOLAR-M2-PRIOR-G1R2-W200-CIRCULAR):
# same layout/mechanics as G1, corrected pairing+MOD window (w=200).
REPRO_GATE_G1R2 = {
    "peak_center_ps": 50,
    "peak_sigma_ps": 112.45189572400645,
    "status": "ok",
    "n_pairs": 1259992,
    "n_frames": 4921,
}
G1R2_PACKET_DIR = _REPO_ROOT / ".workbuddy" / "queue" / "NBPOLAR-M2-PRIOR-G1R2-W200-CIRCULAR"
G1R2_CONFIG_NAME = "g1r2_freeze_config.json"

# ---------------------------------------------------------------------------
# G2 constants + pure helpers (NBPOLAR-M2-PRIOR-G2-DECODE, g2_freeze.md).
#
# Routing (blocking-fix B3) is STAGE-KEYED, never window-only: only the G2
# packet's own freeze (config name ``g2_freeze_config.json`` at window 200,
# i.e. the G1R2 science mechanics) reaches the decode body. The G2 stage
# writes NO packet dir at all (Phase-B outputs are out-root-only); in
# particular it SHALL NOT write to the G1 or G1R2 packet dirs.
# ---------------------------------------------------------------------------

G2_PACKET = "NBPOLAR-M2-PRIOR-G2-DECODE"
G2_PACKET_DIR = _REPO_ROOT / ".workbuddy" / "queue" / "NBPOLAR-M2-PRIOR-G2-DECODE"
G2_CONFIG_NAME = "g2_freeze_config.json"
G2_LABEL = "G2"

# Frozen decode constants (g2_freeze.md "Frozen decode constants").
G2_N = 32768
G2_K1 = FROZEN_K1  # 319
G2_K2 = FROZEN_K2  # 6492
G2_TAG_BITS = 64
G2_DISCLOSED_BITS = 5
G2_CHUNK_ROWS = 512  # frozen `sc._minus_block` default (P11 contract)
G2_FLOOR = 1e-15
# Tag/seed provenance (freeze rows 7 + B1/R7): INHERITED from G1R2
# (value-identical); G1R2 was decoder-free so no tag/seed stream was ever
# consumed there. Rule TAG_MASTER = EVAL_SEED + 10000.
G2_EVAL_SEED = 2026093001
G2_TAG_MASTER = 2026103001
# Construction provenance (freeze clarification N2): canonical P16 path
# (never re-derived); the pinned digest is the INNER P16 procedure digest
# (the wrapper file's own sha256 differs — expected, P17-established).
G2_CONSTRUCTION_PATH = (
    _REPO_ROOT / ".workbuddy" / "queue"
    / "NBPOLAR-PHASE4-P16-N32768-OPERATIONAL-F13" / "operational_f13_gate"
    / "construction_and_allocation.json"
)
G2_CONSTRUCTION_DIGEST = (
    "055c906472dd2a09761761b18aceb5f31d8b5db19bac658721f8dc49c3faea1b"
)

# Frozen EVAL layout: post-skip frames 2398–4189 = 14 blocks × 128 frames
# × 256 pairs; N = 32768 pairs per block.
G2_EVAL_FIRST = 2398
G2_EVAL_LAST = 4189
G2_BLOCK_FRAMES = 128
G2_BLOCKS = 14

# Wilson gate uses the two-sided 95% score interval (z=1.96) — NOT the
# frozen protocol one-sided lower bound (WILSON_Z=1.6449).
G2_WILSON_Z = 1.96

G2_ARMS = (
    "A1_M0_1024f_incumbent",
    "A2_M0_32f_matched",
    "B_M2_32f_candidate",
)
# Each arm fits on its OWN sacrificed CAL (freeze row 5): A1 on the
# 1024-frame incumbent budget (262,144 pairs), A2/B on the matched
# 32-frame CAL (8,192 pairs). Ranges are post-skip frame ids, inclusive.
G2_ARM_CAL = {
    "A1_M0_1024f_incumbent": (0, 1023),
    "A2_M0_32f_matched": (1024, 1055),
    "B_M2_32f_candidate": (1024, 1055),
}

G2_OUTCOMES = (
    "exact",
    "verify_failed",
    "undetected",
    "decode_failed",
    "nonfinite",
    "resource_abort",
)

G2_BUDGET_S = 900.0

# Verbatim-inherited rule literals (G1R2 closure values; the G2 body
# refuses drift on the rules it consumes).
G2_CAL_SPLIT_RULE = (
    "RULE-FIT32-SCORE-HELDOUT: fit all 32, score disjoint held-out, seed N/A"
)
G2_SUCCESS_RULE = (
    "Wilson-lower(B) > Wilson-upper(A2), strict non-overlap, z=1.96"
)
G2_INCONCLUSIVE_RULE = (
    "point(B) > point(A2) but CIs overlap => bounded negative"
)
G2_FAIL_RULE = "point(B) <= point(A2)"
G2_FALLBACK_RULE = (
    "COMPLETE-BLOCKS-ONLY, else INSUFFICIENT=>INCONCLUSIVE "
    "(never pad/reuse/shrink)"
)

# Caveats carried into the G2 record (freeze review N1 + truncation R5).
G2_CAVEATS = (
    "a) the census far-offset accidental baseline is structured, not uniform "
    "(S11 R4: far-offset tail ~= 0.40 vs uniform 0.997): the w=200 accidental "
    "estimate (0.0058) must NOT be read as a uniform-accidental level; "
    "b) q_rest = 0 is a weak statement at a 32-frame CAL (zero-observation "
    "upper bound 3/8192 = 3.66e-4): G2 is precisely the test of whether that "
    "matters, so a FAIL/INCONCLUSIVE verdict must NOT later be misread as "
    "premise validation; "
    "c) w=200 keeps a timing-truncated population (c0 count identical across "
    "windows but jitter-heavy coincidences preferentially dropped): state it "
    "in any rate/efficiency/leakage sentence. "
    "M2 is a CANDIDATE, never the baseline."
)


def check_g2_config_route(config_path) -> str | None:
    """None when ``--freeze-config`` routes to the G2 body, else the reason.

    Stage-keyed (B3), never window-only: the G2 decode body executes ONLY
    for the G2 packet's own freeze name (``g2_freeze_config.json``) and
    never for a path at/under the G1 or G1R2 packet dirs. A non-None
    return means exit 3 ``STAGE_BODY_PENDING_FREEZE`` (this freeze carries
    no G2 body) with zero data contact — never a silent fallback, never a
    write. Pure: resolves paths but creates nothing.
    """
    if config_path is None:
        return "no --freeze-config path supplied (G2 body needs its stage-keyed freeze)"
    p = Path(config_path)
    if p.name != G2_CONFIG_NAME:
        return (
            f"config name {p.name!r} != stage-keyed {G2_CONFIG_NAME!r}: "
            "the G2 body runs only under its own packet freeze (never window-only)"
        )
    try:
        r = p.expanduser()
        if not r.is_absolute():
            r = Path.cwd() / r
        r = r.resolve()
    except Exception as exc:
        return f"cannot resolve --freeze-config {config_path!s}: {exc}"
    for foreign in (G1_PACKET_DIR, G1R2_PACKET_DIR):
        try:
            f = foreign.resolve()
        except Exception:
            f = foreign
        if r == f or f in r.parents or r == f / G1_CONFIG_NAME or r == f / G1R2_CONFIG_NAME:
            return (
                f"refusing routed path {r}: at/under a G1/G1R2 packet dir; "
                "the G2 stage never runs off (or writes to) those dirs"
            )
    return None


def g2_eval_blocks() -> list:
    """Frozen EVAL block list: 14 blocks × [start,end] post-skip frames.

    Block b covers frames 2398+128*b .. +127; the last block ends exactly
    at 4189. Pure.
    """
    blocks = []
    for b in range(G2_BLOCKS):
        s = G2_EVAL_FIRST + b * G2_BLOCK_FRAMES
        blocks.append([s, s + G2_BLOCK_FRAMES - 1])
    if blocks[-1][1] != G2_EVAL_LAST or blocks[0][0] != G2_EVAL_FIRST:
        raise AssertionError(f"G2 EVAL layout drift: {blocks[0]}..{blocks[-1]}")
    return blocks


def g2_cal_ids(arm: str) -> list:
    """Post-skip CAL frame ids for one frozen arm name (pure).

    Only the three freeze spellings route anywhere; anything else raises
    (never a silent default CAL).
    """
    try:
        s, e = G2_ARM_CAL[arm]
    except (KeyError, TypeError):
        raise ValueError(f"unknown G2 arm {arm!r} (frozen arms: {list(G2_ARMS)})")
    return list(range(s, e + 1))


def wilson_interval(k, n, z=G2_WILSON_Z) -> dict:
    """Two-sided Wilson score interval for a binomial proportion (pure).

    ``k`` exact of ``n`` blocks at ``z`` (frozen 1.96). Boundaries clamp:
    k=0 -> lower 0.0, k=n -> upper 1.0. Stdlib-only.
    """
    k = int(k)
    n = int(n)
    z = float(z)
    if n <= 0:
        raise ValueError(f"n must be positive, got {n!r}")
    if not 0 <= k <= n:
        raise ValueError(f"k must lie in 0..n, got k={k!r} n={n!r}")
    if not z > 0 or not math.isfinite(z):
        raise ValueError(f"z must be finite and positive, got {z!r}")
    p = k / n
    denom = 1.0 + z * z / n
    center = (p + z * z / (2.0 * n)) / denom
    half = z * math.sqrt(p * (1.0 - p) / n + z * z / (4.0 * n * n)) / denom
    return {
        "k": k,
        "n": n,
        "z": z,
        "p_hat": p,
        "lower": max(0.0, center - half),
        "upper": min(1.0, center + half),
    }


def eval_g2_gate(b_exact, a2_exact, n=G2_BLOCKS, z=G2_WILSON_Z) -> dict:
    """Preregistered G2 Wilson gate (pure; A1 descriptive, no gate).

    SUCCESS iff Wilson-lower(B) > Wilson-upper(A2) (strict non-overlap);
    FAIL iff point(B) <= point(A2); else INCONCLUSIVE (bounded negative,
    no tuning, no rerun). ``undetected`` never enters: callers pass exact
    counts only.
    """
    b = wilson_interval(b_exact, n, z)
    a = wilson_interval(a2_exact, n, z)
    if b["lower"] > a["upper"]:
        verdict = "SUCCESS"
    elif b["p_hat"] <= a["p_hat"]:
        verdict = "FAIL"
    else:
        verdict = "INCONCLUSIVE"
    return {"b": b, "a2": a, "n": int(n), "verdict": verdict}


def g2_exact_from(tag_pass, label_match) -> dict:
    """Tag-verified exactness with ``undetected`` isolated (pure).

    ``exact`` = tag_pass AND label_match; ``undetected`` = tag pass
    without label match — a separate key, never merged into success/FER.
    """
    tag = bool(tag_pass)
    match = bool(label_match)
    return {
        "tag_pass": tag,
        "label_match": match,
        "exact": bool(tag and match),
        "undetected": bool(tag and not match),
    }


def g2_first_error(high_hat, high_true, low_hat, low_true) -> dict:
    """First operational error coordinate AND layer (pure, no I/O).

    Source-symbol index of the first position where either layer hat
    differs from truth; layer is ``L1`` when the high layer differs there,
    else ``L2``. No hats (L1 failure) or no mismatch ->
    ``(None, None)``. Hats are read-only here; never mutated.
    """
    if high_hat is None or low_hat is None:
        return {"coordinate": None, "layer": None}
    hh = np.asarray(high_hat, dtype=np.int64).ravel()
    ht = np.asarray(high_true, dtype=np.int64).ravel()
    lh = np.asarray(low_hat, dtype=np.int64).ravel()
    lt = np.asarray(low_true, dtype=np.int64).ravel()
    if not (hh.shape == ht.shape == lh.shape == lt.shape):
        raise ValueError(
            f"hat/truth shape mismatch: {hh.shape}/{ht.shape}/{lh.shape}/{lt.shape}"
        )
    bad = (hh != ht) | (lh != lt)
    idx = np.flatnonzero(bad)
    if idx.size == 0:
        return {"coordinate": None, "layer": None}
    i = int(idx[0])
    return {"coordinate": i, "layer": "L1" if hh[i] != ht[i] else "L2"}


def g2_truth_views(alice, polar_fn) -> dict:
    """Source/transform truth views for one EVAL block (pure).

    ``high = alice >> 5``, ``low = alice & 31`` (frozen
    ``A = 32*U1 + U2`` packing); ``u1/u2 = polar_fn(high/low)``;
    ``labels = alice``. ``polar_fn`` is injected (production: the frozen
    chain ``polar_transform``; tests: an explicit fake). Symbols are
    validated to [0,1023]; inputs never mutated.
    """
    a = np.asarray(alice, dtype=np.int64).ravel()
    if a.size == 0:
        raise ValueError("empty alice block")
    if a.min() < 0 or a.max() > 1023:
        raise ValueError("alice symbols out of [0,1023]")
    high = (a >> 5).astype(np.int64)
    low = (a & 31).astype(np.int64)
    u1 = np.asarray(polar_fn(high), dtype=np.int64).ravel()
    u2 = np.asarray(polar_fn(low), dtype=np.int64).ravel()
    if u1.shape != a.shape or u2.shape != a.shape:
        raise ValueError(
            f"polar_fn shape mismatch: {u1.shape}/{u2.shape} vs {a.shape}"
        )
    return {"high": high, "low": low, "u1": u1, "u2": u2, "labels": a.copy()}


def g2_l2_nll_bits(p2_table, bob, u1cond, u2true, prior_mod, provenance) -> dict | None:
    """Mean L2 NLL (bits) of true ``u2`` under one H-conditioning (pure).

    Gathers frozen L2 rows for the conditioning ``u1cond`` (true-H for the
    oracle view, hard candidate-H for the operational view) and scores
    ``-log2 P(u2true)`` via the UNCHANGED frozen metric pipeline.
    ``u1cond=None`` (L2 never ran) -> None. Decoder-free scoring only.
    """
    if u1cond is None:
        return None
    b = np.asarray(bob, dtype=np.int64).ravel()
    h = np.asarray(u1cond, dtype=np.int64).ravel()
    u = np.asarray(u2true, dtype=np.int64).ravel()
    if not (b.shape == h.shape == u.shape):
        raise ValueError(f"bob/u1cond/u2 shape mismatch: {b.shape}/{h.shape}/{u.shape}")
    g = np.asarray(
        prior_mod.gather_p2_metrics(b[None, :], h[None, :], p2_table),
        dtype=np.float64,
    ).reshape(-1, 32)
    s = prior_mod.probs_to_symbol_metric(g, provenance=provenance)
    nll = -np.asarray(s.logp)[np.arange(u.size), u] / math.log(2)
    return {"n_symbols": int(u.size), "nll_mean_bits": float(nll.mean())}


def g2_floor_audit(raw_joint, joint, alice, bob) -> dict:
    """Raw-zero vs fixed-floor accounting for one block (pure).

    ``raw_joint`` is the pre-floor table (M0 raw MLE / M2 triple base),
    ``joint`` the floored+renormalized table actually decoded with.
    ``n_raw_zero_hits`` = positions whose true pair sat on an exact raw
    zero (scored at the floor); ``n_floor_lifted`` = positions with
    0 < raw < 1e-15; ``floor_logloss_bits`` = -log2(joint) summed over the
    raw-zero hits. Decoder-free measurement plumbing.
    """
    r = np.asarray(raw_joint, dtype=np.float64)
    j = np.asarray(joint, dtype=np.float64)
    a = np.asarray(alice, dtype=np.int64).ravel()
    b = np.asarray(bob, dtype=np.int64).ravel()
    if r.shape != (G1_D, G1_D) or j.shape != (G1_D, G1_D):
        raise ValueError(f"tables must be (1024,1024), got {r.shape}/{j.shape}")
    if a.shape != b.shape:
        raise ValueError(f"alice/bob length mismatch: {a.shape} vs {b.shape}")
    raw = r[a, b]
    flo = j[a, b]
    if not np.isfinite(flo).all() or (flo <= 0).any():
        raise ValueError("floored table must hold finite positive mass on block pairs")
    zero = raw == 0.0
    lifted = (raw > 0.0) & (raw < G2_FLOOR)
    with np.errstate(divide="ignore"):
        ll = -np.log2(flo[zero]).sum()
    return {
        "n": int(a.size),
        "n_raw_zero_hits": int(zero.sum()),
        "n_floor_lifted": int(lifted.sum()),
        "floor_logloss_bits": float(ll),
    }


def recount_g2_disclosure(records, k1=G2_K1, k2=G2_K2) -> dict:
    """Independent literal disclosure recount over block records (pure).

    Recomputes per-record key/public bits from the frozen accounting rule
    (5 bits per disclosed coordinate, 64 per invoked tag, 10*N+63 public
    seed bits per invoked tag) and diffs against the incremental totals;
    any mismatch invalidates the run. ``tag_invocations`` counts invoked
    per-block final tags.
    """
    n = G2_N
    seed_len = 10 * int(n) + 63
    inc_key = 0
    inc_pub = 0
    inc_tag = 0
    re_key = 0
    re_pub = 0
    re_tag = 0
    for rec in records:
        inc_key += int(rec["key_dependent_bits"])
        inc_pub += int(rec["public_control_bits"])
        inc_tag += int(rec.get("tag_invoked", False))
        want_key = G2_DISCLOSED_BITS * int(k1)
        if rec.get("l2_invoked", False):
            want_key += G2_DISCLOSED_BITS * int(k2)
        if rec.get("tag_invoked", False):
            want_key += G2_TAG_BITS
            re_pub += seed_len
            re_tag += 1
        re_key += want_key
    mismatches = []
    if inc_key != re_key:
        mismatches.append(f"key_dependent_bits:{inc_key}!={re_key}")
    if inc_pub != re_pub:
        mismatches.append(f"public_control_bits:{inc_pub}!={re_pub}")
    if inc_tag != re_tag:
        mismatches.append(f"tag_invocations:{inc_tag}!={re_tag}")
    return {
        "incremental": {
            "key_dependent_bits": inc_key,
            "public_control_bits": inc_pub,
            "tag_invocations": inc_tag,
        },
        "recount": {
            "key_dependent_bits": re_key,
            "public_control_bits": re_pub,
            "tag_invocations": re_tag,
        },
        "mismatches": mismatches,
    }

# Per-contract record. Selection is explicit and deterministic via
# freeze["pairing_window_primary"] (500 -> G1 legacy, 200 -> G1R2) —
# never inferred by reading data. G1's literals stay verbatim so a G1
# invocation reproduces its accepted record; alignment literals
# (peak_center / sigma / status) are shared across both contracts.
CONTRACTS = {
    500: {
        "window": 500,
        "repro_gate": REPRO_GATE,
        "packet_dir": G1_PACKET_DIR,
        "config_name": G1_CONFIG_NAME,
        "packet": "NBPOLAR-M2-PRIOR-G1-REALDATA-NLL",
        "freeze": "NBPOLAR-M2-PRIOR-REALDATA-VALIDATION/g1_freeze.md",
        "label": "G1",
        "science_mode": "g1-science",
    },
    200: {
        "window": 200,
        "repro_gate": REPRO_GATE_G1R2,
        "packet_dir": G1R2_PACKET_DIR,
        "config_name": G1R2_CONFIG_NAME,
        "packet": "NBPOLAR-M2-PRIOR-G1R2-W200-CIRCULAR",
        "freeze": "NBPOLAR-M2-PRIOR-G1R2-W200-CIRCULAR/TASK_PACKET.md",
        "label": "G1R2",
        "science_mode": "g1r2-science",
    },
}


def contract_for_window(window) -> dict:
    """Select the science contract for an explicit pairing window (pure).

    500 selects the G1 legacy contract, 200 the G1R2 successor. Any
    other value exits 2 loudly (never a silent default, never inferred
    from data — the caller passes the freeze value through).
    """
    try:
        w = int(str(window).strip())
    except (TypeError, ValueError):
        w = None
    if w not in CONTRACTS:
        _fail(
            f"pairing_window_primary {window!r} selects no science contract "
            f"(known windows: {sorted(CONTRACTS)}; G1=500, G1R2=200)"
        )
    return CONTRACTS[w]


def contract_for_freeze(freeze: dict) -> dict:
    """Select the science contract from an already-loaded freeze mapping."""
    return contract_for_window(freeze.get("pairing_window_primary"))


def reserve_ids_for_ledger(n_postskip) -> dict:
    """Ledger-driven reserve emission (delta item 8; pure, no I/O).

    The reserve starts at ALLOCATED_FRAMES (frames 0..ALLOCATED_FRAMES-1
    are allocated) and ends at the last available post-skip frame
    (n_postskip - 1): 4190..4255 at the G1 ledger (4256 frames, exactly
    the legacy SEG_RESERVE range), 4190..4218 at the G1R2 ledger (4219
    frames). When no post-skip frame lies beyond the allocation the
    reserve is empty with a recorded note — frame ids are never
    invented, so ids past the ledger end (e.g. 4219+ at w=200) cannot
    be emitted.
    """
    n = int(n_postskip)
    start = ALLOCATED_FRAMES
    end = n - 1
    if end < start:
        return {
            "ids": [],
            "note": (
                f"no post-skip frame beyond allocated {ALLOCATED_FRAMES} "
                f"(ledger {n}); empty reserve, never invented"
            ),
        }
    return {"ids": list(range(start, end + 1)), "note": ""}

MODES = ("LINEAR_ONLY", "CIRCULAR")

BUDGET_CLOSURE_S = 300.0
BUDGET_G1_S = 600.0
BUDGET_RSS_GIB = 2.0


class _InsufficientFrames(Exception):
    """Post-skip ledger below ALLOCATED_FRAMES (freeze §4 fallback path)."""


def _frozen_leaf_module(relpath: str, cache_name: str):
    """Load a frozen NumPy+stdlib-only leaf module read-only by file location.

    The mandated venv cannot use the ``formal_ir`` package import path
    (its ``__init__`` needs pandas, which no venv here provides), so the
    leaf file itself — the identical frozen source — is loaded directly.
    A runtime AST check refuses relative imports, frozen-package-root
    imports, TimeTagger imports, and any decoder entry point before
    loading. The file is only read, never modified.
    """
    import ast
    import importlib.util

    cache = globals().setdefault("_FROZEN_LEAF_CACHE", {})
    if cache_name in cache:
        return cache[cache_name]
    path = _REPO_ROOT / relpath
    if not path.is_file():
        _fail(f"frozen leaf not found: {path}")
    src = path.read_text(encoding="utf-8")
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            if (node.level or 0) != 0:
                _fail(f"frozen leaf {relpath} uses a relative import (refusing file-location load)")
            root = (node.module or "").split(".")[0]
            if root in ("nbpolar", "comparison_bench", "TimeTagger"):
                _fail(f"frozen leaf {relpath} imports frozen/package root {root!r} (refusing file-location load)")
        elif isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.split(".")[0] in ("nbpolar", "comparison_bench", "TimeTagger"):
                    _fail(f"frozen leaf {relpath} imports {alias.name!r} (refusing file-location load)")
    for banned in ("sc_decode", "genie_conditionals"):
        if banned in src:
            _fail(f"frozen leaf {relpath} mentions decoder entry {banned!r} (refusing load)")
    spec = importlib.util.spec_from_file_location(cache_name, str(path))
    module = importlib.util.module_from_spec(spec)
    # Register before exec: dataclass processing resolves the module via
    # sys.modules[cls.__module__]; without this the load fails.
    sys.modules[cache_name] = module
    try:
        spec.loader.exec_module(module)
    except Exception:
        sys.modules.pop(cache_name, None)
        raise
    cache[cache_name] = module
    return module


def _frozen_m2():
    """Stage-1 M2/M0 surface (accepted; CANDIDATE adapter, never baseline)."""
    return _frozen_leaf_module(
        "comparison_bench/src/comparison_bench/formal_ir/prior_m2.py",
        "m2_g1_frozen_prior_m2",
    )


def _frozen_prior():
    """Frozen layer-factorization helpers (derive_p1/derive_p2/...; unchanged)."""
    return _frozen_leaf_module(
        "comparison_bench/src/comparison_bench/formal_ir/nbpolar/prior.py",
        "m2_g1_frozen_nbpolar_prior",
    )


def pair_narrow_nearest_unique(tA_sorted, tB_sorted, offset, window):
    """(N) narrow nearest-unique pairing with census symbol mapping.

    Greedy monotonic 1-1 loop vendored literally from
    ``workspace/dual_rule_census_20260921.py::_count_nearest`` (symmetric
    window, offset applied to Alice raw timestamps); on a match the
    census symbol map applies: ``b = t // 200`` with
    ``tA_aligned = tA_raw + offset``, symbols ``(b_A % 1024,
    b_B % 1024)``. The (W) legacy rule is NEVER used for G1 science.
    Returns ``(alice, bob)`` int64 vectors, chronological.
    """
    a = np.asarray(tA_sorted, dtype=np.int64).ravel()
    b = np.asarray(tB_sorted, dtype=np.int64).ravel()
    aL = a.tolist()
    bL = b.tolist()
    off = int(offset)
    w = int(window)
    if w < 0:
        raise ValueError(f"pairing window must be non-negative, got {window!r}")
    i = j = 0
    na, nb = len(aL), len(bL)
    pa: list = []
    pb: list = []
    bw = G1_BIN_WIDTH_PS
    dd = G1_D
    while i < na and j < nb:
        dt = aL[i] + off - bL[j]
        if dt < -w:
            i += 1
        elif dt > w:
            j += 1
        else:
            pa.append(((aL[i] + off) // bw) % dd)
            pb.append((bL[j] // bw) % dd)
            i += 1
            j += 1
    return (np.asarray(pa, dtype=np.int64), np.asarray(pb, dtype=np.int64))


def chunk_frames(alice, bob, skip_frames, frame_pairs=G1_FRAME_PAIRS):
    """Apply skip, chunk into fixed frames, drop the trailing incomplete frame.

    Returns ``(frames_a, frames_b, ledger)`` with ``(n_complete,
    frame_pairs)`` int64 arrays and a ledger dict (skip/post-skip/drop
    counts). Pure; no I/O.
    """
    a = np.asarray(alice, dtype=np.int64).ravel()
    b = np.asarray(bob, dtype=np.int64).ravel()
    if a.shape != b.shape:
        raise ValueError(f"alice/bob length mismatch: {a.shape} vs {b.shape}")
    fp = int(frame_pairs)
    if fp <= 0:
        raise ValueError(f"frame_pairs must be positive, got {frame_pairs!r}")
    skip_pairs = int(skip_frames) * fp
    if skip_pairs < 0:
        raise ValueError(f"skip_frames must be non-negative, got {skip_frames!r}")
    if a.size < skip_pairs:
        raise ValueError(f"stream of {a.size} pairs shorter than skip {skip_pairs}")
    rest_a = a[skip_pairs:]
    rest_b = b[skip_pairs:]
    n_complete = int(rest_a.size // fp)
    used = n_complete * fp
    ledger = {
        "skip_frames": int(skip_frames),
        "skip_pairs": skip_pairs,
        "preskip_pairs": int(a.size),
        "postskip_pairs": int(rest_a.size),
        "frame_pairs": fp,
        "complete_frames": n_complete,
        "used_pairs": used,
        "dropped_trailing_pairs": int(rest_a.size - used),
    }
    return (
        rest_a[:used].reshape(n_complete, fp),
        rest_b[:used].reshape(n_complete, fp),
        ledger,
    )


def build_counts_1024(alice, bob):
    """Paired symbols -> counts_ab ``[Alice,Bob]`` int64 ``(1024,1024)``."""
    a = np.asarray(alice, dtype=np.int64).ravel()
    b = np.asarray(bob, dtype=np.int64).ravel()
    if a.shape != b.shape:
        raise ValueError(f"alice/bob length mismatch: {a.shape} vs {b.shape}")
    if a.size == 0:
        raise ValueError("empty symbol vectors")
    if a.min() < 0 or a.max() > 1023 or b.min() < 0 or b.max() > 1023:
        raise ValueError("symbols out of [0,1023]")
    counts = np.zeros((G1_D, G1_D), dtype=np.int64)
    np.add.at(counts, (a, b), 1)
    return counts


def mod_tail_counts(alice, bob, mod):
    """Delta-mass triple under the frozen MOD (mirror of fit_m2_triple fit level).

    LINEAR_ONLY: wrap cells (0,1023)/(1023,0) count as tail
    (conservative); CIRCULAR: priced as +/-1 neighbours. Pure.
    """
    if mod not in MODES:
        raise ValueError(f"mod must be one of {list(MODES)}, got {mod!r}")
    a = np.asarray(alice, dtype=np.int64).ravel()
    b = np.asarray(bob, dtype=np.int64).ravel()
    if a.shape != b.shape:
        raise ValueError(f"alice/bob length mismatch: {a.shape} vs {b.shape}")
    n = int(a.size)
    if n == 0:
        raise ValueError("empty symbol vectors")
    n0 = int((a == b).sum())
    if mod == "LINEAR_ONLY":
        d = a - b
        n_plus = int((d == 1).sum())
        n_minus = int((d == -1).sum())
    else:
        d = (a - b) % G1_D
        n_plus = int((d == 1).sum())
        n_minus = int((d == G1_D - 1).sum())
    return {
        "n0": n0,
        "n_plus": n_plus,
        "n_minus": n_minus,
        "n_tail": n - n0 - n_plus - n_minus,
        "n_total": n,
        "mod": mod,
    }


def delta_profile(alice, bob):
    """Delta-mass profile linear AND circular (G1-2, descriptive, no gate).

    Linear bins cover -1023..1023 (offset -1023); circular signed bins
    cover -512..511 (offset -512). Summaries under both MOD values via
    :func:`mod_tail_counts`. Pure.
    """
    a = np.asarray(alice, dtype=np.int64).ravel()
    b = np.asarray(bob, dtype=np.int64).ravel()
    if a.shape != b.shape or a.size == 0:
        raise ValueError("alice/bob must be equal-length non-empty vectors")
    d_lin = a - b
    lin = np.bincount(d_lin + 1023, minlength=2047)
    d_circ = ((d_lin + 512) % G1_D) - 512
    circ = np.bincount(d_circ + 512, minlength=1024)
    return {
        "n": int(a.size),
        "linear_counts": [int(v) for v in lin],
        "linear_offset": -1023,
        "circular_counts": [int(v) for v in circ],
        "circular_offset": -512,
        "summaries": {
            "LINEAR_ONLY": mod_tail_counts(a, b, "LINEAR_ONLY"),
            "CIRCULAR": mod_tail_counts(a, b, "CIRCULAR"),
        },
    }


def clopper_pearson_upper(k, n, alpha=0.05):
    """One-sided exact upper limit: p solving P(X <= k | p) = alpha.

    Stdlib-only (log-domain binomial CDF + bisection; no scipy in the
    mandated venv). ``k >= n`` -> 1.0. Pure.
    """
    k = int(k)
    n = int(n)
    if n <= 0:
        raise ValueError(f"n must be positive, got {n!r}")
    if not 0 <= k <= n:
        raise ValueError(f"k must lie in 0..n, got k={k!r} n={n!r}")
    if k >= n:
        return 1.0
    if not 0 < alpha < 1:
        raise ValueError(f"alpha must lie in (0,1), got {alpha!r}")

    def _cdf_le(p):
        if p <= 0.0:
            return 1.0
        if p >= 1.0:
            return 0.0
        lp = math.log(p)
        lq = math.log1p(-p)
        ln = math.lgamma(n + 1)
        terms = [
            ln - math.lgamma(i + 1) - math.lgamma(n - i + 1) + i * lp + (n - i) * lq
            for i in range(k + 1)
        ]
        mx = max(terms)
        return min(1.0, math.fsum(math.exp(t - mx) for t in terms) * math.exp(mx))

    lo, hi = 0.0, 1.0
    for _ in range(80):
        mid = 0.5 * (lo + hi)
        if _cdf_le(mid) > alpha:
            lo = mid
        else:
            hi = mid
    return hi


def eval_delta_tail(n_tail, n, B_tail):
    """G1-dtail gate exactly per freeze §6 (CHAR only, frozen MOD decides wrap).

    Zero observations -> rule-of-three ``3/n``; else Clopper-Pearson
    upper. PASS iff U < B_tail; FAIL iff phat > B_tail; else
    INCONCLUSIVE (bounded negative, no proceed). Pure.
    """
    n_tail = int(n_tail)
    n = int(n)
    if n <= 0 or not 0 <= n_tail <= n:
        raise ValueError(f"need 0 <= n_tail <= n with n > 0, got {n_tail!r}/{n!r}")
    B = float(B_tail)
    p_hat = n_tail / n
    U = 3.0 / n if n_tail == 0 else clopper_pearson_upper(n_tail, n)
    if U < B:
        verdict = "PASS"
    elif p_hat > B:
        verdict = "FAIL"
    else:
        verdict = "INCONCLUSIVE"
    return {"p_hat": p_hat, "U": U, "n_tail": n_tail, "n": n, "B_tail": B, "verdict": verdict}


def eval_nll_gate(delta, delta_min):
    """G1-NLL gate exactly per freeze §6 (matched-CAL, descriptive only).

    PASS iff Δ > Δ_min; FAIL iff Δ <= 0; else INCONCLUSIVE. Pure.
    """
    d = float(delta)
    m = float(delta_min)
    if d > m:
        verdict = "PASS"
    elif d <= 0:
        verdict = "FAIL"
    else:
        verdict = "INCONCLUSIVE"
    return {"delta_bits": d, "delta_min_bits": m, "verdict": verdict}


def _bits_entropy(probs) -> float:
    p = np.asarray(probs, dtype=np.float64).ravel()
    p = p[p > 0]
    if p.size == 0:
        return 0.0
    return float(-np.sum(p * np.log2(p)))


def model_entropy_bits(joint, p_b, prior_mod):
    """Model-implied H1/H2/H_total via the UNCHANGED frozen derive helpers.

    ``p1 = derive_p1(joint)`` ``[U1,B]``, ``p2 = derive_p2(joint)``
    ``[U1,B,U2]``; expectations weighted by the CAL empirical Bob
    marginal ``p_b`` (the V49 raw-MLE population functional per
    troubleshooting: ``H1 = sum_b p_b H(P1)``,
    ``H2 = sum_b p_b sum_u1 P1(u1|b) H(P2)``). Bits. Pure.
    """
    j = np.asarray(joint, dtype=np.float64)
    if j.shape != (G1_D, G1_D):
        raise ValueError(f"joint must be (1024,1024), got shape {j.shape}")
    pb = np.asarray(p_b, dtype=np.float64).ravel()
    if pb.shape != (G1_D,) or not np.isfinite(pb).all() or (pb < 0).any():
        raise ValueError("p_b must be a finite non-negative length-1024 vector")
    if abs(float(pb.sum()) - 1.0) > 1e-9:
        raise ValueError("p_b must sum to 1")
    p1 = np.asarray(prior_mod.derive_p1(j), dtype=np.float64)
    p2 = np.asarray(prior_mod.derive_p2(j), dtype=np.float64)
    h1 = 0.0
    h2 = 0.0
    for bb in range(G1_D):
        w = float(pb[bb])
        if w == 0.0:
            continue
        h1 += w * _bits_entropy(p1[:, bb])
        row1 = p1[:, bb]
        for u in range(32):
            wu = float(row1[u])
            if wu == 0.0:
                continue
            h2 += w * wu * _bits_entropy(p2[u, bb, :])
    h1 = float(h1)
    h2 = float(h2)
    return {"H1_bits": h1, "H2_bits": h2, "H_total_bits": h1 + h2}


def heldout_nll_bits(joint, bob_frames, alice_frames, prior_mod):
    """Held-out per-symbol NLL (bits) through the frozen metric pipeline.

    ``build_p1_metrics`` / ``gather_p2_metrics`` (hard Alice ``u1`` for
    L2 scoring — oracle scoring of held-out truth, decoder-free) ->
    ``probs_to_symbol_metric(provenance=PRIOR_ONLY)`` per layer; NLL is
    ``-(logp1[u1] + logp2[u2]) / ln2`` averaged over held-out symbols.
    ``bob_frames``/``alice_frames`` are ``(F,P)`` int arrays. Pure.
    """
    bf = np.asarray(bob_frames, dtype=np.int64)
    af = np.asarray(alice_frames, dtype=np.int64)
    if bf.shape != af.shape or bf.ndim != 2 or bf.shape[1] == 0:
        raise ValueError(f"bob/alice frames must be equal non-empty (F,P), got {bf.shape}/{af.shape}")
    if bf.min() < 0 or bf.max() > 1023 or af.min() < 0 or af.max() > 1023:
        raise ValueError("frame symbols out of [0,1023]")
    j = np.asarray(joint, dtype=np.float64)
    if j.shape != (G1_D, G1_D):
        raise ValueError(f"joint must be (1024,1024), got shape {j.shape}")
    p1 = prior_mod.derive_p1(j)
    p2 = prior_mod.derive_p2(j)
    u1 = ((af >> 5) & 31).astype(np.int64)
    u2 = (af & 31).astype(np.int64)
    m1 = np.asarray(prior_mod.build_p1_metrics(bf, p1), dtype=np.float64).reshape(-1, 32)
    s1 = prior_mod.probs_to_symbol_metric(m1, provenance=prior_mod.Provenance.PRIOR_ONLY)
    l1 = -np.asarray(s1.logp)[np.arange(u1.size), u1.ravel()] / math.log(2)
    g2 = np.asarray(prior_mod.gather_p2_metrics(bf, u1, p2), dtype=np.float64).reshape(-1, 32)
    s2 = prior_mod.probs_to_symbol_metric(g2, provenance=prior_mod.Provenance.PRIOR_ONLY)
    l2 = -np.asarray(s2.logp)[np.arange(u2.size), u2.ravel()] / math.log(2)
    tot = l1 + l2
    return {
        "n_symbols": int(u1.size),
        "nll_mean_bits": float(tot.mean()),
        "nll_l1_bits": float(l1.mean()),
        "nll_l2_bits": float(l2.mean()),
    }


def segment_frame_lists(n_postskip):
    """Enumerate the freeze §4 segment lists over post-skip frames.

    Raises :class:`_InsufficientFrames` when the ledger holds fewer
    than ALLOCATED_FRAMES (freeze §4 ``block_formation_fallback``).
    Pure.
    """
    n = int(n_postskip)
    if n < ALLOCATED_FRAMES:
        raise _InsufficientFrames(
            f"post-skip ledger {n} < allocated {ALLOCATED_FRAMES}: "
            "COMPLETE-BLOCKS-ONLY else INSUFFICIENT => INCONCLUSIVE "
            "(never pad/reuse/shrink)"
        )
    return {name: list(range(s, e + 1)) for name, s, e in SEG_RANGES}


def disjointness_matrix(segments):
    """Pairwise-disjointness proof over named frame-ID lists (pure).

    ``segments`` maps name -> iterable of frame ids. Returns the
    segment ranges plus every pairwise overlap count and the
    ``all_disjoint`` flag; any overlap invalidates the run.
    """
    sets = {name: set(int(v) for v in ids) for name, ids in segments.items()}
    names = sorted(sets)
    pairwise = {}
    for ii in range(len(names)):
        for jj in range(ii + 1, len(names)):
            a, b = names[ii], names[jj]
            pairwise[f"{a}|{b}"] = len(sets[a] & sets[b])
    ranges = {
        name: [min(sets[name]), max(sets[name])] if sets[name] else []
        for name in names
    }
    return {
        "segments": ranges,
        "pairwise_overlap": pairwise,
        "all_disjoint": all(v == 0 for v in pairwise.values()),
    }


def remainder_split_ids(n_frames=REMAINDER_N_FRAMES):
    """Remainder mini-layout: 32 CAL + 69 held-out (chronological, pure)."""
    n = int(n_frames)
    if n != REMAINDER_N_FRAMES:
        raise ValueError(f"remainder population holds {REMAINDER_N_FRAMES} frames, got {n!r}")
    return {
        "cal_ids": list(range(0, REMAINDER_CAL_FRAMES)),
        "heldout_ids": list(range(REMAINDER_CAL_FRAMES, REMAINDER_N_FRAMES)),
    }


def _peak_rss_gib_advisory():
    """VmHWM-based peak RSS in GiB (advisory only; never a gate)."""
    try:
        with open("/proc/self/status", encoding="utf-8") as fh:
            for line in fh:
                if line.startswith("VmHWM:"):
                    kb = float(line.split()[1])
                    return kb / 1024.0**2
    except Exception:
        pass
    return None


def _read_timetags_production(acq_id):
    """Production timetag read: inventory primary ONLY (autofollow rule).

    Deferred TimeTagger shim + ``src.qkd_io`` import (import purity:
    never at module top). SHG `_2` is refused loudly here. Returns
    ``(tA_sorted, tB_sorted)`` int64 raw timestamps.
    """
    if acq_id == "20260113_SHG_Type2PPLN_3s_2" or str(acq_id).endswith("_2"):
        _fail(
            f"refusing protected acquisition {acq_id!r}: SHG `_2` is frozen "
            "for G3 (no G1/G2 contact of any kind)"
        )
    _ensure_timetagger_shim()
    from scripts.census_intake_20260921 import (  # deferred: runs its own shim+src import
        HW_A,
        HW_B,
        _acq_files,
    )
    from src.qkd_io.ttbin_pipeline import read_ttbin_events  # deferred

    prim, _cont = _acq_files(acq_id)
    if not prim.exists():
        _fail(f"raw file not found: {prim} (run from repo root)")
    try:
        ev = read_ttbin_events(prim)  # primary ONLY; FileReader auto-follows `.1`
    except Exception as exc:
        _fail(f"{acq_id}: FileReader(primary) failed: {exc}")
    ch = np.asarray(ev.channel).astype(np.int64)
    ts = np.asarray(ev.time_ps).astype(np.int64)
    del ev
    if ch.shape != ts.shape or ch.ndim != 1 or int(ch.size) == 0:
        _fail(f"{acq_id}: primary read self-inconsistent")
    total = int(ch.size)
    uniq, counts = np.unique(ch, return_counts=True)
    chan_hist = {int(k): int(v) for k, v in zip(uniq.tolist(), counts.tolist())}
    other = int(np.sum((ch != HW_A) & (ch != HW_B)))
    import gc as _gc

    tA = np.sort(ts[ch == HW_A])
    tB = np.sort(ts[ch == HW_B])
    del ch, ts
    _gc.collect()
    return {
        "tA": tA,
        "tB": tB,
        "n_events": total,
        "channel_hist": chan_hist,
        "other_count": other,
        "other_frac": other / total if total else 1.0,
        "primary": str(prim),
    }


def _align_frozen(tA, tB):
    """ONE frozen-params alignment call (scan 409600 / bin 100).

    Deferred estimator load (frozen
    ``src/workflow/export_joint_sequence_sidecar.py`` single function).
    Returns the estimator dict.
    """
    from scripts.census_intake_20260921 import _load_peak_estimator  # deferred

    peak_fn, _load_path = _load_peak_estimator()
    return peak_fn(
        np.asarray(tA, dtype=np.int64),
        np.asarray(tB, dtype=np.int64),
        scan_range_ps=G1_SCAN_RANGE_PS,
        bin_ps=G1_BIN_PS_ALIGN,
    )


def _yield_sweep_selfcheck(tA, tB, derived_offset):
    """Mandatory yield-vs-offset self-check ((W) sweep, self-check ONLY).

    The (W) legacy rule is used here exactly as in the census — as an
    alignment self-check, never for G1 science. Deferred import.
    """
    from scripts.census_intake_20260921 import yield_vs_offset  # deferred

    return yield_vs_offset(
        np.asarray(tA, dtype=np.int64),
        np.asarray(tB, dtype=np.int64),
        int(derived_offset),
    )


def _sweep_accept(sweep):
    """Yield-sweep self-check verdict under the census dual_rule convention.

    The frozen provenance (``dual_rule_census_20260921.py:239-247``,
    adopted by ``g1_freeze.md`` §2) treats within-one-coarse-step as
    PASS-with-note: a strict-exact-max miss is recorded as a note, and
    only a beyond-one-step miss is a self-check failure. (The intake
    ``yield_max_ok`` flag additionally demands strict plateau
    membership; the dual_rule convention governs here because the
    freeze's census values carry its PASS-with-note verdict.) Pure.
    """
    within = bool(sweep["within_one_step_of_max_ok"])
    strict = bool(sweep.get("strict_exact_max", sweep.get("plateau_membership_ok")))
    if within:
        note = ("derived offset at sweep maximum" if strict
                else "strict-exact-max miss recorded as note; "
                     "within-one-coarse-step treated as PASS-with-note per 2026-09-21 tasking")
    else:
        note = "SELF-CHECK MISS: derived offset beyond one coarse step of maximum"
    return within, note


def _tier(n_pairs):
    from scripts.census_intake_20260921 import (  # deferred
        TIER_FULL_MIN,
        TIER_REDUCED_MIN,
    )

    n_frames = int(n_pairs) // G1_FRAME_PAIRS
    if n_frames >= TIER_FULL_MIN:
        return "FULL"
    if n_frames >= TIER_REDUCED_MIN:
        return "REDUCED"
    return "INSUFFICIENT"


def _write_json(path: Path, obj: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2), encoding="utf-8")


def _closure_outputs(*, acq_id, out_root: Path, freeze, align, sweep, pairing,
                     ledger, segments, matrix, elapsed_s, _packet_dir=None):
    """Flush Phase-A closure artifacts (workspace + packet-dir config)."""
    contract = contract_for_freeze(freeze)
    gate = contract["repro_gate"]
    reserve = reserve_ids_for_ledger(ledger["complete_frames"])
    seg_text = " / ".join(f"{name} {s}-{e}" for name, s, e in SEG_RANGES)
    if reserve["ids"]:
        seg_text += f" / reserve {reserve['ids'][0]}-{reserve['ids'][-1]}"
    else:
        seg_text += f" / reserve empty ({reserve['note']})"
    g1 = {
        "packet": contract["packet"],
        "freeze": contract["freeze"],
        "mode": "closure-only",
        "acq_id": acq_id,
        "nature": "DESCRIPTIVE/NON-CLAIM, decoder-free; M2 CANDIDATE, never baseline",
        "align": align,
        "yield_sweep": sweep,
        "offset_applied_to_alice": int(align["peak_center_ps"]),
        "offset_sign_convention": "tA_aligned = tA_raw + peak_center_ps",
        "pairing": pairing,
        "reproduction_gate": {
            "expected": dict(gate),
            "observed": {
                "peak_center_ps": align["peak_center_ps"],
                "peak_sigma_ps": align["peak_sigma_ps"],
                "status": align["status"],
                "n_pairs": pairing["n_pairs"],
                "n_frames": pairing["n_frames"],
            },
            "match5": (
                align["peak_center_ps"] == gate["peak_center_ps"]
                and align["peak_sigma_ps"] == gate["peak_sigma_ps"]
                and align["status"] == gate["status"]
                and pairing["n_pairs"] == gate["n_pairs"]
                and pairing["n_frames"] == gate["n_frames"]
            ),
            "verdict": "REPRODUCED",
        },
        "ledger": ledger,
        "segments": {name: [ids[0], ids[-1]] for name, ids in segments.items()},
        "disjointness_all_disjoint": bool(matrix["all_disjoint"]),
        "timing": {
            "wall_s": elapsed_s,
            "wall_budget_s": BUDGET_CLOSURE_S,
            "rss_gib_peak_advisory": _peak_rss_gib_advisory(),
            "rss_budget_gib": BUDGET_RSS_GIB,
        },
    }
    _write_json(out_root / "g1.json", g1)
    _write_json(
        out_root / "cal_ids.json",
        {
            "acq_id": acq_id,
            "ledger_complete_frames": ledger["complete_frames"],
            "layout_rule": "g1_freeze.md §4 (0-based post-skip complete frames)",
            "a1_cal_ids": segments["a1_cal"],
            "cal_frame_ids": segments["cal32"],
            "char_frame_ids": segments["char"],
            "heldout_frame_ids": segments["heldout"],
            "eval_frame_ids": segments["eval"],
            "reserve_frame_ids": reserve["ids"],
            "reserve_note": reserve["note"],
            "disjointness_matrix": matrix,
        },
    )
    lines = [
        f"# {contract['label']} Phase-A closure run log — {contract['packet']}",
        "",
        f"acq: {acq_id}",
        f"mode: closure-only (zero NLL/gate science)",
        f"align: peak_center={align['peak_center_ps']} sigma={align['peak_sigma_ps']} "
        f"to_bg={align['peak_to_bg']} status={align['status']}",
        f"yield_sweep: at_derived={sweep['yield_at_derived']} max={sweep['yield_max']} "
        f"note={sweep.get('yield_note', sweep['yield_max_ok'])}",
        f"pairing (N) w={pairing['window']}: n_pairs={pairing['n_pairs']} "
        f"n_frames={pairing['n_frames']} tier={pairing['tier']}",
        "reproduction_gate: 5/5 exact (peak_center / sigma / status / n_pairs / n_frames)",
        f"ledger post-skip: {ledger['complete_frames']} complete frames "
        f"(allocated>={ALLOCATED_FRAMES} ok={ledger['complete_frames'] >= ALLOCATED_FRAMES})",
        f"segments: {seg_text}",
        f"disjointness all_disjoint={matrix['all_disjoint']}",
        f"wall_s={elapsed_s:.1f} (budget {BUDGET_CLOSURE_S}) "
        f"rss_peak_advisory_GiB={g1['timing']['rss_gib_peak_advisory']}",
        "",
        f"Outputs: g1.json cal_ids.json run_log.md (+ packet-dir {contract['config_name']}).",
    ]
    (out_root / "run_log.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    cfg = {k: freeze[k] for k in REQUIRED_FREEZE_KEYS if k in freeze}
    cfg["a1_cal_ids"] = segments["a1_cal"]
    cfg["cal_frame_ids"] = segments["cal32"]
    cfg["heldout_frame_ids"] = segments["heldout"]
    cfg["disjointness_matrix"] = matrix
    missing = _missing_freeze_keys(cfg)
    if missing:
        _fail(f"closure config missing keys: {', '.join(missing)}")
    # Contract-routed packet-dir emission (never the other contract's
    # dir). _packet_dir is the test-only override (tests MUST pass an
    # explicit fake dir; default None keeps the production routing).
    target_dir = Path(_packet_dir) if _packet_dir is not None else contract["packet_dir"]
    _write_json(target_dir / contract["config_name"], cfg)
    return g1


def run_closure(*, acq_id, out_root: Path, freeze, options, _read_timetags=None):
    """Phase-A freeze closure (SHG `_1`, ONE framing pass; decoder-free).

    No prior fitting, no NLL, no gates. Emits the workspace closure
    artifacts plus the complete packet-dir freeze-config (all 19 keys).
    Returns 0 on REPRODUCED; 1 (loud) on ALIGN/reproduction/ledger
    failures. Creates nothing on the failure paths before the point of
    evidence flush (partial g1.json is flushed for forensics).
    """
    import time as _time

    t0 = _time.time()
    read = _read_timetags or _read_timetags_production
    window = int(freeze["pairing_window_primary"])
    skip = int(freeze["skip_frames"])
    mod = str(freeze["mod_boundary"])

    got = read(acq_id)
    tA, tB = got["tA"], got["tB"]
    if float(got.get("other_frac", 0.0)) > 0.20:
        out_root.mkdir(parents=True, exist_ok=True)
        _write_json(
            out_root / "g1.json",
            {"acq_id": acq_id, "mode": "closure-only", "verdict": "CHANNEL_FAIL",
             "other_frac": got.get("other_frac"), "channel_hist": got.get("channel_hist")},
        )
        print(f"CLOSURE_CHANNEL_FAIL other_frac={got.get('other_frac')}", file=sys.stderr)
        return 1

    peak = _align_frozen(tA, tB)
    align = {
        "estimator_source": "src/workflow/export_joint_sequence_sidecar.py:715",
        "scan_range_ps": G1_SCAN_RANGE_PS,
        "bin_ps": G1_BIN_PS_ALIGN,
        "peak_center_ps": peak.get("peak_center_ps"),
        "peak_sigma_ps": peak.get("peak_sigma_ps"),
        "peak_to_bg": peak.get("peak_to_bg"),
        "status": peak.get("status"),
        "accept": bool(
            peak.get("status") == "ok"
            and peak.get("peak_to_bg") is not None
            and float(peak.get("peak_to_bg")) >= G1_PEAK_TO_BG_MIN
        ),
        "criterion": "status==ok AND peak_to_bg>=10 (unit-independent)",
    }
    if not align["accept"]:
        out_root.mkdir(parents=True, exist_ok=True)
        _write_json(out_root / "g1.json",
                    {"acq_id": acq_id, "mode": "closure-only",
                     "verdict": "ALIGN_FAIL", "align": align})
        print(f"CLOSURE_ALIGN_FAIL status={align['status']} to_bg={align['peak_to_bg']}",
              file=sys.stderr)
        return 1

    offset = int(align["peak_center_ps"])
    sweep = _yield_sweep_selfcheck(tA, tB, offset)
    sweep_ok, sweep["yield_note"] = _sweep_accept(sweep)
    if not sweep_ok:
        out_root.mkdir(parents=True, exist_ok=True)
        _write_json(out_root / "g1.json",
                    {"acq_id": acq_id, "mode": "closure-only",
                     "verdict": "ALIGN_INCONSISTENT", "align": align,
                     "yield_sweep": sweep})
        print(f"CLOSURE_ALIGN_INCONSISTENT offset={offset} "
              f"yield@derived={sweep['yield_at_derived']} max={sweep['yield_max']}",
              file=sys.stderr)
        return 1

    alice, bob = pair_narrow_nearest_unique(tA, tB, offset, window)
    del tA, tB
    n_pairs = int(alice.size)
    n_frames = n_pairs // G1_FRAME_PAIRS
    pairing = {
        "rule": "(N) narrow nearest-unique",
        "window": window,
        "offset_ps": offset,
        "n_pairs": n_pairs,
        "n_frames": n_frames,
        "tier": _tier(n_pairs),
        "frozen": {"d": G1_D, "bin_width_ps": G1_BIN_WIDTH_PS,
                   "period_ps": G1_PERIOD_PS, "frame_pairs": G1_FRAME_PAIRS},
    }
    gate = contract_for_freeze(freeze)["repro_gate"]
    repro_ok = (
        align["peak_center_ps"] == gate["peak_center_ps"]
        and align["peak_sigma_ps"] == gate["peak_sigma_ps"]
        and align["status"] == gate["status"]
        and n_pairs == gate["n_pairs"]
        and n_frames == gate["n_frames"]
    )
    if not repro_ok:
        out_root.mkdir(parents=True, exist_ok=True)
        _write_json(out_root / "g1.json",
                    {"acq_id": acq_id, "mode": "closure-only",
                     "verdict": "ALIGN_INCONSISTENT", "align": align,
                     "yield_sweep": sweep, "pairing": pairing,
                     "reproduction_expected": dict(gate)})
        print("CLOSURE_ALIGN_INCONSISTENT reproduction gate mismatch "
              f"(expected {gate}; observed peak={align['peak_center_ps']}/"
              f"{align['peak_sigma_ps']}/{align['status']} n_pairs={n_pairs} "
              f"n_frames={n_frames})", file=sys.stderr)
        return 1

    _, _, ledger = chunk_frames(alice, bob, skip)
    del alice, bob
    try:
        segments = segment_frame_lists(ledger["complete_frames"])
    except _InsufficientFrames as exc:
        out_root.mkdir(parents=True, exist_ok=True)
        _write_json(out_root / "g1.json",
                    {"acq_id": acq_id, "mode": "closure-only",
                     "verdict": "INSUFFICIENT", "align": align,
                     "pairing": pairing, "ledger": ledger,
                     "detail": str(exc)})
        print(f"CLOSURE_INSUFFICIENT {exc}", file=sys.stderr)
        return 1
    named = {
        "a1_cal": segments["a1_cal"],
        "cal32": segments["cal32"],
        "char": segments["char"],
        "heldout": segments["heldout"],
        "eval": segments["eval"],
    }
    matrix = disjointness_matrix(named)
    if not matrix["all_disjoint"]:
        _fail(f"closure segment overlap invalidates run: {matrix['pairwise_overlap']}")
    for key, want in (("a1_cal_ids", named["a1_cal"]),
                      ("cal_frame_ids", named["cal32"]),
                      ("heldout_frame_ids", named["heldout"])):
        if list(freeze.get(key)) != want:
            _fail(f"closure input freeze {key} != §4 rule enumeration "
                  "(bootstrap the input config from the frozen rules verbatim)")

    elapsed = _time.time() - t0
    _closure_outputs(acq_id=acq_id, out_root=out_root, freeze=freeze,
                     align=align, sweep=sweep, pairing=pairing,
                     ledger=ledger, segments=named,
                     matrix=matrix, elapsed_s=elapsed)
    if elapsed > BUDGET_CLOSURE_S:
        print(f"CLOSURE_BUDGET_EXCEEDED wall_s={elapsed:.1f} > {BUDGET_CLOSURE_S}",
              file=sys.stderr)
        return 1
    print(f"CLOSURE_REPRODUCED acq={acq_id} n_pairs={n_pairs} "
          f"postskip_frames={ledger['complete_frames']} wall_s={elapsed:.1f}")
    return 0


def run_remainder_check(*, out_root: Path, freeze, alice, bob):
    """Remainder NLL/H-only check (32 CAL + 69 held-out; exempt path).

    Takes caller-supplied pair arrays (frozen derived pairs at Phase B;
    synthetic fixtures in tests). NO alignment, NO char sample, NO delta
    gate — exempt per freeze §1.2. Decoder-free. Returns 0.
    """
    import time as _time

    t0 = _time.time()
    mod = str(freeze["mod_boundary"])
    a = np.asarray(alice, dtype=np.int64).ravel()
    b = np.asarray(bob, dtype=np.int64).ravel()
    if a.shape != b.shape:
        raise ValueError(f"alice/bob length mismatch: {a.shape} vs {b.shape}")
    if a.size != REMAINDER_N_FRAMES * G1_FRAME_PAIRS:
        raise ValueError(
            f"remainder population holds {REMAINDER_N_FRAMES * G1_FRAME_PAIRS} pairs, "
            f"got {a.size}"
        )
    fa = a.reshape(REMAINDER_N_FRAMES, G1_FRAME_PAIRS)
    fb = b.reshape(REMAINDER_N_FRAMES, G1_FRAME_PAIRS)
    split = remainder_split_ids()
    m2_mod = _frozen_m2()
    prior_mod = _frozen_prior()
    cal_a = fa[split["cal_ids"]].ravel()
    cal_b = fb[split["cal_ids"]].ravel()
    counts = build_counts_1024(cal_a, cal_b)
    triple = m2_mod.fit_m2_triple(counts, mod=mod)
    joint_m2 = m2_mod.build_m2_joint(triple["q0"], triple["q_plus1"], triple["q_minus1"], mod=mod)
    joint_m0 = m2_mod.build_m0_joint(counts)
    n_cal = float(counts.sum())
    p_b = counts.sum(axis=0) / n_cal
    ent_m2 = model_entropy_bits(joint_m2, p_b, prior_mod)
    ent_m0 = model_entropy_bits(joint_m0, p_b, prior_mod)
    h_cal = fa[split["heldout_ids"]]
    h_calb = fb[split["heldout_ids"]]
    nll_m2 = heldout_nll_bits(joint_m2, h_calb, h_cal, prior_mod)
    nll_m0 = heldout_nll_bits(joint_m0, h_calb, h_cal, prior_mod)
    delta = nll_m0["nll_mean_bits"] - nll_m2["nll_mean_bits"]
    gate = eval_nll_gate(delta, float(freeze.get("delta_min", 0.020)))
    elapsed = _time.time() - t0
    _write_json(out_root / "g1.json", {
        "population": REMAINDER_ACQ_ID,
        "scope": "NLL_H_COMPARISON_ONLY",
        "exemptions": ["G1-1_alignment_EXEMPT_frozen_derived_pairs",
                       "delta_tail_200k_EXEMPT_only_25856_pairs_available"],
        "mod": mod,
        "cal_frames": REMAINDER_CAL_FRAMES,
        "heldout_frames": REMAINDER_N_FRAMES - REMAINDER_CAL_FRAMES,
        "m2_triple": {k: (float(v) if isinstance(v, float) else v) for k, v in triple.items()},
        "H_M2_bits": ent_m2,
        "H_M0_bits": ent_m0,
        "NLL_M2_bits": nll_m2,
        "NLL_M0_bits": nll_m0,
        "nll_delta_bits": delta,
        "nll_gate": gate,
        "timing": {"wall_s": elapsed},
    })
    _write_json(out_root / "cal_ids.json", {
        "population": REMAINDER_ACQ_ID,
        "cal_ids": split["cal_ids"],
        "heldout_ids": split["heldout_ids"],
    })
    (out_root / "run_log.md").write_text(
        "# G1 remainder NLL/H check — NLL/H comparison only (exempt population)\n\n"
        f"cal=32 heldout=69 delta_bits={delta:.6f} gate={gate['verdict']} "
        f"wall_s={elapsed:.1f}\n",
        encoding="utf-8",
    )
    print(f"REMAINDER_DONE delta_bits={delta:.6f} gate={gate['verdict']} wall_s={elapsed:.1f}")
    return 0


def run_g1_science(*, acq_id, out_root: Path, freeze, options, _read_timetags=None):
    """Phase-B G1 execution (SHG `_1`; decoder-free; preregistered gates).

    Re-verifies the §6 reproduction gate bit-exact, then G1-1..G1-4:
    alignment record; pairing at W_P (+W_S sensitivity readout, no
    switching); δ-profile linear+circular + δtail gate on CHAR; CAL32
    FIT + matched-CAL held-out NLL + H tables both models + NLL gate.
    Returns 0 with all verdicts recorded (gates are descriptive).
    """
    import time as _time

    t0 = _time.time()
    read = _read_timetags or _read_timetags_production
    window_p = int(freeze["pairing_window_primary"])
    window_s = int(freeze["pairing_window_sensitivity"])
    skip = int(freeze["skip_frames"])
    mod = str(freeze["mod_boundary"])
    char_pairs = int(freeze["char_sample_pairs"])
    B_tail = float(freeze["B_tail"])
    delta_min = float(freeze["delta_min"])
    contract = contract_for_freeze(freeze)
    gate = contract["repro_gate"]
    label = contract["label"]

    got = read(acq_id)
    tA, tB = got["tA"], got["tB"]
    peak = _align_frozen(tA, tB)
    align = {
        "estimator_source": "src/workflow/export_joint_sequence_sidecar.py:715",
        "scan_range_ps": G1_SCAN_RANGE_PS,
        "bin_ps": G1_BIN_PS_ALIGN,
        "peak_center_ps": peak.get("peak_center_ps"),
        "peak_sigma_ps": peak.get("peak_sigma_ps"),
        "peak_to_bg": peak.get("peak_to_bg"),
        "status": peak.get("status"),
        "accept": bool(
            peak.get("status") == "ok"
            and peak.get("peak_to_bg") is not None
            and float(peak.get("peak_to_bg")) >= G1_PEAK_TO_BG_MIN
        ),
        "criterion": "status==ok AND peak_to_bg>=10 (unit-independent)",
    }
    if not align["accept"]:
        _fail(f"{label} ALIGN_FAIL status={align['status']} to_bg={align['peak_to_bg']}")
    offset = int(align["peak_center_ps"])
    sweep = _yield_sweep_selfcheck(tA, tB, offset)
    sweep_ok, sweep["yield_note"] = _sweep_accept(sweep)
    if not sweep_ok:
        _fail(f"{label} ALIGN_INCONSISTENT offset={offset} "
              f"yield@derived={sweep['yield_at_derived']} max={sweep['yield_max']}")

    alice, bob = pair_narrow_nearest_unique(tA, tB, offset, window_p)
    n_pairs = int(alice.size)
    n_frames = n_pairs // G1_FRAME_PAIRS
    repro = {
        "peak_center_ps": align["peak_center_ps"],
        "peak_sigma_ps": align["peak_sigma_ps"],
        "status": align["status"],
        "n_pairs": n_pairs,
        "n_frames": n_frames,
    }
    if not (repro["peak_center_ps"] == gate["peak_center_ps"]
            and repro["peak_sigma_ps"] == gate["peak_sigma_ps"]
            and repro["status"] == gate["status"]
            and repro["n_pairs"] == gate["n_pairs"]
            and repro["n_frames"] == gate["n_frames"]):
        _fail(f"{label} ALIGN_INCONSISTENT reproduction gate mismatch: {repro} != {gate}")

    # W_S sensitivity readout (no switching): counts + δ triple only.
    sens_a, sens_b = pair_narrow_nearest_unique(tA, tB, offset, window_s)
    del tA, tB
    sensitivity = {"window": window_s, "n_pairs": int(sens_a.size),
                   "triple": mod_tail_counts(sens_a, sens_b, mod)}
    del sens_a, sens_b

    frames_a, frames_b, ledger = chunk_frames(alice, bob, skip)
    del alice, bob
    try:
        segments = segment_frame_lists(ledger["complete_frames"])
    except _InsufficientFrames as exc:
        out_root.mkdir(parents=True, exist_ok=True)
        _write_json(out_root / "g1.json",
                    {"acq_id": acq_id, "verdict": "INSUFFICIENT",
                     "align": align, "ledger": ledger, "detail": str(exc)})
        print(f"{label}_INSUFFICIENT {exc}", file=sys.stderr)
        return 1
    named = {name: segments[name] for name, _, _ in SEG_RANGES}
    matrix = disjointness_matrix(
        {k: v for k, v in
         [("a1_cal", named["a1_cal"]), ("cal32", named["cal32"]),
          ("char", named["char"]), ("heldout", named["heldout"]),
          ("eval", named["eval"])]}
    )
    if not matrix["all_disjoint"]:
        _fail(f"{label} segment overlap invalidates run: {matrix['pairwise_overlap']}")

    char_a = frames_a[named["char"]].ravel()
    char_b = frames_b[named["char"]].ravel()
    if int(char_a.size) != char_pairs:
        _fail(f"CHAR sample {int(char_a.size)} != frozen char_sample_pairs {char_pairs}")
    prof = delta_profile(char_a, char_b)
    tail = mod_tail_counts(char_a, char_b, mod)
    dtail_gate = eval_delta_tail(tail["n_tail"], tail["n_total"], B_tail)

    m2_mod = _frozen_m2()
    prior_mod = _frozen_prior()
    cal_a = frames_a[named["cal32"]].ravel()
    cal_b = frames_b[named["cal32"]].ravel()
    counts = build_counts_1024(cal_a, cal_b)
    triple = m2_mod.fit_m2_triple(counts, mod=mod)
    joint_m2 = m2_mod.build_m2_joint(triple["q0"], triple["q_plus1"], triple["q_minus1"], mod=mod)
    joint_m0 = m2_mod.build_m0_joint(counts)
    n_cal = float(counts.sum())
    p_b = counts.sum(axis=0) / n_cal
    ent_m2 = model_entropy_bits(joint_m2, p_b, prior_mod)
    ent_m0 = model_entropy_bits(joint_m0, p_b, prior_mod)
    h_a = frames_a[named["heldout"]]
    h_b = frames_b[named["heldout"]]
    del frames_a, frames_b
    nll_m2 = heldout_nll_bits(joint_m2, h_b, h_a, prior_mod)
    nll_m0 = heldout_nll_bits(joint_m0, h_b, h_a, prior_mod)
    delta = nll_m0["nll_mean_bits"] - nll_m2["nll_mean_bits"]
    nll_gate = eval_nll_gate(delta, delta_min)
    elapsed = _time.time() - t0

    _write_json(out_root / "g1.json", {
        "packet": contract["packet"],
        "mode": contract["science_mode"],
        "acq_id": acq_id,
        "nature": "DESCRIPTIVE/NON-CLAIM, decoder-free; M2 CANDIDATE, never baseline",
        "align": align,
        "yield_sweep": sweep,
        "offset_applied_to_alice": offset,
        "offset_sign_convention": "tA_aligned = tA_raw + peak_center_ps",
        "pairing": {"rule": "(N) narrow nearest-unique", "window_primary": window_p,
                    "n_pairs": n_pairs, "n_frames": n_frames,
                    "sensitivity": sensitivity,
                    "frozen": {"d": G1_D, "bin_width_ps": G1_BIN_WIDTH_PS,
                               "period_ps": G1_PERIOD_PS, "frame_pairs": G1_FRAME_PAIRS}},
        "reproduction_gate": {"expected": dict(gate), "observed": repro,
                              "match5": True, "verdict": "REPRODUCED"},
        "ledger": ledger,
        "cal": {"n_frames": 32, "n_pairs": int(cal_a.size),
                "m2_triple": {k: (float(v) if isinstance(v, float) else v)
                              for k, v in triple.items()}},
        "H_M2_bits": ent_m2,
        "H_M0_bits": ent_m0,
        "NLL_M2_bits": nll_m2,
        "NLL_M0_bits": nll_m0,
        "nll_delta_bits": delta,
        "gates": {"delta_tail": dtail_gate, "nll": nll_gate},
        "timing": {"wall_s": elapsed, "wall_budget_s": BUDGET_G1_S,
                   "rss_gib_peak_advisory": _peak_rss_gib_advisory(),
                   "rss_budget_gib": BUDGET_RSS_GIB},
    })
    _write_json(out_root / "delta_profiles.json", {
        "acq_id": acq_id, "segment": "char", "n_pairs": int(char_a.size),
        "mod_frozen": mod, "profile": prof,
        "tail_gate": dtail_gate,
        "sensitivity_triple": sensitivity["triple"],
    })
    _write_json(out_root / "cal_ids.json", {
        "acq_id": acq_id, "layout_rule": "g1_freeze.md §4",
        "a1_cal_ids": named["a1_cal"], "cal_frame_ids": named["cal32"],
        "char_frame_ids": named["char"], "heldout_frame_ids": named["heldout"],
        "eval_frame_ids": named["eval"],
        "disjointness_matrix": matrix,
    })
    (out_root / "run_log.md").write_text(
        f"# {label} science run log — {contract['packet']}\n\n"
        f"acq: {acq_id}\n"
        f"reproduction_gate: 5/5 exact\n"
        f"delta_tail: phat={dtail_gate['p_hat']:.3e} U={dtail_gate['U']:.3e} "
        f"B={B_tail:.1e} verdict={dtail_gate['verdict']}\n"
        f"nll: M0={nll_m0['nll_mean_bits']:.6f} M2={nll_m2['nll_mean_bits']:.6f} "
        f"delta={delta:.6f} min={delta_min} verdict={nll_gate['verdict']}\n"
        f"H_M0={ent_m0['H_total_bits']:.6f} H_M2={ent_m2['H_total_bits']:.6f}\n"
        f"wall_s={elapsed:.1f} (budget {BUDGET_G1_S})\n",
        encoding="utf-8",
    )
    if elapsed > BUDGET_G1_S:
        print(f"{label}_BUDGET_EXCEEDED wall_s={elapsed:.1f} > {BUDGET_G1_S}", file=sys.stderr)
        return 1
    if dtail_gate["verdict"] == "FAIL":
        print(f"{label} recorded: delta-tail FAIL ⇒ premise fails on this source; "
              "NOT proceeding toward G2", file=sys.stderr)
    print(f"{label}_DONE acq={acq_id} dtail={dtail_gate['verdict']} nll={nll_gate['verdict']} "
          f"wall_s={elapsed:.1f}")
    return 0


def run_stage_g1_nll(*, acq_id: str, out_root: Path, freeze: dict, options: dict,
                     closure_only: bool = False, _read_timetags=None) -> int:
    """G1 held-out NLL entry (decoder-free; NO decoder call on any path).

    ``closure_only=True`` restricts the body to the Phase-A closure
    (frame ledger + segment lists + packet-dir freeze-config; zero
    NLL/gate science). Otherwise the full Phase-B G1 science runs
    (``remainder_101f`` takes the exempt NLL/H-only remainder path on
    caller-supplied pairs). ``_read_timetags`` is the injectable
    acquisition reader (tests MUST pass an explicit fake; default
    ``None`` selects the production FileReader path).
    """
    if acq_id == REMAINDER_ACQ_ID and not closure_only:
        if _read_timetags is None:
            _fail(
                f"remainder population {acq_id!r}: the frozen derived-pairs "
                "binding belongs to the Phase-B dispatch; refusing to invent "
                "an artifact path (pass pairs explicitly)"
            )
        kwargs = _read_timetags(acq_id)
        return run_remainder_check(out_root=out_root, freeze=freeze, **kwargs)
    if closure_only:
        return run_closure(acq_id=acq_id, out_root=out_root, freeze=freeze,
                           options=options, _read_timetags=_read_timetags)
    return run_g1_science(acq_id=acq_id, out_root=out_root, freeze=freeze,
                          options=options, _read_timetags=_read_timetags)


def _load_g2_decoder_chain():
    """Deferred production-only import of the frozen decoder chain.

    Loads the REAL frozen modules (``operational_f13``,
    ``operational_f13_replication`` (P17 procedure), ``two_layer``,
    ``transform``, ``algebra``, ``sc``, ``shared``) by file location
    through bare parent packages: the real ``formal_ir``/``nbpolar``
    ``__init__`` files are NEVER executed (the mandated venv has no
    pandas), and NO frozen file is modified. If pandas is missing, a
    fail-closed alias is installed: any attribute access raises
    ``ImportError`` loudly, so pandas can never silently affect numerics
    (the G2 path never touches it; ``shared.py`` uses ``pd`` only inside
    functions this path never calls, with lazy annotations). The frozen
    chunk contract (P11: ``sc._minus_block`` default exactly 512) is
    asserted fail-closed. Returns a namespace of frozen callables.

    Production path ONLY (called from ``run_stage_g2`` with
    ``_decode_chain=None``). Tests/selfcheck/closure MUST pass an
    explicit fake chain and never call this.
    """
    import importlib
    import importlib.util
    import types as _types

    base_formal = "comparison_bench.src.comparison_bench.formal_ir"
    base_nb = base_formal + ".nbpolar"
    formal_dir = (
        _REPO_ROOT / "comparison_bench" / "src" / "comparison_bench" / "formal_ir"
    )
    nb_dir = formal_dir / "nbpolar"
    for name, path in ((base_formal, formal_dir), (base_nb, nb_dir)):
        if name not in sys.modules:
            stub = _types.ModuleType(name)
            stub.__path__ = [str(path)]
            sys.modules[name] = stub
    if importlib.util.find_spec("pandas") is None and "pandas" not in sys.modules:
        class _FailClosedPandas(_types.ModuleType):
            def __getattr__(self, name):
                raise ImportError(
                    "pandas is not installed in the mandated venv; refusing "
                    f"pd use (attribute {name!r}) on the G2 decode path"
                )

        stub_pd = _FailClosedPandas("pandas")
        stub_pd.__version__ = "0-stub-fail-closed"
        sys.modules["pandas"] = stub_pd
    opf = importlib.import_module(base_nb + ".operational_f13")
    rep = importlib.import_module(base_nb + ".operational_f13_replication")
    tl = importlib.import_module(base_nb + ".two_layer")
    tf = importlib.import_module(base_nb + ".transform")
    alg = importlib.import_module(base_nb + ".algebra")
    sc_mod = importlib.import_module(base_nb + ".sc")
    shared = importlib.import_module(base_formal + ".shared")
    import inspect as _inspect

    try:
        chunk_default = _inspect.signature(sc_mod._minus_block).parameters[
            "chunk_rows"
        ].default
    except (KeyError, AttributeError, ValueError) as exc:
        _fail(f"frozen chunk contract drift: cannot read _minus_block signature: {exc}")
    if chunk_default != G2_CHUNK_ROWS:
        _fail(
            "frozen chunk contract drift: _minus_block chunk_rows default "
            f"{chunk_default!r} != frozen {G2_CHUNK_ROWS}"
        )
    return _types.SimpleNamespace(
        run_operational_block=opf.run_operational_block,
        classify_operational_outcome=opf.classify_operational_outcome,
        operational_seed_bits=opf.operational_seed_bits,
        verify_predecessor_construction=rep.verify_predecessor_construction,
        sc_decode=sc_mod.sc_decode,
        toeplitz_tag=shared.toeplitz_tag,
        labels_to_bits=tl.labels_to_bits,
        seed_bits_for=tl.seed_bits_for,
        polar_transform=tf.polar_transform,
        make_gf32=alg.make_gf32,
        disclosed_bits_per_coordinate=tl.DISCLOSED_BITS_PER_COORDINATE,
        tag_bits=tl.TAG_BITS,
        alpha=tl.ALPHA,
    )


def fit_g2_arm(arm, cal_a, cal_b, mod, m2_mod) -> dict:
    """Fit one arm's prior on its OWN sacrificed CAL (pure + frozen leaves).

    A1/A2 (incumbent, as-deployed): raw-MLE M0 via ``build_m0_joint``;
    B (CANDIDATE): ±1 triple via ``fit_m2_triple`` -> ``build_m2_joint``
    (frozen MOD). Returns the floored joint actually decoded with, the
    pre-floor raw table for the floor audit, and the triple (B only).
    Only the three frozen arm spellings route anywhere.
    """
    if arm not in G2_ARM_CAL:
        raise ValueError(f"unknown G2 arm {arm!r} (frozen arms: {list(G2_ARMS)})")
    a = np.asarray(cal_a, dtype=np.int64).ravel()
    b = np.asarray(cal_b, dtype=np.int64).ravel()
    if a.shape != b.shape:
        raise ValueError(f"alice/bob length mismatch: {a.shape} vs {b.shape}")
    counts = build_counts_1024(a, b)
    n_cal = int(counts.sum())
    if arm == "B_M2_32f_candidate":
        triple = m2_mod.fit_m2_triple(counts, mod=mod)
        joint = m2_mod.build_m2_joint(
            triple["q0"], triple["q_plus1"], triple["q_minus1"], mod=mod
        )
        d = np.arange(G1_D)
        raw = np.zeros((G1_D, G1_D), dtype=np.float64)
        raw[d, d] = float(triple["q0"])
        raw[(d + 1) % G1_D, d] = float(triple["q_plus1"])
        raw[(d - 1) % G1_D, d] = float(triple["q_minus1"])
        mode = "M2"
    else:
        triple = None
        joint = m2_mod.build_m0_joint(counts)
        mat = counts.astype(np.float64)
        n_b = mat.sum(axis=0)
        empty = n_b == 0
        denom = np.where(empty, 1.0, n_b)
        raw = mat / denom[None, :]
        if empty.any():
            raw[:, empty] = 1.0 / G1_D
        mode = "M0"
    return {
        "arm": arm,
        "mode": mode,
        "n_cal_pairs": n_cal,
        "triple": triple,
        "joint": np.asarray(joint, dtype=np.float64),
        "raw": raw,
    }


def _bind_g2_polar(polar_fn, field, alpha):
    """Bind the frozen polar call shape ``(vec, *, field, alpha)`` (pure).

    The frozen ``polar_transform`` requires keyword-only ``field``; this
    adapter binds the chain's field/alpha once so block code calls
    ``polar_fn(vec)``. No data contact; used by ``run_stage_g2`` with the
    production chain and by tests with a signature-strict fake.
    """
    _p, _f, _a = polar_fn, field, int(alpha)
    return lambda v, _p=_p, _f=_f, _a=_a: np.asarray(
        _p(np.asarray(v, dtype=np.int64), field=_f, alpha=_a), dtype=np.int64
    )


def run_g2_block(
    *,
    arm,
    block_index,
    eval_frames,
    bob,
    alice,
    fit,
    p1_table,
    p2_table,
    l1_order,
    l2_order,
    k1,
    k2,
    tag_master,
    eval_seed,
    chain,
    polar_fn,
    prior_mod,
) -> dict:
    """Decode ONE arm × EVAL block (scalar record; arrays never persisted).

    Operational path: two-layer causal SC by importing and calling the
    frozen ``run_operational_block`` (accepted chunked ``sc_decode``,
    chunk_rows=512 by the frozen default; 64-bit Toeplitz tag from
    ``tag_master``; ``exact`` = tag_pass AND label_match, ``undetected``
    isolated). Plus the G2 measurement set: ``oracle_l2_exact`` (third SC
    call, true-H-conditioned L2 metric, same disclosures — isolated
    diagnostic, never touches the operational outcome), first-error
    coordinate+layer, raw-zero/floor audit + log loss, true-H and
    candidate-H L2 NLL, disclosure bits, wall/RSS, SC/tag call counts.
    ``chain`` is the production loader namespace or an explicit fake
    (tests MUST pass a fake). Returns the scalar block record.
    """
    import time as _time

    t0 = _time.perf_counter()
    n = int(np.asarray(bob).size)
    views = g2_truth_views(alice, polar_fn)
    field = chain.make_gf32()
    label_bits = chain.labels_to_bits(views["labels"])
    l1_pos = np.asarray(l1_order, dtype=np.int64)[: int(k1)]
    l2_pos = np.asarray(l2_order, dtype=np.int64)[: int(k2)]
    calls = {"sc": 0, "tag": 0}

    def _tag_fn(bits, seed, tag_bits):
        calls["tag"] = int(calls.get("tag", 0)) + 1
        return chain.toeplitz_tag(bits, seed, tag_bits)

    res = chain.run_operational_block(
        n=n,
        stream_seed=int(eval_seed),
        block_index=int(block_index),
        bob=np.asarray(bob, dtype=np.int64),
        high_true=views["high"],
        low_true=views["low"],
        u1_true=views["u1"],
        u2_true=views["u2"],
        labels_true=views["labels"],
        labels_true_bits=np.asarray(label_bits),
        field=field,
        p1_table=np.asarray(p1_table, dtype=np.float64),
        p2_table=np.asarray(p2_table, dtype=np.float64),
        l1_order=[int(v) for v in list(l1_pos)],
        l2_order=[int(v) for v in list(l2_pos)],
        k1=int(k1),
        k2=int(k2),
        master=int(tag_master),
        tag_fn=_tag_fn,
        calls=calls,
    )
    # Oracle L2 (isolated diagnostic): true-high-conditioned metric, SAME
    # D2 disclosures, fresh SC call, ORACLE lineage. Never alters the
    # operational outcome; failure records None loudly, never silently.
    oracle_exact = None
    oracle_error = None
    try:
        g_or = np.asarray(
            prior_mod.gather_p2_metrics(
                np.asarray(bob, dtype=np.int64)[None, :],
                views["u1"][None, :],
                np.asarray(p2_table, dtype=np.float64),
            ),
            dtype=np.float64,
        ).reshape(-1, 32)
        s_or = prior_mod.probs_to_symbol_metric(
            g_or, provenance=prior_mod.Provenance.ORACLE_CONDITIONED
        )
        calls["sc"] = int(calls.get("sc", 0)) + 1
        sc_or = chain.sc_decode(
            s_or.logp,
            field=field,
            alpha=int(chain.alpha),
            known_positions=l2_pos,
            known_values=np.asarray(views["u2"], dtype=np.int64)[l2_pos],
        )
        oracle_exact = bool(
            np.array_equal(np.asarray(sc_or.x_hat), views["low"])
        )
    except Exception as exc:
        oracle_error = type(exc).__name__
    cand_u1 = None
    if getattr(res, "high_hat", None) is not None:
        cand_u1 = np.asarray(res.high_hat, dtype=np.int64).ravel()
    nll_true = g2_l2_nll_bits(
        np.asarray(p2_table, dtype=np.float64),
        np.asarray(bob, dtype=np.int64),
        views["u1"],
        views["u2"],
        prior_mod,
        prior_mod.Provenance.ORACLE_CONDITIONED,
    )
    nll_cand = g2_l2_nll_bits(
        np.asarray(p2_table, dtype=np.float64),
        np.asarray(bob, dtype=np.int64),
        cand_u1,
        views["u2"],
        prior_mod,
        prior_mod.Provenance.CANDIDATE_CONDITIONED,
    )
    first = g2_first_error(
        getattr(res, "high_hat", None),
        views["high"],
        getattr(res, "low_hat", None),
        views["low"],
    )
    floor = g2_floor_audit(
        fit["raw"],
        fit["joint"],
        views["labels"],
        np.asarray(bob, dtype=np.int64),
    )
    verdict = g2_exact_from(res.tag_pass, res.label_match)
    wall = _time.perf_counter() - t0
    return {
        "arm": arm,
        "block_index": int(block_index),
        "eval_frames": [int(eval_frames[0]), int(eval_frames[1])],
        "n": n,
        "outcome": str(res.outcome),
        "exact": bool(verdict["exact"]),
        "undetected": bool(verdict["undetected"]),
        "tag_pass": bool(verdict["tag_pass"]),
        "label_match": bool(verdict["label_match"]),
        "l1_exact": bool(res.l1_exact),
        "hard_l2_exact": bool(res.hard_l2_exact),
        "oracle_l2_exact": oracle_exact,
        "oracle_error": oracle_error,
        "pair_exact": bool(res.pair_exact),
        "first_error_coordinate": first["coordinate"],
        "first_error_layer": first["layer"],
        "n_raw_zero_hits": floor["n_raw_zero_hits"],
        "n_floor_lifted": floor["n_floor_lifted"],
        "floor_logloss_bits": floor["floor_logloss_bits"],
        "nll_l2_trueH_bits": (nll_true["nll_mean_bits"] if nll_true else None),
        "nll_l2_candH_bits": (nll_cand["nll_mean_bits"] if nll_cand else None),
        "l1_executed": bool(res.l1_executed),
        "l1_decode_failed": bool(res.l1_decode_failed),
        "l2_invoked": bool(res.l2_invoked),
        "l2_skipped_by_l1_failure": bool(res.l2_skipped_by_l1_failure),
        "l2_decode_failed": bool(res.l2_decode_failed),
        "tag_invoked": bool(res.tag_invoked),
        "key_dependent_bits": int(res.key_dependent_bits),
        "public_control_bits": int(res.public_control_bits),
        "nonfinite": bool(res.nonfinite),
        "truth_leak_violation": bool(res.truth_leak_violation),
        "l1_error_type": res.l1_error_type,
        "l2_error_type": res.l2_error_type,
        "wall_s": float(wall),
        "rss_gib_peak_advisory": _peak_rss_gib_advisory(),
        "sc_calls": int(calls.get("sc", 0)),
        "tag_fn_calls": int(calls.get("tag", 0)),
    }


def _g2_abort_record(arm, block_index, eval_frames) -> dict:
    """Scalar resource_abort record (budget stop; never decoded)."""
    return {
        "arm": arm,
        "block_index": int(block_index),
        "eval_frames": [int(eval_frames[0]), int(eval_frames[1])],
        "n": G2_N,
        "outcome": "resource_abort",
        "exact": False,
        "undetected": False,
        "tag_pass": False,
        "label_match": False,
        "l1_exact": False,
        "hard_l2_exact": False,
        "oracle_l2_exact": None,
        "oracle_error": "resource_abort",
        "pair_exact": False,
        "first_error_coordinate": None,
        "first_error_layer": None,
        "n_raw_zero_hits": 0,
        "n_floor_lifted": 0,
        "floor_logloss_bits": 0.0,
        "nll_l2_trueH_bits": None,
        "nll_l2_candH_bits": None,
        "l1_executed": False,
        "l1_decode_failed": False,
        "l2_invoked": False,
        "l2_skipped_by_l1_failure": False,
        "l2_decode_failed": False,
        "tag_invoked": False,
        "key_dependent_bits": 0,
        "public_control_bits": 0,
        "nonfinite": False,
        "truth_leak_violation": False,
        "l1_error_type": None,
        "l2_error_type": None,
        "wall_s": 0.0,
        "rss_gib_peak_advisory": _peak_rss_gib_advisory(),
        "sc_calls": 0,
        "tag_fn_calls": 0,
    }


def run_g2_eval(
    *,
    out_root: Path,
    frames_a,
    frames_b,
    eval_blocks,
    arms_fit,
    p_tables,
    l1_order,
    l2_order,
    k1,
    k2,
    tag_master,
    eval_seed,
    chain,
    polar_fn,
    prior_mod,
    budget_s=G2_BUDGET_S,
    budget_rss_gib=BUDGET_RSS_GIB,
) -> tuple:
    """Decode all arms × EVAL blocks; flush ``per_block_outcomes.jsonl``.

    ``frames_a``/``frames_b`` are post-skip complete-frame arrays;
    ``eval_blocks`` the frozen ``[[start,end]]`` list; ``arms_fit`` maps
    arm -> :func:`fit_g2_arm` record; ``p_tables`` maps arm ->
    ``(p1, p2)`` layer tables. ``chain`` is production or explicit fake.
    Budget stop (wall/RSS) marks remaining blocks ``resource_abort``
    (never padded, reused, or shrunk). Returns ``(records, metre)`` where
    ``metre`` carries elapsed wall, abort flag, and SC/tag totals.
    """
    import time as _time

    t0 = _time.time()
    fa = np.asarray(frames_a, dtype=np.int64)
    fb = np.asarray(frames_b, dtype=np.int64)
    if fa.shape != fb.shape or fa.ndim != 2:
        raise ValueError(f"frames must be equal (F,P), got {fa.shape}/{fb.shape}")
    records: list = []
    aborted = False
    sc_total = 0
    tag_total = 0
    for arm in G2_ARMS:
        fit = arms_fit[arm]
        p1, p2 = p_tables[arm]
        for b, (s, e) in enumerate(eval_blocks):
            if _time.time() - t0 > float(budget_s):
                aborted = True
            elif _peak_rss_gib_advisory() is not None and float(
                _peak_rss_gib_advisory()
            ) > float(budget_rss_gib):
                aborted = True
            if aborted:
                records.append(_g2_abort_record(arm, b, [s, e]))
                continue
            rec = run_g2_block(
                arm=arm,
                block_index=b,
                eval_frames=[s, e],
                bob=fb[s : e + 1].ravel(),
                alice=fa[s : e + 1].ravel(),
                fit=fit,
                p1_table=p1,
                p2_table=p2,
                l1_order=l1_order,
                l2_order=l2_order,
                k1=k1,
                k2=k2,
                tag_master=tag_master,
                eval_seed=eval_seed,
                chain=chain,
                polar_fn=polar_fn,
                prior_mod=prior_mod,
            )
            sc_total += rec["sc_calls"]
            tag_total += int(rec["tag_invoked"])
            records.append(rec)
    out_root.mkdir(parents=True, exist_ok=True)
    with open(out_root / "per_block_outcomes.jsonl", "w", encoding="utf-8") as fh:
        for rec in records:
            fh.write(json.dumps(rec, sort_keys=True) + "\n")
    metre = {
        "wall_s": _time.time() - t0,
        "budget_aborted": bool(aborted),
        "sc_calls": int(sc_total),
        "tag_invocations": int(tag_total),
    }
    return records, metre


def run_stage_g2(
    *,
    acq_id: str,
    out_root: Path,
    freeze: dict,
    options: dict,
    _read_timetags=None,
    _decode_chain=None,
    _frames_bundle=None,
    _config_path=None,
) -> int:
    """G2 one-shot three-arm decode (SHG `_1`, w=200/CIRCULAR; Tier-Y).

    Stage-keyed routing first: any freeze that is not the G2 packet's own
    ``g2_freeze_config.json`` (or not at window 200) exits 3
    ``STAGE_BODY_PENDING_FREEZE`` with zero data contact — the G2 body is
    pending for THAT freeze, never a silent window-only fallback, and no
    G1/G1R2 packet path is ever written. Under the G2 freeze: re-verify
    the G1R2 reproduction literals bit-exact (mismatch => loud STOP),
    verify the P16 construction (P17 procedure, pinned inner digest)
    BEFORE any SC call, fit per-arm priors on each arm's OWN sacrificed
    CAL, decode 14 EVAL blocks × 3 arms through the frozen operational
    path, and render the preregistered Wilson gate (``undetected``
    isolated). Returns 0 with the verdict recorded (SUCCESS/FAIL/
    INCONCLUSIVE are complete Tier-Y returns); 1 for INSUFFICIENT/budget
    stops (INCONCLUSIVE recorded); 2 for guard/mismatch refusals.

    ``_read_timetags``/``_decode_chain``/``_frames_bundle`` are the
    injectable seams: production passes none (FileReader + real frozen
    chain + real align/pair); tests MUST pass explicit fakes and never
    enter the production decoder.
    """
    import time as _time

    t0 = _time.time()
    # -- Stage-keyed routing (B3): not our freeze => exit 3, zero contact.
    # The route check runs BEFORE contract selection so a non-G2 freeze
    # name alone (even with a non-200 window) exits 3 without consulting
    # anything else.
    routed = check_g2_config_route(_config_path)
    if routed is not None:
        print(
            "STAGE_BODY_PENDING_FREEZE: " + routed + (
                f" (packet {G2_PACKET}; acq {acq_id}; "
                "zero data contact: nothing read, nothing created)"
            ),
            file=sys.stderr,
        )
        return 3
    contract = contract_for_freeze(freeze)
    if contract["label"] != "G1R2":
        print(
            "STAGE_BODY_PENDING_FREEZE: freeze window routes to "
            f"{contract['label']}, not the w=200 G1R2 science mechanics "
            "the G2 body requires "
            f"(packet {G2_PACKET}; acq {acq_id}; "
            "zero data contact: nothing read, nothing created)",
            file=sys.stderr,
        )
        return 3
    # -- G2 freeze-content pins (exit 2, listing; the freeze file is
    # authoritative but the body refuses drift on what it consumes).
    pins = [
        ("pairing_window_primary", 200),
        ("pairing_window_sensitivity", 500),
        ("skip_frames", 702),
        ("mod_boundary", "CIRCULAR"),
        ("g2_blocks", G2_BLOCKS),
        ("tag_master", G2_TAG_MASTER),
    ]
    bad_pins = [
        f"{key}={freeze.get(key)!r} != frozen {want!r}"
        for key, want in pins
        if freeze.get(key) != want
    ]
    if list(freeze.get("g2_arms", [])) != list(G2_ARMS):
        bad_pins.append(f"g2_arms={freeze.get('g2_arms')!r} != frozen {list(G2_ARMS)!r}")
    for key in (
        "cal_split_rule",
        "g2_success_rule",
        "g2_inconclusive_rule",
        "g2_fail_rule",
        "block_formation_fallback",
    ):
        want = {
            "cal_split_rule": G2_CAL_SPLIT_RULE,
            "g2_success_rule": G2_SUCCESS_RULE,
            "g2_inconclusive_rule": G2_INCONCLUSIVE_RULE,
            "g2_fail_rule": G2_FAIL_RULE,
            "block_formation_fallback": G2_FALLBACK_RULE,
        }[key]
        if freeze.get(key) != want:
            bad_pins.append(f"{key} != frozen literal")
    if bad_pins:
        _fail(
            "G2 freeze-content drift (refusing to run off-contract): "
            + "; ".join(bad_pins)
        )
    chain = _decode_chain or _load_g2_decoder_chain()
    # -- Construction identity BEFORE any SC call (P17 procedure, pinned
    # inner digest; wrapper-file sha differs — expected).
    try:
        identity = chain.verify_predecessor_construction(
            G2_CONSTRUCTION_PATH, expected_digest=G2_CONSTRUCTION_DIGEST
        )
    except Exception as exc:
        _fail(f"G2 construction identity FAILED: {exc}")
    l1_order = identity["l1_order"]
    l2_order = identity["l2_order"]
    if len(l1_order) != G2_N or len(l2_order) != G2_N:
        _fail(f"G2 orders length {len(l1_order)}/{len(l2_order)} != N={G2_N}")

    m2_mod = _frozen_m2()
    prior_mod = _frozen_prior()
    window = int(freeze["pairing_window_primary"])
    skip = int(freeze["skip_frames"])
    mod = str(freeze["mod_boundary"])

    if _frames_bundle is None:
        read = _read_timetags or _read_timetags_production
        got = read(acq_id)
        tA, tB = got["tA"], got["tB"]
        if float(got.get("other_frac", 0.0)) > 0.20:
            _fail(f"G2 CHANNEL_FAIL other_frac={got.get('other_frac')}")
        peak = _align_frozen(tA, tB)
        if not (
            peak.get("status") == "ok"
            and peak.get("peak_to_bg") is not None
            and float(peak.get("peak_to_bg")) >= G1_PEAK_TO_BG_MIN
        ):
            _fail(f"G2 ALIGN_FAIL status={peak.get('status')} to_bg={peak.get('peak_to_bg')}")
        offset = int(peak.get("peak_center_ps"))
        sweep = _yield_sweep_selfcheck(tA, tB, offset)
        sweep_ok, sweep["yield_note"] = _sweep_accept(sweep)
        if not sweep_ok:
            _fail(f"G2 ALIGN_INCONSISTENT offset={offset}")
        alice, bob = pair_narrow_nearest_unique(tA, tB, offset, window)
        del tA, tB
        n_pairs = int(alice.size)
        n_frames = n_pairs // G1_FRAME_PAIRS
        gate = contract["repro_gate"]
        if not (
            peak.get("peak_center_ps") == gate["peak_center_ps"]
            and peak.get("peak_sigma_ps") == gate["peak_sigma_ps"]
            and peak.get("status") == gate["status"]
            and n_pairs == gate["n_pairs"]
            and n_frames == gate["n_frames"]
        ):
            _fail(
                "G2 ALIGN_INCONSISTENT reproduction gate mismatch "
                f"(expected {gate}; observed peak={peak.get('peak_center_ps')}/"
                f"{peak.get('peak_sigma_ps')}/{peak.get('status')} "
                f"n_pairs={n_pairs} n_frames={n_frames})"
            )
        frames_a, frames_b, ledger = chunk_frames(alice, bob, skip)
        del alice, bob
        align_rec = {
            "peak_center_ps": peak.get("peak_center_ps"),
            "peak_sigma_ps": peak.get("peak_sigma_ps"),
            "status": peak.get("status"),
        }
    else:
        # Test-only bundle: explicit fake frames (synthetic; decoder-free
        # except the injected fake chain). Reproduction checks are skipped
        # (no census literals apply to synthetic fixtures); layout, CAL
        # fitting, metrics, NLL, floor audit, gate, and routing run real.
        frames_a = np.asarray(_frames_bundle["frames_a"], dtype=np.int64)
        frames_b = np.asarray(_frames_bundle["frames_b"], dtype=np.int64)
        ledger = {"complete_frames": int(_frames_bundle["ledger_complete"])}
        align_rec = {"peak_center_ps": 50, "status": "synthetic-bundle"}
    try:
        segments = segment_frame_lists(ledger["complete_frames"])
    except _InsufficientFrames as exc:
        out_root.mkdir(parents=True, exist_ok=True)
        verdict = {
            "packet": G2_PACKET,
            "mode": "g2-decode",
            "acq_id": acq_id,
            "verdict": "INCONCLUSIVE",
            "reason": f"INSUFFICIENT: {exc}",
            "fallback": G2_FALLBACK_RULE,
        }
        _write_json(out_root / "g2_summary.json", verdict)
        print(f"G2_INSUFFICIENT {exc}", file=sys.stderr)
        return 1
    for key, want in (
        ("a1_cal_ids", segments["a1_cal"]),
        ("cal_frame_ids", segments["cal32"]),
        ("heldout_frame_ids", segments["heldout"]),
    ):
        if list(freeze.get(key)) != want:
            _fail(
                f"G2 input freeze {key} != §4 rule enumeration "
                "(bootstrap the input config from the frozen rules verbatim)"
            )
    named = {name: segments[name] for name, _, _ in SEG_RANGES}
    matrix = disjointness_matrix(
        {k: named[k] for k in ("a1_cal", "cal32", "char", "heldout", "eval")}
    )
    if not matrix["all_disjoint"]:
        _fail(f"G2 segment overlap invalidates run: {matrix['pairwise_overlap']}")
    eval_blocks = g2_eval_blocks()
    if eval_blocks[-1][1] >= ledger["complete_frames"]:
        _fail(
            f"G2 EVAL {eval_blocks[-1]} beyond post-skip ledger "
            f"{ledger['complete_frames']} (never pad/reuse/shrink)"
        )

    arms_fit = {}
    p_tables = {}
    for arm in G2_ARMS:
        cal_ids = g2_cal_ids(arm)
        cal_a = frames_a[cal_ids].ravel()
        cal_b = frames_b[cal_ids].ravel()
        fit = fit_g2_arm(arm, cal_a, cal_b, mod, m2_mod)
        arms_fit[arm] = fit
        p_tables[arm] = (
            np.asarray(prior_mod.derive_p1(fit["joint"]), dtype=np.float64),
            np.asarray(prior_mod.derive_p2(fit["joint"]), dtype=np.float64),
        )
        del cal_a, cal_b
    polar_fn = getattr(chain, "polar_transform", None)
    if polar_fn is None:
        _fail("G2 decode chain lacks polar_transform")
    # The frozen polar_transform(symbols, *, field, alpha) requires the
    # keyword-only field: build it ONCE here and bind it (plus alpha) into
    # the wrapper. Field construction is decode-external (no data contact).
    try:
        _g2_field = chain.make_gf32()
        _g2_alpha = int(chain.alpha)
    except Exception as exc:
        _fail(f"G2 decode chain field/alpha unavailable: {exc}")
    _polar, _field, _alpha = polar_fn, _g2_field, _g2_alpha
    records, metre = run_g2_eval(
        out_root=out_root,
        frames_a=frames_a,
        frames_b=frames_b,
        eval_blocks=eval_blocks,
        arms_fit=arms_fit,
        p_tables=p_tables,
        l1_order=l1_order,
        l2_order=l2_order,
        k1=G2_K1,
        k2=G2_K2,
        tag_master=int(freeze["tag_master"]),
        eval_seed=G2_EVAL_SEED,
        chain=chain,
        polar_fn=_bind_g2_polar(_polar, _field, _alpha),
        prior_mod=prior_mod,
        budget_s=G2_BUDGET_S,
        budget_rss_gib=BUDGET_RSS_GIB,
    )
    del frames_a, frames_b
    by_arm = {}
    for arm in G2_ARMS:
        arm_recs = [r for r in records if r["arm"] == arm]
        by_arm[arm] = {
            "n_blocks": len(arm_recs),
            "exact": sum(1 for r in arm_recs if r["exact"]),
            "undetected": sum(1 for r in arm_recs if r["undetected"]),
            "outcomes": {o: sum(1 for r in arm_recs if r["outcome"] == o) for o in G2_OUTCOMES},
        }
    gate = eval_g2_gate(by_arm["B_M2_32f_candidate"]["exact"], by_arm["A2_M0_32f_matched"]["exact"])
    recount = recount_g2_disclosure(records)
    if recount["mismatches"]:
        _fail(f"G2 disclosure recount mismatch: {recount['mismatches']}")
    elapsed = _time.time() - t0
    summary = {
        "packet": G2_PACKET,
        "freeze": f"{G2_PACKET}/g2_freeze.md",
        "contract": {"window": window, "label": contract["label"], "mode": "g2-decode"},
        "acq_id": acq_id,
        "nature": "Tier-Y decision gate, decoder run; M2 CANDIDATE, never baseline",
        "align": align_rec,
        "ledger": ledger,
        "construction": {
            "path": str(G2_CONSTRUCTION_PATH),
            "inner_digest": G2_CONSTRUCTION_DIGEST,
            "k1": G2_K1,
            "k2": G2_K2,
            "n": G2_N,
        },
        "arms": {
            arm: {
                "mode": arms_fit[arm]["mode"],
                "n_cal_pairs": arms_fit[arm]["n_cal_pairs"],
                "triple": (
                    {k: (float(v) if isinstance(v, float) else v)
                     for k, v in arms_fit[arm]["triple"].items()}
                    if arms_fit[arm]["triple"] else None
                ),
                **by_arm[arm],
            }
            for arm in G2_ARMS
        },
        "gate": gate,
        "verdict": (
            gate["verdict"] if not metre["budget_aborted"] else "INCONCLUSIVE"
        ),
        "budget_aborted": bool(metre["budget_aborted"]),
        "disclosure_recount": recount,
        "caveats": G2_CAVEATS,
        "timing": {
            "wall_s": elapsed,
            "wall_budget_s": G2_BUDGET_S,
            "rss_gib_peak_advisory": _peak_rss_gib_advisory(),
            "rss_budget_gib": BUDGET_RSS_GIB,
        },
        "calls": {
            "sc_calls": metre["sc_calls"],
            "tag_invocations": metre["tag_invocations"],
        },
    }
    _write_json(out_root / "g2_summary.json", summary)
    _write_json(
        out_root / "cal_ids.json",
        {
            "acq_id": acq_id,
            "layout_rule": "g2_freeze.md §4 (0-based post-skip complete frames)",
            "a1_cal_ids": named["a1_cal"],
            "cal_frame_ids": named["cal32"],
            "char_frame_ids": named["char"],
            "heldout_frame_ids": named["heldout"],
            "eval_blocks": eval_blocks,
            "disjointness_matrix": matrix,
        },
    )
    (out_root / "run_log.md").write_text(
        f"# G2 one-shot run log — {G2_PACKET}\n\n"
        f"acq: {acq_id}\n"
        f"arms: A1 exact={by_arm['A1_M0_1024f_incumbent']['exact']}/14 "
        f"(descriptive) | A2 exact={by_arm['A2_M0_32f_matched']['exact']}/14 | "
        f"B exact={by_arm['B_M2_32f_candidate']['exact']}/14\n"
        f"gate: {gate['verdict']} "
        f"(B {gate['b']['lower']:.4f}-{gate['b']['upper']:.4f} vs "
        f"A2 {gate['a2']['lower']:.4f}-{gate['a2']['upper']:.4f})\n"
        f"undetected: A1={by_arm['A1_M0_1024f_incumbent']['undetected']} "
        f"A2={by_arm['A2_M0_32f_matched']['undetected']} "
        f"B={by_arm['B_M2_32f_candidate']['undetected']} (isolated, never success)\n"
        f"disclosure recount mismatches={recount['mismatches']}\n"
        f"sc_calls={metre['sc_calls']} tag_invocations={metre['tag_invocations']} "
        f"wall_s={elapsed:.1f} (budget {G2_BUDGET_S})\n",
        encoding="utf-8",
    )
    if metre["budget_aborted"] or elapsed > G2_BUDGET_S:
        print(f"G2_BUDGET_EXCEEDED wall_s={elapsed:.1f} > {G2_BUDGET_S}", file=sys.stderr)
        return 1
    print(
        f"G2_DONE acq={acq_id} verdict={summary['verdict']} "
        f"A2={by_arm['A2_M0_32f_matched']['exact']}/14 "
        f"B={by_arm['B_M2_32f_candidate']['exact']}/14 wall_s={elapsed:.1f}"
    )
    return 0


def _selfcheck() -> int:
    """Verify Stage-1 wiring using ONLY pure logic. Touches no data.

    Covers: freeze-config loading + missing-key detection, the
    ``--authorized`` guard, the out-root guards (forbidden trees +
    ``workspace/`` confinement), flag/freeze cross-check, the frozen
    319/6492 K pin, the G2 stage-keyed routing (non-G2 freeze exits 3
    ``STAGE_BODY_PENDING_FREEZE`` with zero data contact), and the G2
    pure helpers (Wilson gate, EVAL layout, first-error, floor audit,
    recount) plus one fake-chain G2 block (synthetic; production decoder
    never entered). Prints one PASS/FAIL line per check; returns 0
    iff all pass.
    """
    import contextlib
    import io
    import tempfile

    failures: list[str] = []

    def check(name: str, fn) -> None:
        try:
            fn()
        except AssertionError as exc:
            failures.append(f"{name}: {exc}")
            print(f"FAIL {name}: {exc}")
        except Exception as exc:
            failures.append(f"{name}: unexpected {type(exc).__name__}: {exc}")
            print(f"FAIL {name}: unexpected {type(exc).__name__}: {exc}")
        else:
            print(f"PASS {name}")

    print(f"selfcheck: numpy {np.__version__}; required keys: {len(REQUIRED_FREEZE_KEYS)}")

    def _expect_exit2(fn) -> str:
        buf = io.StringIO()
        try:
            with contextlib.redirect_stderr(buf):
                fn()
        except SystemExit as exc:
            assert exc.code == 2, f"exit code {exc.code!r}, want 2"
            return buf.getvalue()
        raise AssertionError("did not exit(2)")

    with tempfile.TemporaryDirectory(prefix="m2skel_selfcheck_") as td:
        tmp = Path(td)
        full = {k: f"value-{k}" for k in REQUIRED_FREEZE_KEYS}

        def t_complete_json_loads() -> None:
            p = tmp / "full.json"
            p.write_text(json.dumps(full), encoding="utf-8")
            got = load_freeze_config(p)
            assert set(REQUIRED_FREEZE_KEYS) <= set(got), "round-trip lost keys"

        def t_missing_two_keys_exit2_lists_exactly() -> None:
            drop = ["delta_min", "tag_master"]
            cfg = {k: v for k, v in full.items() if k not in drop}
            assert _missing_freeze_keys(cfg) == sorted(drop), (
                "pure helper must list exactly the dropped keys"
            )
            p = tmp / "missing2.json"
            p.write_text(json.dumps(cfg), encoding="utf-8")
            err = _expect_exit2(lambda: load_freeze_config(p))
            for k in drop:
                assert k in err, f"{k} not listed in: {err.strip()}"
            for k in REQUIRED_FREEZE_KEYS:
                if k not in drop:
                    assert k not in err, f"unexpected key {k} listed in: {err.strip()}"

        def t_null_counts_as_missing() -> None:
            cfg = dict(full)
            cfg["B_tail"] = None
            assert _missing_freeze_keys(cfg) == ["B_tail"], "explicit null must count as missing"

        def t_missing_file_exit2() -> None:
            err = _expect_exit2(lambda: load_freeze_config(tmp / "nope.json"))
            assert "not found" in err, f"unclear message: {err.strip()}"

        def t_bad_suffix_exit2() -> None:
            p = tmp / "f.txt"
            p.write_text(json.dumps(full), encoding="utf-8")
            err = _expect_exit2(lambda: load_freeze_config(p))
            assert "suffix" in err, f"unclear message: {err.strip()}"

        def t_yaml_branch() -> None:
            import importlib.util

            p = tmp / "f.yaml"
            p.write_text("B_tail: 1\n", encoding="utf-8")
            if importlib.util.find_spec("yaml") is None:
                err = _expect_exit2(lambda: load_freeze_config(p))
                assert "PyYAML" in err, f"unclear message: {err.strip()}"
            else:
                import yaml  # deferred, test-only

                p.write_text(yaml.safe_dump(dict(full)), encoding="utf-8")
                got = load_freeze_config(p)
                assert set(REQUIRED_FREEZE_KEYS) <= set(got), "yaml round-trip lost keys"

        def t_authorized_guard() -> None:
            buf = io.StringIO()
            try:
                with contextlib.redirect_stderr(buf):
                    _require_authorized(False)
            except SystemExit as exc:
                assert exc.code == 2, f"exit code {exc.code!r}, want 2"
            else:
                raise AssertionError("guard did not exit(2) without --authorized")
            assert "--authorized" in buf.getvalue(), "refusal must name --authorized"
            _require_authorized(True)  # must not raise

        def t_out_root_guard() -> None:
            assert _out_root_refusal(_REPO_ROOT / "results" / "x") is not None
            assert _out_root_refusal(_REPO_ROOT / "results") is not None
            assert (
                _out_root_refusal(
                    _REPO_ROOT / "comparison_bench" / "outputs_comparison" / "y"
                )
                is not None
            )
            assert (
                _out_root_refusal(tmp / "workspace" / "m2_prior_validation") is None
            )

        def t_g2_route_exit3_unrouted_zero_contact() -> None:
            # Stage-keyed routing (B3): a non-G2 freeze (Stage-1-era name +
            # window-500 contract) exits 3 with zero data contact — the G2
            # body is pending for THAT freeze, never a silent fallback.
            target = tmp / "never_created_g2"
            buf = io.StringIO()
            with contextlib.redirect_stderr(buf):
                rc = run_stage_g2(
                    acq_id="X", out_root=target, freeze=dict(full), options={},
                    _config_path=tmp / "freeze.json",
                )
            assert rc == 3, f"run_stage_g2 returned {rc!r}, want 3"
            assert "STAGE_BODY_PENDING_FREEZE" in buf.getvalue(), (
                "unrouted G2 freeze must name STAGE_BODY_PENDING_FREEZE"
            )
            assert not target.exists(), "unrouted G2 freeze created output"
            # G1/G1R2 packet-dir paths never route, even with a G2 name.
            for foreign in (
                G1_PACKET_DIR / G1_CONFIG_NAME,
                G1R2_PACKET_DIR / G1R2_CONFIG_NAME,
                G1_PACKET_DIR / G2_CONFIG_NAME,
            ):
                assert check_g2_config_route(foreign) is not None, foreign
            assert check_g2_config_route(None) is not None
            assert (
                check_g2_config_route(tmp / G2_CONFIG_NAME) is None
            ), "a G2-named temp freeze must route"

        def t_g2_pure_helpers() -> None:
            # EVAL layout: 14 blocks x 128 frames x 256 pairs = N=32768;
            # A1-CAL 262,144 pairs; A2/B-CAL 8,192 pairs.
            blocks = g2_eval_blocks()
            assert len(blocks) == 14, len(blocks)
            assert blocks[0] == [2398, 2525], blocks[0]
            assert blocks[-1] == [4062, 4189], blocks[-1]
            assert all(e - s + 1 == 128 for s, e in blocks)
            assert 128 * 256 == G2_N == 32768, (128 * 256, G2_N)
            assert 14 * G2_BLOCK_FRAMES * 256 == 14 * G2_N == 458752
            assert len(g2_cal_ids("A1_M0_1024f_incumbent")) * 256 == 262144
            assert len(g2_cal_ids("A2_M0_32f_matched")) * 256 == 8192
            assert len(g2_cal_ids("B_M2_32f_candidate")) * 256 == 8192
            assert g2_cal_ids("A1_M0_1024f_incumbent") == list(range(0, 1024))
            try:
                g2_cal_ids("A9")
            except ValueError as exc:
                assert "unknown G2 arm" in str(exc)
            else:
                raise AssertionError("unknown arm must raise")
            # Wilson boundaries: 0/14 clamps lower to 0, 14/14 upper to 1.
            z0 = wilson_interval(0, 14)
            assert z0["lower"] == 0.0 and 0.0 < z0["upper"] < 1.0, z0
            assert abs(z0["upper"] - 0.21533) < 1e-4, z0
            z14 = wilson_interval(14, 14)
            assert z14["upper"] == 1.0 and 0.0 < z14["lower"] < 1.0, z14
            assert abs(z14["lower"] - 0.78467) < 1e-4, z14
            for bad_k, bad_n in ((-1, 14), (15, 14), (3, 0)):
                try:
                    wilson_interval(bad_k, bad_n)
                except ValueError:
                    pass
                else:
                    raise AssertionError(f"wilson({bad_k},{bad_n}) must raise")
            # Gate: strict non-overlap SUCCESS; equal points FAIL;
            # better-point overlap INCONCLUSIVE.
            assert eval_g2_gate(14, 0)["verdict"] == "SUCCESS"
            assert eval_g2_gate(7, 7)["verdict"] == "FAIL"
            assert eval_g2_gate(0, 14)["verdict"] == "FAIL"
            assert eval_g2_gate(8, 7)["verdict"] == "INCONCLUSIVE"
            # exact/undetected isolation.
            assert g2_exact_from(True, True) == {
                "tag_pass": True, "label_match": True,
                "exact": True, "undetected": False,
            }
            assert g2_exact_from(True, False)["undetected"] is True
            assert g2_exact_from(True, False)["exact"] is False
            assert g2_exact_from(False, True)["exact"] is False
            # First-error coordinate AND layer.
            fe = g2_first_error(
                np.array([1, 2, 3]), np.array([1, 2, 3]),
                np.array([4, 5, 6]), np.array([4, 0, 6]),
            )
            assert fe == {"coordinate": 1, "layer": "L2"}, fe
            fe = g2_first_error(
                np.array([1, 9, 3]), np.array([1, 2, 3]),
                np.array([4, 5, 6]), np.array([4, 5, 6]),
            )
            assert fe == {"coordinate": 1, "layer": "L1"}, fe
            assert g2_first_error(None, None, None, None) == {
                "coordinate": None, "layer": None,
            }
            assert g2_first_error(
                np.array([1]), np.array([1]), np.array([2]), np.array([2])
            ) == {"coordinate": None, "layer": None}
            # Floor audit on a toy joint (raw zero hit + lifted cell).
            raw = np.full((1024, 1024), 0.5 / 1024)
            raw[7, 3] = 0.0
            raw[9, 3] = 1e-16
            joint = np.maximum(raw, 1e-15)
            joint = joint / joint.sum(axis=0, keepdims=True)
            fa = g2_floor_audit(
                raw, joint, np.array([7, 9, 5]), np.array([3, 3, 3])
            )
            assert fa["n_raw_zero_hits"] == 1, fa
            assert fa["n_floor_lifted"] == 1, fa
            assert fa["floor_logloss_bits"] > 40.0, fa
            # Disclosure recount: incremental vs literal recompute.
            recs = [
                {"key_dependent_bits": 5 * 319 + 5 * 6492 + 64,
                 "public_control_bits": 10 * 32768 + 63,
                 "tag_invoked": True, "l2_invoked": True},
                {"key_dependent_bits": 5 * 319,
                 "public_control_bits": 0,
                 "tag_invoked": False, "l2_invoked": False},
            ]
            assert recount_g2_disclosure(recs)["mismatches"] == []
            bad = [dict(recs[0], key_dependent_bits=1)]
            assert recount_g2_disclosure(bad)["mismatches"] != []

        def t_g2_fake_block() -> None:
            # One synthetic G2 block through an explicit FAKE chain
            # (production decoder never entered). Exercises wiring only.
            import types as _st

            prior_mod = _frozen_prior()
            m2_mod = _frozen_m2()
            n = 256
            rng = np.random.default_rng(20260922)
            alice = rng.integers(0, 1024, size=n).astype(np.int64)
            bob = rng.integers(0, 1024, size=n).astype(np.int64)
            fit = fit_g2_arm(
                "B_M2_32f_candidate", alice, bob, "CIRCULAR", m2_mod
            )
            assert fit["mode"] == "M2" and fit["triple"] is not None
            fit0 = fit_g2_arm(
                "A2_M0_32f_matched", alice, bob, "CIRCULAR", m2_mod
            )
            assert fit0["mode"] == "M0" and fit0["triple"] is None
            p1 = prior_mod.derive_p1(fit["joint"])
            p2 = prior_mod.derive_p2(fit["joint"])
            views = g2_truth_views(alice, lambda v: np.asarray(v).copy())
            assert views["labels"].tolist() == alice.tolist()
            assert (((views["high"] << 5) + views["low"]) == alice).all()

            truth = {}

            def _fake_run_block(**kw):
                truth.update(kw)
                calls = kw.get("calls")
                if calls is not None:
                    calls["sc"] = int(calls.get("sc", 0)) + 2
                tag_fn = kw.get("tag_fn")
                if tag_fn is not None:
                    tag_fn(b"0" * 10, b"1" * 73, 64)
                    tag_fn(b"0" * 10, b"1" * 73, 64)
                return _st.SimpleNamespace(
                    outcome="exact", tag_pass=True, label_match=True,
                    l1_exact=True, hard_l2_exact=True, pair_exact=True,
                    high_hat=np.array(kw["high_true"], copy=True),
                    low_hat=np.array(kw["low_true"], copy=True),
                    l1_executed=True, l1_decode_failed=False,
                    l2_invoked=True, l2_skipped_by_l1_failure=False,
                    l2_decode_failed=False, tag_invoked=True,
                    key_dependent_bits=5 * 319 + 5 * 6492 + 64,
                    public_control_bits=10 * n + 63,
                    nonfinite=False, truth_leak_violation=False,
                    l1_error_type=None, l2_error_type=None,
                )

            def _fake_sc(logp, *, field, alpha, known_positions, known_values):
                assert int(alpha) == 2
                return _st.SimpleNamespace(x_hat=np.zeros(logp.shape[0], dtype=np.int64))

            fake = _st.SimpleNamespace(
                run_operational_block=_fake_run_block,
                sc_decode=_fake_sc,
                toeplitz_tag=lambda bits, seed, tb: b"fake",
                make_gf32=lambda: object(),
                labels_to_bits=lambda lab: np.zeros(10 * len(lab), dtype=np.uint8),
                alpha=2,
            )
            rec = run_g2_block(
                arm="B_M2_32f_candidate", block_index=0,
                eval_frames=[2398, 2525], bob=bob, alice=alice, fit=fit,
                p1_table=p1, p2_table=p2,
                l1_order=list(range(n)), l2_order=list(range(n)),
                k1=3, k2=5, tag_master=G2_TAG_MASTER, eval_seed=G2_EVAL_SEED,
                chain=fake, polar_fn=lambda v: np.asarray(v).copy(),
                prior_mod=prior_mod,
            )
            assert rec["outcome"] == "exact" and rec["exact"] is True
            assert rec["undetected"] is False
            assert rec["sc_calls"] == 3, rec["sc_calls"]
            assert rec["tag_fn_calls"] == 2, rec["tag_fn_calls"]
            assert rec["key_dependent_bits"] == 5 * 319 + 5 * 6492 + 64
            assert truth["n"] == n and truth["master"] == G2_TAG_MASTER
            assert truth["k1"] == 3 and truth["k2"] == 5

        def t_g1_pure_helpers() -> None:
            import math as _math

            # Framing: skip + chunk + trailing-drop arithmetic.
            n = 3 * 4 + 2
            a = np.arange(n, dtype=np.int64) % 1024
            b = (np.arange(n, dtype=np.int64) * 7) % 1024
            fa, fb, led = chunk_frames(a, b, 1, 4)
            assert led["skip_pairs"] == 4 and led["postskip_pairs"] == n - 4
            assert led["complete_frames"] == (n - 4) // 4
            assert led["dropped_trailing_pairs"] == (n - 4) % 4
            assert fa.shape == (led["complete_frames"], 4)
            try:
                chunk_frames(a, b, 99, 4)
            except ValueError as exc:
                assert "shorter than skip" in str(exc)
            else:
                raise AssertionError("overskip must raise")

            # MOD tail counts: wrap cells are tail under LINEAR_ONLY.
            wa = np.array([5, 6, 0, 1023, 100], dtype=np.int64)
            wb = np.array([5, 5, 1023, 0, 200], dtype=np.int64)
            lin = mod_tail_counts(wa, wb, "LINEAR_ONLY")
            assert (lin["n0"], lin["n_plus"], lin["n_minus"], lin["n_tail"]) == (1, 1, 0, 3), lin
            cir = mod_tail_counts(wa, wb, "CIRCULAR")
            assert (cir["n0"], cir["n_plus"], cir["n_minus"], cir["n_tail"]) == (1, 2, 1, 1), cir
            try:
                mod_tail_counts(wa, wb, "WRAP")
            except ValueError as exc:
                assert "mod must be" in str(exc)
            else:
                raise AssertionError("bad MOD must raise")

            # Delta-tail gate: zero-obs rule-of-three; k=n upper is 1.0 FAIL.
            g0 = eval_delta_tail(0, 200192, 2.0e-4)
            assert g0["U"] == 3.0 / 200192 and g0["verdict"] == "PASS", g0
            assert clopper_pearson_upper(7, 7) == 1.0
            g1 = eval_delta_tail(7, 7, 2.0e-4)
            assert g1["verdict"] == "FAIL", g1
            u = clopper_pearson_upper(1, 10)
            assert 0.1 < u < 1.0, u
            assert clopper_pearson_upper(2, 10) > u, "CP upper must grow with k"
            gn = eval_nll_gate(0.03, 0.020)
            assert gn["verdict"] == "PASS"
            assert eval_nll_gate(0.0, 0.020)["verdict"] == "FAIL"
            assert eval_nll_gate(0.01, 0.020)["verdict"] == "INCONCLUSIVE"

            # Segments + disjointness on the frozen layout size.
            segs = segment_frame_lists(4256)
            assert [len(segs[k]) for k in ("a1_cal", "cal32", "char", "heldout", "eval")] == [
                1024, 32, 782, 560, 1792,
            ], [len(v) for v in segs.values()]
            mx = disjointness_matrix(
                {"a1_cal": segs["a1_cal"], "cal32": segs["cal32"],
                 "char": segs["char"], "heldout": segs["heldout"],
                 "eval": segs["eval"]}
            )
            assert mx["all_disjoint"] and set(mx["pairwise_overlap"]) != set()
            assert len(mx["pairwise_overlap"]) == 10
            bad = disjointness_matrix({"x": [1, 2], "y": [2, 3]})
            assert not bad["all_disjoint"] and bad["pairwise_overlap"] == {"x|y": 1}
            try:
                segment_frame_lists(4189)
            except _InsufficientFrames as exc:
                assert "INSUFFICIENT" in str(exc)
            else:
                raise AssertionError("short ledger must raise _InsufficientFrames")

            # Remainder mini-layout: 32 CAL + 69 held-out covering 101.
            sp = remainder_split_ids()
            assert len(sp["cal_ids"]) == 32 and len(sp["heldout_ids"]) == 69
            assert sp["cal_ids"][-1] + 1 == sp["heldout_ids"][0]
            assert set(sp["cal_ids"]) | set(sp["heldout_ids"]) == set(range(101))

            # Frozen-pairing literal spot check (hand-computed greedy trace).
            pa, pb = pair_narrow_nearest_unique(
                np.array([0, 250, 10000], dtype=np.int64),
                np.array([40, 300, 10060], dtype=np.int64),
                50, 500,
            )
            assert pa.tolist() == [0, 1, 50] and pb.tolist() == [0, 1, 50], (
                pa.tolist(), pb.tolist(),
            )

        def t_closure_only_store_true_ast() -> None:
            import ast as _ast

            tree = _ast.parse(Path(__file__).read_text(encoding="utf-8"))
            found = False
            for node in _ast.walk(tree):
                if isinstance(node, _ast.Call) and getattr(node.func, "attr", "") == "add_argument":
                    names = [
                        a.value
                        for a in node.args
                        if isinstance(a, _ast.Constant) and isinstance(a.value, str)
                    ]
                    kw = {k.arg: k.value for k in node.keywords}
                    action = kw.get("action")
                    if "--closure-only" in names:
                        found = True
                        assert isinstance(action, _ast.Constant) and action.value == "store_true", (
                            "t: --closure-only must be action='store_true'"
                        )
            assert found, "t: --closure-only argument not found"

        def t_cross_check_detects_mismatch() -> None:
            bad = {"window_primary": "501", "mod": "value-mod_boundary"}
            mism = _cross_check_mismatches(bad, dict(full))
            assert len(mism) == 1 and "pairing_window_primary" in mism[0], (
                f"must list exactly the mismatched key: {mism}"
            )
            good = {"window_primary": "value-pairing_window_primary"}
            assert _cross_check_mismatches(good, dict(full)) == [], (
                "matching flags must pass the cross-check"
            )
            listed = {"arms": "value-g2_arms"}
            assert _cross_check_mismatches(listed, dict(full)) == [], (
                "matching flags must pass the cross-check"
            )
            assert _norm_crosscheck(["A1", "A2", "B"]) == _norm_crosscheck("A1,A2,B"), (
                "freeze-list vs CLI-spelling arms must normalize equal"
            )

        def t_k_pin() -> None:
            _check_k_pin("319", "6492")  # must not raise
            _check_k_pin(None, None)  # absent flags are unchecked
            err = _expect_exit2(lambda: _check_k_pin("320", "6492"))
            assert "319" in err, f"k-pin refusal must name 319: {err.strip()}"

        def t_workspace_confinement() -> None:
            assert (
                _out_root_workspace_refusal(
                    _REPO_ROOT / "workspace" / "m2_prior_validation"
                )
                is None
            )
            outside = tmp / "ws_outside_probe"
            # tmp itself is a system temp dir here (outside repo workspace):
            assert _out_root_workspace_refusal(outside) is not None, (
                "system-temp roots must be refused (Stage-1 allows workspace/ only)"
            )

        def t_contracts_g1_g1r2() -> None:
            # Explicit window-keyed selection: 500 -> G1 legacy literals,
            # 200 -> G1R2 successor; anything else exits 2 (never a
            # default, never data-inferred).
            g1c = contract_for_window(500)
            assert g1c["repro_gate"] is REPRO_GATE, "G1 contract must keep the legacy gate object"
            assert g1c["repro_gate"]["n_pairs"] == 1269268, g1c["repro_gate"]
            assert g1c["repro_gate"]["n_frames"] == 4958, g1c["repro_gate"]
            assert g1c["packet_dir"] == G1_PACKET_DIR, g1c["packet_dir"]
            assert g1c["config_name"] == "g1_freeze_config.json", g1c["config_name"]
            assert g1c["label"] == "G1", g1c["label"]
            r2c = contract_for_window("200")
            assert r2c["repro_gate"]["n_pairs"] == 1259992, r2c["repro_gate"]
            assert r2c["repro_gate"]["n_frames"] == 4921, r2c["repro_gate"]
            assert r2c["packet_dir"] == G1R2_PACKET_DIR, r2c["packet_dir"]
            assert r2c["config_name"] == "g1r2_freeze_config.json", r2c["config_name"]
            assert r2c["label"] == "G1R2", r2c["label"]
            # Alignment literals stay shared across both contracts.
            for cc in (g1c, r2c):
                assert cc["repro_gate"]["peak_center_ps"] == 50, cc
                assert cc["repro_gate"]["peak_sigma_ps"] == 112.45189572400645, cc
                assert cc["repro_gate"]["status"] == "ok", cc
            # Ledger-driven reserve: G1 ledger -> legacy 4190-4255 range;
            # G1R2 ledger -> 4190-4218 (never 4219+); empty + note below
            # the allocation (never invented ids).
            assert reserve_ids_for_ledger(4256)["ids"] == list(range(4190, 4256)), (
                "G1 ledger must reproduce the legacy SEG_RESERVE range"
            )
            r200 = reserve_ids_for_ledger(4219)
            assert r200["ids"] == list(range(4190, 4219)) and r200["note"] == "", r200
            assert r200["ids"][-1] == 4218 and all(i < 4219 for i in r200["ids"])
            rempty = reserve_ids_for_ledger(4190)
            assert rempty["ids"] == [] and "never invented" in rempty["note"], rempty
            err = _expect_exit2(lambda: contract_for_window(300))
            assert "no science contract" in err, f"unclear message: {err.strip()}"
            err = _expect_exit2(lambda: contract_for_freeze({}))
            assert "no science contract" in err, f"unclear message: {err.strip()}"

        for name, fn in [
            ("complete-json-loads", t_complete_json_loads),
            ("missing-two-keys-exit2-lists-exactly", t_missing_two_keys_exit2_lists_exactly),
            ("null-counts-as-missing", t_null_counts_as_missing),
            ("missing-file-exit2", t_missing_file_exit2),
            ("bad-suffix-exit2", t_bad_suffix_exit2),
            ("yaml-branch", t_yaml_branch),
            ("authorized-guard", t_authorized_guard),
            ("out-root-guard", t_out_root_guard),
            ("stage-g2-route-exit3-unrouted-zero-contact", t_g2_route_exit3_unrouted_zero_contact),
            ("g2-pure-helpers", t_g2_pure_helpers),
            ("g2-fake-block", t_g2_fake_block),
            ("g1-pure-helpers", t_g1_pure_helpers),
            ("closure-only-store-true", t_closure_only_store_true_ast),
            ("cross-check-detects-mismatch", t_cross_check_detects_mismatch),
            ("k-pin-319-6492", t_k_pin),
            ("contracts-g1-g1r2", t_contracts_g1_g1r2),
            ("workspace-confinement", t_workspace_confinement),
        ]:
            check(name, fn)

    if failures:
        print(f"SELFCHECK_FAIL {len(failures)} failing check(s)")
        return 1
    print("SELFCHECK_PASS all Stage-1 wiring checks passed (no data touched)")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        description="M2 prior validation runner (Stage-1 guards real; G1 body "
        "decoder-free per g1_freeze.md; G2 one-shot three-arm decode per "
        "g2_freeze.md, stage-keyed freeze only).",
    )
    ap.add_argument(
        FLAG_G1,
        dest="stage_g1",
        action="store_true",
        help="G1 held-out NLL entry (packet §5). Decoder-free: --closure-only "
        "restricts to the Phase-A closure (ledger + lists + freeze-config); "
        "otherwise the full G1 science runs.",
    )
    ap.add_argument(
        FLAG_G2,
        dest="stage_g2",
        action="store_true",
        help="G2 one-shot three-arm decode (NBPOLAR-M2-PRIOR-G2-DECODE). "
        "Stage-keyed: runs ONLY under g2_freeze_config.json at window 200; "
        "any other freeze exits 3 STAGE_BODY_PENDING_FREEZE with zero data "
        "contact. M2 is a CANDIDATE, never the baseline.",
    )
    ap.add_argument(
        "--closure-only",
        action="store_true",
        default=False,
        help="G1 Phase-A only: restrict the body to closure outputs (frame "
        "ledger + segment lists + packet-dir freeze-config); zero NLL/gate "
        "science. Applies to --stage-g1-nll only.",
    )
    ap.add_argument(
        "--selfcheck",
        action="store_true",
        help="Verify skeleton wiring (pure logic only; touches no data).",
    )
    ap.add_argument(
        "--authorized",
        action="store_true",
        default=False,
        help="Stage modes run ONLY with --authorized (exits 2 if absent).",
    )
    ap.add_argument(
        "--freeze-config",
        default=None,
        help="JSON/YAML file with all 19 STATUS.yaml to_freeze keys (no defaults).",
    )
    ap.add_argument("--acq-id", default=None, help="Acquisition id (required for stage modes).")
    ap.add_argument("--out-root", default=None, help="Additive output root (required for stage modes).")
    # Descriptive per-stage flags for readability (packet §5/§6 commands);
    # authoritative values come from --freeze-config, never from these alone.
    ap.add_argument("--window-primary", default=None)
    ap.add_argument("--window-sensitivity", default=None)
    ap.add_argument("--skip", default=None)
    ap.add_argument("--mod", default=None)
    ap.add_argument("--char-pairs", default=None)
    ap.add_argument("--arms", default=None)
    ap.add_argument("--blocks", default=None)
    ap.add_argument("--k1", default=None)
    ap.add_argument("--k2", default=None)
    ap.add_argument("--tag-master", default=None)
    a = ap.parse_args(argv)

    if sum([bool(a.stage_g1), bool(a.stage_g2), bool(a.selfcheck)]) != 1:
        _fail(f"pick exactly one of {FLAG_G1} / {FLAG_G2} / --selfcheck")
    if a.selfcheck:
        return _selfcheck()
    # Authorization BEFORE any freeze-config parsing or file access.
    _require_authorized(bool(a.authorized))
    stage_flag = FLAG_G1 if a.stage_g1 else FLAG_G2
    if not a.freeze_config:
        _fail(f"--freeze-config <path> is required with {stage_flag} (all 19 to_freeze keys; never a default)")
    freeze = load_freeze_config(a.freeze_config)
    if not a.acq_id:
        _fail("--acq-id is required for stage modes")
    if not a.out_root:
        _fail("--out-root is required for stage modes")
    refusal = _out_root_refusal(a.out_root)
    if refusal is not None:
        print(f"ERROR: {refusal}", file=sys.stderr)
        raise SystemExit(2)
    confinement = _out_root_workspace_refusal(a.out_root)
    if confinement is not None:
        print(f"ERROR: {confinement}", file=sys.stderr)
        raise SystemExit(2)
    options = {
        k: getattr(a, k)
        for k in (
            "window_primary",
            "window_sensitivity",
            "skip",
            "mod",
            "char_pairs",
            "arms",
            "blocks",
            "k1",
            "k2",
            "tag_master",
        )
    }
    mismatches = _cross_check_mismatches(options, freeze)
    if mismatches:
        _fail(
            "flag/freeze-config mismatch (freeze file is authoritative, "
            "never an override): " + "; ".join(mismatches)
        )
    _check_k_pin(options.get("k1"), options.get("k2"))
    if a.closure_only and not a.stage_g1:
        _fail("--closure-only applies to --stage-g1-nll only")
    if a.stage_g1:
        return run_stage_g1_nll(
            acq_id=a.acq_id, out_root=Path(a.out_root), freeze=freeze, options=options,
            closure_only=bool(a.closure_only),
        )
    return run_stage_g2(
        acq_id=a.acq_id, out_root=Path(a.out_root), freeze=freeze, options=options,
        _config_path=Path(a.freeze_config),
    )


if __name__ == "__main__":
    raise SystemExit(main())
