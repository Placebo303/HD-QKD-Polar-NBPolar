import sys
sys.path.insert(0, "/mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar")
import numpy as np
from src.reconciliation.real_polar_sc_rescue import polar_encode_non_systematic

for n_log in (2, 3, 4, 6):
    n = 1 << n_log
    rng = np.random.default_rng(0)
    for _ in range(30):
        u = rng.integers(0, 2, size=n).astype(np.int8)
        x = polar_encode_non_systematic(u, n_log)
        u2 = polar_encode_non_systematic(x, n_log)
        assert np.array_equal(u, u2), (n_log, u, x, u2)
print("self-inverse: CONFIRMED for n_log in (2,3,4,6)")
