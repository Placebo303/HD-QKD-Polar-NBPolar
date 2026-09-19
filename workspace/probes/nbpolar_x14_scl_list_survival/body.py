#!/usr/bin/env python3
"""NBPOLAR-X14-SCL-LIST-SURVIVAL - Tier-X probe body (frozen).

Synthetic-only, decoder-free except the single greedy-SC (L=1) mismatch
oracle run per block for Q2. Stdlib + numpy only. Read-only reuse of the
accepted nbpolar modules (empirical_channel sampling recipes, prior
derive/convert, algebra field, transform re-encode check, sc oracle).
No list decoder is implemented or imported. No protected artifact
(pairs/V25 counts/parquet/1M/1.5M/2M content) is stat'ed, opened, or
imported - enforced by own-path-only file access plus a sys.modules
blocklist assert. Only file written: results.json (this directory).
Two injected self-tests run under --selftest (no results.json write).

Frozen recipes (TASK_PACKET.md sections 2-3):
  f_full[A,B] (1024x1024): per column b, s=96 deterministic rare Alice
    symbols rare(b) = {(b + 37*k) mod 1024} (37 coprime to 1024, hence 96
    distinct, no RNG) carry pre-floor mass 0; the other 928 share one
    symmetric Dirichlet(alpha=1.0) draw per column from the table-master
    stream, then the P20M pipeline verbatim (raw-count MLE + 1e-15 floor
    via prior.apply_explicit_floor + column renormalize) to derive_p1 /
    derive_p2 (A = 32*U1 + U2, FULL_BOB_ONLY) to probs_to_symbol_metric.
  h_j = -log2 p2[u1_cond_j, b_j, u2_true_j] (frozen hazard atom).
  u1_cond = per-position argmax_u1 p1[u1,b] (operational hard-u1 path,
    decoder-free, P20S U1hard convention, ties to smallest index).
  pm = mean(h) over the disclosed prefix = first K2_synth=52 positions of
    the static table-marginal-E[h] order (positions iid under the model,
    so E[h] is position-free and the static order is the natural order).
  spike iff e_j = h_j - pm >= 2.0 bits; strata [2,4)/[4,8)/[8,inf) + ref.
  Q1 rank: true u2_j in p2[u1_cond_j,b_j,:] mass-descending order, ties to
    smallest index; survives(L) iff rank <= L, L in {4,8}. Q1b: true u1_j
    in p1[:,b_j] column order, same rule.
  Q2 F-median8 (user decision 2026-09-20; P20S section 3 verbatim):
    d_j = h_j - median(h over [j-8,j+8] clipped to [0,N)); detector =
    top-52 by d_j, baseline = top-52 by h_j (desc, ties to ascending
    index); coverage = selected-mismatch fraction of the single greedy
    sc_decode (L=1) run per block on hard-u1-conditioned L2 metrics.
"""

import argparse
import datetime
import hashlib
import json
import math
import os
import statistics
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", "..", ".."))

# Repo-root import of the accepted package (same convention as
# comparison_bench/tests/test_nbpolar_sc.py). No other sys.path edits.
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import numpy as np

from comparison_bench.src.comparison_bench.formal_ir.nbpolar import (
    algebra,
    empirical_channel,
    prior,
    sc,
    transform,
)

# NOTE: "parquet" is intentionally NOT a module fragment here: importing the
# accepted comparison_bench package surface transitively loads
# pandas.io.parquet (pandas submodule, no file touched). Protected parquet
# *files* can never be opened: _own_path confines every file access to the
# probe root, and no reader for protected formats is ever imported.
_REFUSED_MODULE_FRAGMENTS = (
    "pairs_loader",
    "toeplitz",
    "v25",
    "counts_ab",
    "raw_prior",
    "per_block_arm",
    "alt_l2_tables",
    "l2_alt_hold",
    "l2_alt_maintain",
    "l2_mechanism_probe",
)
for _mod_name in sys.modules:
    for _frag in _REFUSED_MODULE_FRAGMENTS:
        assert _frag not in _mod_name, (
            "X14_STOP_PROTECTED_PATH: refused module loaded: %s" % _mod_name
        )

# --- frozen constants (prereg line 2 verbatim values) ---
PROBE_ID = "NBPOLAR-X14-SCL-LIST-SURVIVAL"
TIER = "X"
STATUS_OK = "X14_PROBE_COMPLETE_DESCRIPTIVE_ONLY"
N = 256
Q = 32
ALPHA = 2
CHUNK_ROWS = 512
FLOOR = 1e-15
N_B = 1024
S_RARE = 96
RARE_STEP = 37  # coprime to 1024 -> 96 distinct rare symbols per column
K2_SYNTH = 52
MASTER_SEED = 2026092350
BLOCK_SEEDS = (
    2026092351,
    2026092352,
    2026092353,
    2026092354,
    2026092355,
    2026092356,
    2026092357,
)
BLOCKS_PER_SEED = 4
R_MEDIAN = 8
SPIKE_MARGIN = 2.0
BINS = ("[2,4)", "[4,8)", "[8,inf)", "nonsplike_ref")
LS = (4, 8)
COMMAND = (
    "cd /mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar && "
    "export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 "
    "MALLOC_ARENA_MAX=2 && timeout 300 "
    "/mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python "
    "workspace/probes/nbpolar_x14_scl_list_survival/body.py"
)
T0 = time.time()


class _Stop(Exception):
    def __init__(self, status, detail):
        super().__init__(detail)
        self.status = status
        self.detail = detail


# --- own-path-only file access (probe root only; never stat/open elsewhere) ---
def _own_path(rel):
    ap = os.path.normpath(os.path.join(HERE, rel))
    if ap != HERE and not ap.startswith(HERE + os.sep):
        raise _Stop("X14_STOP_PROTECTED_PATH", "path escapes probe root: %r" % rel)
    return ap


def _open_own(rel, mode):
    return open(_own_path(rel), mode, encoding="utf-8")


def _sha_file(rel):
    digest = hashlib.sha256()
    with open(_own_path(rel), "rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _check_prereg():
    try:
        with _open_own("prereg.md", "r") as handle:
            text = handle.read()
    except OSError as exc:
        raise _Stop("X14_STOP_PREREG_MISMATCH", "prereg.md unreadable: %s" % exc)
    for token in (
        "NBPOLAR-X14-SCL-LIST-SURVIVAL",
        "F-median8",
        "2026092350",
        "2026092351..2026092357",
        "K2_synth=52",
        "N=256",
        "timeout 300",
    ):
        if token not in text:
            raise _Stop(
                "X14_STOP_PREREG_MISMATCH", "prereg.md missing frozen token: %s" % token
            )
    return text


def _finish(payload):
    with _open_own("results.json", "w") as handle:
        json.dump(payload, handle, indent=1)
        handle.write("\n")
    return os.stat(_own_path("results.json")).st_size


def _stop_payload(status, detail, notes):
    try:
        import resource

        rss = int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * 1024)
    except Exception:
        rss = 0
    return {
        "probe_id": PROBE_ID,
        "tier": TIER,
        "status": status,
        "stop_detail": detail,
        "question": "Q1/Q1b top-L true-cell survival at frozen-hazard spikes + Q2 F-median8 local-spike vs mean-hazard coverage (descriptive only).",
        "command": COMMAND,
        "interpreter": {
            "executable": sys.executable,
            "version": sys.version.splitlines()[0],
        },
        "wall_s": time.time() - T0,
        "rss_bytes": rss,
        "decoder_calls": 0,
        "rng_calls": 0,
        "tag_calls": 0,
        "protected_opens_attempted": False,
        "writes": [],
        "notes": notes,
    }


def _stop(status, detail, notes):
    payload = _stop_payload(status, detail, notes)
    _finish(payload)
    sys.stderr.write("STOP %s: %s\n" % (status, detail))
    sys.exit(2)


# --- frozen channel recipe (section 3) ---
def _rare_symbols(b):
    return [(b + RARE_STEP * k) % N_B for k in range(S_RARE)]


def build_table(master_seed):
    """Build the synthetic joint + arm tables; return dict of arrays/scalars.

    Returns (info, rng_calls_table). info holds f_pre, f, p1, p2,
    floor_hit_measured, model_mean_hazard_bits.
    """
    rng = empirical_channel.make_rng(int(master_seed))
    rng_calls = 0
    f_pre = np.empty((N_B, N_B), dtype=np.float64)
    ones = np.ones(N_B - S_RARE, dtype=np.float64)
    for b in range(N_B):
        rare = _rare_symbols(b)
        if len(set(rare)) != S_RARE:
            raise _Stop(
                "X14_STOP_NONFINITE",
                "rare-symbol collision in column %d" % b,
            )
        draw = rng.dirichlet(ones)
        rng_calls += 1
        col = np.empty(N_B, dtype=np.float64)
        col[:] = 0.0
        mask = np.ones(N_B, dtype=bool)
        mask[np.asarray(rare, dtype=np.int64)] = False
        col[mask] = draw
        f_pre[:, b] = col
    # Accepted P20M pipeline verbatim: raw-count MLE (= f_pre holding the
    # planted zeros) + 1e-15 floor + column renormalize. (prior helpers
    # floor/renormalize over the last axis, which is the Bob axis here, so
    # the column renormalization is written explicitly.)
    f = np.maximum(f_pre, FLOOR)
    f /= f.sum(axis=0, keepdims=True)
    if not (np.isfinite(f).all() and (f > 0).all()):
        raise _Stop("X14_STOP_NONFINITE", "non-positive/nonfinite floored table")
    p1 = prior.derive_p1(f)
    p2 = prior.derive_p2(f)
    floor_hit_measured = float((f_pre == 0.0).sum()) / float(N_B * N_B)
    if not math.isfinite(floor_hit_measured):
        raise _Stop("X14_STOP_NONFINITE", "nonfinite floor-hit rate")
    # Table-marginal expected hazard E[h], sampling-free exact: E over
    # b ~ uniform, u2|b from the floored joint column, u1_cond = argmax p1.
    u1c_all = np.argmax(p1, axis=0)  # (1024,), ties to smallest
    acc = 0.0
    for b in range(N_B):
        col_u2 = f.reshape(Q, Q, N_B)[:, :, b].sum(axis=0)  # P(u2|b), sums to 1
        row = p2[int(u1c_all[b]), b, :]
        acc += float(np.sum(col_u2 * -np.log2(row)))
    model_mean = acc / float(N_B)
    if not math.isfinite(model_mean):
        raise _Stop("X14_STOP_NONFINITE", "nonfinite model-mean hazard")
    return (
        {
            "f_pre": f_pre,
            "f": f,
            "p1": p1,
            "p2": p2,
            "floor_hit_measured": floor_hit_measured,
            "model_mean_hazard_bits": model_mean,
        },
        rng_calls,
    )


def _ranks_in_mass_order(mass_rows, true_symbols):
    """1-based rank of each true symbol under mass-descending order.

    Ties break toward the smallest symbol index (the sc.py argmax
    convention) via stable descending argsort.
    """
    order = np.argsort(-np.asarray(mass_rows, dtype=np.float64), axis=1, kind="stable")
    true = np.asarray(true_symbols, dtype=np.int64).reshape(-1, 1)
    return (np.argmax(order == true, axis=1) + 1).astype(np.int64)


def _bin_of_excess(e):
    if e >= 8.0:
        return "[8,inf)"
    if e >= 4.0:
        return "[4,8)"
    if e >= SPIKE_MARGIN:
        return "[2,4)"
    return "nonsplike_ref"


def _median8(h):
    out = np.empty(N, dtype=np.float64)
    for j in range(N):
        lo = j - R_MEDIAN if j - R_MEDIAN > 0 else 0
        hi = j + R_MEDIAN + 1 if j + R_MEDIAN + 1 < N else N
        out[j] = float(np.median(h[lo:hi]))
    return out


def _topk(desc_score, k):
    idx = np.lexsort(
        (np.arange(N, dtype=np.int64), -np.asarray(desc_score, dtype=np.float64))
    )
    return idx[:k]


def run_block(rng, tables, field, counters):
    """Run one N=256 block; return per-position records + block scalars."""
    p_b = np.full(N_B, 1.0 / float(N_B), dtype=np.float64)
    bob, _, u1_true, u2_true = empirical_channel.sample_full_block(
        rng, p_b, tables["f"], Q, Q, N
    )
    counters["rng_calls"] += 2  # sample_bob + sample_full_block random draws
    p1 = tables["p1"]
    p2 = tables["p2"]
    u1_cond = np.argmax(p1[:, bob], axis=0)  # operational hard-u1, ties smallest
    mass_true = p2[u1_cond, bob, u2_true]
    if not (np.isfinite(mass_true).all() and (mass_true > 0).all()):
        raise _Stop("X14_STOP_NONFINITE", "non-positive/nonfinite true-cell mass")
    h = -np.log2(mass_true)
    pm = float(np.mean(h[:K2_SYNTH]))  # static order = natural order (E[h] flat)
    if not math.isfinite(pm):
        raise _Stop("X14_STOP_NONFINITE", "nonfinite prefix mean")
    excess = h - pm
    # Q1 / Q1b ranks (vectorized, sc.py tie convention).
    rank_q1 = _ranks_in_mass_order(p2[u1_cond, bob, :], u2_true)
    rank_q1b = _ranks_in_mass_order(p1[:, bob].transpose(1, 0), u1_true)
    # Q2 sole decoder use: one greedy sc_decode (L=1) on hard-u1 L2 metrics.
    l2_rows = p2[u1_cond, bob, :]
    metric = prior.probs_to_symbol_metric(
        l2_rows,
        conditioning=prior.Conditioning.FULL_BOB_ONLY,
        provenance=prior.Provenance.CANDIDATE_CONDITIONED,
    )
    res = sc.sc_decode(metric.logp, field=field, alpha=ALPHA)
    counters["decoder_calls"] += 1
    if not np.array_equal(
        res.x_hat, transform.polar_transform(res.u_hat, field=field, alpha=ALPHA)
    ):
        raise _Stop("X14_STOP_SC_CONSISTENCY", "sc re-encode check failed")
    mismatch = res.u_hat != u2_true
    # Q2 F-median8 detector vs mean-hazard baseline, top-52 each.
    d = h - _median8(h)
    sel_local = set(_topk(d, K2_SYNTH).tolist())
    sel_base = set(_topk(h, K2_SYNTH).tolist())
    mm = set(np.flatnonzero(mismatch).tolist())
    return {
        "excess": excess,
        "rank_q1": rank_q1,
        "rank_q1b": rank_q1b,
        "n_mismatch": len(mm),
        "n_mm_in_local": len(mm & sel_local),
        "n_mm_in_base": len(mm & sel_base),
    }


def _pooled_stats(values):
    xs = [float(v) for v in values if v is not None]
    if not xs:
        return {"n": 0, "mean": None, "sample_std": None, "min": None, "max": None}
    out = {
        "n": len(xs),
        "mean": float(statistics.fmean(xs)),
        "sample_std": float(statistics.stdev(xs)) if len(xs) >= 2 else None,
        "min": float(min(xs)),
        "max": float(max(xs)),
    }
    for key in ("mean", "sample_std", "min", "max"):
        val = out[key]
        if val is not None and not math.isfinite(val):
            raise _Stop("X14_STOP_NONFINITE", "nonfinite pooled stat %s" % key)
    return out


def _assert_finite_tree(node, path="root"):
    if node is None:
        return
    if isinstance(node, bool):
        return
    if isinstance(node, (int, np.integer)):
        return
    if isinstance(node, (float, np.floating)):
        if not math.isfinite(float(node)):
            raise _Stop("X14_STOP_NONFINITE", "nonfinite at %s" % path)
        return
    if isinstance(node, (str, np.str_)):
        return
    if isinstance(node, dict):
        for key, val in node.items():
            _assert_finite_tree(val, "%s.%s" % (path, key))
        return
    if isinstance(node, (list, tuple, np.ndarray)):
        for i, val in enumerate(list(node)):
            _assert_finite_tree(val, "%s[%d]" % (path, i))
        return
    raise _Stop(
        "X14_STOP_NONFINITE", "non-scalar leaf at %s: %r" % (path, type(node))
    )


def _to_plain(node):
    if node is None or isinstance(node, (str, bool)):
        return node
    if isinstance(node, (np.bool_,)):
        return bool(node)
    if isinstance(node, (np.integer,)):
        return int(node)
    if isinstance(node, (np.floating,)):
        return float(node)
    if isinstance(node, (int, float)):
        return node
    if isinstance(node, dict):
        return {str(k): _to_plain(v) for k, v in node.items()}
    if isinstance(node, (list, tuple)):
        return [_to_plain(v) for v in node]
    if isinstance(node, np.ndarray):
        return [_to_plain(v) for v in node.tolist()]
    raise _Stop("X14_STOP_NONFINITE", "non-plain leaf: %r" % type(node))


# --- injected self-tests (--selftest only; never write results.json) ---
def _selftest_rank_sanity():
    for true in (0, 7, 31):
        row = np.full((1, Q), 0.1 / 31.0, dtype=np.float64)
        row[0, true] = 0.9
        got = _ranks_in_mass_order(row, np.asarray([true], dtype=np.int64))
        assert int(got[0]) == 1, "peaked-row rank != 1 for true=%d" % true
    flat = np.full((1, Q), 1.0 / Q, dtype=np.float64)
    got = _ranks_in_mass_order(flat, np.arange(Q, dtype=np.int64))
    assert got.shape == (Q,), "uniform-row rank shape wrong"
    for k in range(Q):
        one = _ranks_in_mass_order(flat, np.asarray([k], dtype=np.int64))
        assert int(one[0]) == k + 1, "tie-break rank wrong at %d" % k
    print("SELFTEST rank-1-peaked-row+TIE-BREAK: PASS")


def _selftest_floor_smoke():
    tables, _ = build_table(MASTER_SEED)
    rate = tables["floor_hit_measured"]
    assert math.isfinite(rate) and 0.0 <= rate <= 1.0
    assert tables["p1"].shape == (Q, N_B) and tables["p2"].shape == (Q, N_B, Q)
    print(
        "SELFTEST floor-hit-rate-smoke: PASS (measured=%.6f vs pin=0.093750; "
        "recorded, never gated)" % rate
    )


def main():
    parser = argparse.ArgumentParser(prog="body.py")
    parser.add_argument("--selftest", action="store_true")
    args = parser.parse_args()
    if args.selftest:
        _selftest_rank_sanity()
        _selftest_floor_smoke()
        return 0

    _check_prereg()
    notes = [
        "Tier-X descriptive probe only: no thresholds, no pass/fail, no verdicts; SCL stays locked whatever the numbers say.",
        "u1_cond = per-position argmax_u1 p1 (operational hard-u1, decoder-free, P20S U1hard convention); single sc_decode(L=1) per block on hard-u1 L2 metrics = sole decoder use (Q2 mismatch oracle).",
        "Static order = natural order: positions iid under the model so table-marginal E[h] is position-free; prefix = first 52 positions; pm per block.",
        "Q1/Q1b per-seed fraction = survived/spike-positions pooled over the seed's 4 blocks; pooled = mean/sample-std(n-1)/range over 7 seeds; null when denominator is 0.",
        "Q2 per-seed coverage = selected-mismatches/mismatches pooled over the seed's 4 blocks (null when 0 mismatches); pooled = ratio-of-sums over all blocks plus seed mean/std/range.",
        "rng_calls counts Generator method calls: 1024 table-Dirichlet + 56 block-sampling = 1080; tag_calls = 0; zero protected opens.",
        "Measured floor-hit rate is over full f_full cells (planted-zero fraction); sampling never adjusts it.",
    ]
    try:
        tables, table_rng_calls = build_table(MASTER_SEED)
        counters = {"decoder_calls": 0, "rng_calls": int(table_rng_calls)}
        field = algebra.make_gf32()

        per_seed = {}
        for seed in BLOCK_SEEDS:
            rng = empirical_channel.make_rng(int(seed))
            surv_q1 = {b: {L: [0, 0] for L in LS} for b in BINS}
            surv_q1b = {b: {L: [0, 0] for L in LS} for b in BINS}
            spike_n = {b: 0 for b in BINS}
            mm_tot = mm_loc = mm_bas = 0
            for _ in range(BLOCKS_PER_SEED):
                blk = run_block(rng, tables, field, counters)
                for j in range(N):
                    b = _bin_of_excess(float(blk["excess"][j]))
                    spike_n[b] += 1
                    for L in LS:
                        s = surv_q1[b][L]
                        s[1] += 1
                        s[0] += 1 if int(blk["rank_q1"][j]) <= L else 0
                        t = surv_q1b[b][L]
                        t[1] += 1
                        t[0] += 1 if int(blk["rank_q1b"][j]) <= L else 0
                mm_tot += blk["n_mismatch"]
                mm_loc += blk["n_mm_in_local"]
                mm_bas += blk["n_mm_in_base"]
            seed_key = str(seed)
            q1_tab = {}
            q1b_tab = {}
            for b in BINS:
                for L in LS:
                    s = surv_q1[b][L]
                    q1_tab["%s|L%d" % (b, L)] = {
                        "frac": (s[0] / s[1]) if s[1] else None,
                        "n": s[1],
                    }
                    t = surv_q1b[b][L]
                    q1b_tab["%s|L%d" % (b, L)] = {
                        "frac": (t[0] / t[1]) if t[1] else None,
                        "n": t[1],
                    }
            per_seed[seed_key] = {
                "q1": q1_tab,
                "q1b": q1b_tab,
                "q2": {
                    "coverage_local_spike": (mm_loc / mm_tot) if mm_tot else None,
                    "coverage_mean_hazard": (mm_bas / mm_tot) if mm_tot else None,
                    "n_mismatch": mm_tot,
                },
                "spike_counts": dict(spike_n),
            }

        pooled_q1 = {}
        pooled_q1b = {}
        for b in BINS:
            for L in LS:
                key = "%s|L%d" % (b, L)
                pooled_q1[key] = _pooled_stats(
                    [per_seed[str(s)]["q1"][key]["frac"] for s in BLOCK_SEEDS]
                )
                pooled_q1b[key] = _pooled_stats(
                    [per_seed[str(s)]["q1b"][key]["frac"] for s in BLOCK_SEEDS]
                )
        q2_loc = [per_seed[str(s)]["q2"]["coverage_local_spike"] for s in BLOCK_SEEDS]
        q2_bas = [per_seed[str(s)]["q2"]["coverage_mean_hazard"] for s in BLOCK_SEEDS]
        mm_all = sum(per_seed[str(s)]["q2"]["n_mismatch"] for s in BLOCK_SEEDS)
        pooled_q2 = {
            "local_spike_seed_stats": _pooled_stats(q2_loc),
            "mean_hazard_seed_stats": _pooled_stats(q2_bas),
            "ratio_of_sums": {
                "n_mismatch_total": mm_all,
            },
        }
        pooled_spike = {
            b: sum(per_seed[str(s)]["spike_counts"][b] for s in BLOCK_SEEDS)
            for b in BINS
        }
        floor_pin = S_RARE / float(N_B)
        floor_recorded = 3063.0 / 32768.0
        payload = {
            "probe_id": PROBE_ID,
            "tier": TIER,
            "status": STATUS_OK,
            "question": "Q1/Q1b top-L true-cell survival at frozen-hazard spikes + Q2 F-median8 local-spike vs mean-hazard coverage (descriptive only).",
            "frozen": {
                "N": N,
                "q": Q,
                "alpha": ALPHA,
                "gf32_poly": 37,
                "chunk_rows": CHUNK_ROWS,
                "floor": FLOOR,
                "s_rare": S_RARE,
                "K2_synth": K2_SYNTH,
                "R_median": R_MEDIAN,
                "spike_margin_bits": SPIKE_MARGIN,
                "table_master_seed": MASTER_SEED,
                "block_seeds": list(BLOCK_SEEDS),
                "blocks_per_seed": BLOCKS_PER_SEED,
                "q2_detector": "F-median8: d_j = h_j - median(h over R=8 clipped natural neighborhood of j)",
            },
            "per_seed": per_seed,
            "pooled": {
                "q1": pooled_q1,
                "q1b": pooled_q1b,
                "q2": pooled_q2,
                "spike_counts_total": pooled_spike,
            },
            "floor_hit": {
                "measured": tables["floor_hit_measured"],
                "pin_planted": floor_pin,
                "recorded_real_block0": floor_recorded,
            },
            "model_mean_hazard_bits": tables["model_mean_hazard_bits"],
            "command": COMMAND,
            "interpreter": {
                "executable": sys.executable,
                "version": sys.version.splitlines()[0],
            },
            "env_pins": {
                "OPENBLAS_NUM_THREADS": os.environ.get("OPENBLAS_NUM_THREADS"),
                "OMP_NUM_THREADS": os.environ.get("OMP_NUM_THREADS"),
                "MKL_NUM_THREADS": os.environ.get("MKL_NUM_THREADS"),
                "MALLOC_ARENA_MAX": os.environ.get("MALLOC_ARENA_MAX"),
            },
            "wall_s": time.time() - T0,
            "decoder_calls": counters["decoder_calls"],
            "rng_calls": counters["rng_calls"],
            "tag_calls": 0,
            "protected_opens_attempted": False,
            "writes": [],
            "notes": notes,
            "prereg_sha256": _sha_file("prereg.md"),
            "body_sha256": _sha_file("body.py"),
        }
        # Ratio-of-sums pooled Q2 needs mismatch-weighted sums; recompute
        # exactly from per-seed counts (cov*n per seed).
        loc_hit = sum(
            (per_seed[str(s)]["q2"]["coverage_local_spike"] or 0.0)
            * per_seed[str(s)]["q2"]["n_mismatch"]
            for s in BLOCK_SEEDS
        )
        bas_hit = sum(
            (per_seed[str(s)]["q2"]["coverage_mean_hazard"] or 0.0)
            * per_seed[str(s)]["q2"]["n_mismatch"]
            for s in BLOCK_SEEDS
        )
        pooled_q2["ratio_of_sums"]["coverage_local_spike"] = (
            (loc_hit / mm_all) if mm_all else None
        )
        pooled_q2["ratio_of_sums"]["coverage_mean_hazard"] = (
            (bas_hit / mm_all) if mm_all else None
        )
        payload = _to_plain(payload)
        _assert_finite_tree(payload)
        size = _finish(payload)
        if size > 2 * 1024 * 1024:
            _stop(
                "X14_STOP_OVERSIZE",
                "results.json %d bytes > 2 MB" % size,
                notes,
            )
        payload["writes"] = [
            {
                "path": "workspace/probes/nbpolar_x14_scl_list_survival/results.json",
                "size_bytes": size,
            }
        ]
        payload["wall_s"] = time.time() - T0
        _assert_finite_tree(payload)
        _finish(payload)
        print(
            "X14 probe complete: %d blocks, decoder_calls=%d rng_calls=%d "
            "floor_hit=%.6f mismatches=%d" % (
                len(BLOCK_SEEDS) * BLOCKS_PER_SEED,
                counters["decoder_calls"],
                counters["rng_calls"],
                tables["floor_hit_measured"],
                mm_all,
            )
        )
        return 0
    except _Stop as exc:
        _stop(exc.status, exc.detail, notes)
        return 2


if __name__ == "__main__":
    sys.exit(main())
