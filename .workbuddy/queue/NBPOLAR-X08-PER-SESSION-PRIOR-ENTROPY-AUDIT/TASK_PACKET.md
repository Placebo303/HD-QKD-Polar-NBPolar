# X08 Tier-X packet — per-session prior entropy audit (lambda vs raw-MLE+floor)

## Question
Did the P20H per-session calibration's lambda=137.3823795883264 concentration
smoothing inflate the 1.5M TRAIN prior entropy H1 relative to the P7-equivalent
raw-count MLE + 1e-15 floor rule, and by how much? Descriptive decision input only.

## Frozen inputs
- Exactly ONE worktree-artifact content open (read-only, no reopen):
  .workbuddy/queue/NBPOLAR-PHASE4-P20H-PER-SESSION-CALIBRATION/per_session_calibration/calibrated_prior.npz
  keys exactly PRIOR_NPZ_KEYS; np.load(allow_pickle=False).
  Canonical digest must equal e8dd078a5367ba3af8eba91022d58aeffc114bc30b847b13cd4bb890e5dde43b.
- Code (pure, no I/O): smooth_joint_to_conditional / derive_p1 / derive_p2 (prior.py);
  entropy_bits (target_construction.py); canonical_prior_digest / PRIOR_NPZ_KEYS
  (per_session_calibration.py).
- No protected counts NPZ, no parquet, no sibling-checkout artifact, no decoder/RNG/tag.

## Frozen computation (two variants, same functionals as P20H)
f = smooth_joint_to_conditional(counts_ab, lam); floor 1e-15 per cell; column
renormalize; p1 = derive_p1(f), p2 = derive_p2(f), p_b = column totals / total;
H1 = sum_b p_b * entropy_bits(p1, axis=0);
H2 = sum_b p_b * sum_u1 p1[u1,b] * entropy_bits(p2, axis=2).
Variant L (control): lam = 137.3823795883264; must reproduce stored literals
h1=2.006647056368773, h2=1.9017235959286112 within 1e-12.
Variant R (P7 rule): lam = 0.0 (zero columns fall back to p_global).
No other lambda values. No tuning, no scan.
Independent literal reimplementation of Variant R raw conditional
(counts/n_b; zero columns -> p_global) as cross-check.
Also report: counts total, zero cells, zero columns; floor-hit counts per variant;
implied K_total = floor((1.3*32768*H_total - 64)/5) clipped [0,65536] per variant;
frozen key-bits reference 34119; frozen K1 levels {319,447,575,831} at 5 bits.

## Output
Only: workspace/probes/nbpolar_x08_per_session_prior_entropy_audit/ (prereg.md, body.py,
results.json) and the two packet docs above. Probe root must be ABSENT beforehand.

## Stop rules
Digest mismatch, key-set mismatch, second open, nonfinite value, body/prereg byte
mismatch -> STOP, record, return. A rerun to fix an execution error is allowed and
must be recorded in results.json; no rerun to change results.

## Return
Deltas only: files created, exact command, key numbers, exit code. No verdicts,
no thresholds, no claims, no pass/fail language.
