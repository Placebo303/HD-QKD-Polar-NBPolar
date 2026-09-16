# P11 exact chunked SC gate report

label: EXACT_CHUNKED_SC_CANDIDATE
seed: 2026091800; float64; GF(32) poly 37 alpha 2; chunk_rows 512 vs None
attempts: 1 allowed / 1 consumed at first formal sc_decode call (step-1 N=64 F1_moderate direct arm); no artifact read is authorized or consumed
artifact reads: 0 authorized / 0 consumed. N/A: no artifact/content file is opened at any point; every input is RNG-injected from the frozen seed, so there is nothing to reopen.
wall_total_s: 97.956 (timeout 600 s); rss_final_peak_bytes: 710504448

## Step 1: semantic matrix (default-512 vs None)
primitive cells: 33, all_exact: True
prim rows=1 kind=moderate_m20 exact=True support=True max_finite_abs_err=0.0 support_mismatch_rows=0
prim rows=1 kind=wide_m160 exact=True support=True max_finite_abs_err=0.0 support_mismatch_rows=0
prim rows=1 kind=neginf_support exact=True support=True max_finite_abs_err=0.0 support_mismatch_rows=0
prim rows=31 kind=moderate_m20 exact=True support=True max_finite_abs_err=0.0 support_mismatch_rows=0
prim rows=31 kind=wide_m160 exact=True support=True max_finite_abs_err=0.0 support_mismatch_rows=0
prim rows=31 kind=neginf_support exact=True support=True max_finite_abs_err=0.0 support_mismatch_rows=0
prim rows=32 kind=moderate_m20 exact=True support=True max_finite_abs_err=0.0 support_mismatch_rows=0
prim rows=32 kind=wide_m160 exact=True support=True max_finite_abs_err=0.0 support_mismatch_rows=0
prim rows=32 kind=neginf_support exact=True support=True max_finite_abs_err=0.0 support_mismatch_rows=0
prim rows=33 kind=moderate_m20 exact=True support=True max_finite_abs_err=0.0 support_mismatch_rows=0
prim rows=33 kind=wide_m160 exact=True support=True max_finite_abs_err=0.0 support_mismatch_rows=0
prim rows=33 kind=neginf_support exact=True support=True max_finite_abs_err=0.0 support_mismatch_rows=0
prim rows=127 kind=moderate_m20 exact=True support=True max_finite_abs_err=0.0 support_mismatch_rows=0
prim rows=127 kind=wide_m160 exact=True support=True max_finite_abs_err=0.0 support_mismatch_rows=0
prim rows=127 kind=neginf_support exact=True support=True max_finite_abs_err=0.0 support_mismatch_rows=0
prim rows=128 kind=moderate_m20 exact=True support=True max_finite_abs_err=0.0 support_mismatch_rows=0
prim rows=128 kind=wide_m160 exact=True support=True max_finite_abs_err=0.0 support_mismatch_rows=0
prim rows=128 kind=neginf_support exact=True support=True max_finite_abs_err=0.0 support_mismatch_rows=0
prim rows=129 kind=moderate_m20 exact=True support=True max_finite_abs_err=0.0 support_mismatch_rows=0
prim rows=129 kind=wide_m160 exact=True support=True max_finite_abs_err=0.0 support_mismatch_rows=0
prim rows=129 kind=neginf_support exact=True support=True max_finite_abs_err=0.0 support_mismatch_rows=0
prim rows=511 kind=moderate_m20 exact=True support=True max_finite_abs_err=0.0 support_mismatch_rows=0
prim rows=511 kind=wide_m160 exact=True support=True max_finite_abs_err=0.0 support_mismatch_rows=0
prim rows=511 kind=neginf_support exact=True support=True max_finite_abs_err=0.0 support_mismatch_rows=0
prim rows=512 kind=moderate_m20 exact=True support=True max_finite_abs_err=0.0 support_mismatch_rows=0
prim rows=512 kind=wide_m160 exact=True support=True max_finite_abs_err=0.0 support_mismatch_rows=0
prim rows=512 kind=neginf_support exact=True support=True max_finite_abs_err=0.0 support_mismatch_rows=0
prim rows=513 kind=moderate_m20 exact=True support=True max_finite_abs_err=0.0 support_mismatch_rows=0
prim rows=513 kind=wide_m160 exact=True support=True max_finite_abs_err=0.0 support_mismatch_rows=0
prim rows=513 kind=neginf_support exact=True support=True max_finite_abs_err=0.0 support_mismatch_rows=0
prim rows=2048 kind=moderate_m20 exact=True support=True max_finite_abs_err=0.0 support_mismatch_rows=0
prim rows=2048 kind=wide_m160 exact=True support=True max_finite_abs_err=0.0 support_mismatch_rows=0
prim rows=2048 kind=neginf_support exact=True support=True max_finite_abs_err=0.0 support_mismatch_rows=0
V0 cases: 16, all_parity: True
V0 nan_entry baseline=ValueError: metric contract: logp_x must not contain NaN parity=True
V0 posinf_entry baseline=ValueError: metric contract: logp_x must not contain positive infinity parity=True
V0 all_neginf_row baseline=ValueError: metric contract: every logp_x row needs finite support parity=True
V0 width_mismatch baseline=ValueError: field/shape contract: logp_x width 33 != field q 32 parity=True
V0 non_power_of_two_N baseline=ValueError: field/shape contract: block length N=48 is not a positive power of two parity=True
V0 rank1_input baseline=ValueError: metric contract: logp_x must have shape (N, q), got shape (32,) parity=True
V0 boolean_input baseline=TypeError: metric contract: logp_x must hold float log-scores, got boolean input parity=True
V0 positions_out_of_range baseline=ValueError: known-coordinate contract: positions must lie in 0..7 parity=True
V0 positions_repeat baseline=ValueError: known-coordinate contract: positions must not repeat parity=True
V0 positions_values_length baseline=ValueError: known-coordinate contract: positions and values lengths differ parity=True
V0 positions_none_values_given baseline=ValueError: known-coordinate contract: positions and values must be given together parity=True
V0 positions_given_values_none baseline=ValueError: known-coordinate contract: positions and values must be given together parity=True
V0 float_positions baseline=TypeError: known-coordinate contract: positions must hold integers parity=True
V0 boolean_positions baseline=TypeError: known-coordinate contract: positions must hold integers, got boolean input parity=True
V0 value_out_of_range baseline=ValueError: known-coordinate contract: known_values symbols must lie in 0..31 parity=True
V0 negative_position baseline=ValueError: known-coordinate contract: positions must lie in 0..7 parity=True
N=64 F1_moderate parity=True
N=64 F2_wide parity=True
N=64 F3_neginf_jmod5_evenoff parity=True
N=64 K4_known25pct_positive_support parity=True
N=64 C3_x11_pattern_positive_support parity=True
N=64 C4_impossible_disclosed_value parity=True
N=64 T5_exact_tie parity=True
N=64 T5_ramp parity=True
N=64 T5_near_tie parity=True
N=256 F1_moderate parity=True
N=256 F2_wide parity=True
N=256 F3_neginf_jmod5_evenoff parity=True
N=256 K4_known25pct_positive_support parity=True
N=256 C3_x11_pattern_positive_support parity=True
N=256 C4_impossible_disclosed_value parity=True
N=256 T5_exact_tie parity=True
N=256 T5_ramp parity=True
N=256 T5_near_tie parity=True

## Step 2: paired N=65536 (direct first, then default-512)
parity=True status=ok u_hat_exact=True u_mismatches=0 x_hat_exact=True x_mismatches=0 metrics_exact=True max_finite_metric_abs_err=0.0 support_equal=True argmax_mismatches=0 scores_exact=True max_finite_score_abs_err=0.0 known_mask_exact=True known_count_equal=True provenance_equal=True
wall_s direct=15.684 chunked=14.584; rss_peak_bytes=710504448

## Step 3: N=262144 default-512 completion and resources
status=ok finite_outputs=True wall_s=66.088 (planning target <=120.0 s report-only) rss_peak_bytes=710504448 (hard limit 1610612736; planning target 1073741824 report-only)

## Gates
semantic_parity: True
paired_n65536_exact: True
large_n262144_completion: True
large_n262144_rss: True

## Bounded wording
A candidate means the default-512 allocation path is bitwise-equivalent to the accepted unchunked reference everywhere in the frozen matrix and completes the single N=262144 block within the frozen resource envelope. One draw cannot discriminate timing variance: no throughput superiority claim is allowed, and the 120 s / 1 GiB values are report-only. This is not target-channel FER, efficiency, key-rate, scaling, qualification or promotion evidence; a candidate remains pending main-thread acceptance.
Outputs persist no input vectors, decisions, metrics, decoded keys, raw arrays or artifacts: only parameters, environment, equality/exception parities, counts, error magnitudes, walls, RSS, accounting and gates.
