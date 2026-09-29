# TASK PACKET — r2d-locate-f-k-g2 (Tier X descriptive locating probe, non-claim)

Purpose: locate f and k1/k2 split for the native SCL on real G2 data; choose the config for the later Tier-Y measurement on G3+G2 strata. Base: r2b run.py (unchanged, read-only).
This packet authorizes nothing (STATUS authorizations: []). Text: AUTHORIZATION_PROMPT.md.

## 0. Allowed / forbidden
- Write (must not pre-exist): this dir's results.json, part_<cfg>_G2_<idx:02d>.json (192), logs.
- Forbidden: G3 data read/decode; SC path; changing frozen modules; writing outside this dir; git writes; running without authorization; reruns except one restart after an implementation defect.

## 1. Config table (G2 H_total=0.8168138204, f_book = kdb/(H*32768), CRC-16 extra)
| cfg | f | share | K_total | k1 | k2 | f_book no CRC | f_book with CRC |
|---|---|---|---|---|---|---|---|
| f1.22_s0469 | 1.22 | 0.0469 | 6549 | 307 | 6242 | 1.225801 | 1.226399 |
| f1.22_s0380 | 1.22 | 0.0380 | 6549 | 249 | 6300 | 1.225801 | 1.226399 |
| f1.24_s0469 | 1.24 | 0.0469 | 6657 | 312 | 6345 | 1.245976 | 1.246574 |
| f1.24_s0380 | 1.24 | 0.0380 | 6657 | 253 | 6404 | 1.245976 | 1.246574 |
| f1.26_s0469 | 1.26 | 0.0469 | 6764 | 317 | 6447 | 1.265965 | 1.266563 |
| f1.26_s0380 | 1.26 | 0.0380 | 6764 | 257 | 6507 | 1.265965 | 1.266563 |
(f_book exceeds f_target by ~0.006 because G2's own H is below the H-bar used for K, and tag bits.)
Task order: config-major (rows above), blocks 0..31 within config; 192 tasks, one forked process each, 4 concurrent.

## 2. Acceptance items
- A1 G3 never read (only G2 context built). A2 seeds 2026092903/2026102903. A3 SCL call identical to R2B `_scl_call` with per-config k1/k2 (k1_scl/k2_scl recorded). A4 4 workers, native threads 2 (runtime override `_default_threads`). A5 budgets 300 s/task, 12600 s total (raised from 7200 by main thread 2026-09-29: WSL nproc=8) (not_started, strict >), 4 GiB (advisory + post-check), hard terminate at 420 s. A6 startup guard: results.json/part_* present -> exit 2. A7 taxonomy only from status=="ok"; undetected isolated, STOP_undetected per config. A8 results.json: config_table, per-config taxonomy + Wilson(fail) + L1/L2 attribution, per-block records, cross table vs R2 (f~1.27, L16) and R2B (f=1.20, L32) same-block outcomes (read-only), selection_rule_evaluation.
## 3. Return conditions
All frozen items done, or a concrete blocker (command, error, remedies, single decision needed).
