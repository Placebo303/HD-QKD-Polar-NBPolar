# P3 Stage B Freeze — seed / mask / commands / targets (NOT EXECUTED, attempt 0)

- Scope: P3 Stage B only. No P5. No construction / K / disclosure / rate changes (inherited, untouched here).
- Nothing was executed for this freeze: no decoder / read / DEV / EVAL / benchmark run; no artifact (parquet / TTBin / held-out) read; no sibling / results / outputs write; no commit / push.

## 1. Frozen seed / mask (new)

- `MASTER_SEED = 20260911`, `MASK = 0x5BD1E995` (new for Stage B; prior seeds untouched).
- Per-case: `subseed = MASTER_SEED + case_index`, same MASK for all cases.

| case | id | subseed | mask |
|------|----|---------|------|
| 01 | oracle-n2-n4 | 20260912 | 0x5BD1E995 |
| 02 | multishape-n16-n64 | 20260913 | 0x5BD1E995 |
| 03 | bounded-n256 | 20260914 | 0x5BD1E995 |
| 04 | profile-n64-n256-n1024 | 20260915 | 0x5BD1E995 |
| 05 | attribution | 20260916 | 0x5BD1E995 |

## 2. Frozen matrix (case -> coverage)

- 01: N=2/4 oracle, >=64 blocks each; disclosure shapes axis, shape set inherited (not changed here).
- 02: N=16/64, multi-shape (same inherited shape set).
- 03: N=256, 20-64 blocks, bounded.
- 04: profile (画像) N=64/256/1024, timing/RSS only.
- 05: attribution matrix over cases 01-04 (counts/FER-leakage attribution, no new decoding).

## 3. Frozen budget

- Total wall budget 3600s; per-case soft timeout 120s (`timeout 120`); RSS < 2GiB (`ulimit -v 2097152`).
- Over-budget case stops (soft); no retry / no tuning in Stage B.

## 4. Frozen targets (exactly 5 compact files, all verified ABSENT at freeze)

1. `workspace/p3-stageb/stageb_case01_oracle_n2_n4.compact.json` — ABSENT
2. `workspace/p3-stageb/stageb_case02_multishape_n16_n64.compact.json` — ABSENT
3. `workspace/p3-stageb/stageb_case03_bounded_n256.compact.json` — ABSENT
4. `workspace/p3-stageb/stageb_case04_profile_n64_n256_n1024.compact.json` — ABSENT
5. `workspace/p3-stageb/stageb_case05_attribution.compact.json` — ABSENT
- Attempt counter `workspace/p3-stageb/ATTEMPT_COUNTER.txt` — ABSENT => attempt 0.
- Execution may write ONLY these 5 files; any other write is out of scope.

## 5. Frozen commands (copyable, NOT executed)

- `RUNNER` = the already-frozen P3 Stage B runner from the existing packet (unchanged here; no new entrypoint introduced, no flags invented beyond seed/mask/case/out).
- Each line: soft-timeout + memory cap + fixed seed/mask/case/out. One command writes exactly one target.

```bash
ulimit -v 2097152; timeout 120 $RUNNER --case 01-oracle-n2-n4 --seed 20260912 --mask 0x5BD1E995 --out workspace/p3-stageb/stageb_case01_oracle_n2_n4.compact.json
ulimit -v 2097152; timeout 120 $RUNNER --case 02-multishape-n16-n64 --seed 20260913 --mask 0x5BD1E995 --out workspace/p3-stageb/stageb_case02_multishape_n16_n64.compact.json
ulimit -v 2097152; timeout 120 $RUNNER --case 03-bounded-n256 --seed 20260914 --mask 0x5BD1E995 --out workspace/p3-stageb/stageb_case03_bounded_n256.compact.json
ulimit -v 2097152; timeout 120 $RUNNER --case 04-profile-n64-n256-n1024 --seed 20260915 --mask 0x5BD1E995 --out workspace/p3-stageb/stageb_case04_profile_n64_n256_n1024.compact.json
ulimit -v 2097152; timeout 120 $RUNNER --case 05-attribution --seed 20260916 --mask 0x5BD1E995 --out workspace/p3-stageb/stageb_case05_attribution.compact.json
```

## 6. Freeze status

- Targets: 5/5 confirmed absent (see §4). Attempt: 0 (no counter, no run). Status: FROZEN, awaiting explicit execution authorization; this doc authorizes nothing.
