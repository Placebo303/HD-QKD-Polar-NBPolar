# H2e geometry table (descriptive, scope-stratified; no cross-scope pooling)

Preregistered rule (frozen before computation; applied ONLY in the final adjudication file): C1 = in-scope IR-4 top-16 in-prefix fraction >= 0.50; C2 = IR-2 median over in-scope L2-fails >= 0.50; C1 AND C2 applied per scope separately.

Truncated scope (P20Q, inputs unchanged from v1): IR-4 pooled in-prefix 66/320 = 0.20625; IR-2 over L2-fails n=12 median=0.8830413818359375; IR-5 truncated=true 20/20 total_len=32768 20/20; IR-1 6746/26022/32768 on 20/20 rows.

Full-block scope (P20S, n=1 block caveat): IR-4 pooled in-prefix 0/48 = 0.0; IR-2 over full-block L2-fails n=1 median=0.432220458984375; IR-5 ir5full-v1 total_len=32768 3/3 uncapped per summary (series bytes never opened); IR-1 6746/26022/32768 3/3 rows, tail8 all 0.

Sharpest contrast: {"ir4_top16_in_prefix_full_block": "0/48 pooled (0 on A, B, O)", "ir2_mid_rank_full_block": [0.432220458984375], "note": "fail site is mid-rank while the entire top-16 sits outside-prefix at full-block scope"}

| scope | block | arm | ir4_in_prefix | ir1_tail8 | ir2_rank_pct |
| --- | --- | --- | --- | --- | --- |
| full-block | 0 | A | 0 | 0 | None |
| full-block | 0 | B | 0 | 0 | 0.432220458984375 |
| full-block | 0 | O | 0 | 0 | None |

IR-3 full-block rows (A/O vs B): [{"arm": "A", "arm_raw": "A_anchor_frozen_order", "thresh_lo_bits": 0.8740592319509212, "thresh_hi_bits": 1.7481184639018423, "above_lo_count": 1641, "above_lo_frac": 0.2432552623777053, "above_hi_count": 1641, "above_hi_frac": 0.2432552623777053}, {"arm": "B", "arm_raw": "B_spike_local_order", "thresh_lo_bits": 0.8768295338061611, "thresh_hi_bits": 1.7536590676123223, "above_lo_count": 1651, "above_lo_frac": 0.24473762229469315, "above_hi_count": 1651, "above_hi_frac": 0.24473762229469315}, {"arm": "O", "arm_raw": "O_true_l1_oracle", "thresh_lo_bits": 0.8740592319509212, "thresh_hi_bits": 1.7481184639018423, "above_lo_count": 1641, "above_lo_frac": 0.2432552623777053, "above_hi_count": 1641, "above_hi_frac": 0.2432552623777053}]
