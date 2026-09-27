# op-n32k-ratio — execution transcript (Tier X, non-claim)

Probe root: `workspace/probes/op-n32k-ratio/`. Predecessor: `workspace/probes/op-peak-refine/` (runner + prereg).

## 1. Heartbeat check
- `Get-Date` = 2026-09-27T11:27:11+08:00; `workspace/overnight_state_20260927.md` last_heartbeat = 2026-09-27 05:05
  (> 6 min old; overnight window ended 08:00) -> proceed.

## 2. N=32768 support
- `run_two_layer_block` requires only `n` power of two and `k1,k2 <= n`; `seed_bits_for(n)=10n+63`. No library edit needed.
- Runner N-dependent pieces (x/delta draws, A2 pooled-Z vector, design MC) are N-generic; `Q=1024` symbol alphabet unchanged.

## 3. Timing smoke (NON-RESULT, sizing only)
- Script `workspace/probes/op-n32k-ratio/smoke/smoke.py`, seed 1, 1 design sample, 1 block at (k1,k2)=(715,7224) with d1/d2 from the 1-sample H;
  output `smoke/smoke_timing.json`.
- design sample 14.15 s; block 21.91 s; peak RSS 430,637,056 B (~0.40 GiB); total 36.1 s. Block outcome not a result.
- Sizing: 128 blocks x ~21.9 s ~= 2805 s. DESIGN_MC=128 (~1810 s) -> ~4630 s (86% of 5400 s), judged too tight;
  chose DESIGN_MC=64 (~905 s) -> ~3720 s expected. B = 8 blocks/seed x 2 seeds = 16 per point (target met).

## 4. Grid (frozen before prereg)
H = 0.9318300074841255 bits/symbol, H*N = 30534.2056852398; T = round(f*H*N/5); k1 = round(share*T); k2 = T - k1.

| label | total | f_book | k1 | k2 | k1 share |
|---|---|---|---|---|---|
| T7939_k1_372_k2_7567 | 7939 | 1.3000174430 | 372 | 7567 | 0.0469 |
| T7939_k1_715_k2_7224 | 7939 | 1.3000174430 | 715 | 7224 | 0.0901 |
| T7939_k1_1111_k2_6828 | 7939 | 1.3000174430 | 1111 | 6828 | 0.1399 |
| T7939_k1_1588_k2_6351 | 7939 | 1.3000174430 | 1588 | 6351 | 0.2000 |
| T9771_k1_458_k2_9313 | 9771 | 1.6000088721 | 458 | 9313 | 0.0469 |
| T9771_k1_879_k2_8892 | 9771 | 1.6000088721 | 879 | 8892 | 0.0900 |
| T9771_k1_1368_k2_8403 | 9771 | 1.6000088721 | 1368 | 8403 | 0.1400 |
| T9771_k1_1954_k2_7817 | 9771 | 1.6000088721 | 1954 | 7817 | 0.2000 |

## 5. Pre-launch checks (2026-09-27 ~11:33)
Script (scratchpad, test-only): `prelaunch_check.py`; fake block runner, DESIGN_MC=1, BLOCKS=2, no file writes.
- (a) AST `%`-format check: 7 format expressions, 0 placeholder/argument mismatches; 0 non-formatted strings containing `%%`.
- (b) Aggregation keys: 8 unique labels and 8 unique (total,k1,k2) keys; `points[].per_seed` filtered by `f_label` (not k1);
  fake dry run -> 16/16 cells, each point 2 per-seed rows all matching its own label; per-point totals follow the fake k1-parity pattern exactly; JSON serializable.
- (c) Descriptive strings: grep for stale `K1_GRID|K1_POINTS|TOTAL_K|K2_SINGLE|560|2800|peak|C1|600|1GiB` -> only the derivation comment and `peak_rss_bytes`; budget reason strings `wall_s>5400`/`rss>4GiB`; in-run asserts re-derive T, k1, disclosed and f_book from the rule.
- `results.json` ABSENT at 11:34:15 (+0800).

## 6. Launch
- Launched 2026-09-27T11:34:42+08:00 (background shell task br0exekfj), prereg C command verbatim, stdout -> `workspace/probes/op-n32k-ratio/run_stdout.log`.
- Completion: process exit 0 at ~2026-09-27T12:35+08:00; stdout `WROTE .../results.json`, `STATUS ok WITHIN True CELLS {expected: 16, completed: 16} WALL 3649.563`. reruns=0; no execution_error record.

## 7. Result record (descriptive, Tier X, non-claim)
`workspace/probes/op-n32k-ratio/results.json`: status ok, within_budget true, stop_rules [], wall 3649.6 s
(design 901.6 s for 64 samples; blocks 20.4-22.3 s, mean 21.0 s), peak RSS 1,210,146,816 B (~1.13 GiB).

| total | f_book | k1 | k2 | k1 share | op exact/16 | oracle exact/16 | op verify_failed | undetected | decode_failed | resource_abort |
|---|---|---|---|---|---|---|---|---|---|---|
| 7939 | 1.300017 | 372 | 7567 | 0.0469 | 0 | 0 | 16 | 0 | 0 | 0 |
| 7939 | 1.300017 | 715 | 7224 | 0.0901 | 0 | 0 | 16 | 0 | 0 | 0 |
| 7939 | 1.300017 | 1111 | 6828 | 0.1399 | 0 | 0 | 16 | 0 | 0 | 0 |
| 7939 | 1.300017 | 1588 | 6351 | 0.2000 | 0 | 0 | 16 | 0 | 0 | 0 |
| 9771 | 1.600009 | 458 | 9313 | 0.0469 | 0 | 0 | 16 | 0 | 0 | 0 |
| 9771 | 1.600009 | 879 | 8892 | 0.0900 | 0 | 0 | 16 | 0 | 0 | 0 |
| 9771 | 1.600009 | 1368 | 8403 | 0.1400 | 0 | 0 | 16 | 0 | 0 | 0 |
| 9771 | 1.600009 | 1954 | 7817 | 0.2000 | 0 | 0 | 16 | 0 | 0 | 0 |

Oracle arm: 128/128 verify_failed. Candidate divergence defined 128, true 82 (report-only). kdb observed {39759, 48919}.
Descriptive design note (read from existing results files, no extra run): genie-design mean per-coordinate entropies
H1=0.1306, H2=1.4001 bits (sum 1.5307) at N=32768 vs N=1024 (op-peak-refine) H1=0.1273, H2=1.2691 (sum 1.3963);
channel H = 0.9318 bits/symbol. (H1+H2)/H = 1.643 at N=32768, i.e. both frozen totals lie below the two-layer design-entropy
disclosure floor in f_book units; minimal k2 by design entropy ~ H2*N/5 = 9176 coordinates.
