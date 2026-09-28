# Design — nbpolar-data-use-rules-revision (proposal only — nothing authorized)

Status: **draft — PENDING PI adjudication.** Every decision below is a
planner proposal for the PI to accept, modify, or reject; none is frozen.

## D1 — Security accounting already isolates K/tag/CRC (verified)

`incremental.py:764` — `key_dependent_bits=DISCLOSED_BITS_PER_COORDINATE * k
+ TAG_BITS` (coordinate). Static arm `:711` mirrors this without the tag term
where no tag is invoked. CRC-16 (from `scl_joint.py`, see
`nbpolar-scl-lock-amendment` T2) is counted "toward `f_book` exactly once"
per the C10-style convention already cited in
`nbpolar-r2-fer-measurement-contract`. `nbpolar_incremental.py:182`
(`leak = float(key_dependent)`) and `:228`
(`leak_EC_actual_bits=leak`) carry this into `IRRunResult`; `:202` defines
`beta_eff_formula` in terms of `leak_EC_actual_bits`. CAL32 (32 frames/
session) is excluded from the key denominator as a sacrifice, not double-
counted as leakage (`docs/SECURITY_MODEL.md:107-129`, "The 32-frame CAL is
SACRIFICED... excluded from the key denominator"). **Conclusion**: reusing an
already-decoded block for a new descriptive or confirmatory measurement adds
no leakage beyond what that block's own decode already disclosed and
counted; re-running SCL on already-SC-decoded blocks (as in `decision-log.md`
2026-09-28 "27/28" entry) is exactly this case and added no new key-dependent
bits to the key itself (the check is descriptive, off the frozen operational
contract).

## D2 — `STATE.md:79` is stale (verified)

`STATE.md:79` reads: "`docs/SECURITY_MODEL.md` currently has NO CAL/prior
term at all（grep verified）". `SECURITY_MODEL.md:107-129` is titled "## NB-
Polar M2 CAL / prior accounting (CANDIDATE, descriptive)" and states the CAL
sacrifice-and-exclusion mechanism explicitly. Either `SECURITY_MODEL.md:107-
129` postdates the `STATE.md:79` grep, or the line was never re-verified
after that section was added. Proposed fix (task T3): strike or annotate
`STATE.md:79` with a pointer to `SECURITY_MODEL.md:107-129`.

## D3 — "Never reflow": stated reasons vs. proposed reading

| Source | Stated reason (verbatim/paraphrase) | Category |
|---|---|---|
| `ACQUISITION_SPEC_DRAFT_20260922.md:74-80` (§9) | "decoder 接触过的帧 NEVER 回流为确认样本"; G3 independence = "decoder/model independence, 非 no-prior-contact" | (C) audit/independence |
| `REAL_DATA_FEASIBILITY_STRATEGY.md:113-123` | "joint scoring uses one coherent probability model **without evidence reuse**"; "small preregistered list contains true L1 **often enough**" | (B) statistical selection |
| `R2_MEASUREMENT_CONTRACT_DRAFT_20260924.md` C10/C11 | same "永不回流"/"reservation-partition" language, cites ACQ Annex A §2/§7/§9 | (B)+(C), same sources |

No cited text anywhere in this repo grounds "never reflow" in a leakage
mechanism (D1 already shows leakage is booked per-disclosure, not per-
freshness). The (B)/(C) split is this proposal's own reading of the stated
reasons, not a repo-native taxonomy — flagged explicitly so the PI can reject
or refine it rather than treat it as an existing rule.

**D3 caveat (UNVERIFIED figure)**: the task input asserted "二元基线...每个
会话约 65 块" citing `POLAR_VS_LDPC_CROSS_REPO_COMPARISON_20260927.md:55,91,
236`. Independent verification found: `:55` states 812,620 pairs total, test
region 24×16384=393216 symbols; `:91` confirms an out-of-sample split exists
(`--pool-oos`); `:88-94` and `:233-239` (context around the third cited line)
describe a 2×2 cross-repo run at 16×16384=262,144 symbols, not a "65 blocks/
session" figure. Grepping the whole file for "65", "training", "样本外" and
"out-of-sample" found only the one `--pool-oos` hit at `:91`. **The specific
number 65 could not be reconstructed from this document and is not asserted
as fact here** — only the qualitative point (two-way train/held-out split,
no five-way CAL/CHAR/HELDOUT/EVAL/RESERVE partition) is carried into `R3`.

## D4 — Segmentation comparison (verified)

| | Segments | EVAL yield | Frozen as necessary? |
|---|---|---|---|
| Binary Polar baseline | train / out-of-sample (2-way) | majority of 812,620 pairs | n/a (different project; provenance only) |
| NB-Polar current draft | A1_CAL(1024) / CAL32(32) / CHAR(782) / HELDOUT(560) / EVAL(1792=14×128) / RESERVE | 14 blocks/session | **No** — `D-ACQ-03` `PENDING` (`R2_MEASUREMENT_CONTRACT_DRAFT_20260924.md:175-186`, "配额策略...待 T4 裁定 D-ACQ-03/04") |

`workspace/acq_inventory_20260928/REPORT.md:193-197` (scheme A) confirms this
segmentation is "对 EVAL 高度吝啬（94% 帧数被 CAL/CHAR/HELDOUT 占用）"; `:199-
205` (scheme B, PI-suggested contrast) shows CAL kept at 32 frames only,
remainder split EVAL+RESERVE, yields 32-33 blocks/session on the same two
sessions — but "此方案目前没有任何冻结配置或真实数据执行先例，采用前需要新的
OpenSpec 变更 + freeze review". This proposal's R3/source-list below is one
concrete instantiation between scheme A and scheme B: it keeps CAL32 (32f,
sacrificed) but reclassifies A1_CAL/CHAR/HELDOUT as EVAL-eligible rather than
dropping them, with stratification (R2 below) substituting for exclusion.

## D5 — Two exhaustion batches (verified)

| Batch | Remainder | Status |
|---|---|---|
| Old P-series (2026-01-07/23) | 101 frames never-decoded; 69 after 32f CAL, &lt;1 block | Genuinely exhausted under the current 128-frame block size |
| SHG 2026-01-13 `_1`/`_2` | RESERVE 29/99 frames, both untouched | Not exhausted; simply smaller than one 128-frame block under the *current* 4190-frame fixed prefix |

`FUTURE_DIRECTION_PLAN_20260924.md:36-37`: "'数据耗尽'是人为造成的。每个 3 s 的
SHG 采集约产生 33 个 N=32768 块...卡住进度的是采集时长和流程，不是物理。" This is
consistent with D4: the SHG sessions are not data-scarce, the fixed 4190-
frame segmentation prefix is what leaves &lt;1 block of RESERVE per session.

## D6 — Sample size `n`: two recomputations from the current `p`

Formula (normal approximation, consistent with the frozen contract's own
`C9` derivation table): `n ≈ z²·p(1-p)/w²`, z=1.96 (z²=3.8416), w=0.10
(frozen `D-FER-02`, `R2_MEASUREMENT_CONTRACT_DRAFT_20260924.md:293`).

Current point: `docs/decision-log.md` 2026-09-28 entry — 28 real-data B-arm
blocks (G2 14 + G3 14) at the frozen candidate under SCL(L=16,M=4,CRC-16):
27/28 exact, 1/28 (`G2 block 5`) `verify_failed`.

- **(i) Point estimate `p=1/28≈0.03571`**: `p(1-p)=0.03444`;
  `n=3.8416×0.03444/0.01≈13.23` → **n≈14**.
- **(ii) Wilson-upper on `p̂=1/28`, sample `n=28`** (conservative — avoids
  treating a 1-failure point estimate as exact): center≈0.09173,
  half-width≈0.08540 → **upper≈0.1771**. Using this as the sizing `p`:
  `p(1-p)=0.1457`; `n=3.8416×0.1457/0.01≈55.98` → **n≈56**.

Both are below the frozen `n=65` (itself derived from the stale `p=3/14`,
§`R2_MEASUREMENT_CONTRACT_DRAFT_20260924.md:140`, "`3.8416×0.1684/0.01≈64.7→
65`"). This does **not** silently update `D-FER-03` — `n=65` stays `DECIDED`
until the PI re-adjudicates it against (i) or (ii) (see `tasks.md` T1).
Neither (i) nor (ii) is itself a frozen quota; `decision-log.md:84`'s ban on
back-deriving *acquisition quotas* from `n` is unaffected — this is the
opposite direction (`p`→`n`), matching the contract's own D2 chain order.

## D7 — Proposed new rules (R1-R5), scope and exceptions

- **R1 (security)**: all public disclosures (K-coordinates, tag, CRC,
  CAL-sacrifice exclusion) are counted in `beta_eff`/key denominator per D1;
  re-decoding an already-decoded block adds no new disclosure beyond what
  that block's own decode already counted; "decode ≠ consume."
- **R2 (statistics)**: a reported FER/efficiency number is valid only if (a)
  method and all parameters were frozen before the blocks were seen, (b) the
  full declared block set is reported (no cherry-picking), (c) no post-hoc
  parameter tuning. Blocks that participated in any model-selection step
  (e.g. HELDOUT's NLL scoring) must be labeled and reported in a separate
  stratum, not excluded outright. A companion table of "selection degrees of
  freedom already exercised on real data" is required: the w=200/CIRCULAR
  pairing window was chosen *after* G1's SHG_1 δ-tail FAIL (S11, see
  `REAL_DATA_FEASIBILITY_STRATEGY.md` G1→G1R2 note); SCL was first applied to
  SC-failed blocks (`workspace/m2_scl_rescue_g2g3/`, commit `326594ca`)
  before the fidelity check on SC-successful blocks (commit `16ad0d93`).
- **R3 (segmentation)**: each session sets only CAL32 (32f, sacrificed); all
  remaining frames are decode-eligible by default. CHAR/HELDOUT/A1_CAL are
  carved out only when a specific research comparison needs them, with a
  stated reason. Blocks stay 128 frames; no block crosses a CAL32 boundary.
- **R4 (sample size)**: `n` is recomputed whenever the reference `p` changes;
  `n` may also be used to back-derive the *data volume needed*, but never the
  acquisition *quota policy itself* (`decision-log.md:84` still binds quota
  back-derivation). Formula and both (i)/(ii) results are D6.
- **R5 (process)**: before asserting "new acquisition needed", check
  `docs/nbpolar/DATA_LEDGER.md` (task T2) and compute the actual gap; do not
  assert scarcity from memory of a stale STATE.md line.

## D8 — R2 contract amendment (proposed values, PI-adjudicable)

- **Source**: SHG `_1`/`_2`, full sessions. Frames 0-1023 (8 blocks, ex
  A1_CAL) + 1056-2397 (10 blocks, 62-frame remainder, ex CHAR+HELDOUT) +
  2398-4189 (14 blocks, ex EVAL) = 32 blocks/session, 64 total. CAL32 stays
  1024-1055. Arithmetic check: 1342 frames (CHAR 782 + HELDOUT 560) / 128 =
  10.48 → 10 blocks, remainder 62 (`REPORT.md:141-158` segment lengths).
  **Stratification label**: the 28 blocks at 2398-4189 (EVAL) are already
  decoded under the frozen candidate (SC and, descriptively, SCL — D6); the
  10 blocks at 1056-2397 (HELDOUT half) participated in M2's NLL model
  selection and must be reported as a separate stratum per R2; the 8 blocks
  at 0-1023 (A1_CAL) were used only for the M0 incumbent table fit — a
  characterization use, not a decode — and get their own stratum label too.
- **Candidate decode configuration**: M2 prior + SCL(L=16, top_m=4, CRC-16),
  K1=319/K2=6492, per the `nbpolar-scl-lock-amendment` unlock-for-real-data-
  candidate outcome (D4 point) and the 2026-09-28 decision-log "Consequences"
  note suggesting this exact listing as an R2 candidate configuration. P16
  construction order per `b4defb1e` (Tier-X, focused-review PASS).
- **D-ACQ-02/03 replacement**: replace with the source/stratification above;
  `D-ACQ-03`'s CAL/CHAR/HELDOUT/EVAL/RESERVE mutual-exclusion requirement is
  narrowed to "CAL32 exclusive of everything else" only (R3).
  `D-ACQ-04`(Type0) is unaffected.
- **D-ACQ-05 rewording**: scope narrowed to "applies only to the two
  2026-01-13 SHG acquisitions' own conditions" (config verified identical,
  `workspace/acq_inventory_20260928/REPORT.md:26-68`) — since this candidate
  plan uses no new acquisition, the general new-source comparability
  question stays `PENDING` for any future acquisition, unchanged.
- Execution still goes Pre-EXECUTE → one-shot execution → Pre-RESULT
  (AGENTS.md §10.3); nothing here authorizes execution.

## D9 — `participation_ledger.json` review (verified, not a confirmed bug)

The task input asserted an "accounting error" in
`workspace/acq_inventory_20260928/participation_ledger.json` — "把 EVAL 放在
4190 之后". Direct read found the ledger's `scheme_A` block already places
EVAL correctly at 2398-4189 (14 blocks) and separately computes
`eval_blocks_per_session_formula: floor((n_frames_post_skip - 4190) / 128)`
labeled explicitly as `"extra_eval_blocks_beyond_the_14_already_used"` (value
0 for both sessions, since RESERVE &lt;128). The *numbers* are not wrong. The
only defensible issue is a **naming ambiguity**: the formula key
`eval_blocks_per_session_formula` could be misread as counting the frozen
14-block EVAL segment itself rather than additional post-4190 blocks.
Recorded as a documentation-clarity task (T6), not an accounting-error fix;
the PI/main thread should confirm this reading before task T6 proceeds.

## D10 — What this design explicitly does not decide

No rule (R1-R5) is adopted; no `D-FER-03`/`n` value changes; no `D-ACQ-02/
03/05` wording changes; no `STATE.md`/`AGENTS.md` edit; no execution. All are
`tasks.md` T1 PI decisions.
