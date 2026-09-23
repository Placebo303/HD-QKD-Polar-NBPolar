#!/usr/bin/env python3
"""Tier-X Step-1 screening builder (packet-local, stdlib + numpy).

Packet: NBPOLAR-EXPLORATION-STEP1-SCREENING (amendment 2).
Frozen: native q-ary polar SC (arm A, read-only reuse of
comparison_bench.formal_ir.nbpolar) vs Gray bit-plane MLC-polar with MSD
hard conditioning (arm B, packet-local binary polar). Synthetic F4 channel
only. Single invocation: gates -> designs -> screening -> ONE end-of-run
write of results.json + notes.md. Any gate failure exits non-zero with NO
output-root writes. This file never imports real data and never modifies
comparison_bench/ (imports only).
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
G3_SMOKE_BLOCKS = 256
DESIGN_MC_SAMPLES = 3000
TIE_TOL = 1e-9  # log-domain gap below which a coordinate is tie-tolerated

P_F4 = {  # P(delta=0), P(delta=+1), P(delta=-1), rest mass over other offsets
    "p0": 0.75,
    "p1": 0.24,
    "pm1": 0.005,
    "prest": 0.005,
}


# ---------------- Small helpers ----------------
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


# ---------------- Packet-local binary polar (arm B) ----------------
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


def build_sym_tables(r):
    """Gray bit convention (frozen): plane i = bit i (LSB-first) of the
    reflected Gray codeword, i.e. plane order 0..r-1 runs over increasing
    Gray significance. Shared by both arms' message bookkeeping."""
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
    """Exact induced binary transition (later-marginalized, earlier-hard):
    S_j(b) = logsumexp_l logp_sym[j, sym(e_j, b, l)]."""
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


# ---------------- Arm-A design: MC genie-SC entropy via sc_decode ----------------
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


# ---------------- Arm-B design: exact Bhattacharyya + joint top ----------------
def design_armB(q, r, Wmat, K):
    Zb = []
    for i in range(r):
        EJB = build_EJB(r, i)
        # P[y, e, b] = (1/2^(r-1)) sum_l W(y | sym(e, b, l)): the 1/2^(r-1)
        # normalization keeps Bhattacharyya values comparable across planes.
        P = Wmat[:, EJB].sum(axis=3) / (1 << (r - 1))
        Z0 = float(np.sqrt(P[:, :, 0] * P[:, :, 1]).sum())
        # standard even/odd recursion from the base value
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


# ---------------- Batch q-ary codebooks (gates) ----------------
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
    # also exercise the reused oracle enumerator pattern once per (q, n),
    # within its tiny-domain cap (q**n <= 4096)
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


# ---------------- Gate G1 ----------------
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


def brute_successive_bplane(y, logp_sym_row, froz, Emat, sym_of, r, i):
    """Independent per-plane successive MAP: own later-marginalization loops
    (no EJB tables, no SC recursion), exhaustive over plane codewords.

    Textbook-SC semantics: all future plane positions (info and frozen)
    are marginalized; only the decided prefix constrains candidates."""
    n = len(y)
    Ew = Emat  # (n, i) decoded earlier bits
    # own later-marginalization M_j(b)
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
    # enumerate plane codewords
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
                # No constraint on future positions (info or frozen):
                # textbook-SC semantics marginalize all of them.
                vals.append(sum(M[j, xe[j]] for j in range(n)))
            sc.append(np.logaddexp.reduce(np.array(vals)))
        order = np.argsort([-sc[0], -sc[1]], kind="stable")
        gaps[p] = float(abs(sc[0] - sc[1]))
        pre.append(int(order[0]))
    return np.array(pre, dtype=np.int64), gaps


def gate1_armB(q, r, pmf, logpmf):
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
                # MSD decode with hard conditioning on decoded earlier planes
                # (CODEWORD bits: re-encoded — y depends on transmitted bits)
                dec = []
                E = np.zeros((n, 0), dtype=np.int64)
                for i in range(r):
                    L0, L1 = plane_priors(logp_sym, E, EJBs[i])
                    uh = bdec(L0, L1, frozs[i])
                    dec.append(uh)
                    E = (np.column_stack([E, benc(uh)]) if E.shape[1]
                         else benc(uh)[:, None])
                dec_sym = np.array(
                    [sym_of([int(dec[i][j]) for i in range(r)])
                     for j in range(n)],
                    dtype=np.int64,
                )
                # independent brute-force MSD enumerator, conditioned on the
                # DECODER's earlier planes (the same hard MSD conditioning)
                strict = True
                for i in range(r):
                    Econd = (np.column_stack([benc(d) for d in dec[:i]]) if i
                             else np.zeros((n, 0), dtype=np.int64))
                    bu, gaps = brute_successive_bplane(
                        y, logp_sym,
                        [bool(v) for v in frozs[i]], Econd, sym_of, r, i
                    )
                    if not np.array_equal(dec[i], bu):
                        strict = False
                        # First divergence in plane order; later positions
                        # are cascade once prefixes differ.
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


# ---------------- Block encode/decode ----------------
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
        # MSD conditions on earlier planes' CODEWORD bits: re-encode.
        E = np.column_stack([E, benc(uh)])
    got = []
    for i, p in sel_order:
        got.append(int(dec[i][p]))
    # regroup into symbols
    ok = True
    for s_idx, s in enumerate(msg):
        chunk = got[s_idx * r:(s_idx + 1) * r]
        if sym_of(chunk) != int(s):
            ok = False
            break
    return ok


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
        # MSD conditions on earlier planes' CODEWORD bits: re-encode.
        E = np.column_stack([E, benc(uh)])
    got = [int(dec[i][p]) for i, p in sel_order]
    for s_idx, s in enumerate(msg):
        if sym_of(got[s_idx * r:(s_idx + 1) * r]) != int(s):
            return False
    return True


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
        field = make_gf2m(MS[q], PRIMS[q])  # raises if pin mismatches F3
        pmf = f4_pmf(q)
        logpmf = np.log(pmf)
        H = h_delta_bits(pmf)
        Wmat = pmf[(np.arange(q)[:, None] - np.arange(q)[None, :]) % q]
        G, GINV, bits_of, sym_of = build_sym_tables(MS[q])
        ctx[q] = {
            "field": field, "pmf": pmf, "logpmf": logpmf, "H": H,
            "Wmat": Wmat, "sym_of": sym_of,
            "EJBs": [build_EJB(MS[q], i) for i in range(MS[q])],
        }

    gates = {}
    # ---- G1 oracle agreement (before any screening arithmetic) ----
    for q in QS:
        recA = gate1_armA(ctx[q]["field"], q, ctx[q]["pmf"], ctx[q]["logpmf"])
        if "error" in recA:
            fail("G1 armA q=%d: %s" % (q, recA["error"]))
        recB = gate1_armB(q, MS[q], ctx[q]["pmf"], ctx[q]["logpmf"])
        gates["G1_q%d" % q] = {"armA": recA, "armB": recB}
        for arm, rec in (("armA", recA), ("armB", recB)):
            if rec["n_instances"] < 200 or rec["hard_mismatches"] != 0:
                fail("G1 %s q=%d: n=%d hard=%d" % (
                    arm, q, rec["n_instances"], rec["hard_mismatches"]))

    # ---- Designs (in memory; no files written) ----
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

    # ---- G2 noiseless round-trip (R=0.50 info sets) ----
    for q in QS:
        for arm in ("armA", "armB"):
            rng = np.random.default_rng([DESIGN_SEED, 800 + q,
                                         1 if arm == "armA" else 2])
            K = K_SYMS[2]
            okc = 0
            for _ in range(20):
                msg = rng.integers(0, q, size=K).astype(np.int64)
                if arm == "armA":
                    info_idx = designs[q]["armA"][0.50]
                    frozen_idx = np.array(
                        [i for i in range(N_SYM)
                         if i not in set(info_idx.tolist())])
                    u = np.zeros(N_SYM, dtype=np.int64)
                    u[info_idx] = msg
                    x = polar_transform(u, field=ctx[q]["field"], alpha=ALPHA)
                    logp = np.full((N_SYM, q), -np.inf)
                    logp[np.arange(N_SYM), x] = 0.0
                    res = sc_decode(
                        logp, field=ctx[q]["field"], alpha=ALPHA,
                        known_positions=frozen_idx,
                        known_values=np.zeros(len(frozen_idx),
                                              dtype=np.int64),
                    )
                    okc += int(np.array_equal(res.u_hat[info_idx], msg))
                else:
                    ib = designs[q]["armB"][0.50]
                    r = MS[q]
                    sel = sorted(
                        [(i, int(p)) for i in range(r) for p in ib[i]])
                    okc += int(armB_block_noiseless(
                        msg, sel, ib, q, r, ctx[q]["sym_of"]))
            gates["G2_q%d_%s" % (q, arm)] = {"ok": okc, "n": 20}
            if okc != 20:
                fail("G2 %s q=%d: %d/20" % (arm, q, okc))

    # ---- G3 low-rate smoke (R=0.30, dedicated sample, in-memory designs) ----
    for q in QS:
        for ai, arm in enumerate(("armA", "armB")):
            rng = np.random.default_rng([DESIGN_SEED, 900 + q, ai + 1])
            K = K_SYMS[0]
            fails = 0
            for _ in range(G3_SMOKE_BLOCKS):
                msg = rng.integers(0, q, size=K).astype(np.int64)
                noise = rng.choice(q, size=N_SYM, p=ctx[q]["pmf"])
                if arm == "armA":
                    info_idx = designs[q]["armA"][0.30]
                    frozen_idx = np.array(
                        [i for i in range(N_SYM)
                         if i not in set(info_idx.tolist())])
                    good = armA_block(msg, info_idx, frozen_idx,
                                      ctx[q]["field"], q, noise,
                                      ctx[q]["logpmf"])
                else:
                    ib = designs[q]["armB"][0.30]
                    r = MS[q]
                    sel = sorted(
                        [(i, int(p)) for i in range(r) for p in ib[i]])
                    good = armB_block(msg, sel, ib, q, r, noise,
                                      ctx[q]["logpmf"], ctx[q]["sym_of"],
                                      ctx[q]["EJBs"])
                fails += int(not good)
            fer = fails / G3_SMOKE_BLOCKS
            gates["G3smoke_q%d_%s" % (q, arm)] = {
                "fer": fer, "fails": fails, "n": G3_SMOKE_BLOCKS}
            if fer >= 0.5:
                fail("G3 smoke %s q=%d: FER=%r" % (arm, q, fer))

    # ---- Screening (paired within each (q, R, seed, block)) ----
    cells = {}
    for q in QS:
        r = MS[q]
        H = ctx[q]["H"]
        for R, K in zip(RS, K_SYMS):
            infoA = designs[q]["armA"][R]
            frozenA = np.array([i for i in range(N_SYM)
                                if i not in set(infoA.tolist())])
            infoB = designs[q]["armB"][R]
            selB = sorted([(i, int(p)) for i in range(r) for p in infoB[i]])
            assert len(selB) == r * K
            ferA_seeds, ferB_seeds, dfer_seeds = [], [], []
            for seed in SCREEN_SEEDS:
                rng = np.random.default_rng([seed, q, K])
                fa = fb = 0
                for _ in range(BLOCKS_PER_SEED):
                    msg = rng.integers(0, q, size=K).astype(np.int64)
                    noise = rng.choice(q, size=N_SYM, p=ctx[q]["pmf"])
                    goodA = armA_block(msg, infoA, frozenA, ctx[q]["field"],
                                       q, noise, ctx[q]["logpmf"])
                    goodB = armB_block(msg, selB, infoB, q, r, noise,
                                       ctx[q]["logpmf"], ctx[q]["sym_of"],
                                       ctx[q]["EJBs"])
                    fa += int(not goodA)
                    fb += int(not goodB)
                feA, feB = fa / BLOCKS_PER_SEED, fb / BLOCKS_PER_SEED
                ferA_seeds.append(feA)
                ferB_seeds.append(feB)
                dfer_seeds.append(feB - feA)
            sA, sB, sD = (summarize(ferA_seeds), summarize(ferB_seeds),
                          summarize(dfer_seeds))
            f = r * K / (N_SYM * H)
            cells["q%d_R%.2f" % (q, R)] = {
                "q": q, "R": R, "K_sym": K, "n_sym": N_SYM,
                "H_delta_bits": H, "f": f, "n_blocks": N_BLOCKS,
                "n_seeds": len(SCREEN_SEEDS),
                "blocks_per_seed": BLOCKS_PER_SEED,
                "armA_fer": sA, "armB_fer": sB, "paired_dFER": sD,
            }
            key = "q%d_R%.2f" % (q, R)
            if cells[key]["armA_fer"]["mean"] >= 0.5 and R == 0.30:
                fail("G3 full-screen recheck armA %s" % key)
            if cells[key]["armB_fer"]["mean"] >= 0.5 and R == 0.30:
                fail("G3 full-screen recheck armB %s" % key)
            print("cell %s f=%.4f FER_A=%.4f FER_B=%.4f dFER=%.4f" % (
                key, f, sA["mean"], sB["mean"], sD["mean"]), flush=True)

    wall = time.time() - t0
    # ---- Single end-of-run write (only reachable with all gates passed) ----
    results = {
        "probe": "NBPOLAR-EXPLORATION-STEP1-SCREENING",
        "tier": "X",
        "question": ("does native-symbol decoding (arm A) separate from "
                     "bit-plane binary decomposition with ordered MSD "
                     "conditioning (arm B) on FER-f at matched "
                     "rate/block-length/prior over q in {4,8,16}?"),
        "freeze": {
            "F1": "arm A = q-ary polar SC via read-only reuse of "
                  "comparison_bench.formal_ir.nbpolar "
                  "(make_gf2m/transform.polar_transform alpha=2/sc.sc_decode, "
                  "oracle enumerator pattern for gate spot-checks)",
            "F2": "arm B = r-level Gray bit-plane MLC-polar, packet-local "
                  "binary butterfly + Arikan SC (log-domain), MSD hard "
                  "conditioning on earlier decoded planes, plane order "
                  "0..r-1, plane i = bit i (LSB-first) of reflected Gray",
            "F3": "GF(4)=0b111, GF(8)=0b1011, GF(16)=0b10011; alpha=2; "
                  "reflected Gray shared by both arms",
            "F4": "P(d=0)=0.75, P(d=+1)=0.24, P(d=-1)=0.005, 0.005 uniform "
                  "over other q-3 offsets (mod q)",
            "F5": "n_sym=128; R in {0.30,0.40,0.50,0.60}; "
                  "K_sym={38,51,64,77}; design seed 2026092400",
            "F6": "screening seeds 2026092401..2026092416 (16); 64 "
                  "blocks/seed => 1024 blocks per (q,R,arm); paired "
                  "message+noise per (seed,block) across arms; "
                  "numpy default_rng",
            "F7": "arm-A design: MC mean posterior entropy under genie "
                  "(true-prefix) SC via the reused sc_decode, top-K_sym; "
                  "arm-B design: exact base Bhattacharyya of the induced "
                  "binary channel + binary even/odd recursion, joint "
                  "top-(r*K_sym) across planes (stable order)",
            "F8": "FER = block-error fraction over 1024 blocks; "
                  "f = r*K_sym/(n_sym*H_delta); per-seed series + "
                  "mean/sample-std/range; paired dFER = FER_B - FER_A; "
                  "no numeric threshold (qualitative bar only)",
        },
        "gates": gates,
        "population": {
            "kind": "synthetic (L2 screening ledger; never L1 real-data FER)",
            "n_sym": N_SYM,
            "q_set": list(QS),
            "channel": "F4 single member (see freeze.F4)",
            "design_seed": DESIGN_SEED,
            "design_mc_samples_armA": DESIGN_MC_SAMPLES,
            "screening_seeds": list(SCREEN_SEEDS),
        },
        "cells": cells,
        "attestation": {
            "no_real_data": True,
            "no_fer_claim": True,
            "ledger": "L2 synthetic screening - never cited as L1 "
                      "real-data FER",
        },
        "counters": {"s1_runs": 1, "reruns": 0, "rebuilds": 0},
        "stop_rules_fired": [],
        "wall_s": wall,
    }
    with open(os.path.join(root, "results.json"), "w") as fh:
        json.dump(results, fh, indent=2)
        fh.write("\n")
    lines = []
    lines.append("# Notes - NBPOLAR-EXPLORATION-STEP1-SCREENING (Tier-X)")
    lines.append("")
    lines.append("Synthetic L2 screening readout. No claim about real-data "
                 "FER, efficiency, promotion, qualification, or "
                 "composable-key yield.")
    lines.append("")
    lines.append("Exact command: PYTHONPATH=comparison_bench/src "
                 "/home/karel_303/.venvs/hd-qkd-polar-comparison/bin/python "
                 ".workbuddy/queue/NBPOLAR-EXPLORATION-STEP1-SCREENING/"
                 "s1_screen.py --probe-root " + root)
    lines.append("Interpreter: primary per amendment 2 (no substitution "
                 "was needed).")
    lines.append("Wall time: %.1f s (budget 5400 s). Single-threaded; "
                 "no reruns." % wall)
    lines.append("")
    lines.append("## Frozen readings applied in this builder")
    lines.append("- G1 'brute-force MAP codeword' is read as independent "
                 "brute-force SUCCESSIVE-MAP enumeration (exhaustive, no "
                 "shared recursion): arm A via batch q-ary codebooks "
                 "spot-checked against polar_transform_reference and the "
                 "reused oracle.oracle_block_log_score; arm B via "
                 "symbol-level exhaustive MSD enumeration with its own "
                 "later-marginalization loops. Both enumerators use "
                 "textbook-SC semantics: every future position (info and "
                 "frozen) is marginalized and only the decided prefix "
                 "constrains candidates, exactly what sc_decode and the "
                 "packet-local binary SC compute. A frozen-conditioned "
                 "enumerator was tried during build and disagreed with the "
                 "frozen sc_decode on 44/200 tiny instances by definition "
                 "(future frozen marginalized, e.g. u0 picked via u1 != 0 "
                 "paths), not by defect; plain block-MAP would likewise "
                 "disagree with any SC decoder by algorithm nature. The "
                 "successive-marginalizing reading is the only gate with "
                 "defect-detection power here (it caught a real plus-branch "
                 "swap in the packet-local binary SC during build).")
    lines.append("- Tie rule: a coordinate where the brute-force top-two "
                 "log-scores differ by <= 1e-9 is tie-tolerated (either "
                 "tied-best choice accepted); a differing non-tied FIRST "
                 "divergence (natural order; later differences are cascade "
                 "once prefixes differ) is a hard mismatch (gate needs 0). "
                 "Discrete F4-family metrics make exact ties possible, "
                 "hence the rule.")
    lines.append("- G1 mix per (arm, q): 100 F4-family (50 n_sym=2 + 50 "
                 "n_sym=4) + 100 random uniform transition matrices "
                 "(50 n_sym=2 + 50 n_sym=4); random K in 0..n and random "
                 "info positions per instance.")
    lines.append("- Random transition matrices: rows iid Uniform(0.05, 1), "
                 "row-normalized (continuous, strictly positive support).")
    lines.append("- Gate RNG streams derive from the design seed with fixed "
                 "salts ([seed, 700+q, arm] G1; [seed, 800+q, arm] G2; "
                 "[seed, 900+q, arm] G3 smoke); codebook spot-check draws "
                 "from fixed seed 777000+q*10+n. Screening streams are "
                 "[seed, q, K] per (q, R, seed). All deterministic.")
    lines.append("- G2 uses the R=0.50 in-memory info sets; 20 blocks per "
                 "(q, arm).")
    lines.append("- G3 smoke uses a dedicated 256-block sample at R=0.30 "
                 "per (q, arm) with the in-memory designs, before any "
                 "screening arithmetic; the full-screening R=0.30 cells "
                 "are rechecked against the same < 0.5 bar before writing.")
    lines.append("- Arm-B rate allocation: joint top-(r*K_sym) over all "
                 "r*N plane positions by Bhattacharyya value (stable "
                 "flattened order); message bits assigned in symbol-major "
                 "Gray order to selected (plane, position) sorted by "
                 "(plane, position).")
    lines.append("- Arm-B design seed note: the Bhattacharyya design is "
                 "exact (no sampling); the frozen design seed is consumed "
                 "by the arm-A Monte-Carlo design only.")
    lines.append("")
    lines.append("## Headline screening table (per-seed mean FER; dFER "
                 "= FER_B - FER_A)")
    for q in QS:
        for R in RS:
            c = cells["q%d_R%.2f" % (q, R)]
            lines.append(
                "q=%d R=%.2f f=%.4f FER_A=%.4f (std %.4f) FER_B=%.4f "
                "(std %.4f) dFER=%.4f (std %.4f, range %s)" % (
                    q, R, c["f"], c["armA_fer"]["mean"],
                    c["armA_fer"]["sample_std"], c["armB_fer"]["mean"],
                    c["armB_fer"]["sample_std"], c["paired_dFER"]["mean"],
                    c["paired_dFER"]["sample_std"],
                    c["paired_dFER"]["range"]))
    lines.append("")
    lines.append("H_delta bits: " + ", ".join(
        "q=%d %.6f" % (q, ctx[q]["H"]) for q in QS))
    lines.append("Counters: s1_runs=1 reruns=0 rebuilds=0. "
                 "Stop rules fired: none.")
    lines.append("Write scope: this root holds exactly prereg.md "
                 "(P1 copy, byte-identical), results.json, notes.md. "
                 "comparison_bench/formal_ir imported read-only.")
    with open(os.path.join(root, "notes.md"), "w") as fh:
        fh.write("\n".join(lines) + "\n")
    print("WROTE results.json + notes.md in %.1f s" % wall, flush=True)


if __name__ == "__main__":
    main()