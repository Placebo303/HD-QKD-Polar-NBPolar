# P2-R1 CAL prior validation (diagnostic-index recovery)

Attempt: R1 1/1 consumed at first NPZ/JSON open; P2 attempt 1/1 preserved MODEL_F_INPUT_CANDIDATE BLOCKED.
Artifact: `/mnt/d/Code/HD-QKD_Polar_Comparison/workspace/v72p2d5_model_f_input/20260907_r1` (`model_f_input.npz` 208467 B + `model_f_input_summary.json` 752 B), session `20260123_1M_600k_0dB`, CAL 702..1725, 1024 frames x 256 pairs = 262144 symbols, axis [Alice,Bob], GF32 poly37, lambda* 137.3823795883264.

Method (frozen, repaired): `f3` layout `[U1,B,U2]` (32,1024,32); selection `f3[u1,nz_b,:] -> (K,32)`; weights `p_b[nz_b,None] -> (K,1)`; loader `prior_artifact.load_prior_artifact` (allow_pickle=False, exact keys/shapes/sums/identity); formula `prior.smooth_joint_to_conditional/derive_p1/derive_p2`; entropy `cal_diagnostic.select_bob_slice/weighted_conditional_entropy` plus independent `math.log2` triple-loop oracle.

Gates (all PASS, single earliest would BLOCK):
- schema/identity/packing/bans/provenance: PASS (transpose sentinel |p_b - row-marginal| max 2.098e-04; packing 1024/1024; PRIOR_ONLY/FULL_BOB_ONLY).
- formula: max |prod - literal| 0.000e+00 <= 1e-12; spot 3-column loop max 0.000e+00.
- normalization: f-col 2.931e-14, P1-col 6.661e-16, P2-row 2.554e-15 <= 1e-12; slice loop max 3.331e-16.
- fallbacks/support: unseen-B 0, zero-(U1,B) 0, exact-zero f cells 0, K 1024/1024, bad empirical-zero 0.
- entropy oracle: |H1-oracle| 3.553e-15, |H2-oracle| 6.217e-15, |direct-oracle| 0.000e+00 <= 1e-12.
- chain: discrepancy |chain - direct| 8.882e-16 <= 1e-10 (oracle chain discrepancy 8.882e-16).

Results (bits/symbol, CAL-resubstitution descriptives only):
- H(U1|B) = 4.286720430201
- H(U2|U1,B) = 3.222719884634
- H(chain) = 7.509440314836
- H(A|B) direct = 7.509440314836
- chain discrepancy = 8.882e-16
- CE resubstitution = 5.598503961835 (training fit only, never threshold/selection)

Resources: wall 0.370 s (budget 300 s), peak RSS 183656448 B (ceiling 2147483648 B).

Scope: CAL-only descriptions; no FER/leakage/key-rate, no DEV/EVAL, no SC/oracle decode, no construction/K, no Model-F fit, no lambda/floor change, no parquet/TTBin, no sibling/production writes, no commit/push, no P3, no promotion. Candidate requires independent Pre-RESULT review; self-acceptance forbidden.
