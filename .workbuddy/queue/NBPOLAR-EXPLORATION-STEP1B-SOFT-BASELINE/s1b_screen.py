#!/usr/bin/env python3
"""Tier-X Step-1B screening builder (packet-local, stdlib + numpy).

Packet: NBPOLAR-EXPLORATION-STEP1B-SOFT-BASELINE (amendments 1 + 2).
Four paired arms on the frozen Step-1 envelope: arm A native q-ary SC
(read-only reuse of comparison_bench.formal_ir.nbpolar), arm B-hard
(Step-1 arm B verbatim), arm B-soft (same decomposition/design, exact
soft-carrying MSD decoding), arm B-lab (read-only import of the
qkd-reconciliation-lab production binary pipeline). Synthetic F4 only.
Single invocation: designs -> G0 -> oracles G1/G1b/G1c -> G2 -> G3 ->
four-arm screening -> G3 recheck -> G4 -> ONE end-of-run write of
results.json + notes.md. Any gate failure exits non-zero with NO
output-root writes beyond the frozen prereg.md.

Amendment 2: G1c is a MIN-SUM MIRROR oracle — the lab-arm decode must
equal the decode of the independently coded packet-local min-sum
recursion mirror (integration fidelity, 0 hard mismatches). The
lab-arm-vs-exact-MAP divergence (min-sum approximation) is measured on
the same instances and recorded as the NON-gating diagnostic
results.json gates.G1c_approx_gap (a documented property of the
production baseline; never tuned away).
"""

# ---- Read-only hygiene env: MUST run before numpy/numba/lab imports ----
# Prevents .pyc writes in comparison_bench/ and the lab repo, redirects the
# lab's numba cache=True writes out of the lab tree, and pins single-thread.
import os
import sys

sys.dont_write_bytecode = True
os.environ.setdefault("PYTHONDONTWRITEBYTECODE", "1")
os.environ.setdefault("NUMBA_CACHE_DIR", "/tmp/opencode/s1b_numba_cache")
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["NUMBA_NUM_THREADS"] = "1"

import argparse
import json
import subprocess
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

# READ-ONLY lab import (amendment 1). The lab repo is never written; the
# hygiene env above keeps bytecode and numba caches out of it.
LAB_SRC = "/mnt/d/Code/qkd-reconciliation-lab/src"
LAB_REPO = "/mnt/d/Code/qkd-reconciliation-lab"
sys.path.insert(0, LAB_SRC)
from qkd_recon import polar_core as pc
from qkd_recon import msd_conditional as msd

# ---------------- Frozen constants (F3/F4/F5/F6) ----------------
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
G2_BLOCKS = 20
G3_SMOKE_BLOCKS = 256
DESIGN_MC_SAMPLES = 3000
TIE_TOL = 1e-9  # log-domain gap below which a coordinate is tie-tolerated
STEP1_RESULTS = "workspace/exploration/nbpolar-native-highdim/step1/results.json"

P_F4 = {  # P(delta=0), P(delta=+1), P(delta=-1), rest mass over other offsets
    "p0": 0.75,
    "p1": 0.24,
    "pm1": 0.005,
    "prest": 0.005,
}


# ---------------- Small helpers (Step-1 verbatim) ----------------
def gray(s):
    return s ^ (s >> 1)


def gray_inv(g, r):
    s = g
    shift = 1
    while g >> shift:
        s ^= g >> shift
        shift += 1
    return s & ((1 << r) - 1)


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


def h_delta_bits(pmf):
    return float(-(pmf[pmf > 0] * np.log2(pmf[pmf > 0])).sum())


def logp_from_y(y, logpmf, q):
    return logpmf[(y[:, None] - np.arange(q)[None, :]) % q]


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


# ---------------- Packet-local binary polar (arm B, Step-1 verbatim) ----------------
def benc(u):
    u = np.array(u, dtype=np.int64).copy()
    n = u.shape[0]
    s = 1
    while s < n:
        for b in range(0, n, 2 * s):
            for j in range(s):
                u[b + j] ^= u[b + j + s]
        s *= 2
    return u


def bdec(L0, L1, froz):
    """Log-domain Arikan SC, natural order, frozen pinned to 0, ties to 0."""
    L0 = np.asarray(L0, dtype=float)
    L1 = np.asarray(L1, dtype=float)
    froz = np.asarray(froz, dtype=bool)

    def rec(a0, a1, fz):
        m = a0.shape[0]
        if m == 1:
            return np.array(
                [0 if (fz[0] or a0[0] >= a1[0]) else 1], dtype=np.int64
            )
        h = m // 2
        A0, A1 = a0[:h], a1[:h]
        B0, B1 = a0[h:], a1[h:]
        M0 = np.logaddexp(A0 + B0, A1 + B1)
        M1 = np.logaddexp(A0 + B1, A1 + B0)
        mx = np.maximum(M0, M1)
        M0 = M0 - mx
        M1 = M1 - mx
        left = rec(M0, M1, fz[:h])
        beta = benc(left)
        # plus: P_b = A[u0 xor b] + B[b] (binary kernel x0 = u0 xor u1)
        P0 = np.where(beta == 0, A0 + B0, A1 + B0)
        P1 = np.where(beta == 0, A1 + B1, A0 + B1)
        mx = np.maximum(P0, P1)
        P0 = P0 - mx
        P1 = P1 - mx
        right = rec(P0, P1, fz[h:])
        return np.concatenate([left, right])

    return rec(L0, L1, froz)


def bdec_soft(L0, L1, froz):
    """bdec plus per-leaf posterior q_t = P(u_t = 1 | y, decided prefix).

    Frozen leaves are pinned to bit 0 AND to q_t = 0 (deterministic value;
    neutral factor in the parity re-encode). q_t = sigmoid(M1 - M0) at the
    leaf; after the per-node max subtraction one of the two values is 0, so
    the difference is nan-free (both -inf never occurs on a consistent
    instance)."""
    L0 = np.asarray(L0, dtype=float)
    L1 = np.asarray(L1, dtype=float)
    froz = np.asarray(froz, dtype=bool)

    def sigmoid(d):
        if np.isnan(d):
            return 0.5
        if d >= 0.0:
            return 1.0 / (1.0 + np.exp(-d))
        e = np.exp(d)
        return e / (1.0 + e)

    def rec(a0, a1, fz):
        m = a0.shape[0]
        if m == 1:
            if fz[0]:
                return (np.array([0], dtype=np.int64),
                        np.array([0.0], dtype=float))
            q1 = float(sigmoid(a1[0] - a0[0]))
            return (np.array([0 if a0[0] >= a1[0] else 1], dtype=np.int64),
                    np.array([q1], dtype=float))
        h = m // 2
        A0, A1 = a0[:h], a1[:h]
        B0, B1 = a0[h:], a1[h:]
        M0 = np.logaddexp(A0 + B0, A1 + B1)
        M1 = np.logaddexp(A0 + B1, A1 + B0)
        mx = np.maximum(M0, M1)
        M0 = M0 - mx
        M1 = M1 - mx
        left, ql = rec(M0, M1, fz[:h])
        beta = benc(left)
        P0 = np.where(beta == 0, A0 + B0, A1 + B0)
        P1 = np.where(beta == 0, A1 + B1, A0 + B1)
        mx = np.maximum(P0, P1)
        P0 = P0 - mx
        P1 = P1 - mx
        right, qr = rec(P0, P1, fz[h:])
        return (np.concatenate([left, right]), np.concatenate([ql, qr]))

    return rec(L0, L1, froz)


def build_sym_tables(r):
    """Gray bit convention (frozen): plane i = bit i (LSB-first) of the
    reflected Gray codeword. Shared by both packet-local arms."""
    q = 1 << r
    G = np.array([gray(s) for s in range(q)], dtype=np.int64)
    GINV = np.array([gray_inv(g, r) for g in range(q)], dtype=np.int64)
    assert set(GINV.tolist()) == set(range(q))

    def bits_of(sym):
        g = int(G[int(sym)])
        return [(g >> i) & 1 for i in range(r)]

    def sym_of(bits):
        g = 0
        for i, b in enumerate(bits):
            g |= (int(b) & 1) << i
        return int(GINV[g])

    return G, GINV, bits_of, sym_of


def build_EJB(r, i):
    """EJB[e, b, l] = symbol for earlier-pattern e, input bit b, later
    pattern l (exact induced-bit symbol map used by plane priors)."""
    _, _, bits_of, sym_of = build_sym_tables(r)
    E, L = 1 << i, 1 << (r - 1 - i)
    out = np.empty((E, 2, L), dtype=np.int64)
    for e in range(E):
        eb = [(e >> p) & 1 for p in range(i)]
        for b in (0, 1):
            for l in range(L):
                lb = [(l >> t) & 1 for t in range(r - 1 - i)]
                out[e, b, l] = sym_of(eb + [b] + lb)
    return out


def plane_priors(logp_sym, earlier_bits, EJB):
    """Exact induced binary transition (later-marginalized, earlier-hard)."""
    N = logp_sym.shape[0]
    i = earlier_bits.shape[1] if earlier_bits.ndim == 2 else 0
    if i == 0:
        T = EJB[0]  # (2, L)
        TT = np.broadcast_to(T[None, :, :], (N, 2, T.shape[1]))
    else:
        e = (earlier_bits * (1 << np.arange(i))).sum(axis=1).astype(np.int64)
        TT = EJB[e]  # (N, 2, L)
    acc = logp_sym[np.arange(N)[:, None, None], TT]
    out = np.logaddexp.reduce(acc, axis=2)
    return out[:, 0], out[:, 1]


# ---------------- Arm-A design (Step-1 verbatim) ----------------
def design_armA(field, q, pmf, logpmf):
    rng = np.random.default_rng(DESIGN_SEED)
    H = np.zeros(N_SYM)
    allpos = np.arange(N_SYM)
    for _ in range(DESIGN_MC_SAMPLES):
        u = rng.integers(0, q, size=N_SYM).astype(np.int64)
        x = polar_transform(u, field=field, alpha=ALPHA)
        d = rng.choice(q, size=N_SYM, p=pmf)
        y = (x + d) % q
        logp = logp_from_y(y, logpmf, q)
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


# ---------------- Arm-B design (Step-1 verbatim) ----------------
def design_armB(q, r, Wmat, K):
    Zb = []
    for i in range(r):
        EJB = build_EJB(r, i)
        P = Wmat[:, EJB].sum(axis=3) / (1 << (r - 1))
        Z0 = float(np.sqrt(P[:, :, 0] * P[:, :, 1]).sum())
        Z = np.array([Z0])
        while Z.shape[0] < N_SYM:
            z = Z
            Zn = np.empty(2 * z.shape[0])
            Zn[0::2] = np.minimum(1.0, 2 * z - z * z)
            Zn[1::2] = z * z
            Z = Zn
        Zb.append(Z)
    Zall = np.stack(Zb)
    order = np.argsort(Zall.ravel(), kind="stable")
    sel = order[: r * K]
    infos = []
    for i in range(r):
        infos.append(np.sort(sel[sel // N_SYM == i] % N_SYM))
    return infos, [z.tolist() for z in Zb]


# ---------------- Batch q-ary codebooks (Step-1 verbatim) ----------------
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
    """Independent successive-MAP via exhaustive enumeration (no sc.py)."""
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


def brute_successive_from_M(M, froz):
    """Independent binary successive-MAP from per-position log-priors M
    (n x 2, log P(bit) up to per-position constants). Exhaustive over
    codewords via the packet-local benc; textbook-SC semantics (future
    info AND frozen positions marginalized; only the decided prefix,
    including past frozen pins, constrains candidates)."""
    n = M.shape[0]
    candU = [np.array([(v >> (n - 1 - j)) & 1 for j in range(n)],
                      dtype=np.int64)
             for v in range(1 << n)]
    candX = [benc(v) for v in candU]
    pre = []
    gaps = {}
    for p in range(n):
        if froz[p]:
            pre.append(0)
            continue
        sc = []
        for c in (0, 1):
            vals = []
            for v, xe in zip(candU, candX):
                if list(v[: len(pre)]) != pre or v[len(pre)] != c:
                    continue
                vals.append(sum(M[j, xe[j]] for j in range(n)))
            sc.append(np.logaddexp.reduce(np.array(vals)) if vals else -np.inf)
        order = np.argsort([-sc[0], -sc[1]], kind="stable")
        gaps[p] = float(abs(sc[0] - sc[1]))
        pre.append(int(order[0]))
    return np.array(pre, dtype=np.int64), gaps


# ---------------- Gate G1 (arm A, Step-1 verbatim) ----------------
def gate1_armA(field, q, pmf, logpmf):
    rng = np.random.default_rng([DESIGN_SEED, 700 + q, 1])
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
                    d = rng.choice(q, size=n, p=pmf)
                    y = (x + d) % q
                    logp = logp_from_y(y, logpmf, q)
                else:
                    T = rng.uniform(0.05, 1.0, size=(q, q))
                    T /= T.sum(axis=1, keepdims=True)
                    logT = np.log(T)
                    y = np.array(
                        [rng.choice(q, p=T[int(x[j])]) for j in range(n)]
                    )
                    logp = logT[:, y].T.copy()
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


def gate1_armB(q, r, pmf, logpmf):
    """Step-1 arm-B oracle, kept for reference symmetry (B-hard is gated by
    G0 bit-exact reproduction; this validates the shared instance stream)."""
    rng = np.random.default_rng([DESIGN_SEED, 700 + q, 2])
    _, _, bits_of, sym_of = build_sym_tables(r)
    EJBs = [build_EJB(r, i) for i in range(r)]
    rec = {"strict_matches": 0, "tie_tolerated": 0, "hard_mismatches": 0,
           "n_instances": 0, "by_group": {}}
    for group in ("F4", "randT"):
        g = {"strict_matches": 0, "tie_tolerated": 0, "hard_mismatches": 0,
             "n_instances": 0}
        for n, reps in ((2, 50), (4, 50)):
            for _ in range(reps):
                kinfos = []
                frozs = []
                for _ in range(r):
                    k = int(rng.integers(0, n + 1))
                    info = (np.sort(rng.choice(n, size=k, replace=False))
                            if k else np.empty(0, dtype=np.int64))
                    kinfos.append(info)
                    fz = np.zeros(n, dtype=bool)
                    fz[[t for t in range(n) if t not in set(info.tolist())]] = True
                    frozs.append(fz)
                ubits = []
                for i in range(r):
                    ub = np.zeros(n, dtype=np.int64)
                    if len(kinfos[i]):
                        ub[kinfos[i]] = rng.integers(0, 2, size=len(kinfos[i]))
                    ubits.append(ub)
                xbits = [benc(ub) for ub in ubits]
                sym = np.array(
                    [sym_of([int(xbits[i][j]) for i in range(r)])
                     for j in range(n)],
                    dtype=np.int64,
                )
                if group == "F4":
                    d = rng.choice(q, size=n, p=pmf)
                    y = (sym + d) % q
                    logp_sym = logp_from_y(y, logpmf, q)
                else:
                    T = rng.uniform(0.05, 1.0, size=(q, q))
                    T /= T.sum(axis=1, keepdims=True)
                    logT = np.log(T)
                    y = np.array(
                        [rng.choice(q, p=T[int(sym[j])]) for j in range(n)]
                    )
                    logp_sym = logT[:, y].T.copy()
                dec = []
                E = np.zeros((n, 0), dtype=np.int64)
                for i in range(r):
                    L0, L1 = plane_priors(logp_sym, E, EJBs[i])
                    uh = bdec(L0, L1, frozs[i])
                    dec.append(uh)
                    E = (np.column_stack([E, benc(uh)]) if E.shape[1]
                         else benc(uh)[:, None])
                strict = True
                for i in range(r):
                    bu, gaps = brute_successive_bplane(
                        y, logp_sym,
                        [bool(v) for v in frozs[i]],
                        (np.column_stack([benc(d) for d in dec[:i]]) if i
                         else np.zeros((n, 0), dtype=np.int64)),
                        sym_of, r, i,
                    )
                    if not np.array_equal(dec[i], bu):
                        strict = False
                        for p in sorted(kinfos[i].tolist()):
                            if int(dec[i][p]) != int(bu[p]):
                                if gaps[p] > TIE_TOL:
                                    g["hard_mismatches"] += 1
                                else:
                                    g["tie_tolerated"] += 1
                                break
                g["strict_matches"] += int(strict)
                g["n_instances"] += 1
        rec["by_group"][group] = g
        for k in ("strict_matches", "tie_tolerated", "hard_mismatches",
                  "n_instances"):
            rec[k] += g[k]
    return rec


def brute_successive_bplane(y, logp_sym_row, froz, Emat, sym_of, r, i):
    """Independent per-plane successive MAP (Step-1 verbatim)."""
    n = len(y)
    Ew = Emat
    M = np.empty((n, 2))
    L = 1 << (r - 1 - i)
    for j in range(n):
        eb = [int(Ew[j, p]) for p in range(i)]
        for b in (0, 1):
            vals = []
            for l in range(L):
                lb = [(l >> t) & 1 for t in range(r - 1 - i)]
                s = sym_of(eb + [b] + lb)
                vals.append(logp_sym_row[j, s])
            M[j, b] = np.logaddexp.reduce(np.array(vals))
    candU = []
    for v in range(1 << n):
        candU.append(np.array([(v >> (n - 1 - j)) & 1 for j in range(n)]))
    candX = [benc(v) for v in candU]
    pre = []
    gaps = {}
    for p in range(n):
        if froz[p]:
            pre.append(0)
            continue
        sc = []
        for c in (0, 1):
            vals = []
            for v, xe in zip(candU, candX):
                if list(v[: len(pre)]) != pre or v[len(pre)] != c:
                    continue
                vals.append(sum(M[j, xe[j]] for j in range(n)))
            sc.append(np.logaddexp.reduce(np.array(vals)))
        order = np.argsort([-sc[0], -sc[1]], kind="stable")
        gaps[p] = float(abs(sc[0] - sc[1]))
        pre.append(int(order[0]))
    return np.array(pre, dtype=np.int64), gaps


# ---------------- Arm-B-soft: soft-carrying MSD (F3 / R1) ----------------
_BENC_G = {}


def benc_generator(n):
    """G[t, p] = benc(e_t)[p]; x = benc(u) <=> x[p] = xor_t G[t,p] u_t."""
    if n not in _BENC_G:
        G = np.zeros((n, n), dtype=np.int8)
        e = np.zeros(n, dtype=np.int64)
        for t in range(n):
            e[:] = 0
            e[t] = 1
            G[t] = benc(e)
        _BENC_G[n] = G
    return _BENC_G[n]


def codeword_belief(q_leaf, n):
    """Posterior over the plane's CODEWORD bit at each position p:
    P(x_p = 1) = (1 - prod_{t in S_p} (1 - 2 q_t)) / 2 with
    S_p = {t : benc(e_t)[p] = 1}; frozen factors are neutral (q_t = 0)."""
    G = benc_generator(n)
    fac = 1.0 - 2.0 * np.asarray(q_leaf, dtype=float)
    prod = np.prod(np.where(G.T == 1, fac[None, :], 1.0), axis=1)
    return (1.0 - prod) / 2.0


def soft_priors(Wp, beliefs, EJB, r, i):
    """Exact soft-carrying binary log-prior for plane i > 0 (frozen F3):
    log S_b - log(S_0 + S_1) with
    S_b(p) = sum_{e,l} Wp[p, symbol(e,b,l)] * prod_{j<i} belief_j(p, e_j)
             * 2^{-(r-1-i)},
    Wp[p, s] = P(y_p | s) (probability domain; F4 = Wmat[y], randT gate =
    T.T[y], noiseless G2 = exact delta metric exp(log p)), later planes
    marginalized uniformly. Raw-vs-normalized per-position constants are
    decision-invariant."""
    n = Wp.shape[0]
    E = 1 << i
    scale = 2.0 ** (-(r - 1 - i))
    w = np.ones((E, n), dtype=float)
    for e in range(E):
        for j in range(i):
            bj = beliefs[j]
            w[e] *= bj if ((e >> j) & 1) else (1.0 - bj)
    S = np.zeros((n, 2), dtype=float)
    for e in range(E):
        for b in (0, 1):
            Te = Wp[:, EJB[e, b, :]].sum(axis=1)  # sum over later patterns
            S[:, b] += w[e] * Te
    S *= scale
    with np.errstate(divide="ignore", invalid="ignore"):
        l0 = np.log(S[:, 0])
        l1 = np.log(S[:, 1])
        lt = np.logaddexp(l0, l1)
    if np.any(~np.isfinite(lt)):  # both S zero at a position: only
        ok = np.isfinite(lt)      # reachable after an upstream noiseless
        return (np.where(ok, l0 - lt, 0.0),   # misdecode (caught by G2)
                np.where(ok, l1 - lt, 0.0))
    return l0 - lt, l1 - lt


def naive_M_soft(logp_sym, Wp, beliefs, EJB, r, i):
    """Gate-only independent recomputation of the plane-i soft priors as
    per-position log-scores M[j, b] (own nested loops; no vectorized
    tensor path). Plane 0 = later-marginalized induced channel."""
    n = Wp.shape[0]
    M = np.empty((n, 2), dtype=float)
    if i == 0:
        L = 1 << (r - 1)
        for j in range(n):
            for b in (0, 1):
                vals = [logp_sym[j, EJB[0, b, l]] for l in range(L)]
                M[j, b] = np.logaddexp.reduce(np.array(vals))
    else:
        E = 1 << i
        Lt = 1 << (r - 1 - i)
        scale = 2.0 ** (-(r - 1 - i))
        for j in range(n):
            for b in (0, 1):
                s = 0.0
                for e in range(E):
                    w = 1.0
                    for jj in range(i):
                        w *= (beliefs[jj][j] if ((e >> jj) & 1)
                              else (1.0 - beliefs[jj][j]))
                    if w == 0.0:
                        continue
                    for l in range(Lt):
                        s += w * float(Wp[j, EJB[e, b, l]])
                M[j, b] = np.log(s * scale) if s > 0.0 else -np.inf
    return M


def soft_decode_planes(logp_sym, Wp, frozs, EJBs, r):
    """Decode all r planes with soft-carrying MSD; returns decoded u-planes,
    the per-plane priors used, and the codeword beliefs per plane."""
    n = Wp.shape[0]
    dec, beliefs, priors = [], [], []
    z = np.zeros((n, 0), dtype=np.int64)
    for i in range(r):
        if i == 0:
            L0, L1 = plane_priors(logp_sym, z, EJBs[i])
        else:
            L0, L1 = soft_priors(Wp, beliefs, EJBs[i], r, i)
        uh, qleaf = bdec_soft(L0, L1, frozs[i])
        dec.append(uh)
        priors.append((L0, L1))
        beliefs.append(codeword_belief(qleaf, n))
    return dec, priors, beliefs


def gate1_armBsoft(q, r, pmf, logpmf, Wmat):
    """G1b: B-soft oracle on the Step-1 arm-B instance stream (salt 2)."""
    rng = np.random.default_rng([DESIGN_SEED, 700 + q, 2])
    _, _, bits_of, sym_of = build_sym_tables(r)
    EJBs = [build_EJB(r, i) for i in range(r)]
    rec = {"strict_matches": 0, "tie_tolerated": 0, "hard_mismatches": 0,
           "n_instances": 0, "by_group": {}}
    for group in ("F4", "randT"):
        g = {"strict_matches": 0, "tie_tolerated": 0, "hard_mismatches": 0,
             "n_instances": 0}
        for n, reps in ((2, 50), (4, 50)):
            for _ in range(reps):
                kinfos = []
                frozs = []
                for _ in range(r):
                    k = int(rng.integers(0, n + 1))
                    info = (np.sort(rng.choice(n, size=k, replace=False))
                            if k else np.empty(0, dtype=np.int64))
                    kinfos.append(info)
                    fz = np.zeros(n, dtype=bool)
                    fz[[t for t in range(n) if t not in set(info.tolist())]] = True
                    frozs.append(fz)
                ubits = []
                for i in range(r):
                    ub = np.zeros(n, dtype=np.int64)
                    if len(kinfos[i]):
                        ub[kinfos[i]] = rng.integers(0, 2, size=len(kinfos[i]))
                    ubits.append(ub)
                xbits = [benc(ub) for ub in ubits]
                sym = np.array(
                    [sym_of([int(xbits[i][j]) for i in range(r)])
                     for j in range(n)],
                    dtype=np.int64,
                )
                if group == "F4":
                    d = rng.choice(q, size=n, p=pmf)
                    y = (sym + d) % q
                    logp_sym = logp_from_y(y, logpmf, q)
                    Wp = Wmat[y]
                else:
                    T = rng.uniform(0.05, 1.0, size=(q, q))
                    T /= T.sum(axis=1, keepdims=True)
                    logT = np.log(T)
                    y = np.array(
                        [rng.choice(q, p=T[int(sym[j])]) for j in range(n)]
                    )
                    logp_sym = logT[:, y].T.copy()
                    Wp = T.T[y]
                dec, _, beliefs = soft_decode_planes(
                    logp_sym, Wp, frozs, EJBs, r)
                strict = True
                for i in range(r):
                    # independent naive recomputation of the SAME priors
                    # (conditions on this decoder's earlier-plane beliefs,
                    # as the frozen soft formula requires), then exhaustive
                    # successive-MAP under those priors.
                    M = naive_M_soft(logp_sym, Wp, beliefs, EJBs[i], r, i)
                    bu, gaps = brute_successive_from_M(M, frozs[i])
                    if not np.array_equal(dec[i], bu):
                        strict = False
                        for p in sorted(kinfos[i].tolist()):
                            if int(dec[i][p]) != int(bu[p]):
                                if gaps[p] > TIE_TOL:
                                    g["hard_mismatches"] += 1
                                else:
                                    g["tie_tolerated"] += 1
                                break
                g["strict_matches"] += int(strict)
                g["n_instances"] += 1
        rec["by_group"][group] = g
        for k in ("strict_matches", "tie_tolerated", "hard_mismatches",
                  "n_instances"):
            rec[k] += g[k]
    return rec


# ---------------- Block encode/decode (Step-1 verbatim) ----------------
def armA_block(msg, info_idx, frozen_idx, field, q, noise, logpmf):
    u = np.zeros(N_SYM, dtype=np.int64)
    u[info_idx] = msg
    x = polar_transform(u, field=field, alpha=ALPHA)
    y = (x + noise) % q
    logp = logp_from_y(y, logpmf, q)
    res = sc_decode(
        logp, field=field, alpha=ALPHA, known_positions=frozen_idx,
        known_values=np.zeros(len(frozen_idx), dtype=np.int64),
    )
    return bool(np.array_equal(res.u_hat[info_idx], msg))


def armB_block(msg, sel_order, plane_infos, q, r, noise, logpmf, sym_of, EJBs):
    bits = []
    for s in msg:
        g = gray(int(s))
        bits.extend([(g >> i) & 1 for i in range(r)])
    ubits = [np.zeros(N_SYM, dtype=np.int64) for _ in range(r)]
    for bit, (i, p) in zip(bits, sel_order):
        ubits[i][p] = bit
    xbits = [benc(ub) for ub in ubits]
    sym = np.array(
        [sym_of([int(xbits[i][j]) for i in range(r)])
         for j in range(N_SYM)],
        dtype=np.int64,
    )
    y = (sym + noise) % q
    logp_sym = logp_from_y(y, logpmf, q)
    dec = []
    E = np.zeros((N_SYM, 0), dtype=np.int64)
    frozs = []
    for i in range(r):
        fz = np.ones(N_SYM, dtype=bool)
        fz[plane_infos[i]] = False
        frozs.append(fz)
        L0, L1 = plane_priors(logp_sym, E, EJBs[i])
        uh = bdec(L0, L1, fz)
        dec.append(uh)
        E = np.column_stack([E, benc(uh)])
    got = []
    for i, p in sel_order:
        got.append(int(dec[i][p]))
    for s_idx, s in enumerate(msg):
        chunk = got[s_idx * r:(s_idx + 1) * r]
        if sym_of(chunk) != int(s):
            return False
    return True


def armB_block_noiseless(msg, sel_order, plane_infos, q, r, sym_of):
    """Error-free round-trip through the arm-B encoder/decoder only."""
    bits = []
    for s in msg:
        g = gray(int(s))
        bits.extend([(g >> i) & 1 for i in range(r)])
    ubits = [np.zeros(N_SYM, dtype=np.int64) for _ in range(r)]
    for bit, (i, p) in zip(bits, sel_order):
        ubits[i][p] = bit
    xbits = [benc(ub) for ub in ubits]
    logp_sym = np.full((N_SYM, q), -np.inf)
    for j in range(N_SYM):
        logp_sym[j, sym_of([int(xbits[i][j]) for i in range(r)])] = 0.0
    dec = []
    E = np.zeros((N_SYM, 0), dtype=np.int64)
    EJBs = [build_EJB(r, i) for i in range(r)]
    for i in range(r):
        fz = np.ones(N_SYM, dtype=bool)
        fz[plane_infos[i]] = False
        L0, L1 = plane_priors(logp_sym, E, EJBs[i])
        uh = bdec(L0, L1, fz)
        dec.append(uh)
        E = np.column_stack([E, benc(uh)])
    got = [int(dec[i][p]) for i, p in sel_order]
    for s_idx, s in enumerate(msg):
        if sym_of(got[s_idx * r:(s_idx + 1) * r]) != int(s):
            return False
    return True


# ---------------- Arm-B-soft blocks ----------------
def armB_block_soft(msg, sel_order, plane_infos, q, r, noise, logpmf, sym_of,
                    EJBs, Wmat):
    """Same encode/decomposition as armB_block; soft-carrying MSD decode."""
    bits = []
    for s in msg:
        g = gray(int(s))
        bits.extend([(g >> i) & 1 for i in range(r)])
    ubits = [np.zeros(N_SYM, dtype=np.int64) for _ in range(r)]
    for bit, (i, p) in zip(bits, sel_order):
        ubits[i][p] = bit
    xbits = [benc(ub) for ub in ubits]
    sym = np.array(
        [sym_of([int(xbits[i][j]) for i in range(r)])
         for j in range(N_SYM)],
        dtype=np.int64,
    )
    y = (sym + noise) % q
    logp_sym = logp_from_y(y, logpmf, q)
    Wp = Wmat[y]  # per-position rows of the frozen transition table
    frozs = []
    for i in range(r):
        fz = np.ones(N_SYM, dtype=bool)
        fz[plane_infos[i]] = False
        frozs.append(fz)
    dec, _, _ = soft_decode_planes(logp_sym, Wp, frozs, EJBs, r)
    got = [int(dec[i][p]) for i, p in sel_order]
    for s_idx, s in enumerate(msg):
        if sym_of(got[s_idx * r:(s_idx + 1) * r]) != int(s):
            return False
    return True


def armB_block_noiseless_soft(msg, sel_order, plane_infos, q, r, sym_of):
    """Error-free round-trip through the B-soft stack with the Step-1
    noiseless delta-metric convention (W rows = exp(log p) indicators)."""
    bits = []
    for s in msg:
        g = gray(int(s))
        bits.extend([(g >> i) & 1 for i in range(r)])
    ubits = [np.zeros(N_SYM, dtype=np.int64) for _ in range(r)]
    for bit, (i, p) in zip(bits, sel_order):
        ubits[i][p] = bit
    xbits = [benc(ub) for ub in ubits]
    logp_sym = np.full((N_SYM, q), -np.inf)
    for j in range(N_SYM):
        logp_sym[j, sym_of([int(xbits[i][j]) for i in range(r)])] = 0.0
    with np.errstate(over="ignore", invalid="ignore"):
        Wp = np.exp(logp_sym)
    Wp = np.where(np.isnan(Wp), 0.0, Wp)
    frozs = []
    EJBs = [build_EJB(r, i) for i in range(r)]
    for i in range(r):
        fz = np.ones(N_SYM, dtype=bool)
        fz[plane_infos[i]] = False
        frozs.append(fz)
    dec, _, _ = soft_decode_planes(logp_sym, Wp, frozs, EJBs, r)
    got = [int(dec[i][p]) for i, p in sel_order]
    for s_idx, s in enumerate(msg):
        if sym_of(got[s_idx * r:(s_idx + 1) * r]) != int(s):
            return False
    return True


# ---------------- Arm-B-lab (amendment 1) ----------------
def lab_n_log(n):
    return int(round(np.log2(n)))


def lab_plane_masks(K, r, n=N_SYM):
    """Uniform per-plane k_i = K, lab 3GPP-PW top-k mask (beta = 2**0.25)."""
    order = pc.reliable_order(n)
    return [pc.info_mask_from_order(order, K, n).copy() for _ in range(r)]


def lab_slots(plane_infos):
    """(plane, position) slots sorted plane-major (frozen placement)."""
    return sorted([(i, int(p)) for i in range(len(plane_infos))
                   for p in plane_infos[i]])


def lab_encode_a(msg, slots, r, n):
    """Message bits natural LSB-first per symbol -> plane/position slots;
    frozen u = 0 channel framing; transmit a[p] = sum_i x_i[p] << (r-1-i)
    (plane 0 = MSB = the lab's natural plane order, NOT Gray)."""
    stream = []
    for s in msg:
        for b in range(r):
            stream.append((int(s) >> b) & 1)
    ubits = [np.zeros(n, dtype=np.int64) for _ in range(r)]
    for bit, (i, p) in zip(stream, slots):
        ubits[i][p] = bit
    a = np.zeros(n, dtype=np.int64)
    n_log = lab_n_log(n)
    for i in range(r):
        x = pc.polar_encode(ubits[i], n_log)
        a |= x.astype(np.int64) << (r - 1 - i)
    return a


def lab_decode_planes(y, tables, masks, r, n):
    """Plane-by-plane lab decode: conditional_llr hard-prefix (physical
    planes) -> per-plane SC (frozen u = 0) -> re-encode for the prefix."""
    n_log = lab_n_log(n)
    dec_x, uhs = [], []
    for i in range(r):
        pref = (msd.prefix_from_bits(dec_x, i) if i
                else np.zeros(n, dtype=np.int64))
        llr = msd.conditional_llr(tables, i, y, pref)
        uh = pc.sc_decode_frame(np.ascontiguousarray(llr, dtype=np.float64),
                                masks[i], n_log=n_log, frozen_value=0)
        xh = pc.polar_encode(uh, n_log)
        dec_x.append(xh)
        uhs.append(uh)
    return uhs, dec_x


def lab_extract(uhs, slots, r):
    """Mirror of lab_encode_a: slots -> stream -> natural LSB-first symbols."""
    got = [int(uhs[i][p]) for i, p in slots]
    out = []
    for s_idx in range(len(got) // r):
        chunk = got[s_idx * r:(s_idx + 1) * r]
        v = 0
        for b in range(r):
            v |= (chunk[b] & 1) << b
        out.append(v)
    return out


def armB_lab_block(msg, slots, masks, q, r, noise, tables):
    a = lab_encode_a(msg, slots, r, N_SYM)
    y = (a + noise) % q
    uhs, _ = lab_decode_planes(y, tables, masks, r, N_SYM)
    got = lab_extract(uhs, slots, r)
    return all(g == int(s) for g, s in zip(got, msg))


def armB_lab_block_noiseless(msg, slots, masks, r, tables):
    a = lab_encode_a(msg, slots, r, N_SYM)
    uhs, _ = lab_decode_planes(a, tables, masks, r, N_SYM)
    got = lab_extract(uhs, slots, r)
    return all(g == int(s) for g, s in zip(got, msg))


LAB_CLIP = 30.0  # lab table-build clip (amendment 1); re-applied in mirror


def mirror_min_sum_sc(llr, info_mask, clip=LAB_CLIP):
    """INDEPENDENT packet-local min-sum SC mirror (Amendment 2, G1c).

    Coded here from the documented semantics, structurally different from
    (and not copied out of) the lab's iterative tree-walk `sc_decode_frame`:

    - f-node (min-sum): sign(l)*sign(r)*min(|l|,|r|), sign(x)=+1 for x>=0
      (the lab's `_left_alpha` documented rule)
    - g-node (exact):   r + (1-2*p)*l  => r+l for p=0, r-l for p=1, where
      p = benc(left-half decisions) is the partial-sum feedback (the lab's
      `_merge_beta` tree reconstructs exactly F^otimes h over the decided
      left half; benc here is the packet-local butterfly, proven equal to
      the lab's polar_encode at startup)
    - leaf: decide bit 1 iff LLR < 0 else 0 (LLR = log P(0)/P(1))
    - frozen positions (info_mask==0) pinned to 0
    - the lab's clip applied to the leaf LLRs: conditional_llr outputs are
      table lookups already within +-clip, so np.clip here is idempotent.

    Same priors (shared conditional_llr tables), same frozen masks, same
    natural-order plane structure as the lab arm; only the SC recursion is
    independently implemented (recursive formulation, packet-local).
    """
    L = np.clip(np.asarray(llr, dtype=np.float64), -float(clip), float(clip))
    n = int(L.size)
    if n == 0 or (n & (n - 1)) != 0:
        raise ValueError("mirror SC needs a power-of-two length, got %d" % n)
    info = np.asarray(info_mask).astype(bool)
    out = np.zeros(n, dtype=np.int64)

    def rec(vec, base):
        m = vec.size
        if m == 1:
            if info[base]:  # frozen leaves stay 0 (pinned)
                out[base] = 1 if vec[0] < 0.0 else 0
            return
        h = m // 2
        left_in = vec[:h]
        right_in = vec[h:]
        # min-sum f-node, lab sign convention (x >= 0 => +1)
        sl = np.where(left_in >= 0.0, 1.0, -1.0)
        sr = np.where(right_in >= 0.0, 1.0, -1.0)
        fnode = sl * sr * np.minimum(np.abs(left_in), np.abs(right_in))
        rec(fnode, base)
        # exact g-node conditioned on the re-encoded (partial-sum
        # feedback) left half: p = benc(uleft)
        pleft = benc(out[base:base + h].copy())
        gnode = right_in + (1.0 - 2.0 * pleft.astype(np.float64)) * left_in
        rec(gnode, base + h)

    rec(L, 0)
    return out


def mirror_decode_planes(y, tables, masks, r, n):
    """Mirror arm chain: same priors/prefix wiring, mirror SC per plane
    (own prefix from the mirror's OWN decoded planes, packet-local benc
    re-encode for the next prefix)."""
    dec_u, dec_x = [], []
    for i in range(r):
        pref = (msd.prefix_from_bits(dec_x, i) if i
                else np.zeros(n, dtype=np.int64))
        llr = msd.conditional_llr(tables, i, y, pref)
        uh = mirror_min_sum_sc(llr, masks[i])
        dec_u.append(uh)
        dec_x.append(benc(uh))
    return dec_u, dec_x


def _first_divergence(a, b, kinfos, gaps):
    """First differing info position (natural order) between two decoded
    planes; returns (kind, gap) with kind in {equal, tie, hard}."""
    if np.array_equal(a, b):
        return "equal", None
    for p in kinfos:
        if int(a[p]) != int(b[p]):
            gp = float(gaps.get(int(p), 0.0)) if gaps else 0.0
            return ("hard", gp) if gp > TIE_TOL else ("tie", gp)
    return "equal", None  # differ only at frozen positions (both pinned 0)


def gate1_armBlab(q, r, pmf, tables_f4):
    """G1c (Amendment 2): TWO records on the SAME salt-5 instance stream
    (100 F4-family + 100 random uniform per q; n in {2,4}).

    Returns (mirror_rec, approx_rec):
      mirror_rec  -- GATE: lab-arm decode vs the independent packet-local
          min-sum mirror (integration fidelity; requires 0 hard
          mismatches, ties <= 1e-9).
      approx_rec  -- NON-gating diagnostic gates.G1c_approx_gap: the SAME
          lab-arm decode vs exact brute-force MAP, counted with the same
          first-divergence/tie convention (documented property of the
          min-sum production baseline).
    """
    rng = np.random.default_rng([DESIGN_SEED, 700 + q, 5])
    mirror_rec = {"oracle": "min_sum_mirror", "strict_matches": 0,
                  "tie_tolerated": 0, "hard_mismatches": 0,
                  "n_instances": 0, "by_group": {}}
    approx_rec = {"oracle": "exact_brute_MAP", "strict_matches": 0,
                  "tie_tolerated": 0, "hard_mismatches": 0,
                  "n_instances": 0, "hard_gap_magnitudes": [],
                  "by_group": {}, "by_n": {2: {"n_instances": 0,
                                               "hard_mismatches": 0},
                                           4: {"n_instances": 0,
                                               "hard_mismatches": 0}}}
    for group in ("F4", "randT"):
        gm = {"strict_matches": 0, "tie_tolerated": 0,
              "hard_mismatches": 0, "n_instances": 0}
        ga = {"strict_matches": 0, "tie_tolerated": 0,
              "hard_mismatches": 0, "n_instances": 0}
        for n, reps in ((2, 50), (4, 50)):
            n_log = lab_n_log(n)
            order = pc.reliable_order(n)
            for _ in range(reps):
                kinfos = []
                masks = []
                for _ in range(r):
                    k = int(rng.integers(0, n + 1))
                    mask = pc.info_mask_from_order(order, k, n)
                    masks.append(mask)
                    kinfos.append(np.flatnonzero(mask).astype(np.int64))
                ubits = [np.zeros(n, dtype=np.int64) for _ in range(r)]
                for i in range(r):
                    if len(kinfos[i]):
                        ubits[i][kinfos[i]] = rng.integers(
                            0, 2, size=len(kinfos[i]))
                a = np.zeros(n, dtype=np.int64)
                for i in range(r):
                    x = pc.polar_encode(ubits[i], n_log)
                    a |= x.astype(np.int64) << (r - 1 - i)
                if group == "F4":
                    d = rng.choice(q, size=n, p=pmf)
                    y = (a + d) % q
                    tables = tables_f4
                else:
                    T = rng.uniform(0.05, 1.0, size=(q, q))
                    T /= T.sum(axis=1, keepdims=True)
                    y = np.array(
                        [rng.choice(q, p=T[int(a[j])]) for j in range(n)]
                    )
                    # randT is not circulant: joint build, NOT the shift
                    # projection (smoothing 0 keeps it ratio-exact).
                    tables = msd.build_msd_llr_tables(
                        T, q, smoothing=0.0, clip=30.0)
                # (1) lab-arm decode (production chain, hard-prefix)
                uhs, dec_x = lab_decode_planes(y, tables, masks, r, n)
                # (2) independent min-sum mirror chain (same priors/masks)
                uhs_m, _ = mirror_decode_planes(y, tables, masks, r, n)
                # (3) exact brute successive-MAP under the LAB chain priors
                #     (for the first-divergence gaps AND the approx gap)
                brutes = []
                for i in range(r):
                    pref = (msd.prefix_from_bits(dec_x[:i], i) if i
                            else np.zeros(n, dtype=np.int64))
                    llr = msd.conditional_llr(tables, i, y, pref)
                    M = np.zeros((n, 2), dtype=float)
                    M[:, 1] = -llr  # log-odds: llr = log P(0)/P(1)
                    froz = np.asarray(masks[i]) == 0
                    brutes.append(brute_successive_from_M(M, froz))
                # G1c gate: lab vs mirror (first-divergence classification
                # uses the same exact-MAP top-two gaps as the convention)
                ok_m = True
                for i in range(r):
                    kind, gp = _first_divergence(
                        uhs[i], uhs_m[i], kinfos[i], brutes[i][1])
                    if kind != "equal":
                        ok_m = False
                        if kind == "hard":
                            gm["hard_mismatches"] += 1
                        else:
                            gm["tie_tolerated"] += 1
                gm["strict_matches"] += int(ok_m)
                gm["n_instances"] += 1
                # Diagnostic: lab vs exact MAP (approx gap, NON-gating)
                ok_a = True
                hard_this = 0
                for i in range(r):
                    bu, gaps = brutes[i]
                    kind, gp = _first_divergence(
                        uhs[i], bu, kinfos[i], gaps)
                    if kind != "equal":
                        ok_a = False
                        if kind == "hard":
                            ga["hard_mismatches"] += 1
                            hard_this += 1
                            approx_rec["hard_gap_magnitudes"].append(gp)
                        else:
                            ga["tie_tolerated"] += 1
                ga["strict_matches"] += int(ok_a)
                ga["n_instances"] += 1
                approx_rec["by_n"][n]["n_instances"] += 1
                approx_rec["by_n"][n]["hard_mismatches"] += hard_this
        mirror_rec["by_group"][group] = gm
        approx_rec["by_group"][group] = ga
        for k in ("strict_matches", "tie_tolerated", "hard_mismatches",
                  "n_instances"):
            mirror_rec[k] += gm[k]
            approx_rec[k] += ga[k]
    approx_rec["hard_gap_magnitudes"].sort()
    return mirror_rec, approx_rec


def lab_head():
    try:
        out = subprocess.run(
            ["git", "-C", LAB_REPO, "rev-parse", "HEAD"],
            capture_output=True, text=True, check=True,
        )
        return out.stdout.strip()
    except Exception as exc:  # provenance still recorded, never silently
        return "unavailable: %r" % (exc,)


def fail(msg):
    sys.stderr.write("GATE-FAIL: " + msg + "\n")
    sys.exit(1)


def check_encoder_equivalence():
    """benc (packet-local) and pc.polar_encode (lab) must both be F^otimes n."""
    rng = np.random.default_rng(20260924)
    for n in (2, 4, 128):
        n_log = lab_n_log(n)
        for _ in range(5):
            u = rng.integers(0, 2, size=n).astype(np.int64)
            if not np.array_equal(benc(u),
                                  pc.polar_encode(u, n_log).astype(np.int64)):
                fail("encoder equivalence benc vs polar_encode n=%d" % n)


def prepare_cell(q, R, K, designs, ctx):
    r = MS[q]
    infoA = designs[q]["armA"][R]
    frozenA = np.array([i for i in range(N_SYM)
                        if i not in set(infoA.tolist())])
    infoB = designs[q]["armB"][R]
    selB = sorted([(i, int(p)) for i in range(r) for p in infoB[i]])
    assert len(selB) == r * K
    lab_masks_list = lab_plane_masks(K, r)
    lab_infos = [np.flatnonzero(m).astype(np.int64) for m in lab_masks_list]
    slots_lab = lab_slots(lab_infos)
    assert len(slots_lab) == r * K
    return {"q": q, "R": R, "K": K, "r": r,
            "infoA": infoA, "frozenA": frozenA,
            "infoB": infoB, "selB": selB,
            "lab_masks": lab_masks_list, "slots_lab": slots_lab}


def excerpt_fails(pack, seed, ctx):
    q, r, K = pack["q"], pack["r"], pack["K"]
    rng = np.random.default_rng([seed, q, K])
    fails = {"A": [], "Bhard": [], "Bsoft": [], "Blab": []}
    for _ in range(BLOCKS_PER_SEED):
        msg = rng.integers(0, q, size=K).astype(np.int64)
        noise = rng.choice(q, size=N_SYM, p=ctx[q]["pmf"])
        fails["A"].append(not armA_block(
            msg, pack["infoA"], pack["frozenA"], ctx[q]["field"], q,
            noise, ctx[q]["logpmf"]))
        fails["Bhard"].append(not armB_block(
            msg, pack["selB"], pack["infoB"], q, r, noise,
            ctx[q]["logpmf"], ctx[q]["sym_of"], ctx[q]["EJBs"]))
        fails["Bsoft"].append(not armB_block_soft(
            msg, pack["selB"], pack["infoB"], q, r, noise,
            ctx[q]["logpmf"], ctx[q]["sym_of"], ctx[q]["EJBs"],
            ctx[q]["Wmat"]))
        fails["Blab"].append(not armB_lab_block(
            msg, pack["slots_lab"], pack["lab_masks"], q, r, noise,
            ctx[q]["tables_f4"]))
    return fails


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--probe-root", required=True)
    args = ap.parse_args()
    root = args.probe_root
    t0 = time.time()

    # One-shot: never overwrite an existing result (rerun guard).
    for fname in ("results.json", "notes.md"):
        if os.path.exists(os.path.join(root, fname)):
            fail("target output already exists: %s" % fname)
    if not os.path.exists(os.path.join(root, "prereg.md")):
        fail("frozen prereg.md missing from probe root")

    assert K_SYMS == tuple(int(round(R * N_SYM)) for R in RS), "K grid changed"
    check_encoder_equivalence()

    ctx = {}
    for q in QS:
        field = make_gf2m(MS[q], PRIMS[q])  # raises if pin mismatches F3
        pmf = f4_pmf(q)
        logpmf = np.log(pmf)
        H = h_delta_bits(pmf)
        Wmat = pmf[(np.arange(q)[:, None] - np.arange(q)[None, :]) % q]
        G, GINV, bits_of, sym_of = build_sym_tables(MS[q])
        # Lab F4 tables (frozen amendment 1): exact F4 difference pmf ->
        # shift-invariant joint with scale = n_sym (ratio-invariant at
        # smoothing 0) -> MSD LLR tables, smoothing 0.0, clip 30.0.
        joint = msd.shift_invariant_joint(pmf, q, scale=float(N_SYM))
        tables_f4, _ = msd.build_msd_llr_tables_shift(
            joint, q, smoothing=0.0, clip=30.0)
        ctx[q] = {
            "field": field, "pmf": pmf, "logpmf": logpmf, "H": H,
            "Wmat": Wmat, "sym_of": sym_of,
            "EJBs": [build_EJB(MS[q], i) for i in range(MS[q])],
            "tables_f4": tables_f4,
        }

    gates = {}
    approx_gap = {}  # filled by the amended G1c (non-gating diagnostic)

    # ---- Designs (deterministic re-design, seed 2026092400; in memory) ----
    designs = {}
    for q in QS:
        infosA, HA = design_armA(ctx[q]["field"], q, ctx[q]["pmf"],
                                 ctx[q]["logpmf"])
        designs[q] = {"armA": infosA, "Hmc": HA}
        infosB = {}
        for R, K in zip(RS, K_SYMS):
            ib, _ = design_armB(q, MS[q], ctx[q]["Wmat"], K)
            infosB[R] = ib
        designs[q]["armB"] = infosB

    # ---- G0: dedicated B-hard-only reproduction pass (bit-exact vs Step-1) ----
    with open(STEP1_RESULTS) as fh:
        step1 = json.load(fh)
    g0_cells = {}
    for q in QS:
        r = MS[q]
        for R, K in zip(RS, K_SYMS):
            infoB = designs[q]["armB"][R]
            selB = sorted([(i, int(p)) for i in range(r) for p in infoB[i]])
            fes = []
            for seed in SCREEN_SEEDS:
                rng = np.random.default_rng([seed, q, K])
                fb = 0
                for _ in range(BLOCKS_PER_SEED):
                    msg = rng.integers(0, q, size=K).astype(np.int64)
                    noise = rng.choice(q, size=N_SYM, p=ctx[q]["pmf"])
                    good = armB_block(msg, selB, infoB, q, r, noise,
                                      ctx[q]["logpmf"], ctx[q]["sym_of"],
                                      ctx[q]["EJBs"])
                    fb += int(not good)
                fes.append(fb / BLOCKS_PER_SEED)
            mean = summarize(fes)["mean"]
            key = "q%d_R%.2f" % (q, R)
            ref = step1["cells"][key]["armB_fer"]["mean"]
            g0_cells[key] = {"computed": mean, "step1": ref,
                             "equal": bool(mean == ref)}
            if mean != ref:
                fail("G0 %s: computed %r != step1 %r" % (key, mean, ref))
    gates["G0"] = {"cells": g0_cells, "all_equal": True, "n_cells": 12}
    print("G0 PASS: 12/12 cells bit-exact vs Step-1", flush=True)

    # ---- Oracles G1 (arm A) / G1b (B-soft) / G1c (B-lab) ----
    for q in QS:
        recA = gate1_armA(ctx[q]["field"], q, ctx[q]["pmf"], ctx[q]["logpmf"])
        if "error" in recA:
            fail("G1 armA q=%d: %s" % (q, recA["error"]))
        gates["G1_q%d" % q] = recA
        if recA["n_instances"] < 200 or recA["hard_mismatches"] != 0:
            fail("G1 armA q=%d: n=%d hard=%d" % (
                q, recA["n_instances"], recA["hard_mismatches"]))

        recS = gate1_armBsoft(q, MS[q], ctx[q]["pmf"], ctx[q]["logpmf"],
                              ctx[q]["Wmat"])
        gates["G1b_q%d" % q] = recS
        if recS["n_instances"] < 200 or recS["hard_mismatches"] != 0:
            fail("G1b Bsoft q=%d: n=%d hard=%d" % (
                q, recS["n_instances"], recS["hard_mismatches"]))

        recL_m, recL_a = gate1_armBlab(q, MS[q], ctx[q]["pmf"],
                                       ctx[q]["tables_f4"])
        gates["G1c_q%d" % q] = recL_m
        approx_gap["q%d" % q] = recL_a
        if recL_m["n_instances"] < 200 or recL_m["hard_mismatches"] != 0:
            fail("G1c Blab mirror q=%d: n=%d hard=%d" % (
                q, recL_m["n_instances"], recL_m["hard_mismatches"]))
        print("G1/G1b/G1c q=%d: A %d/%d hard=%d | soft %d/%d hard=%d | "
              "lab-mirror %d/%d hard=%d | approx-gap lab-vs-MAP hard=%d "
              "(ties=%d)" % (
                  q, recA["strict_matches"], recA["n_instances"],
                  recA["hard_mismatches"],
                  recS["strict_matches"], recS["n_instances"],
                  recS["hard_mismatches"],
                  recL_m["strict_matches"], recL_m["n_instances"],
                  recL_m["hard_mismatches"],
                  recL_a["hard_mismatches"],
                  recL_a["tie_tolerated"]), flush=True)

    # Amendment 2: NON-gating diagnostic record (min-sum vs exact MAP).
    gates["G1c_approx_gap"] = {
        "oracle": "exact_brute_MAP (lab-arm decode vs brute-force MAP; "
                  "diagnostic property of the min-sum production baseline; "
                  "NOT a gate failure, never tuned away)",
        "per_q": approx_gap,
    }

    # ---- G2 noiseless round-trip (R=0.50 info sets; 4 arms x 20) ----
    for q in QS:
        r = MS[q]
        for ai, arm in enumerate(("A", "Bhard", "Bsoft", "Blab")):
            rng = np.random.default_rng([DESIGN_SEED, 800 + q, ai + 1])
            K = K_SYMS[2]
            pack = prepare_cell(q, 0.50, K, designs, ctx)
            okc = 0
            for _ in range(G2_BLOCKS):
                msg = rng.integers(0, q, size=K).astype(np.int64)
                if arm == "A":
                    u = np.zeros(N_SYM, dtype=np.int64)
                    u[pack["infoA"]] = msg
                    x = polar_transform(u, field=ctx[q]["field"], alpha=ALPHA)
                    logp = np.full((N_SYM, q), -np.inf)
                    logp[np.arange(N_SYM), x] = 0.0
                    res = sc_decode(
                        logp, field=ctx[q]["field"], alpha=ALPHA,
                        known_positions=pack["frozenA"],
                        known_values=np.zeros(len(pack["frozenA"]),
                                              dtype=np.int64),
                    )
                    okc += int(np.array_equal(res.u_hat[pack["infoA"]], msg))
                elif arm == "Bhard":
                    okc += int(armB_block_noiseless(
                        msg, pack["selB"], pack["infoB"], q, r,
                        ctx[q]["sym_of"]))
                elif arm == "Bsoft":
                    okc += int(armB_block_noiseless_soft(
                        msg, pack["selB"], pack["infoB"], q, r,
                        ctx[q]["sym_of"]))
                else:
                    okc += int(armB_lab_block_noiseless(
                        msg, pack["slots_lab"], pack["lab_masks"], r,
                        ctx[q]["tables_f4"]))
            gates["G2_q%d_arm%s" % (q, arm)] = {"ok": okc, "n": G2_BLOCKS}
            if okc != G2_BLOCKS:
                fail("G2 %s q=%d: %d/%d" % (arm, q, okc, G2_BLOCKS))

    # ---- G3 low-rate smoke (R=0.30; dedicated sample; 4 arms) ----
    for q in QS:
        r = MS[q]
        for ai, arm in enumerate(("A", "Bhard", "Bsoft", "Blab")):
            rng = np.random.default_rng([DESIGN_SEED, 900 + q, ai + 1])
            K = K_SYMS[0]
            pack = prepare_cell(q, 0.30, K, designs, ctx)
            fails = 0
            for _ in range(G3_SMOKE_BLOCKS):
                msg = rng.integers(0, q, size=K).astype(np.int64)
                noise = rng.choice(q, size=N_SYM, p=ctx[q]["pmf"])
                if arm == "A":
                    good = armA_block(msg, pack["infoA"], pack["frozenA"],
                                      ctx[q]["field"], q, noise,
                                      ctx[q]["logpmf"])
                elif arm == "Bhard":
                    good = armB_block(msg, pack["selB"], pack["infoB"], q, r,
                                      noise, ctx[q]["logpmf"],
                                      ctx[q]["sym_of"], ctx[q]["EJBs"])
                elif arm == "Bsoft":
                    good = armB_block_soft(msg, pack["selB"], pack["infoB"],
                                           q, r, noise, ctx[q]["logpmf"],
                                           ctx[q]["sym_of"], ctx[q]["EJBs"],
                                           ctx[q]["Wmat"])
                else:
                    good = armB_lab_block(msg, pack["slots_lab"],
                                          pack["lab_masks"], q, r, noise,
                                          ctx[q]["tables_f4"])
                fails += int(not good)
            fer = fails / G3_SMOKE_BLOCKS
            gates["G3smoke_q%d_%s" % (q, arm)] = {
                "fer": fer, "fails": fails, "n": G3_SMOKE_BLOCKS}
            if fer >= 0.5:
                fail("G3 smoke %s q=%d: FER=%r" % (arm, q, fer))

    # ---- Screening (paired: one msg + one noise per (q,R,seed,block),
    #      fed to ALL FOUR arms; rng discipline identical to Step-1) ----
    cells = {}
    packs = {}
    for q in QS:
        r = MS[q]
        H = ctx[q]["H"]
        for R, K in zip(RS, K_SYMS):
            pack = prepare_cell(q, R, K, designs, ctx)
            packs["q%d_R%.2f" % (q, R)] = pack
            fA, fBh, fBs, fBl = [], [], [], []
            for seed in SCREEN_SEEDS:
                rng = np.random.default_rng([seed, q, K])
                ca = cbh = cbs = cbl = 0
                for _ in range(BLOCKS_PER_SEED):
                    msg = rng.integers(0, q, size=K).astype(np.int64)
                    noise = rng.choice(q, size=N_SYM, p=ctx[q]["pmf"])
                    goodA = armA_block(msg, pack["infoA"], pack["frozenA"],
                                       ctx[q]["field"], q, noise,
                                       ctx[q]["logpmf"])
                    goodBh = armB_block(msg, pack["selB"], pack["infoB"],
                                        q, r, noise, ctx[q]["logpmf"],
                                        ctx[q]["sym_of"], ctx[q]["EJBs"])
                    goodBs = armB_block_soft(msg, pack["selB"], pack["infoB"],
                                             q, r, noise, ctx[q]["logpmf"],
                                             ctx[q]["sym_of"], ctx[q]["EJBs"],
                                             ctx[q]["Wmat"])
                    goodBl = armB_lab_block(msg, pack["slots_lab"],
                                            pack["lab_masks"], q, r, noise,
                                            ctx[q]["tables_f4"])
                    ca += int(not goodA)
                    cbh += int(not goodBh)
                    cbs += int(not goodBs)
                    cbl += int(not goodBl)
                fA.append(ca / BLOCKS_PER_SEED)
                fBh.append(cbh / BLOCKS_PER_SEED)
                fBs.append(cbs / BLOCKS_PER_SEED)
                fBl.append(cbl / BLOCKS_PER_SEED)
            sA = summarize(fA)
            sBh = summarize(fBh)
            sBs = summarize(fBs)
            sBl = summarize(fBl)
            d_ba = [b - a for b, a in zip(fBs, fA)]
            d_bh = [b - h for b, h in zip(fBs, fBh)]
            d_la = [l - a for l, a in zip(fBl, fA)]
            f = r * K / (N_SYM * H)
            key = "q%d_R%.2f" % (q, R)
            cells[key] = {
                "q": q, "R": R, "K_sym": K, "n_sym": N_SYM,
                "H_delta_bits": H, "f": f, "n_blocks": N_BLOCKS,
                "n_seeds": len(SCREEN_SEEDS),
                "blocks_per_seed": BLOCKS_PER_SEED,
                "armA_fer": sA, "armB_hard_fer": sBh,
                "armB_soft_fer": sBs, "armB_lab_fer": sBl,
                "paired_dfer_Bsoft_A": summarize(d_ba),
                "paired_dfer_Bsoft_Bhard": summarize(d_bh),
                "paired_dfer_Blab_A": summarize(d_la),
            }
            if R == 0.30:
                for arm_key, s in (("A", sA), ("Bhard", sBh),
                                   ("Bsoft", sBs), ("Blab", sBl)):
                    if s["mean"] >= 0.5:
                        fail("G3 full-screen recheck arm%s %s" % (arm_key, key))
            print("cell %s f=%.4f FER_A=%.4f FER_Bhard=%.4f FER_Bsoft=%.4f "
                  "FER_Blab=%.4f d(Bsoft-A)=%.4f d(Blab-A)=%.4f" % (
                      key, f, sA["mean"], sBh["mean"], sBs["mean"],
                      sBl["mean"], sBs["mean"] - sA["mean"],
                      sBl["mean"] - sA["mean"]), flush=True)

    gates["G3recheck"] = {
        "ok": True,
        "cells": {k: {a: cells[k][s]["mean"] for a, s in
                      (("A", "armA_fer"), ("Bhard", "armB_hard_fer"),
                       ("Bsoft", "armB_soft_fer"), ("Blab", "armB_lab_fer"))}
                  for k in cells if cells[k]["R"] == 0.30},
    }

    # ---- G4 determinism excerpt (q4 R0.40, seed 2026092401, four arms) ----
    g4_key = "q4_R0.40"
    g4_seed = 2026092401
    run1 = excerpt_fails(packs[g4_key], g4_seed, ctx)
    run2 = excerpt_fails(packs[g4_key], g4_seed, ctx)
    runs_identical = all(run1[a] == run2[a] for a in run1)
    series_key = {"A": "armA_fer", "Bhard": "armB_hard_fer",
                  "Bsoft": "armB_soft_fer", "Blab": "armB_lab_fer"}
    matches = all(
        sum(run1[a]) / BLOCKS_PER_SEED
        == cells[g4_key][series_key[a]]["series"][0] for a in run1)
    gates["G4"] = {
        "cell": g4_key, "seed": g4_seed,
        "runs_identical": bool(runs_identical),
        "matches_screening": bool(matches),
        "fail_counts": {a: int(sum(run1[a])) for a in run1},
        "n": BLOCKS_PER_SEED,
    }
    if not runs_identical:
        fail("G4: excerpt reruns differ")
    if not matches:
        fail("G4: excerpt differs from screening series[0]")

    wall = time.time() - t0
    if wall > 7200:
        fail("budget exceeded: wall=%.1f s > 7200" % wall)

    # ---- Single end-of-run write (only reachable with all gates passed) ----
    results = {
        "probe": "NBPOLAR-EXPLORATION-STEP1B-SOFT-BASELINE",
        "tier": "X",
        "question": ("on the frozen Step-1 envelope (F4, q in {4,8,16}, "
                     "n_sym=128, R in {0.30,0.40,0.50,0.60}, identical "
                     "seeds/blocks/pairing), does the native q-ary SC "
                     "separation SURVIVE when the bit-plane arm is upgraded "
                     "from hard to exact soft-carrying MSD conditioning, and "
                     "how does the production binary baseline compare?"),
        "freeze": {
            "F1": "arm A native = UNCHANGED Step-1 arm A (q-ary polar SC "
                  "via read-only comparison_bench.formal_ir.nbpolar; "
                  "GF(4)=0b111, GF(8)=0b1011, GF(16)=0b10011; alpha=2; "
                  "design seed 2026092400)",
            "F2": "arm B-hard = faithful Step-1 arm B (Gray bit-plane "
                  "MLC-polar, packet-local binary butterfly + Arikan SC, "
                  "MSD hard conditioning, joint top-(r*K_sym) design); "
                  "fidelity gated bit-exactly by G0",
            "F3": "arm B-soft = same decomposition/design as F2, decoding "
                  "only changed to exact soft-carrying MSD: plane 0 raw "
                  "marginal induced channel; plane i>0 per-position binary "
                  "log-prior log S_b - log(S_0+S_1) with S_b = sum W[y-sym] "
                  "* prod_{j<i} belief_j * 2^{-(r-1-i)} over reflected-Gray "
                  "symbol() terms, later planes uniform, beliefs = plane j "
                  "SC leaf posteriors re-encoded to codeword-bit beliefs",
            "F4": "channel/seeds: P(d=0)=0.75, P(d=+1)=0.24, P(d=-1)=0.005, "
                  "0.005 uniform over other q-3 offsets (mod q); screening "
                  "seeds 2026092401..2026092416 (16) x 64 blocks = 1024 per "
                  "(q,R); one message + one noise per (seed,block) shared "
                  "across ALL FOUR arms; numpy default_rng",
            "F5": "metric: FER per (q,R,arm) over 1024 blocks; per-seed "
                  "series + mean/sample-std/range; primary paired dFER = "
                  "Bsoft-A; secondary Bsoft-Bhard; tertiary Blab-A; "
                  "H_delta 0.8818511717297366 / 0.8934608122041734 / "
                  "0.900353370320442 (q4/q8/q16); f = r*K_sym/(n_sym*H); "
                  "NO numeric threshold; negatives kept as evidence",
            "F6": "gates (all binding): G0 bit-exact B-hard reproduction "
                  "vs Step-1 on 12 cells; G1/G1b oracles >=200 tiny "
                  "instances per q (arm A / B-soft) vs brute-force "
                  "successive-MAP, 0 hard mismatches (ties <=1e-9, "
                  "first-divergence cascade); G1c (amendment 2): lab-arm "
                  "decode vs an INDEPENDENTLY coded packet-local min-sum "
                  "recursion mirror, >=200 tiny instances per q "
                  "(100 F4-family + 100 random uniform), 0 hard "
                  "mismatches, ties <=1e-9 (integration fidelity); the "
                  "lab-vs-exact-MAP divergence is recorded NON-gating in "
                  "gates.G1c_approx_gap; G2 noiseless 20/20 per q per "
                  "arm; G3 smoke FER(R=0.30) < 0.5 all four arms; G4 "
                  "determinism excerpt identical; failure => STOP with zero "
                  "output writes",
            "F7": "interpreter: "
                  "/home/karel_303/.venvs/hd-qkd-polar-comparison/bin/python "
                  "(numpy 2.4.4, pandas 3.0.2, numba); nothing installed",
            "AMENDMENT_1": "fourth arm B-lab = read-only import of "
                           "/mnt/d/Code/qkd-reconciliation-lab "
                           "(qkd_recon.polar_core + qkd_recon."
                           "msd_conditional; 3GPP PW order beta=2^0.25; "
                           "shift-invariant exact-F4 MSD tables smoothing "
                           "0.0 clip 30.0; uniform per-plane k_i=K_sym; "
                           "hard-prefix soft metric; natural-plane order, "
                           "plane 0 = MSB, NOT Gray); gate G1c; tertiary "
                           "paired metric Blab-A; wall budget 7200 s",
            "AMENDMENT_2": "G1c redefined to a min-sum MIRROR oracle: "
                           "lab-arm decode must equal an independently "
                           "coded packet-local min-sum SC mirror "
                           "(f-node sign*min(|l|,|r|), exact g-node, "
                           "lab clip; same priors/masks/plane structure), "
                           "0 hard mismatches; the min-sum-vs-exact-MAP "
                           "hard-mismatch counts are measured on the same "
                           "instances and recorded in "
                           "gates.G1c_approx_gap as a documented "
                           "property of the production baseline (NOT a "
                           "gate failure, never tuned away)",
        },
        "gates": gates,
        "population": {
            "kind": "synthetic (L2 screening ledger; never L1 real-data FER)",
            "n_sym": N_SYM,
            "q_set": list(QS),
            "channel": "F4 single member (see freeze.F4)",
            "arms": ["A", "Bhard", "Bsoft", "Blab"],
            "design_seed": DESIGN_SEED,
            "design_mc_samples_armA": DESIGN_MC_SAMPLES,
            "screening_seeds": list(SCREEN_SEEDS),
        },
        "cells": cells,
        "attestation": {
            "no_real_data": True,
            "no_fer_claim": True,
            "ledger": "L2 synthetic screening — never cited as L1 "
                      "real-data FER",
        },
        "counters": {"s1b_runs": 1, "reruns": 0, "rebuilds": 0},
        "stop_rules_fired": [],
        "wall_s": wall,
    }
    with open(os.path.join(root, "results.json"), "w") as fh:
        json.dump(results, fh, indent=2)
        fh.write("\n")

    # ---- notes.md ----
    head = lab_head()
    lines = []
    lines.append("# Notes - NBPOLAR-EXPLORATION-STEP1B-SOFT-BASELINE (Tier-X)")
    lines.append("")
    lines.append("Synthetic L2 screening readout. No claim about real-data "
                 "FER, efficiency, promotion, qualification, or "
                 "composable-key yield.")
    lines.append("")
    lines.append("Exact command: PYTHONPATH=comparison_bench/src "
                 "/home/karel_303/.venvs/hd-qkd-polar-comparison/bin/python "
                 ".workbuddy/queue/NBPOLAR-EXPLORATION-STEP1B-SOFT-BASELINE/"
                 "s1b_screen.py --probe-root " + root)
    lines.append("Interpreter used: %s (F7 primary; no substitution needed)."
                 % sys.executable)
    lines.append("Read-only hygiene env (set by the script before any lab/"
                 "numba import and exported for the official command): "
                 "PYTHONDONTWRITEBYTECODE=1, "
                 "NUMBA_CACHE_DIR=/tmp/opencode/s1b_numba_cache, "
                 "OMP/OPENBLAS/MKL/NUMBA_NUM_THREADS=1 (plus "
                 "sys.dont_write_bytecode=True). These prevent .pyc writes "
                 "in comparison_bench/ and the lab repo and redirect the "
                 "lab's numba cache=True writes out of the lab tree.")
    lines.append("Wall time: %.1f s (budget 7200 s). Single-threaded; "
                 "s1b_runs=1, reruns=0, rebuilds=0; stop rules fired: "
                 "none." % wall)
    lines.append("")
    lines.append("## G0 reproduction (B-hard vs frozen Step-1)")
    for key in sorted(g0_cells):
        ev = g0_cells[key]
        lines.append("- %s: computed=%r step1=%r equal=%s" % (
            key, ev["computed"], ev["step1"], ev["equal"]))
    lines.append("All 12 cells bit-exact (identical float means): the "
                 "packet-local B-hard is a faithful Step-1 re-implementation "
                 "and the screening draw order (per (q,R,seed) rng "
                 "[seed,q,K], message then noise per block, arms consume no "
                 "rng) is unchanged.")
    lines.append("")
    lines.append("## B-soft soft-carrying MSD as implemented (F3/R1)")
    lines.append("- Plane 0: the Step-1 raw plane_priors (later-marginalized "
                 "induced binary channel, log domain).")
    lines.append("- Plane i>0: per-position binary log-prior "
                 "log S_b - log(S_0+S_1) with S_b(p) = sum_{e,l} "
                 "W[p, symbol(e,b,l)] * prod_{j<i} belief_j(p, e_j) * "
                 "2^{-(r-1-i)}; symbol() is the shared reflected-Gray map "
                 "(via the EJB tables), later planes a_{>i} are marginalized "
                 "uniformly (<= 2^(r-1) <= 8 terms per (position, b)), and "
                 "W[p, s] = P(y_p | s) is the frozen transition table in "
                 "probability domain: F4 screening/gates use Wmat[y, s] = "
                 "P_F4((y-s) mod q); the randT gate group uses the drawn "
                 "T.T[y]; the noiseless G2 run uses the exact delta metric "
                 "rows exp(log p) per the Step-1 noiseless convention.")
    lines.append("- belief_j(p, ·) is plane j's posterior over its "
                 "CODEWORD bit at position p (codeword domain is what "
                 "symbol() composes): leaf posteriors q_t = "
                 "sigmoid(M1-M0) from the packet-local log-domain SC "
                 "(bdec_soft), frozen leaves pinned q_t = 0, then exact "
                 "parity re-encode through the self-inverse benc: "
                 "P(x_p=1) = (1 - prod_{t in S_p} (1-2 q_t))/2 with "
                 "S_p = {t : benc(e_t)[p] = 1} (frozen factors neutral, "
                 "q_t=0 gives factor 1).")
    lines.append("- Raw-vs-normalized per-position constants are "
                 "decision-invariant: a constant common to both b values at "
                 "one position shifts the score of EVERY candidate codeword "
                 "assignment by the same total, so decisions and top-two "
                 "gaps are unchanged (both bdec and the brute enumerator "
                 "compare candidates within one position set). Plane 0 is "
                 "used raw; planes i>0 are normalized log S_b - "
                 "log(S_0+S_1) as frozen.")
    lines.append("- Deterministic float64; no numerical tolerance beyond "
                 "the frozen tie rule.")
    lines.append("")
    lines.append("## Oracle tie rule (G1/G1b/G1c)")
    lines.append("A coordinate where the brute top-two log-scores differ by "
                 "<= 1e-9 is tie-tolerated (either tied-best choice "
                 "accepted); a differing non-tied FIRST divergence (natural "
                 "position order; later differences are cascade once "
                 "prefixes differ) is a hard mismatch (gate needs 0). "
                 "Discrete F4-family metrics make exact ties possible, "
                 "hence the rule. Brute enumerators use textbook-SC "
                 "semantics: every future position (info AND frozen) is "
                 "marginalized; only the decided prefix (past info decisions "
                 "plus past frozen pins) constrains candidates. Divergences "
                 "are classified per divergent plane at its first differing "
                 "information position; later planes inherit the diverged "
                 "prefix (cascade).")
    lines.append("G1/G1b mix per q: 100 F4-family + 100 random uniform "
                 "transition matrices (50 each of n_sym=2 and n_sym=4), "
                 "random K in 0..n and random info positions per instance; "
                 "salts [design_seed, 700+q, 1] (arm A, Step-1 verbatim) "
                 "and [design_seed, 700+q, 2] (B-soft on the same Step-1 "
                 "arm-B instance stream). G1c uses salt "
                 "[design_seed, 700+q, 5] with random k per plane but "
                 "PW-top-k positions.")
    lines.append("Random transition matrices: rows iid Uniform(0.05, 1), "
                 "row-normalized. G1b recomputes each plane's priors with "
                 "an independent naive nested-loop implementation before "
                 "the brute enumeration (cross-check of the vectorized "
                 "soft_priors path).")
    lines.append("")
    lines.append("## G1c min-sum MIRROR oracle (amendment 2, GATE)")
    lines.append("G1c compares the lab-arm decode against an "
                 "INDEPENDENTLY coded packet-local min-sum SC mirror "
                 "(mirror_min_sum_sc in this builder): recursive "
                 "natural-order formulation, f-node sign*min(|l|,|r|) "
                 "with the lab sign convention (x >= 0 => +1), exact "
                 "g-node r + (1-2*p)*l with p = benc(decided left half) "
                 "(partial-sum feedback; the packet-local butterfly, "
                 "proven equal to the lab polar_encode), leaf decides 1 "
                 "iff LLR < 0, frozen pinned to 0, lab clip (30.0) "
                 "re-applied "
                 "(idempotent: conditional_llr outputs are table lookups "
                 "already within +-clip). The mirror runs its OWN "
                 "plane-prefix chain from its own decoded planes "
                 "(packet-local benc re-encode), with the SAME "
                 "conditional_llr priors, the SAME frozen masks, and the "
                 "SAME natural (non-Gray) plane structure as the lab arm. "
                 "It is NOT a copy of the lab's iterative sc_decode_frame "
                 "recursion; the gate therefore tests integration "
                 "fidelity (masks/priors/plane wiring + documented "
                 "min-sum semantics), not optimality. "
                 "Requirement: >=200 instances per q (100 F4-family + "
                 "100 random uniform), 0 hard mismatches, ties <= 1e-9.")
    lines.append("Instance stream identical to the diagnostic below: "
                 "salt [design_seed, 700+q, 5], random k per plane, "
                 "PW-top-k positions, 50 each of n_sym in {2,4} per "
                 "channel group.")
    lines.append("")
    lines.append("## Documented approximation gap (B-lab property, "
                 "NON-gating: gates.G1c_approx_gap)")
    lines.append("On the SAME G1c instances the lab-arm decode is also "
                 "compared against the exact brute-force MAP under "
                 "identical priors (first-divergence/tie convention "
                 "above). The lab production decoder's f-node is MIN-SUM "
                 "(an approximation), so nonzero counts here are a "
                 "property of the production baseline, NOT a gate "
                 "failure, and must not be tuned away. Arms A and "
                 "B-hard/B-soft use exact recursions; the native-vs-"
                 "binary axis is held clean by B-soft, and B-lab is the "
                 "production reference with its approximation on record.")
    for qk in sorted(approx_gap):
        ar = approx_gap[qk]
        lines.append(
            "- %s: lab-vs-exact-MAP hard=%d ties=%d strict=%d/%d "
            "(by_n: n2 hard=%d/%d, n4 hard=%d/%d)" % (
                qk, ar["hard_mismatches"], ar["tie_tolerated"],
                ar["strict_matches"], ar["n_instances"],
                ar["by_n"][2]["hard_mismatches"],
                ar["by_n"][2]["n_instances"],
                ar["by_n"][4]["hard_mismatches"],
                ar["by_n"][4]["n_instances"]))
        if ar["hard_gap_magnitudes"]:
            lines.append("    hard-divergence exact-MAP gap magnitudes: "
                         "min=%.4g max=%.4g (all > 1e-9 tie tol)" % (
                             ar["hard_gap_magnitudes"][0],
                             ar["hard_gap_magnitudes"][-1]))
    lines.append("")
    lines.append("## B-lab provenance (amendment 1)")
    lines.append("- Lab path: %s ; git HEAD: %s ; license: MIT. READ-ONLY: "
                 "the lab repo is never modified or written." % (LAB_REPO, head))
    lines.append("- Import: sys.path.insert(0, \"%s\") then "
                 "qkd_recon.polar_core and qkd_recon.msd_conditional. "
                 "Functions used: polar_core.reliable_order "
                 "(beta=2**0.25), polar_core.info_mask_from_order, "
                 "polar_core.polar_encode (non-systematic F^otimes n; "
                 "verified equal to the packet-local benc at startup), "
                 "polar_core.sc_decode_frame; msd_conditional."
                 "shift_invariant_joint, build_msd_llr_tables_shift, "
                 "build_msd_llr_tables, conditional_llr, "
                 "prefix_from_bits." % LAB_SRC)
    lines.append("- F4 tables: shift_invariant_joint(exact F4 offset pmf, "
                 "q, scale=n_sym=128) then build_msd_llr_tables_shift(., q, "
                 "smoothing=0.0, clip=30.0). scale=n_sym is ratio-invariant "
                 "at smoothing 0 (only count RATIOS enter the LLRs; no "
                 "pseudo-counts), and the pmf is exact, so smoothing would "
                 "only add pseudo-counts. clip=30.0 is the lab default and "
                 "inactive at F4 magnitudes.")
    lines.append("- G1c randT tables: build_msd_llr_tables(exact drawn T, "
                 "q, smoothing=0.0, clip=30.0) on the joint counts "
                 "directly -- the shift build would project a NON-circulant "
                 "random T onto the circulant model.")
    lines.append("- Lab conventions: plane order = natural binary "
                 "(plane 0 = MSB = symbol bit r-1-i, prefix MSB-first), "
                 "NOT Gray; message bits natural LSB-first per symbol "
                 "placed into (plane, position) slots sorted plane-major "
                 "(a FER-invariant bijection; extraction mirrors it); "
                 "uniform per-plane k_i = K_sym (lab adaptive "
                 "rate_allocation.py out of scope - recorded "
                 "simplification); frozen u=0 channel framing; decode = "
                 "conditional_llr (hard decoded prefix of physical planes) "
                 "-> sc_decode_frame -> polar_encode for the next prefix.")
    lines.append("- G2 for B-lab: noise = 0 through the actual frozen F4 "
                 "tables (not a delta shortcut).")
    lines.append("")
    lines.append("## Gates and conventions")
    lines.append("- G2 noiseless: 20 blocks per (q, arm), four arms, R=0.50 "
                 "info sets; streams [design_seed, 800+q, 1..4] for "
                 "A/Bhard/Bsoft/Blab (A and Bhard streams identical to "
                 "Step-1).")
    lines.append("- G3 smoke: 256 blocks at R=0.30 per (q, arm) with "
                 "dedicated streams [design_seed, 900+q, 1..4], applied to "
                 "ALL FOUR arms (strictest reading), before any screening "
                 "arithmetic; the full-screening R=0.30 cells of all four "
                 "arms are rechecked against the same < 0.5 bar "
                 "pre-write.")
    lines.append("- G4 determinism: excerpt cell q4_R0.40, seed 2026092401, "
                 "64 blocks, four arms, re-run twice from a fresh rng; both "
                 "runs identical AND equal to the screening per-seed series "
                 "value of that seed.")
    lines.append("- Arm-A design seed note: design seed 2026092400 is "
                 "consumed by the arm-A Monte-Carlo design only; the "
                 "arm-B design (Bhattacharyya) and the lab masks (static "
                 "PW order) are exact/deterministic.")
    lines.append("")
    lines.append("## Headline screening table (per-seed mean FER over 16 "
                 "seeds x 64 blocks; d = paired per-seed differences)")
    for q in QS:
        for R in RS:
            c = cells["q%d_R%.2f" % (q, R)]
            lines.append(
                "q=%d R=%.2f f=%.4f FER_A=%.4f FER_Bhard=%.4f "
                "FER_Bsoft=%.4f FER_Blab=%.4f d(Bsoft-A)=%.4f+-%.4f "
                "d(Bsoft-Bhard)=%.4f+-%.4f d(Blab-A)=%.4f+-%.4f" % (
                    q, R, c["f"], c["armA_fer"]["mean"],
                    c["armB_hard_fer"]["mean"], c["armB_soft_fer"]["mean"],
                    c["armB_lab_fer"]["mean"],
                    c["paired_dfer_Bsoft_A"]["mean"],
                    c["paired_dfer_Bsoft_A"]["sample_std"],
                    c["paired_dfer_Bsoft_Bhard"]["mean"],
                    c["paired_dfer_Bsoft_Bhard"]["sample_std"],
                    c["paired_dfer_Blab_A"]["mean"],
                    c["paired_dfer_Blab_A"]["sample_std"]))
    lines.append("")
    lines.append("H_delta bits: " + ", ".join(
        "q=%d %.16g" % (q, ctx[q]["H"]) for q in QS))
    lines.append("Gate summary: G0 12/12 bit-exact; " + "; ".join(
        "G1_q%d n=%d hard=%d" % (q, gates["G1_q%d" % q]["n_instances"],
                                 gates["G1_q%d" % q]["hard_mismatches"])
        for q in QS) + "; " + "; ".join(
        "G1b_q%d n=%d hard=%d" % (q, gates["G1b_q%d" % q]["n_instances"],
                                  gates["G1b_q%d" % q]["hard_mismatches"])
        for q in QS) + "; " + "; ".join(
        "G1c-mirror_q%d n=%d hard=%d" % (q,
                                         gates["G1c_q%d" % q]["n_instances"],
                                         gates["G1c_q%d" % q]["hard_mismatches"])
        for q in QS) + "; G1c_approx_gap (NON-gating): " + "; ".join(
        "q%d hard=%d/200 (n4=%d)" % (
            q, approx_gap["q%d" % q]["hard_mismatches"],
            approx_gap["q%d" % q]["by_n"][4]["hard_mismatches"])
        for q in QS) + "; G2 20/20 x 4 arms x 3 q; G3 smoke < 0.5 (four "
        "arms); G3 recheck ok; G4 identical=" +
        str(gates["G4"]["runs_identical"]) + " matches_screening=" +
        str(gates["G4"]["matches_screening"]) + ".")
    lines.append("Counters: s1b_runs=1 reruns=0 rebuilds=0. "
                 "Stop rules fired: none. Qualitative reading only -- no "
                 "numeric threshold anywhere in this probe.")
    lines.append("Write scope: this root holds exactly prereg.md (P1 copy, "
                 "byte-identical), results.json, notes.md. "
                 "comparison_bench/formal_ir and the lab repo imported "
                 "read-only under the hygiene env.")
    with open(os.path.join(root, "notes.md"), "w") as fh:
        fh.write("\n".join(lines) + "\n")
    print("WROTE results.json + notes.md in %.1f s" % wall, flush=True)


if __name__ == "__main__":
    main()
