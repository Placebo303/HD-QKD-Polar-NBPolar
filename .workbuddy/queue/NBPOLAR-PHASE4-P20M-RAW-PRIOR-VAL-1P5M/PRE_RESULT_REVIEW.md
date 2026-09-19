# P20M Pre-RESULT review (independent; before acceptance/publication)

- Reviewer: `reviewer-go` (independent subagent), session `ses_f4867e19dffeqmQF1neRfPzhV0`, 2026-09-19.
- Scope (`AGENTS.md` §10.3 + packet §14 P20M-R7): re-check plan pins/thresholds,
  per-arm breakdown, `undetected` isolation, accounting/decomposition, disclosure
  recount, non-access, anti-drift, and operator-return claims against the ACTUAL
  artifacts before any publication/commit.
- Verdict: **PASS (PR1–PR8 all PASS)**. The Stage-B result may be published and
  accepted by the main thread as **descriptive evidence only** under label
  `TARGET_EMPIRICAL_N32768_VAL_RAW_PRIOR_1P5M_COMPLETE`. No blocking issue; no
  rework required by this gate. (The reviewer marks nothing accepted.)

## Verdicts (abridged evidence)

| ID | Verdict | Key evidence |
|---|---|---|
| PR1 inventory+freeze identity | PASS | Exactly 5 files in `raw_prior_val_1p5m/`; prior canonical digest `372dcc1c…f7d46ac`, order sha `a9f18a9f…1da11bc638` match; `frozen_plan.json` K_total 7020 / K1 331 / K2 6689, DEV 1660..2043, blocks 1660..1787/1788..1915/1916..2043, remainder 2044..2212, build 0..1659, tag master 2026092280, caps 34119/35164/33509 + 327743; input stats (dev/prior/lambda) before==after. |
| PR2 per-record recount | PASS | 9 records, keys unique+exhaustive; outcomes: G0 0/3 (L1/24, L1/5, L1/17), G1 0/3 (L2/26 `l1_exact` TRUE, L1/848, L2/31 `l1_exact` TRUE), G2 0/3 (L2/26, L2/3646, L2/31, `oracle_l2_exact` false); nonfinite/decode_failed/resource_abort/undetected all 0; floor fields present on all 9; operating points per arm correct (G0 λ 319/6492 order `e3aea072…`; G1 raw 331/6689 `a9f18a9f…`; G2 raw 0/6689). |
| PR3 accounting identities | PASS | Key `308376` = 3·34119+3·35164+3·33509 exact; public `2949687` = 9·327743 exact; tags 9/9; SC 15/15; `stage_b_sampling_calls` 0; recount mismatch 0. |
| PR4 integrity gates | PASS | 25 gates, `integrity_all_pass: true`, `failing_integrity_gates: []`; spot-verified from raw records: `corrected_prior_identity` (digest + λ-0.0 + floor + H≤1e-12 + `p_b` maxdev 0.0), `order_derivation_identity` (seeds + 16 blocks + file-bytes equality), `budget_literal_recomputed` (K 7020 same-run H), `floor_hit_rate_reported`, `dev_block_range_identity` (S2-ii `build [0,1659]` vs `dev [1660,2043]` disjoint true), `truth_isolation`, `oracle_isolation` (G2 excluded, `deployable: false`), `undetected_zero`, `nonfinite_zero`, `no_unregistered_access`, `input_stat_unchanged`, `resource_limits_met_and_no_abort` (wall 104.85 s < 600 s; RSS 556785664 B < 2 GiB). |
| PR5 read accounting + non-access | PASS | counts 0/0; DEV 1/1; HOLD 0/1; attempts 1/1 (`retries` 0, `reopen_attempted` false); opened==registered (3 paths: raw prior + P20H calibrated + 1.5M DEV parquet); `refused_1m_path`/`refused_2m_path` pinned; V25 counts NPZ never content-opened; 1M refused; 2M never opened/statted/listed. |
| PR6 last-ulp H display | PASS (benign) | Independent recompute from `raw_prior_1p5m.npz`: h1 Δ0.0, h2 Δ2.22e-16, total `0.8255660516732961` vs frozen `…2963` (Δ1 ulp, within 1e-12); `budget_k_total` = 7020 for frozen/in-run/recomputed H identically; cannot change K/thresholds/outcomes; operator reported it as non-blocking accurately. |
| PR7 anti-drift / no-tuning | PASS | Artifact mtimes predate the run (10:26–10:28 vs run 10:52–10:53); no post-run pin edits (digests still match); single execution (retries 0, reopen false, one ~105 s window); no K/seed/order change; no commit (P20M dir fully untracked); writes confined to packet dir + frozen out-dir; label/`claim_scope` descriptive-only (no FER/qualification/promotion; `undetected` never success; oracle excluded from operational aggregates). |
| PR8 operator-return check | PASS | `FROZEN_COMMAND` == freeze §5 == `OPERATOR_RETURN.md` §3 (all 9 pins byte-present); recorded start ~02:52:03Z / end 02:53:48Z / exit 0 / wall 104.848503 s / RSS 556785664 B match `aggregate_summary.json`; five-file inventory matches; label + §0 honest-scope statement verbatim. |

## Caveats (non-blocking)

- `STATUS.yaml` bookkeeping lag at review time (`stage_b_authorized`/`protected_data_read_authorized`/
  `decoder_execution_authorized` still `false`; `pre_execute_review: PENDING_INDEPENDENT_ADJUDICATION`)
  despite the executed authorized attempt — reconciled by the main thread in
  `MAIN_THREAD_ACCEPTANCE.md` / `STATUS.yaml`.
- Worktree dirt outside the P20M manifest is pre-existing and was NOT adjudicated
  by this scoped review.
- "FER/qualification/promotion/recovery/superiority/efficiency" keyword hits live
  exclusively in the negating `claim_scope`/disclaimer sentences (benign, required).
- Budget-literal display last-ulp split (`…2963` frozen vs `…2961` in-run) is benign
  per PR6.

Publication statement: **all PR1–PR8 PASS** — the result may be published/accepted
by the main thread as descriptive only. This review marks nothing accepted and
performs no commit/push.
