# P20O Pre-EXECUTE review (independent; Stage A -> Stage B gate)

- Reviewer: `reviewer-go` (independent subagent), session `ses_f46e4e9ddffeqvIlFewSzcTLVv`, 2026-09-19.
- Scope (packet §14 + `AGENTS.md` §10.3): §3 prior/alt derivation, §5 budget/K-literal,
  §4 gate family/population, §2 runner-delta design, §7 instrumentation (incl. the ninth
  U-domain scalar), branch/scope/authorization/target-output absence/focused tests, and
  the two disclosed Stage-A deviations.
- Verdict: **PASS (PX1–PX7; no blocking issues, no caveats)**. Stage B MAY be authorized
  once the filled STEP-2 text is pasted and target-output absence is re-confirmed.
  (The reviewer accepts nothing and authorizes nothing.)

Read-accounting constraint honored: the reviewer performed NO open/stat/listing of the
protected V25 counts NPZ, the 2M pairs parquet, or any 1M/1.5M/2M content; independent
recomputation used only the Stage-A worktree artifacts.

## Verdicts (abridged evidence)

| ID | Verdict | Key evidence |
|---|---|---|
| PX1 command/pins/deviations | PASS | `FROZEN_COMMAND` == freeze §8 == filled STEP-2 (5 placeholders, 0 remaining; 1435 chars); pins: prior canonical digest `b16f5216…ae1c587` (canonical recipe; npz file-bytes `5fb531b3…` correctly distinct), alt file sha `98e25495…ae5fb5`, order file sha `b2255449…0906`, K `334/6746/7080`, H literals, budget literal 7080, VAL DEV `2187 2826` + remainder `2827 2915`, master 2026092310, caps 35464/35464/33794/33794, public 327743, totals 692580/6554860. Deviation 1 (canonical absolute counts path): substantively preserved — `_check_counts_path` accepts only a path resolving to `holdout_microcheck.FROZEN_COUNTS_PATH`; single 2M-array open, array sha `e391a346…092351e4`, total 559872. Deviation 2 (early `ls -la` of the 2M pairs dir): metadata only; runner derive opens only the counts file; size/sha pins are build-manifest constants never recomputed from content — no effect. |
| PX2 prior derivation | PASS | Independent recompute from `raw_prior_2m.npz` `counts_ab`: `f_raw`/`p1`/`p2`/`p_b` max-abs-diff `0.0`; exact 10-key set; `lambda_star 0.0`; `floor_value 1e-15`; total 559872; floor hits 1045941/1048576; zero columns 0; H1 `0.02566204884275839` / H2 `0.8069006731309893` / H `0.8325627219737477` diff 0.0; canonical digest matches pin; `counts_ab` array sha matches `e391a346…`. |
| PX3 alt + D1/D2 | PASS | 9-key set, `alpha 1.0`, file sha `98e25495…`; `f_alt`/`p2_alt` diff 0.0; `p1`-equality 0.0; `ce_alt 0.8850983725781965` diff 0.0, `ce_incumbent 0.8069006731253678` diff 1.1e-16, `alt_ideal_length_bits 29002.90347264234` → D2 **FEASIBLE**, margin `4791.09652735766` (recomputed diff ~1.5e-12); frozen before any VAL contact (VAL-DEV 0, Stage-B root absent). |
| PX4 budget/split/orders/population | PASS | `budget_k_total(32768, H, 1.3) == 7080` replayed; split via accepted `select_empirical_split` (16 blocks, seeds 2026092321..2324, 32 genie calls, residual 3.603823440223586e-07); orders file digest + full L1/L2 permutations + provenance; population manifest-justified (2M TRAIN 2187/559872 + VAL 729/186624 + HOLD 729/186624; bases TRAIN 0..2186 / VAL 2187..2915 / DEV first-640 as 5×128 / remainder 2827..2915 = 89 frames; pair arithmetic checks); gate family (a)→(g) verified before any protected open/SC. |
| PX5 delta + instrumentation | PASS | d1–d8 only vs accepted importer; 4 hardcoded arms (A/B 334/6746, C/D 0/6746; Δ caps 0); `HAZARD_FIELDS` 9 = eight X09-R1 + ninth `l2_fail_in_prefix_u_domain` frozen **PRESENT** (U-domain via `polar_transform(low_hat)` vs `view['u2']`); null-unless-L2-fail, R=8, post-decode recording-only (sentinel-tested); no extra factors/sweeps/λ/CLI K overrides. |
| PX6 checklist | PASS | Branch `codex/nbpolar-phase0`; STEP-1 recorded, `stage_b_authorized: false`; Stage-B root ABSENT; focused suite `20 passed in 38.84s` (sibling venv); accepted-module hashes match the notes table; reads counts 1/1 + VAL-DEV 0/1 + VAL-remainder 0 + HOLD 0 + 1M/1.5M 0 + decoder 0 + attempts 0/1. |
| PX7 write scope | PASS | New module (`ee446380…`, 3476 lines), new test (`84f6e751…`, 1123 lines), packet dir (freeze, notes, STATUS, three artifacts), `workspace/p20o/8da2574c51b74d039606110bc55b0d72/` derive capture; no `results/`/`outputs_comparison/` writes; no commit; pre-existing dirt preserved. |

## Caveats

- None. (Last-bit notes: `ce_incumbent` 1.1e-16; D2 margin ~1.5e-12 — within frozen
  tolerance.)

No files were edited by this review; no commit/push; not a self-acceptance.
