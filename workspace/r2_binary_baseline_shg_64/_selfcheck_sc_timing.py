"""Timing probe (synthetic, no real data): measures wall time of ONE
`polar_sc_decode_with_frozen` call at N=4096 (the packet's real LAYER_N),
after JIT warm-up, to quantify the O(N^2 log N) finding precisely rather
than by extrapolation from a killed run."""
import sys
import time
from pathlib import Path

import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from src.reconciliation.real_polar_sc_rescue import polar_sc_decode_with_frozen, polar_encode_non_systematic

n = 4096
n_log = 12
rng = np.random.default_rng(0)
u = rng.integers(0, 2, size=n).astype(np.int8)
x = polar_encode_non_systematic(u, n_log)
llr = np.where(x == 0, 5.0, -5.0).astype(np.float64)
mask = np.ones(n, dtype=np.int8)
frozen_values = np.zeros(n, dtype=np.int8)

# warm-up (JIT compile)
_ = polar_sc_decode_with_frozen(llr, mask, frozen_values, n_log)

n_trials = 20
t0 = time.perf_counter()
for _ in range(n_trials):
    _ = polar_sc_decode_with_frozen(llr, mask, frozen_values, n_log)
dt = time.perf_counter() - t0
per_call = dt / n_trials
print(f"N={n}: {n_trials} calls in {dt:.4f}s -> {per_call*1000:.3f} ms/call (post-JIT)")

# also measure N=1024 and N=256 for the O(N^2 log N) scaling check
for nn, nl in ((1024, 10), (256, 8)):
    uu = rng.integers(0, 2, size=nn).astype(np.int8)
    xx = polar_encode_non_systematic(uu, nl)
    ll = np.where(xx == 0, 5.0, -5.0).astype(np.float64)
    mm = np.ones(nn, dtype=np.int8)
    ff = np.zeros(nn, dtype=np.int8)
    _ = polar_sc_decode_with_frozen(ll, mm, ff, nl)
    t0 = time.perf_counter()
    for _ in range(n_trials):
        _ = polar_sc_decode_with_frozen(ll, mm, ff, nl)
    dt = time.perf_counter() - t0
    print(f"N={nn}: {n_trials} calls in {dt:.4f}s -> {dt/n_trials*1000:.3f} ms/call (post-JIT)")
