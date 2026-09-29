import numpy as np, sys
sys.setrecursionlimit(10000)
def f_ms(a, b):
    return np.sign(a) * np.sign(b) * np.minimum(np.abs(a), np.abs(b))
def f_ex(a, b):
    p = np.tanh(np.clip(a, -30, 30) / 2) * np.tanh(np.clip(b, -30, 30) / 2)
    return 2 * np.arctanh(np.clip(p, -1 + 1e-15, 1 - 1e-15))
def genie_sc_stats(llr, u, fnode=f_ms, clipg=None):
    """llr,u: (F,N). Returns (Zsum(N), errsum(N), Ssum(N)) accumulated over frames, genie SC with true u."""
    F, N = llr.shape
    Z = np.zeros(N); E = np.zeros(N); S = np.zeros(N)
    def rec(al, us, off):
        n = al.shape[1]
        if n == 1:
            s = al[:, 0] * (1 - 2.0 * us[:, 0])
            s = np.clip(s, -700, 700)
            Z[off] += np.exp(-s / 2).sum(); E[off] += (s < 0).sum() + 0.5 * (s == 0).sum(); S[off] += s.sum()
            return us.astype(np.int8)
        h = n // 2
        l, r = al[:, :h], al[:, h:]
        bl = rec(fnode(l, r), us[:, :h], off)
        br_in = r + (1 - 2.0 * bl) * l
        if clipg is not None: br_in = np.clip(br_in, -clipg, clipg)
        br = rec(br_in, us[:, h:], off + h)
        return np.concatenate([bl ^ br, br], axis=1)
    rec(llr.astype(np.float64), u.astype(np.int8), 0)
    return Z, E, S

def sc_decode(llr, mask, u_true, fnode=f_ms):
    """Vectorised SC over frames with true frozen values. llr (F,N) float; mask (N,) 1=info; u_true (F,N).
    Returns per-frame error bool (any info-bit decision wrong == codeword wrong)."""
    F, N = llr.shape
    bad = np.zeros(F, bool)
    def rec(al, off):
        n = al.shape[1]
        if n == 1:
            if mask[off]:
                bit = (al[:, 0] < 0).astype(np.int8)
                bad[:] |= (bit != u_true[:, off])
            else:
                bit = u_true[:, off].astype(np.int8)
            return bit[:, None]
        h = n // 2; l, r = al[:, :h], al[:, h:]
        bl = rec(fnode(l, r), off)
        br = rec(r + (1 - 2.0 * bl) * l, off + h)
        return np.concatenate([bl ^ br, br], axis=1)
    rec(llr.astype(np.float64), 0)
    return bad
