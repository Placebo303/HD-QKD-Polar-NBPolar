# AUTHORIZATION — r2-fer-shg-64

**Status: TEMPLATE. NOT YET GRANTED.** Unlike a packet that already has PI
sign-off on file, this is a copy-paste template for the PI to read, edit if
needed, and paste back verbatim in chat. Per AGENTS.md §10.1, links alone
are insufficient — the full text below must be pasted by the PI (or by the
main thread quoting the PI) for authorization to take effect.

**Before this can be pasted "as is," two gaps must close first** (see
`TASK_PACKET.md` §4a/§5, `STATUS.yaml` `open_questions_for_main_thread`):

1. `run.py`'s `R2_TAG_MASTER`/`R2_EVAL_SEED` placeholders must be filled
   (candidate values found in `T6_PACKET_SKELETON_20260928.md` §2:
   `eval_seed=2026092801` / `tag_master=2026102801` — main thread verifies
   and transcribes).
2. The budget line in §3 below is a *suggested, non-binding* value
   (`PENDING-BUDGET`, SCL wall) — the PI must either accept it explicitly as
   part of this authorization or supply a different number. It is NOT yet a
   `DECIDED` D-ACQ-06 amendment.
3. Independent Pre-EXECUTE review of this packet must PASS before the
   command in `prereg.md` C is actually run, even after authorization.

---

## Scope of what this authorization would cover

**A. Measurement**: one Tier-Y, one-shot, claim-bearing FER measurement of
the M2-prior + SCL(L=16, top_m=4, CRC-16) candidate configuration on the
frozen 64-block pool defined in `docs/nbpolar/DATA_LEDGER.md` §7 /
`T6_PACKET_SKELETON_20260928.md` §3:

- **SHG `_1`** (`20260113_SHG_Type2PPLN_3s`) — 32 blocks: 8
  `A1_CAL_characterization` (frames 0–1023), 10 `HELDOUT_model_selection`
  (frames 1056–2335, 62-frame remainder 2336–2397 unused), 14
  `EVAL_already_decoded` (frames 2398–4189).
- **SHG `_2`** (`20260113_SHG_Type2PPLN_3s_2`) — the identical 32-block
  layout.
- **Total: 64 blocks.** CAL32 (frames 1024–1055, 32 frames/session) stays
  excluded throughout, in both sessions, never entering the pool.
- No frame or block outside this frozen 64-block list is drawn for any
  purpose other than reproducing the CAL32 fit itself.

**B. Frozen execution configuration**:

| Field | Value |
|---|---|
| Decoder | M2 prior + SCL(L=16, top_m=4, CRC-16-aided joint two-layer) |
| K1 / K2 | 319 / 6492 |
| P16 construction digest | `055c906472dd2a09761761b18aceb5f31d8b5db19bac658721f8dc49c3faea1b` |
| Pairing window / readout window / mode | W_P=200 / W_S=500 / CIRCULAR |
| Skip | 702 frames |
| tag_master (shared, both sessions) | `2026102801` *(verify against `T6_PACKET_SKELETON_20260928.md` §2 before this line is treated as final)* |
| eval_seed (shared, both sessions) | `2026092801` *(same verification note)* |
| CRC | CRC-16, counted once in disclosure (`kdb_with_crc = kdb_no_crc + 16 = 34135`) |
| H(X\|Y) | per-session empirical fit from that session's own CAL32 triple; G2=0.8168138, G3=0.8214782076249098 (both re-derived live by `run.py`, not hand-filled) |

**C. Budget — PENDING, requires explicit PI sign-off as part of this
authorization** (suggested values, NOT a `DECIDED` D-ACQ-06 amendment):

- Per-block wall ≤ 1200 s
- Per-block RSS ≤ 2 GiB
- Total wall ≤ 3 h (10800 s)
- Parallelism: 8-way
- Stop-on-overbudget: STOP, no tuning, no retry to "beat" the clock

(For contrast: the currently-`DECIDED` D-ACQ-06 is 40 s/block, single-process
exclusive, 5400 s total — based on **SC** timing, not SCL. Running under
those literal numbers would abort nearly every block, since a single
SCL(L=16) block alone measures ~600 s. This authorization, if given, either
adopts the suggested numbers above as a working budget for this one
execution, or the PI should state different numbers.)

**D. Judgment rule (frozen, for reference — the script itself computes no
verdict)**:

1. Decode all 64 blocks; classify each into the five-way taxonomy (`exact`
   / `verify_failed` / `decode_failed` / `undetected` / `resource_abort`).
2. Effective denominator `D = #exact + #verify_failed + #decode_failed`
   (excludes `undetected` and `resource_abort`).
3. If `D < 56` ⇒ `INSUFFICIENT` ⇒ `INCONCLUSIVE` (no pad/reuse/shrink N).
4. Point estimate `p̂ = (#verify_failed + #decode_failed) / D`; Wilson 95%
   CI (z=1.96).
5. **P-1 (pooled-denominator reading)**: the `n=56` threshold check uses the
   **pooled**, cross-stratum denominator (`64 ≥ 56`); no single stratum
   alone reaches 56 (largest is EVAL at 28). The pooled table and the
   per-stratum (`A1_CAL_characterization` / `HELDOUT_model_selection` /
   `EVAL_already_decoded`) table must always be reported **together, in the
   same place** — never a pooled number alone.
6. `undetected` check (D-FER-06 O-6a): if `undetected ≥ 1` — isolate the
   block id(s), loud STOP statement, **defer** the `FER_MEASURED_AT_CONTRACT`
   verdict, escalate to PI. **P-2**: this STOP still counts as the one-shot
   Tier-Y attempt — it is not discarded and rerun to chase a clean result.
   Whether a deferred verdict can later be promoted from this same result,
   or requires a new measurement, is a separate PI decision.
7. If `undetected = 0` and `D ≥ 56`: `FER_MEASURED_AT_CONTRACT` MAY be
   judged for this configuration and pool — scope-limited to "the two
   2026-01-13 SHG acquisitions' own conditions" (D-ACQ-05). This judgment is
   a main-thread act after Pre-RESULT review, not something `run.py` itself
   outputs.

**E. Output directory**: `workspace/r2_fer_shg_64/` only —
`results.json` + 64 `part_<SESSION>_<global_block_index:02d>.json` files +
`EXECUTION_TRANSCRIPT.md` (written after). No write anywhere else
(`results/`, `comparison_bench/outputs_comparison/`, any existing
`workspace/m2_prior_validation/*`, any `.workbuddy/queue/` packet dir, or
the predecessor `workspace/m2_scl_check_g2g3_success/`, are all off
limits).

**F. One-shot / no-rerun**: `reruns=0`. `results.json` and all 64
`part_*.json` must be absent before launch (enforced in code). A rerun is
permitted ONLY to fix a pre-measurement implementation defect — never a
parameter, seed, threshold, or budget-number change under any outcome —
and must be recorded as a separate, explicit attempt, never a silent
overwrite. A STOP triggered by `undetected≥1` (D above) still consumes this
one-shot attempt (P-2); it is not grounds for a "clean" rerun.

---

## Copy-paste authorization text (PI fills in / confirms, then pastes)

> 授权执行 r2-fer-shg-64：在 SHG `_1`/`_2` 全会话共 64 块（`DATA_LEDGER.md` §7
> / `T6_PACKET_SKELETON_20260928.md` §3 冻结清单）上，用 M2 先验 + SCL(L=16,
> top_m=4, CRC-16) 做一次性 FER 测量。tag_master/eval_seed 采用
> `T6_PACKET_SKELETON_20260928.md` §2 的冻结值（`tag_master=2026102801` /
> `eval_seed=2026092801`），已核对 `docs/decision-log.md` 2026-09-28 条目。
> 预算：每块 wall ≤ 1200 s、RSS ≤ 2 GiB、总 wall ≤ 3 h、8 路并行、超预算即
> STOP 不调参（**在此确认将此预算数值作为本次执行的正式依据**，或改为：
> ___________）。判定规则、P-1（跨层汇总+分层并列）、P-2（STOP 计入
> one-shot）均按 `T6_PACKET_SKELETON_20260928.md` §5 执行。输出仅限
> `workspace/r2_fer_shg_64/`。one-shot，reruns=0（仅实现缺陷可重启，绝不因
> 结果不干净而重跑）。本授权**不**替代独立 Pre-EXECUTE 复核，也**不**替代
> `FER_MEASURED_AT_CONTRACT` 的最终裁定——两者仍在执行后/发布前分别把关。

*(English gloss, for reference only — the Chinese text above is the
operative copy-paste block): "Authorize executing r2-fer-shg-64: a one-shot
FER measurement of M2-prior + SCL(L=16, top_m=4, CRC-16) on the frozen
64-block SHG `_1`/`_2` pool. tag_master/eval_seed use the T6 skeleton's
frozen values (verified against the 2026-09-28 decision-log entry). Budget:
confirmed as 1200s/block wall, 2GiB/block RSS, 3h total wall, 8-way
parallel, STOP-on-overbudget-no-tuning (or state a different number).
Judgment rule, P-1, P-2 per the T6 skeleton §5. Output confined to
`workspace/r2_fer_shg_64/`. One-shot, reruns=0. This authorization does not
substitute for independent Pre-EXECUTE review or for the
`FER_MEASURED_AT_CONTRACT` verdict itself."*

---

## Explicitly NOT authorized by this template, even once pasted

- Skipping independent Pre-EXECUTE review before execution.
- Skipping independent Pre-RESULT review before `results.json` is cited in
  any adjudication document, decision-log entry, or commit.
- Any change to `NBPOLAR_M2_PRIOR_G2_SUCCESS` / `NBPOLAR_M2_PRIOR_G3_SUCCESS`
  / the M2 status ladder / any prior Wilson-gate verdict.
- Drawing any frame/block outside the frozen 64-block pool.
- Modifying any frozen decoder/prior/protocol file, or writing under
  `results/`, `comparison_bench/outputs_comparison/`, any pre-existing
  `workspace/m2_prior_validation/*` directory, any G2/G3 `.workbuddy/queue/`
  packet dir, or the predecessor's `workspace/m2_scl_check_g2g3_success/`.
- git commit/push.
- A rerun after a STOP or an unwelcome result, or any parameter/seed/
  budget-number change under any outcome.
- A `FER_MEASURED_AT_CONTRACT` verdict itself — that is a main-thread
  adjudication after Pre-RESULT review, not something this authorization
  grants directly.

`STATUS.yaml`: `authorizations: []` until this text (or the PI's edited
version of it) is actually pasted in chat and recorded there;
`execution_authorized: false` until independent Pre-EXECUTE review also
PASSes.
