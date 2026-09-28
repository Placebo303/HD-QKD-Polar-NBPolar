# T6 — Tier-Y Packet Skeleton (`authorizations: []`) — 2026-09-28

Status: **non-executable skeleton.** `authorizations: []` (empty, by
construction). No `AUTHORIZATION_PROMPT.md` accompanies this file — per
`tasks.md` T6's "deferred by construction" clause and the proposal's Scope
OUT, that artifact is generated only later, under an explicit user
instruction, and is not generated here. **T7 (acquisition), T8
(decode/measurement execution), and T9 (Pre-RESULT/publication) remain NOT
AUTHORIZED.** Nothing in this file grants, implies, or schedules execution.

This skeleton exists so that every frozen field an eventual Tier-Y execution
packet would need is already written down from the `§5` ledger (all 15 rows
`DECIDED`, see `docs/nbpolar/R2_MEASUREMENT_CONTRACT_DRAFT_20260924.md` §5/§9)
and the T5 quota arithmetic (`tasks.md` T5 section). One field — the SCL wall
budget — could **not** be frozen from existing PI rulings and is recorded
below as `PENDING-BUDGET` with a suggested (non-binding) value.

---

## 1. Execution configuration (frozen)

| Field | Value | Source |
|---|---|---|
| Method | M2 prior + SCL(L=16, top_m=4, CRC-16) | `docs/nbpolar/DATA_LEDGER.md` §7; `nbpolar-scl-lock-amendment` T1 |
| K1 | 319 | G2/G3 frozen contract, inherited unchanged (D-ACQ-07 O-7b) |
| K2 | 6492 | G2/G3 frozen contract, inherited unchanged (D-ACQ-07 O-7b) |
| P16 construction | inherited from G2/G3, digest `055c906472dd2a09761761b18aceb5f31d8b5db19bac658721f8dc49c3faea1b` | `docs/decision-log.md:177,201` |
| P16 construction (Tier-X SCL gate config identity, separate citation — not asserted identical to the above digest, recorded for cross-reference only) | `b4defb1e` (Tier-X focused review PASS) | `docs/nbpolar/DATA_LEDGER.md:140` |
| Pairing window | W_P=200 | G2/G3 frozen contract, inherited unchanged |
| Readout window | W_S=500 | G2/G3 frozen contract, inherited unchanged |
| Pairing mode | CIRCULAR | G2/G3 frozen contract, inherited unchanged |
| Skip | 702 frames | G2/G3 frozen contract, inherited unchanged |
| CRC | CRC-16, counted once in disclosure (`kdb_with_crc`) | D-FER-05 O-5a |
| H(X\|Y) substitution | per-session empirical fit from own CAL32 triple, no shared constant | D-FER-04 O-4a |
| H_total (SHG `_1` / G2) | 0.8168138 | `docs/decision-log.md`, 2026-09-22 G1R2 entry |
| H_total (SHG `_2` / G3) | 0.8214782076249098 | `docs/decision-log.md`, 2026-09-28 "真实数据 G2/G3 B 臂失败块 SCL 重解" entry |
| f_FER accounting | `f_FER = f_book_with_crc = kdb_with_crc / (H_total_bits × 32768)`; `kdb_no_crc = disclosed_bits_per_coordinate×(K1+K2) + tag_bits`; `kdb_with_crc = kdb_no_crc + 16` | D-FER-05 O-5a |
| Type0 inclusion | not included | D-ACQ-04 O-4a |
| Branch | A (50–100 blocks) | D-ACQ-01 O-1a |
| Sessions | SHG `_1` (`20260113_SHG_Type2PPLN_3s`) + SHG `_2` (`20260113_SHG_Type2PPLN_3s_2`); satisfies the ≥2-session roadmap gate | D-ACQ-08 O-8a |

## 2. New tag_master / eval_seed (frozen)

- **`eval_seed = 2026092801`**
- **`tag_master = 2026102801`** (derived as `eval_seed + 10000`, the
  established convention verified by G3: `EVAL_SEED 2026100101` →
  `tag_master 2026110101`, `docs/decision-log.md:177`)
- **Single, shared across both sessions** — unlike G2 (`tag_master 2026103001`,
  inherited) and G3 (`tag_master 2026110101`, G3-fresh), which each used their
  own master. R2's D-ACQ-07 (O-7b) explicitly requires one new master shared
  by both sessions, distinct from either prior value.
- **Generation basis**: `2026092801` encodes the freeze/decision date
  (2026-09-28) as `YYYYMMDD` + session index `01`. Checked for collision
  against all previously used tag_master/eval_seed values in this repo
  (`2026103001`, `2026110101`, `2026100101`) — no collision.
- **Reproducibility statement (verbatim requirement for any eventual R2
  report)**: G2/G3's own frozen SC results (their 42 tags each,
  `per_block_outcomes.jsonl`) and the 2026-09-28 SCL descriptive merge
  (27/28) are produced under their own tag_masters and are **unaffected** by
  this new master. Once R2 executes, all 64 blocks (including the 28 already
  SC-decoded EVAL blocks) will get **new tag byte values** under
  `tag_master=2026102801` — these are **not bit-identical** to the old
  artifacts (expected, not an inconsistency), though the taxonomy
  classification (`exact`/`verify_failed` counts) is expected to agree
  (Toeplitz universal-hash misdetection probability is the same order of
  magnitude regardless of master).

## 3. 64-block list (frozen; 3 stratum intervals per session)

Both sessions share the identical frame-boundary structure (`g3_freeze_config.json`'s
`disjointness_matrix`/`eval_blocks`/`skip_frames`/`pairing_window_*` fields
are byte-identical to G2's, `docs/nbpolar/DATA_LEDGER.md` §2). Block size =
128 frames throughout; CAL32 (1024–1055) is excluded from all strata in both
sessions.

| Stratum | Frame interval (post-skip) | Block formula | Block count/session | Two-session total | Note |
|---|---|---|---|---|---|
| `A1_CAL_characterization` | 0–1023 | `[128i, 128i+127]` for i=0..7 | 8 | 16 | Used for M0 prior characterization; label as stratified |
| `HELDOUT_model_selection` | 1056–2335 (62 unused frames: 2336–2397) | `[1056+128i, 1056+128i+127]` for i=0..9 | 10 | 20 | Participated in NLL model selection; label as stratified |
| `EVAL_already_decoded` | 2398–4189 | `[2398+128i, 2398+128i+127]` for i=0..13 | 14 | 28 | Already SC-decoded (+2026-09-28 SCL descriptive); label as "already decoded" |
| **Total** | — | — | **32** | **64** | CAL32 (1024–1055, 32 frames/session) always excluded |

Source: `docs/nbpolar/DATA_LEDGER.md` §1/§2/§7.

## 4. Quota arithmetic (T5, frozen)

- `16 + 20 + 28 = 64` blocks (matches `DATA_LEDGER.md:50,70-71,75`).
- Against `D-FER-03`'s `n=56`: margin = `64 − 56 = 8` blocks (~12.5%).
- Threshold check uses the **pooled** (cross-stratum) denominator per P-1
  (`R2_MEASUREMENT_CONTRACT_DRAFT_20260924.md` §9.2): `64 ≥ 56` meets
  threshold. No single stratum alone reaches 56 (largest is EVAL at 28) —
  P-1 resolves this reading explicitly.

## 5. Judgment rule (frozen)

1. Execute (only after Pre-EXECUTE PASS and explicit user authorization —
   **not granted by this document**): decode all 64 blocks under the frozen
   candidate (§1 above), classify each into the five-way taxonomy (`exact` /
   `verify_failed` / `decode_failed` / `undetected` / `resource_abort`),
   record stratum membership per block.
2. Effective denominator `D = #exact + #verify_failed + #decode_failed`
   (excludes `undetected` and `resource_abort`).
3. COMPLETE-BLOCKS-ONLY check: if `D < 56` ⇒ `INSUFFICIENT` ⇒
   `INCONCLUSIVE`. Never pad/reuse/shrink N.
4. Point estimate `p̂ = (#verify_failed + #decode_failed) / D`.
5. Wilson 95% CI (z=1.96):
   `center = (p̂ + z²/2D) / (1 + z²/D)`;
   `half_width ≈ z·sqrt(p̂(1−p̂)/D + z²/4D²) / (1 + z²/D)`.
6. `undetected` check (D-FER-06 O-6a + P-2): if `undetected ≥ 1` — isolate the
   block id(s), loud STOP statement in the summary, **defer** the
   `FER_MEASURED_AT_CONTRACT` verdict, escalate to PI. This execution still
   counts as the one-shot Tier-Y attempt (P-2) — it is not discarded and
   rerun to obtain a clean result. If `undetected = 0` (matching the G2/G3
   42/42 precedent), continue to step 7.
7. Promotion: `D ≥ 56` and step 6 did not trigger STOP ⇒
   `FER_MEASURED_AT_CONTRACT` may be judged for this candidate configuration
   and 64-block pool, scope-limited per D-ACQ-05 ("applies only to the two
   2026-01-13 SHG acquisitions' own conditions").
8. Mandatory report contents (none may be omitted):
   - Per-stratum taxonomy counts + per-stratum Wilson CI (descriptive), for
     all three strata;
   - Pooled (cross-stratum) taxonomy counts + pooled Wilson CI (primary
     point estimate; the `n=56` threshold check uses this row) — **must
     appear in the same table as the per-stratum breakdown** (P-1);
   - "Selection degrees of freedom already exercised" table (R2(b)): which
     blocks (`A1_CAL`/`HELDOUT`) participated in which M0/M2 model-selection
     step;
   - `undetected` and `resource_abort` counts and per-block ids, even when
     zero (must be written explicitly, not left blank);
   - `f_FER` (D-FER-05 formula) and `H_total` (D-FER-04, listed per session);
     computed f vs stated f side by side;
   - Carried caveats (a)–(d) (C1, verbatim) + D-ACQ-05 scope statement.
9. The full flow remains subject to `AGENTS.md` §10.3 Pre-EXECUTE (before
   execution) and Pre-RESULT (before publication) review gates. This file
   does not change `authorizations: []`; T7/T8/T9 still require separate
   explicit user authorization.

## 6. Budget

| Field | Value | Status |
|---|---|---|
| `wall_per_block` (SC) | 40 s | `DECIDED` (D-ACQ-06, 2026-09-27) |
| `rss_per_block` | 2 GiB | `DECIDED` (D-ACQ-06, 2026-09-27) |
| `wall_total` (SC) | 5400 s | `DECIDED` (D-ACQ-06, 2026-09-27) |
| machine/parallelism (SC) | single-process exclusive on this machine | `DECIDED` (D-ACQ-06, 2026-09-27) |
| stop-on-overbudget | STOP, no tuning | `DECIDED` (D-ACQ-06, 2026-09-27) |
| **`wall_per_block` (SCL)** | **not frozen — PENDING-BUDGET** | see below |

**PENDING-BUDGET (SCL wall) — flagged, not adjudicated here.** D-ACQ-06's
frozen numbers above were derived from **SC** timing (G3 measured 19.38–20.13
s/block, RSS 1.13 GiB,
`.workbuddy/queue/NBPOLAR-M2-PRIOR-G3-CONFIRM/G3_ADJUDICATION.md:45`). R2's
candidate decode path is **SCL(L=16, top_m=4, CRC-16)**, whose measured
per-block cost (`workspace/scl-gate-t3-packet/`, `workspace/m2_scl_rescue_g2g3/`
timing data) is on the order of **~600 s/block** — roughly 15× the frozen
SC-derived `wall_per_block=40s`. This mismatch was not covered by any of the
8 rows the PI adjudicated on 2026-09-28 and is **not self-adjudicated by this
document**. Suggested (non-binding) values for a future PI supplemental
ruling on D-ACQ-06 for the SCL path:

- `wall_per_block ≤ 1200 s`
- `rss_per_block ≤ 2 GiB` (unchanged)
- `wall_total ≤ 3 h` (10800 s)
- `parallelism = 8-way`
- `stop_on_overbudget = STOP, no tuning` (unchanged)

These suggested values do **not** constitute a decision; T7/T8 remain
`NOT AUTHORIZED` until the PI adjudicates this gap (either accepting these
suggested values or supplying different ones).

## 7. `authorizations: []`

```yaml
authorizations: []
```

Empty by construction. No verbatim authorization text is included anywhere
in this file. T7 (acquisition), T8 (decode/measurement execution), and T9
(Pre-RESULT/publication of any number) remain **NOT AUTHORIZED** by this
document, unchanged from the rest of this openspec change (see `tasks.md`
Scope OUT / O-list O1–O4).

---

*Additive-only. This file does not modify `proposal.md`, `design.md`, or the
existing body of `tasks.md`/`R2_MEASUREMENT_CONTRACT_DRAFT_20260924.md` — it
is a new artifact referenced from both. No execution is authorized by this
document at any point.*
