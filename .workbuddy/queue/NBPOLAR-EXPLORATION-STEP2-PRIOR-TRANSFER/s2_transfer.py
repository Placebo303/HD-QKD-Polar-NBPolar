#!/usr/bin/env python3
"""Tier-X Step-2 transfer-prior probe builder (packet-local, stdlib + numpy).

Packet: NBPOLAR-EXPLORATION-STEP2-PRIOR-TRANSFER (as amended by AMENDMENT 3).
Frozen: the SAME native q-ary polar SC as Step-1 arm A (read-only reuse of
comparison_bench.formal_ir.nbpolar) on the Step-1 envelope (F4 channel,
n_sym=128, R grid, design seed, screening seeds); arms differ ONLY in the
initial-message priors: arm I = frozen M2 CAL32 triple verbatim + floor
1e-15 NOT renormalized; arm U = NO-INJECTION BASELINE = the true F4
channel belief (amendment 3 replaces the degenerate uniform arm, which was
a blind decoder by construction). Paired message+noise per (seed, block)
across arms. Synthetic only. Single invocation: design (deterministic re-design, G0 cross-check) -> gates -> paired probe ->
ONE end-of-run write of results.json + notes.md. Any gate failure exits
non-zero with NO builder writes to the output root. This file never imports
real data and never modifies comparison_bench/ (imports only).
"""

import argparse
import json
import os
import sys
import time

import numpy as np

# READ-ONLY reuse (F1). Import only; zero modification of comparison_bench/.
from comparison_bench.formal_ir.nbpolar.algebra import make_gf2m
from comparison_bench.formal_ir.nbpolar.transform import (
    polar_transform,
    polar_transform_reference,
)
from comparison_bench.formal_ir.nbpolar.sc import sc_decode
from comparison_bench.formal_ir.nbpolar import oracle as oracle_mod

# ---------------- Frozen constants (F1/F2/F5) ----------------
QS = (4, 8, 16)
PRIMS = {4: 0b111, 8: 0b1011, 16: 0b10011}
MS = {4: 2, 8: 3, 16: 4}
ALPHA = 2
N_SYM = 128
RS = (0.30, 0.40, 0.50, 0.60)
K_SYMS = (38, 51, 64, 77)
DESIGN_SEED = 2026092400
SCREEN_SEEDS = tuple(range(2026092401, 2026092417))  # 16 seeds
BLOCKS_PER_SEED = 64
N_BLOCKS = 1024
G3_SMOKE_BLOCKS = 256
DESIGN_MC_SAMPLES = 3000
TIE_TOL = 1e-9  # log-domain gap below which a coordinate is tie-tolerated

P_F4 = {  # TRUE channel F4 (F2): sampling law + design law + H/f basis
    "p0": 0.75,
    "p1": 0.24,
    "pm1": 0.005,
    "prest": 0.005,
}

# ---------------- Frozen M2 reference (F3): verbatim, never recomputed ----
M2_Q0 = 0.7562
M2_QP1 = 0.2419
M2_QM1 = 0.0018
M2_QREST = 0.0
M2_FLOOR = 1e-15  # applied, NOT renormalized (frozen floor rule)


# ---------------- Small helpers ----------------
def f4_pmf(q):
    p = np.zeros(q)
    p[0] = P_F4["p0"]
    p[1 % q] = P_F4["p1"]
    p[(q - 1) % q] = P_F4["pm1"]
    rest = [d for d in range(q) if d not in (0, 1 % q, (q - 1) % q)]
    assert len(rest) == q - 3
    for d in rest:
        p[d] = P_F4["prest"] / (q - 3)
    assert abs(p.sum() - 1.0) < 1e-12
    return p


def informed_pvec(q):
    """Frozen M2 triple verbatim (F3): q0 / q+1 / q-1 / rest 0."""
    p = np.zeros(q)
    p[0] = M2_Q0
    p[1 % q] = M2_QP1
    p[(q - 1) % q] = M2_QM1
    return p


def logp_informed_from_y(y, q):
    """log P_I(y|x') = log(max(p_{d=(y-x') mod q}, 1e-15)); NOT renormalized."""
    p = informed_pvec(q)
    return np.log(np.maximum(p[(y[:, None] - np.arange(q)[None, :]) % q],
                             M2_FLOOR))


def make_logp_true_channel(logpmf_true):
    """No-injection baseline builder (F4-arm-U, amendment 3).

    log P_U(y|x') = log P_F4(y|x'): the decoder uses the true synthetic
    channel belief (standard no-transfer-prior baseline). Replaces the
    degenerate uniform arm (log(1/q) is constant in y and x' — a blind
    decoder by construction; recorded packet history, no discriminative
    information).
    """
    logpmf_true = np.asarray(logpmf_true)

    def build(y, q):
        return logpmf_true[(y[:, None] - np.arange(q)[None, :]) % q]

    return build


def logp_true_from_y(y, logpmf_true, q):
    """TRUE F4 likelihood (design + H/f basis only; never a decode prior)."""
    return logpmf_true[(y[:, None] - np.arange(q)[None, :]) % q]


def h_delta_bits(pmf):
    return float(-(pmf[pmf > 0] * np.log2(pmf[pmf > 0])).sum())


def summarize(xs):
    xs = [float(v) for v in xs]
    n = len(xs)
    mean = sum(xs) / n
    var = sum((v - mean) ** 2 for v in xs) / (n - 1) if n > 1 else 0.0
    return {
        "series": xs,
        "mean": mean,
        "sample_std": float(np.sqrt(var)),
        "range": [min(xs), max(xs)],
        "n": n,
    }


# ---------------- Design: MC genie-SC entropy via sc_decode ----------------
# Verbatim Step-1 arm-A design (F1 "deterministic re-design"): TRUE F4
# likelihood, design seed 2026092400, top-K_sym. Priors F3/F4 enter ONLY
# at decode time, never at design time.
def design_native(field, q, pmf_true, logpmf_true):
    rng = np.random.default_rng(DESIGN_SEED)
    H = np.zeros(N_SYM)
    allpos = np.arange(N_SYM)
    for _ in range(DESIGN_MC_SAMPLES):
        u = rng.integers(0, q, size=N_SYM).astype(np.int64)
        x = polar_transform(u, field=field, alpha=ALPHA)
        d = rng.choice(q, size=N_SYM, p=pmf_true)
        y = (x + d) % q
        logp = logp_true_from_y(y, logpmf_true, q)
        # Genie (true-prefix) conditionals: disclose the full true word so
        # every decision row is P(U_i | y, u_<i true) under the recursion.
        res = sc_decode(
            logp,
            field=field,
            alpha=ALPHA,
            known_positions=allpos,
            known_values=u,
        )
        prow = np.exp(res.decision_metrics)
        with np.errstate(divide="ignore"):
            l2 = np.log2(prow, out=np.zeros_like(prow), where=prow > 0)
        H += -(np.where(prow > 0, prow * l2, 0.0)).sum(axis=1)
    H /= DESIGN_MC_SAMPLES
    order = np.argsort(H, kind="stable")
    infos = {}
    for R, K in zip(RS, K_SYMS):
        infos[R] = np.sort(order[:K])
    return infos, H


# ---------------- Batch q-ary codebooks (gates; Step-1 pattern) ------------
def qary_codebook(field, q, n):
    B = q**n
    U = np.empty((B, n), dtype=np.int64)
    for k in range(B):
        v = k
        for j in range(n - 1, -1, -1):
            U[k, j] = v % q
            v //= q
    addT = np.empty((q, q), dtype=np.int64)
    mulT = np.empty((q, q), dtype=np.int64)
    for a in range(q):
        for b in range(q):
            addT[a, b] = field.add(a, b)
            mulT[a, b] = field.mul(a, b)
    a = ALPHA
    C = U.copy()
    size = 1
    while size < n:
        step = 2 * size
        for base in range(0, n, step):
            for j in range(size):
                C[:, base + j] = addT[C[:, base + j], mulT[a, C[:, base + j + size]]]
        size *= 2
    return U, C


def check_codebook_vs_oracle(field, q, n, U, C):
    idx = list(range(U.shape[0])) if n == 2 else list(
        np.random.default_rng(777000 + q * 10 + n).choice(
            U.shape[0], size=min(64, U.shape[0]), replace=False
        )
    )
    for k in idx:
        ref = polar_transform_reference(U[k], field=field, alpha=ALPHA)
        if not np.array_equal(ref, C[k]):
            return False
    k = idx[0]
    if q**n <= oracle_mod.MAX_ORACLE_CANDIDATES:
        logp = np.zeros((n, q))
        s = oracle_mod.oracle_block_log_score(logp, U[k], field=field,
                                              alpha=ALPHA)
        if not np.isfinite(s):
            return False
    return True


def brute_successive_qary(logp, frozen, U, C):
    """Independent successive-MAP via exhaustive enumeration (no sc.py).

    Textbook-SC semantics: every future position (info AND frozen) is
    marginalized; only the already-decided prefix (past info decisions
    plus past frozen pins) constrains the candidates. This matches what
    sc_decode computes; a frozen-conditioned enumerator would disagree
    with any textbook SC decoder by definition, not by defect.
    """
    n = logp.shape[0]
    q = logp.shape[1]
    B = U.shape[0]
    S = np.zeros(B)
    for j in range(n):
        S += logp[j][C[:, j]]
    fz = np.zeros(n, dtype=bool)
    fz[list(frozen)] = True
    out = np.zeros(n, dtype=np.int64)
    gaps = {}
    mask = np.ones(B, dtype=bool)  # prefix only; future marginalized
    for i in range(n):
        if fz[i]:
            out[i] = 0
            mask &= U[:, i] == 0
            continue
        sc = np.empty(q)
        for c in range(q):
            m = mask & (U[:, i] == c)
            sc[c] = np.logaddexp.reduce(S[m]) if m.any() else -np.inf
        order = np.argsort(-sc, kind="stable")
        gaps[i] = float(sc[order[0]] - sc[order[1]])
        out[i] = int(order[0])
        mask &= U[:, i] == out[i]
    return out, gaps


# ---------------- Gate G1 (per-prior oracle agreement) ----------------
def gate_oracle(field, q, pmf_true, build_logp, salt):
    """sc_decode (arm-prior logp) vs brute successive-MAP on the SAME logp.

    Both groups build logp with the arm prior under test (F3 or F4); the
    groups differ only in y-generation (F4-family draws vs y drawn via a
    random row-stochastic transition). 100 + 100 instances over n in
    {2, 4} (50 + 50 per n per group). First-divergence analysis in
    natural order with tie-tolerance TIE_TOL (same reading as Step-1).
    """
    rng = np.random.default_rng([DESIGN_SEED, salt + q, 1])
    books = {}
    for n in (2, 4):
        U, C = qary_codebook(field, q, n)
        if not check_codebook_vs_oracle(field, q, n, U, C):
            return {"error": "codebook/oracle spot-check failed", "q": q}
        books[n] = (U, C)
    rec = {"strict_matches": 0, "tie_tolerated": 0, "hard_mismatches": 0,
           "n_instances": 0, "by_group": {}}
    for group in ("F4", "randT"):
        g = {"strict_matches": 0, "tie_tolerated": 0, "hard_mismatches": 0,
             "n_instances": 0}
        for n, reps in ((2, 50), (4, 50)):
            U, C = books[n]
            for _ in range(reps):
                K = int(rng.integers(0, n + 1))
                info = np.sort(rng.choice(n, size=K, replace=False)) if K else np.empty(0, dtype=np.int64)
                frozen = np.array([i for i in range(n) if i not in set(info.tolist())], dtype=np.int64)
                msg = rng.integers(0, q, size=K).astype(np.int64) if K else np.empty(0, dtype=np.int64)
                u = np.zeros(n, dtype=np.int64)
                if K:
                    u[info] = msg
                x = polar_transform(u, field=field, alpha=ALPHA)
                if group == "F4":
                    d = rng.choice(q, size=n, p=pmf_true)
                    y = (x + d) % q
                else:
                    T = rng.uniform(0.05, 1.0, size=(q, q))
                    T /= T.sum(axis=1, keepdims=True)
                    y = np.array(
                        [rng.choice(q, p=T[int(x[j])]) for j in range(n)]
                    )
                logp = build_logp(y, q)
                res = sc_decode(
                    logp, field=field, alpha=ALPHA,
                    known_positions=frozen,
                    known_values=np.zeros(len(frozen), dtype=np.int64),
                )
                brute_u, gaps = brute_successive_qary(logp, frozen, U, C)
                x_brute = polar_transform(brute_u, field=field, alpha=ALPHA)
                strict = bool(np.array_equal(res.x_hat, x_brute))
                g["strict_matches"] += int(strict)
                g["n_instances"] += 1
                if not strict:
                    # First-divergence analysis in natural order: prefixes
                    # agree up to the first divergence, so only it is
                    # comparable; anything later is cascade. A tied first
                    # divergence explains the whole instance.
                    for i in sorted(info.tolist()):
                        if int(res.u_hat[i]) != int(brute_u[i]):
                            if gaps[i] > TIE_TOL:
                                g["hard_mismatches"] += 1
                            else:
                                g["tie_tolerated"] += 1
                            break
        rec["by_group"][group] = g
        for k in ("strict_matches", "tie_tolerated", "hard_mismatches", "n_instances"):
            rec[k] += g[k]
    return rec


# ---------------- Block decode (both arms) ----------------
LN2 = float(np.log(2.0))


def arm_block(msg, info_idx, frozen_idx, field, q, noise, build_logp):
    """Decode one paired block; return (ok, nll).

    nll (F6) = -sum_{i in info} log2 P_arm(x_i = true_i | y), the decoder
    output posterior (decision_metrics, ln) at information positions
    evaluated at the true message symbols.
    """
    u = np.zeros(N_SYM, dtype=np.int64)
    u[info_idx] = msg
    x = polar_transform(u, field=field, alpha=ALPHA)
    y = (x + noise) % q
    logp = build_logp(y, q)
    res = sc_decode(
        logp, field=field, alpha=ALPHA, known_positions=frozen_idx,
        known_values=np.zeros(len(frozen_idx), dtype=np.int64),
    )
    ok = bool(np.array_equal(res.u_hat[info_idx], msg))
    true = msg.astype(np.int64)
    nll = float(-(res.decision_metrics[info_idx, true] / LN2).sum())
    return ok, nll


def fail(msg):
    sys.stderr.write("GATE-FAIL: " + msg + "\n")
    sys.exit(1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--probe-root", required=True)
    args = ap.parse_args()
    root = args.probe_root
    t0 = time.time()

    assert K_SYMS == tuple(int(round(R * N_SYM)) for R in RS), "K grid changed"

    ctx = {}
    for q in QS:
        field = make_gf2m(MS[q], PRIMS[q])  # raises if pin mismatches F1
        pmf = f4_pmf(q)
        logpmf = np.log(pmf)
        H = h_delta_bits(pmf)
        ctx[q] = {"field": field, "pmf": pmf, "logpmf": logpmf, "H": H}

    # ---- Designs (in memory; no files written; deterministic re-design) --
    designs = {}
    for q in QS:
        infos, Hmc = design_native(ctx[q]["field"], q, ctx[q]["pmf"],
                                   ctx[q]["logpmf"])
        designs[q] = {"infos": infos, "Hmc": Hmc}

    gates = {}
    # ---- G0 information-set cross-check vs Step-1 results.json ----------
    g0 = {"status": None, "detail": None, "per_cell": {}}
    try:
        with open("workspace/exploration/nbpolar-native-highdim/step1/results.json") as fh:
            s1 = json.load(fh)
        ref_cells = s1.get("cells", {})
        # Step-1 results.json carries per-(q,R) FER summaries but no
        # persisted information-set arrays; equality is unverifiable.
        has_sets = all(
            isinstance(ref_cells.get("q%d_R%.2f" % (q, R)), dict)
            and ("info_set" in ref_cells["q%d_R%.2f" % (q, R)]
                 or "info_positions" in ref_cells["q%d_R%.2f" % (q, R)])
            for q in QS for R in RS
        )
        if has_sets:
            ok = True
            for q in QS:
                for R in RS:
                    key = "q%d_R%.2f" % (q, R)
                    ref = list(ref_cells[key].get("info_set",
                               ref_cells[key].get("info_positions")))
                    mine = designs[q]["infos"][R].tolist()
                    same = (list(map(int, ref)) == list(map(int, mine)))
                    g0["per_cell"][key] = {"equal": bool(same),
                                           "K": len(mine)}
                    ok = ok and same
            g0["status"] = "equal" if ok else "MISMATCH"
            g0["detail"] = "recomputed info sets vs Step-1 results.json"
            if not ok:
                fail("G0 information-set mismatch vs Step-1 results.json")
        else:
            g0["status"] = "reference unavailable, deterministic recompute only"
            g0["detail"] = ("Step-1 results.json is readable but carries no "
                            "per-(q,R) information-set arrays (cells hold "
                            "K_sym/FER summaries only); equality unverifiable")
            for q in QS:
                for R in RS:
                    g0["per_cell"]["q%d_R%.2f" % (q, R)] = {
                        "equal": None,
                        "K": int(len(designs[q]["infos"][R]))}
    except (OSError, ValueError) as exc:
        g0["status"] = "reference unavailable, deterministic recompute only"
        g0["detail"] = "Step-1 results.json unreadable (%s)" % exc
        for q in QS:
            for R in RS:
                g0["per_cell"]["q%d_R%.2f" % (q, R)] = {
                    "equal": None,
                    "K": int(len(designs[q]["infos"][R]))}
    gates["G0"] = g0

    # ---- G1a oracle agreement with the INFORMED prior -------------------
    for q in QS:
        rec = gate_oracle(ctx[q]["field"], q, ctx[q]["pmf"],
                          logp_informed_from_y, 1700)
        if "error" in rec:
            fail("G1a informed q=%d: %s" % (q, rec["error"]))
        gates["G1a_q%d" % q] = rec
        if rec["n_instances"] < 200 or rec["hard_mismatches"] != 0:
            fail("G1a informed q=%d: n=%d hard=%d" % (
                q, rec["n_instances"], rec["hard_mismatches"]))

    # ---- G1b oracle agreement with the TRUE-CHANNEL belief (amendment 3) --
    for q in QS:
        build_U = make_logp_true_channel(ctx[q]["logpmf"])
        rec = gate_oracle(ctx[q]["field"], q, ctx[q]["pmf"],
                          build_U, 1750)
        if "error" in rec:
            fail("G1b true-channel q=%d: %s" % (q, rec["error"]))
        gates["G1b_q%d" % q] = rec
        if rec["n_instances"] < 200 or rec["hard_mismatches"] != 0:
            fail("G1b true-channel q=%d: n=%d hard=%d" % (
                q, rec["n_instances"], rec["hard_mismatches"]))

    # ---- G2 noiseless round-trip 20/20 per q (arm I path, R=0.50 info) --
    for q in QS:
        rng = np.random.default_rng([DESIGN_SEED, 1800 + q, 1])
        K = K_SYMS[2]
        info_idx = designs[q]["infos"][0.50]
        frozen_idx = np.array([i for i in range(N_SYM)
                               if i not in set(info_idx.tolist())])
        okc = 0
        for _ in range(20):
            msg = rng.integers(0, q, size=K).astype(np.int64)
            u = np.zeros(N_SYM, dtype=np.int64)
            u[info_idx] = msg
            x = polar_transform(u, field=ctx[q]["field"], alpha=ALPHA)
            logp = logp_informed_from_y(x, q)  # noiseless: y = x
            res = sc_decode(
                logp, field=ctx[q]["field"], alpha=ALPHA,
                known_positions=frozen_idx,
                known_values=np.zeros(len(frozen_idx), dtype=np.int64),
            )
            okc += int(np.array_equal(res.u_hat[info_idx], msg))
        gates["G2_q%d" % q] = {"ok": okc, "n": 20, "arm": "I", "R": 0.50}
        if okc != 20:
            fail("G2 arm-I q=%d: %d/20" % (q, okc))

    # ---- G3 smoke: R=0.30, dedicated 256-block sample, both arms --------
    for q in QS:
        build_U = make_logp_true_channel(ctx[q]["logpmf"])
        for ai, (arm, builder) in enumerate(
                (("I", logp_informed_from_y), ("U", build_U))):
            rng = np.random.default_rng([DESIGN_SEED, 1900 + q, ai + 1])
            K = K_SYMS[0]
            info_idx = designs[q]["infos"][0.30]
            frozen_idx = np.array([i for i in range(N_SYM)
                                   if i not in set(info_idx.tolist())])
            fails = 0
            for _ in range(G3_SMOKE_BLOCKS):
                msg = rng.integers(0, q, size=K).astype(np.int64)
                noise = rng.choice(q, size=N_SYM, p=ctx[q]["pmf"])
                good, _ = arm_block(msg, info_idx, frozen_idx,
                                    ctx[q]["field"], q, noise, builder)
                fails += int(not good)
            fer = fails / G3_SMOKE_BLOCKS
            gates["G3smoke_q%d_arm%s" % (q, arm)] = {
                "fer": fer, "fails": fails, "n": G3_SMOKE_BLOCKS, "R": 0.30}
            if fer >= 0.9:
                fail("G3 smoke arm-%s q=%d: FER=%r >= 0.9" % (arm, q, fer))

    # ---- Paired probe (paired within each (q, R, seed, block)) ----------
    cells = {}
    DESIGN_METHOD_ECHO = ("Step-1 arm-A design verbatim: MC genie-SC "
                          "entropy via sc_decode under the TRUE F4 "
                          "likelihood, design seed 2026092400, top-K_sym; "
                          "transfer priors enter ONLY at decode time")
    for q in QS:
        r = MS[q]
        H = ctx[q]["H"]
        build_U = make_logp_true_channel(ctx[q]["logpmf"])
        for R, K in zip(RS, K_SYMS):
            info_idx = designs[q]["infos"][R]
            frozen_idx = np.array([i for i in range(N_SYM)
                                   if i not in set(info_idx.tolist())])
            ferI_seeds, ferU_seeds, gsucc_seeds, gnll_seeds = [], [], [], []
            for seed in SCREEN_SEEDS:
                rng = np.random.default_rng([seed, q, K])
                okI = okU = 0
                dnll = 0.0
                for _ in range(BLOCKS_PER_SEED):
                    msg = rng.integers(0, q, size=K).astype(np.int64)
                    noise = rng.choice(q, size=N_SYM, p=ctx[q]["pmf"])
                    goodI, nllI = arm_block(msg, info_idx, frozen_idx,
                                            ctx[q]["field"], q, noise,
                                            logp_informed_from_y)
                    goodU, nllU = arm_block(msg, info_idx, frozen_idx,
                                            ctx[q]["field"], q, noise,
                                            build_U)
                    okI += int(goodI)
                    okU += int(goodU)
                    dnll += nllU - nllI
                ferI_seeds.append(1.0 - okI / BLOCKS_PER_SEED)
                ferU_seeds.append(1.0 - okU / BLOCKS_PER_SEED)
                gsucc_seeds.append((okI - okU) / BLOCKS_PER_SEED)
                gnll_seeds.append(dnll / BLOCKS_PER_SEED)
            f = r * K / (N_SYM * H)
            cells["q%d_R%.2f" % (q, R)] = {
                "q": q, "R": R, "K_sym": K, "n_sym": N_SYM,
                "H_delta_bits": H, "f": f, "n_blocks": N_BLOCKS,
                "n_seeds": len(SCREEN_SEEDS),
                "blocks_per_seed": BLOCKS_PER_SEED, "T_s": BLOCKS_PER_SEED,
                "info_set_summary": {
                    "K_sym": K,
                    "n_frozen": int(N_SYM - K),
                    "design_method": DESIGN_METHOD_ECHO,
                },
                "armI_fer": summarize(ferI_seeds),
                "armU_fer": summarize(ferU_seeds),
                "g_succ": summarize(gsucc_seeds),
                "g_nll": summarize(gnll_seeds),
            }
            key = "q%d_R%.2f" % (q, R)
            print("cell %s f=%.4f FER_I=%.4f FER_U=%.4f g_succ=%.4f "
                  "g_nll=%.4f" % (
                      key, f, cells[key]["armI_fer"]["mean"],
                      cells[key]["armU_fer"]["mean"],
                      cells[key]["g_succ"]["mean"],
                      cells[key]["g_nll"]["mean"]), flush=True)

    wall = time.time() - t0
    # ---- Single end-of-run write (only reachable with all gates passed) --
    results = {
        "probe": "NBPOLAR-EXPLORATION-STEP2-PRIOR-TRANSFER",
        "tier": "X",
        "question": ("does injecting the frozen real-data transition "
                     "structure (the M2 +/-1 finding, with its frozen floor "
                     "rule) as the decoder's channel belief beat the "
                     "standard no-injection baseline on the same frozen "
                     "envelope?"),
        "freeze": {
            "F1": "decoder = Step-1 arm A reused: q-ary polar SC via "
                  "read-only reuse of comparison_bench.formal_ir.nbpolar "
                  "(make_gf2m/polar_transform alpha=2/sc_decode); "
                  "GF(4)=0b111, GF(8)=0b1011, GF(16)=0b10011; design seed "
                  "2026092400; n_sym=128; R in {0.30,0.40,0.50,0.60}; "
                  "K_sym={38,51,64,77}; bit-plane MSD axis NOT in Step 2",
            "F2": "channel F4: P(d=0)=0.75, P(d=+1)=0.24, P(d=-1)=0.005, "
                  "0.005 uniform over other q-3 offsets (mod q)",
            "F3": "arm I informed init = frozen G1R2 CAL32 triple verbatim "
                  "(q0 0.7562, q+1 0.2419, q-1 0.0018, rest 0) with floor "
                  "1e-15 applied, NOT renormalized",
            "F4": ("arm U no-injection baseline (AMENDMENT 3, 2026-09-23; "
                   "replaces the degenerate uniform arm): log P_U(y|x') = "
                   "log P_F4(y|x'), the true synthetic channel belief"),
            "F4_history": ("pre-amendment uniform arm log P_U(y|x') = "
                           "log(1/q) was degenerate by construction (blind "
                           "decoder, FER = 1.0 at probability 1 - q^-K); "
                           "recorded as packet history, no discriminative "
                           "information"),
            "F5": "16 seeds 2026092401..2026092416 x 64 blocks = 1024 "
                  "paired trials per (q,R); shared message+noise per "
                  "(seed,block); numpy default_rng",
            "F6": "per (q,R,seed): g_succ=(sum ok_I - sum ok_U)/T_s, "
                  "g_nll=sum(nll_U - nll_I)/T_s, T_s=64; "
                  "nll_arm=-sum_{i in info} log2 P_arm(x_i=true_i|y); "
                  "per-seed + mean/sample-std/range; NO numeric threshold; "
                  "zero/negative kept as evidence",
            "F7": "no EVAL/RESERVE; no re-fit; no prior_m2.py change; no "
                  "CAL change; no decoder change; M2 values copied only",
            "F8": "G0: info-set equality vs Step-1 results.json if "
                  "readable, else recorded unavailability",
        },
        "gates": gates,
        "population": {
            "kind": "synthetic (L2 screening ledger; never L1 real-data FER)",
            "n_sym": N_SYM,
            "q_set": list(QS),
            "channel": "F4 single member (see freeze.F2)",
            "design_seed": DESIGN_SEED,
            "design_mc_samples": DESIGN_MC_SAMPLES,
            "screening_seeds": list(SCREEN_SEEDS),
        },
        "cells": cells,
        "arm_u_redefinition": ("AMENDMENT 3 (2026-09-23): arm U redefined "
                               "from uniform initial messages to the "
                               "non-degenerate no-injection baseline "
                               "(true F4 channel belief); G1b renamed to "
                               "oracle agreement with the true-channel "
                               "belief; G3 unchanged and now meaningful "
                               "(both arms non-degenerate)"),
        "blind_uniform_degeneracy_note": ("log P_U(y|x') = log(1/q) is "
                                          "constant in y and x': the blind-"
                                          "uniform arm is an information-"
                                          "free decoder (every info "
                                          "decision an exact tie, argmax "
                                          "picks 0; success prob q^-K); "
                                          "FER = 1.0 deterministic; "
                                          "carries no discriminative "
                                          "information"),
        "m2_reference": {
            "q0": M2_Q0,
            "q_plus1": M2_QP1,
            "q_minus1": M2_QM1,
            "q_rest": M2_QREST,
            "floor": M2_FLOOR,
            "renormalized": False,
            "provenance": ("frozen G1R2 CAL32 triple, FIXED NUMERICAL "
                           "REFERENCE only (design R1/R2); copied verbatim, "
                           "never recomputed, never re-fitted"),
        },
        "attestation": {
            "no_real_data": True,
            "no_fer_claim": True,
            "ledger": "L2 synthetic screening - never cited as L1 "
                      "real-data FER",
        },
        "counters": {"s2_runs": 1, "reruns": 0, "rebuilds": 0},
        "stop_rules_fired": [],
        "wall_s": wall,
    }
    with open(os.path.join(root, "results.json"), "w") as fh:
        json.dump(results, fh, indent=2)
        fh.write("\n")
    lines = []
    lines.append("# Notes - NBPOLAR-EXPLORATION-STEP2-PRIOR-TRANSFER (Tier-X)")
    lines.append("")
    lines.append("Synthetic L2 paired readout (informed prior injection vs "
                 "no-injection baseline). No "
                 "claim about real-data FER, efficiency, promotion, "
                 "qualification, or composable-key yield. Zero/negative gain "
                 "is kept evidence, never discarded.")
    lines.append("")
    lines.append("Arm-U redefinition (AMENDMENT 3, 2026-09-23): arm U is the "
                 "NON-DEGENERATE no-injection baseline (true F4 channel "
                 "belief), replacing the degenerate uniform arm. The blind-"
                 "uniform arm (log(1/q) messages) is degenerate by "
                 "construction (FER = 1.0 at probability 1 - q^-K) and "
                 "carries no discriminative information; recorded as packet "
                 "history only.")
    lines.append("")
    lines.append("Exact command: PYTHONPATH=comparison_bench/src "
                 "/home/karel_303/.venvs/hd-qkd-polar-comparison/bin/python "
                 ".workbuddy/queue/NBPOLAR-EXPLORATION-STEP2-PRIOR-TRANSFER/"
                 "s2_transfer.py --probe-root " + root)
    lines.append("Wall time: %.1f s (budget 3600 s). Single-threaded; "
                 "one run; no reruns." % wall)
    lines.append("")
    lines.append("## Frozen readings applied in this builder")
    lines.append("- Design = Step-1 arm-A design verbatim (TRUE F4 "
                 "likelihood, genie-SC MC under design seed 2026092400, "
                 "top-K_sym); the transfer priors F3/F4 enter ONLY at "
                 "decode time, never at design time. Both arms share the "
                 "construction, seeds, messages and noise matrices; ONLY "
                 "the initial-message priors differ.")
    lines.append("- G0: Step-1 results.json carries no per-(q,R) "
                 "information-set arrays (K_sym/FER summaries only), so the "
                 "recorded outcome is 'reference unavailable, deterministic "
                 "recompute only' unless arrays are present.")
    lines.append("- G1 'brute-force MAP codeword' is read as independent "
                 "brute-force SUCCESSIVE-MAP enumeration (exhaustive, no "
                 "shared recursion; Step-1 reading): textbook-SC semantics "
                 "(every future position marginalized, decided prefix only "
                 "constrains), first-divergence analysis in natural order, "
                 "tie-tolerance <= 1e-9. Both groups build logp with the "
                 "arm prior under test and differ only in y-generation "
                 "(F4-family draws vs y via a random row-stochastic "
                 "transition, rows iid Uniform(0.05,1) row-normalized).")
    lines.append("- G1b (amendment 3, renamed) uses the TRUE-CHANNEL belief "
                 "builder (log P_F4); the pre-amendment uniform builder is "
                 "gone.")
    lines.append("- G1 mix per (prior, q): 100 F4-family (50 n_sym=2 + 50 "
                 "n_sym=4) + 100 random-transition (50 n_sym=2 + 50 "
                 "n_sym=4); random K in 0..n and random info positions per "
                 "instance.")
    lines.append("- Gate RNG streams derive from the design seed with fixed "
                 "salts ([seed, 1700+q, 1] G1a; [seed, 1750+q, 1] G1b; "
                 "[seed, 1800+q, 1] G2; [seed, 1900+q, arm] G3 smoke); "
                 "codebook spot-check draws from fixed seed 777000+q*10+n. "
                 "Screening streams are [seed, q, K] per (q, R, seed), "
                 "identical in structure to Step-1. All deterministic.")
    lines.append("- G2 uses the R=0.50 in-memory info sets; 20 noiseless "
                 "blocks per q on the arm-I path.")
    lines.append("- G3 smoke uses a dedicated 256-block sample at R=0.30 "
                 "per (q, arm) with the in-memory designs, before any "
                 "probe arithmetic; bar FER < 0.9 both arms.")
    lines.append("- Metric: per (q, R, seed) g_succ = (ok_I - ok_U)/64 and "
                 "g_nll = sum(nll_U - nll_I)/64 over the 64 paired trials; "
                 "nll_arm(t) = -sum_{i in info} log2 P_arm(x_i = true_i|y) "
                 "from the decoder output posterior (decision_metrics, ln, "
                 "/ ln 2). Per-seed series + mean/sample-std/range per "
                 "cell. No numeric threshold.")
    lines.append("")
    lines.append("## Headline paired table (per-seed means; synthetic L2)")
    for q in QS:
        for R in RS:
            c = cells["q%d_R%.2f" % (q, R)]
            lines.append(
                "q=%d R=%.2f f=%.4f FER_I=%.4f (std %.4f) FER_U=%.4f "
                "(std %.4f) g_succ=%.4f (std %.4f, range %s) g_nll=%.4f "
                "(std %.4f, range %s)" % (
                    q, R, c["f"], c["armI_fer"]["mean"],
                    c["armI_fer"]["sample_std"], c["armU_fer"]["mean"],
                    c["armU_fer"]["sample_std"], c["g_succ"]["mean"],
                    c["g_succ"]["sample_std"], c["g_succ"]["range"],
                    c["g_nll"]["mean"], c["g_nll"]["sample_std"],
                    c["g_nll"]["range"]))
    lines.append("")
    lines.append("H_delta bits: " + ", ".join(
        "q=%d %.6f" % (q, ctx[q]["H"]) for q in QS))
    lines.append("M2 reference verbatim: q0=0.7562 q+1=0.2419 q-1=0.0018 "
                 "rest=0 floor=1e-15 NOT renormalized (G1R2 CAL32 fixed "
                 "numerical reference).")
    lines.append("Counters: s2_runs=1 reruns=0 rebuilds=0. "
                 "Stop rules fired: none.")
    lines.append("Write scope: this root holds exactly prereg.md "
                 "(P1 copy, byte-identical), results.json, notes.md. "
                 "comparison_bench/formal_ir imported read-only.")
    with open(os.path.join(root, "notes.md"), "w") as fh:
        fh.write("\n".join(lines) + "\n")
    print("WROTE results.json + notes.md in %.1f s" % wall, flush=True)


if __name__ == "__main__":
    main()
