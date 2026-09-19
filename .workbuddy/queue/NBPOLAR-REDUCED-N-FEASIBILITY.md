# NBPOLAR Reduced-N (N=8192) Feasibility Study — analysis only

- Status: DRAFT study for user decision. No freeze, no authorization, no implementation,
  no execution, no protected opens, no commit/push.
- Authority: planner subagent, 2026-09-20, branch `codex/nbpolar-phase0`,
  workdir `/mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar`.
- Question: is a reduced-N (N=8192) real-data block from the never-decoded 2M tail
  (3595..3644, 50 frames = 12,800 pairs) a defensible next step, and what exactly
  does it cost/require?
- Inputs read (worktree files + source code only; NO protected opens — no pairs
  parquet, no counts NPZ, no prior/alt NPZ content, no `.bin` series bytes; digests
  and persisted scalars only):
  `.workbuddy/queue/NBPOLAR-PHASE4-NEXT-PHASE-PLAN.md` (ranked options; option (iv));
  `.workbuddy/queue/NBPOLAR-PHASE4-NEXT-BRANCH-DECISION.md` (D1–D4, D1-A, session
  asymmetry); `NBPOLAR-PHASE4-P20S-R1-GATE-FIX/MAIN_THREAD_ACCEPTANCE.md` + `DELTA.md`
  + `l2_mechanism_probe_2m/{frozen_plan.json, aggregate_summary.json,
  input_and_predecessor_identity.json}` (accepted R1 root);
  `NBPOLAR-PHASE4-P20S-MECHANISM-PROBE-2M-MERGED/TASK_PACKET.md` (§§2–4: ledger,
  reuse stance, D1-A amendment); `NBPOLAR-PHASE4-P16-N32768-OPERATIONAL-F13/TASK_PACKET.md`
  + `P16_FREEZE.md` + `operational_f13_gate/construction_and_allocation.json` (header
  fields) + `PRE_EXECUTE_REVIEW.md`/`PRE_RESULT_REVIEW.md` excerpts (via targeted
  grep); `openspec/changes/formal-ir-nbpolar-phase4-p0/specs/` (delta-spec layout);
  `comparison_bench/src/comparison_bench/formal_ir/nbpolar/` dir listing + targeted
  greps (`FROZEN_N`, tag expansion in `protocol.py:144`,
  `target_construction.py:1559` frozen-point gate).
- Method: ledger arithmetic rechecked inclusively (end−start+1); N-dependent
  quantities recomputed as arithmetic only (no code executed, no K hand-filled —
  AGENTS.md §5.5: K/budgets are derived in-packet, never pre-committed; §2 values
  below are shapes/estimates labelled as such).

## Goal

Decide, with cited evidence, whether ONE N=8192 real-data block from the 2M HOLD
tail is a defensible next step: exact population arithmetic, evidence-based cost
inventory (new-derivation vs reusable-read-only), the comparability verdict (the
decisive scientific point), gate class + authorization map, alternatives, a clear
recommendation, and the ONE decision to put to the user.

## Non-Goals

- No production-code change, no runner edit, no decoder/RNG/tag execution, no new
  DEV/HOLD contact, no protected opens, no K/budget/order/alt recompute or
  hand-fill, no new tag domains, no construction/prior/order derivation.
- No FER, efficiency, leakage, key-rate, reliability, recovery-rate,
  scaling-superiority, or promotion claim anywhere in this study (descriptive only).
- No H2 verdict inside this study; no OpenSpec spec edit by this study; no
  overwrite under `results/` or `comparison_bench/outputs_comparison/`; no
  commit/push; this document authorizes nothing.

## Impact Scope

- Reads: worktree queue docs + accepted evidence JSON/md + source-code constants
  (listed above). Touches no runner, no frozen evidence root, no OpenSpec specs.
- Writes (additive only): this file,
  `.workbuddy/queue/NBPOLAR-REDUCED-N-FEASIBILITY.md`.
- Affects: main-thread branch decision only (option (iv) vs (iii)/(i)/(v)).

---

## 1. Population arithmetic (exact, from the ledger)

Ledger source: NEXT-PHASE-PLAN §3 (post-P20S/R1 state), corroborated by DELTA.md
§2 and R1 `frozen_plan.json` (`hold_tail_counted_never_decoded`,
`build_dev_disjointness_s2_ii`, `merged_frame_list`). Frame convention: 256
rows/frame (P20S TASK_PACKET §4: 128 frames = 32768 pairs). N=8192 block =
8192/256 = **32 frames**.

| # | never-decoded segment (post-P20S/R1) | frames (inclusive) | pairs | N=8192 blocks formable |
|---|---|---|---|---|
| 1 | 1.5M VAL stub 2172..2212 | 41 (2212−2172+1) | 10,496 | 1 (32) + 9-frame stub |
| 2 | 1.5M HOLD 2725..2766 | 42 (2766−2725+1) | 10,752 | 1 (32) + 10-frame stub |
| 3 | 2M HOLD tail 3595..3644 | 50 (3644−3595+1) | 12,800 | **1 (32) + 18-frame stub** |
| total | | **133** | **34,048** | |

Totals check: 41+42+50 = 133; 10496+10752+12800 = 34048 — matches NEXT-PHASE-PLAN
§3 verbatim ("Total 133 frames / 34,048 pairs").

**Verdict: YES — 50 frames suffice for exactly one N=8192 block (32 frames),
with an 18-frame remainder.** Exact frame lists (first-contiguous-block rule,
same convention as all P20 DEV selections):

- N=8192 Block R1 (2M HOLD, session `type2_2M_20260121_183657`): frames
  **3595..3626** (3626−3595+1 = 32; 32×256 = 8192 pairs). Single contiguous
  segment, single split (HOLD), single session.
- Declared remainder (counted, never decoded): frames **3627..3644**
  (3644−3627+1 = 18; 18×256 = 4608 pairs).
- 1.5M exact lists (for the record; low-information controls only, §3):
  VAL stub block 2172..2203 (32) + stub 2204..2212 (9 frames / 2304 pairs);
  HOLD block 2725..2756 (32) + stub 2757..2766 (10 frames / 2560 pairs).

**No cross-split combining is needed** for the single 2M block: the 50-frame
tail is one contiguous segment inside one split (HOLD intra-file range
2916..3644 per R1 frozen plan). The D1-A precedent (same-session cross-split
merge VAL 2827..2915 + HOLD 3556..3594, branch-decision §4 D1-A, executed via
P20S) is therefore NOT invoked — but it remains the only authorized form of
merge, and **1.5M↔2M mixing is never permitted** (branch-decision §3 session
asymmetry: true-L1 oracle ceiling ~12.5% on 1.5M vs ~70% on 2M; §5: cross-session
pooling forever forbidden; P20S TASK_PACKET §2(j)). The two 1.5M stubs are
formable into N=8192 blocks arithmetically but are low-information populations
(oracle ceiling 1/8); they may serve only as non-pooled controls, never as
pooled or primary evidence.

---

## 2. What changes at N=8192 (cost inventory, evidence-based)

Frozen N=32768 pins being replaced (all literals from the accepted roots):
construction sha `055c9064…c3faea1b`, `(K_total,K1,K2) = (7080,334,6746)`,
budget literal `1.3*32768*0.8325627219737477−64 over 5 = 7080`, key caps
A/B 35464 / O 33794 bits, public `10*32768+63 = 327743` bits/tag, planned totals
key 104722 / public 983229, orders-A digest `b2255449…0906` (32768-length L1+L2
permutations), alt digest `98e25495…5fb5` (α=1.0, floor 1e-15), spike-B digest
`139f34c3…1864` (F-median8, first-K2 6746), 2M H
`0.02566204884275839 / 0.8069006731309893 / 0.8325627219737477`
(R1 `frozen_plan.json`, `aggregate_summary.json`, DELTA.md §§2–3).

| # | item | N=8192 consequence | class |
|---|---|---|---|
| C1 | `construction_and_allocation.json` rebuild (kernel/transform sizing at N, TRAIN-risk pooling over 8192 positions, `(K1,K2)` exhaustive selection by TRAIN residual per P16 pattern `TASK_PACKET.md` P16-02) | Full re-derivation: new counts-train sampling, new pooled `(e,h,index)` worst-first orders, new K split (K1/K2 NOT carried from 334/6746) | **new derivation required** |
| C2 | Runner `FROZEN_N = 32768` (every real-data module: `l2_mechanism_probe_2m.py:151`, `l2_alt_maintain_2m.py:105`, `l2_alt_hold_ir_2m.py:106`, `raw_prior_val_1p5m.py:92`, `operational_f13.py:142`, `l2_order_position_1p5m.py:137`, et al.; `target_construction.py:1559` hard-gates `n == FROZEN_N`) | New module (or thin-importer + new frozen constants) with `FROZEN_N = 8192` + focused injected tests; cannot pass `--n 8192` to any frozen-point runner | **new derivation required** (code + tests) |
| C3 | K allocation `floor((1.3·N·H−64)/5)`: at N=8192 with 2M H=0.8325627219737477 → 1.3·8192 = 10649.6; ×H ≈ 8866.5; −64 ≈ 8802.5; /5 ≈ 1760.5 → **≈1760** (vs 7080; note 7080/4 = 1770 — the −64 tag term breaks exact quartering) | Value derived in-packet from recomputed H (within 1e-12 per P20S §3 recipe), **never hand-filled** (AGENTS.md §5.5); ≈1760 is an estimate, not a committable literal | **new derivation required** (formula shape reusable) |
| C4 | L1/L2 orders: `raw_prior_orders_2m.json` (32768-length permutations) | Length mismatch + per-N geometry ⇒ **cannot reuse**; fresh worst-first empirical orders at N=8192 (new counts opens + sampling budget). Spike B-order: F-median8 formula-id reusable read-only, but R=8 window convention vs 8192-geometry must be re-frozen (new freeze decision, not automatic carry) | **new derivation required** |
| C5 | Tag length `10·N+63` bits/tag (`protocol.py:144`: 10-bit expansion → `uint8[10·N]`): 327743 → **81983** | Formula reusable read-only; value = frozen arithmetic in packet; new tag domain (master/prefix per packet convention, cf. P20S master 2026092360) | formula **reusable**, value+domain **new** |
| C6 | SC depth: binary polar stages log2(N): 15 → **13** (arithmetic); `chunk_rows=512` geometry re-sizing (P11 chunked-SC precedent) | Code paths (`sc.py`, `sc_chunked_gate.py`, `transform.py`) reusable; all frozen sizing constants new | paths **reusable**, constants **new** |
| C7 | IR-1..IR-5 instrumentation (64-bin hist, rank pct, 1.0×/2.0× thresholds, top-16, `ir5full-v1` bin+manifest encoding) | Formulas/caps reusable (P20Q-identical); N-dependent lengths new (IR-5 series 32768 → 8192: 32 KiB f32 + 8 KiB + 8 KiB = 48 KiB/record); manifest format reusable | formulas **reusable**, lengths **new** |
| C8 | Disclosure accounting `5·(K1+K2)+64`, planned key/public totals, recount gates | Follow C3; recount machinery (P20A pattern) reusable | values **new**, machinery **reusable** |
| C9 | Population gates (single-segment containment, TRAIN-exclusion, consumed-range exclusions, S2-ii disjointness declaration) | Gate pattern reusable; frame sets (3595..3626 DEV, 3627..3644 remainder) new + frozen | pattern **reusable**, sets **new** |
| C10 | Reviews + authorizations | Fresh freeze review, independent Pre-EXECUTE, Pre-RESULT, main-thread acceptance (§4) | **new required** |

**P16 precedent for how long such a change takes.** The N=32768 point was not
one packet but a ladder: P12 (N-scaling profile) → P13 (empirical genie
scaling/construction) → P14 (learning curve) → P15 (mid-N scaling) → P16
(operational f≤1.3 gate: new runner `operational_f13.py` + focused injected
tests + full `test_nbpolar_*` suite + Pre-EXECUTE with wall/RSS prediction +
single Tier-Y execution at 2100 s timeout / 2 GiB / 16 TRAIN + 64 DEV blocks +
Pre-RESULT recomputation of construction/outcomes/Wilson/accounting + acceptance;
P16 `TASK_PACKET.md` + `P16_FREEZE.md` + `AUTHORIZATION_PROMPT.md`). Contrast
P20S-scale thin reuse (byte-identical P20O artifacts, Stage-A zero protected
opens, Stage-B 1200 s envelope with observed 37 s wall, 5 SC + 3 tags,
15-file root): at N=8192 **nothing is thin-reusable except session-H inputs,
formula shapes, and code paths** — the effort replays P16-scale, not P20S-scale.
Rough magnitude: new spec delta + new/tested runner + full-suite green + two
independent reviews + one Tier-Y execution with fresh TRAIN sampling — i.e. a
multi-implementation-turn change with its own freeze, not a same-week reuse
packet.

---

## 3. Comparability cost (the decisive scientific point)

**Per-N results (K, disclosure, hazard geometry, FER-like behavior) are NOT
comparable across N.** Every accepted number below is pinned to N=32768
construction, orders, and disclosure sizes; none transfers to N=8192:

1. **The 1/4→2/5→4/5 restoration chain does NOT transfer.** P20N arm-B 1/4
   (1.5M HOLD) → P20O arm-B 2/5 (2M VAL) → P20Q arm-B 4/5 (2M HOLD) was scored
   at K2=6746 disclosed positions under 32768-length worst-first + spike orders
   (branch-decision §1 table). At N=8192 the disclosed-set size (≈K2 of ≈1760),
   the order geometry, and the operating rate all differ — an N=8192 outcome
   can neither extend nor break this chain.
2. **The H2 verdicts do NOT transfer.** H2a REFUTED / H2b SUPPORTED (median
   r_fail 2.2835, n=37) / H2c SUPPORTED (in-X 35/37) / H2d flat (mean 0.002185)
   / H2e REFUTED-geometry-incoherent-truncated-scope (NEXT-PHASE-PLAN inputs;
   post-R1 updates n→38 per plan §1.2) are adjudications over 63-row
   (post-R1) N=32768 join geometry. An N=8192 block contributes zero rows to
   that join; pooling across N is forbidden by the same logic that forbids
   truncated/full-block pooling (plan §1.1: cross-scope pooling FORBIDDEN).
3. **The IR-5 full-block geometry does NOT transfer.** The accepted
   `ir5full-v1` archive is 3 arms × 32768 positions (hazard f32 + in-prefix u8
   + in-U u8) with arm-A/O byte-identity findings (R1 acceptance §3). An
   8192-length series has different rank structure, prefix fractions, and
   top-k concentration baselines — no curve overlays, no shared thresholds.
4. **The leakage/disclosure accounting does NOT transfer.** Key
   `5·(K1+K2)+64` (35464/35464/33794, total 104722), public `10N+63`
   (327743/tag, total 983229), budget literal `1.3·32768·H` (R1 acceptance
   §2) are N-literals. N=8192 re-derives all of them (C3/C5/C8).

**What a single N=8192 block COULD tell us:** a qualitative, descriptive-only
persistence check — whether the L2-spike failure mechanism (first-error at a
local-hazard spike, fail site vs disclosed prefix under both domain flags) and
spike-order coverage behavior reproduce off the N=32768 point at the new K.
**What it COULD NOT tell us:** any confirmation/denial of an N=32768 claim, any
extension of the restoration chain, any H2 (re-)adjudication input, or any
FER/efficiency/reliability reading — n=1 counts have no discriminating power
(P20R demonstrated exactly this at N=32768: anchor + both oracles non-exact on
an unrecoverable-at-this-point block, branch-decision §2(i)), and first-look
geometry at a new point has no baseline to be anomalous against.

**Recommendation: DO NOT PROCEED with (iv) now.** Deciding criterion: a new-N
Tier-Y execution is justified only when (a) the zero-cost archive (H2 v2 +
geometry mining, option (iii)) leaves a *named* mechanism question that *cannot*
be answered from persisted evidence, AND (b) that question is testable at
N=8192 with a preregistered geometry quantity whose baseline does not require
N=32768 comparability. Both conjuncts currently fail — (iii) has not run, so no
such question exists yet. Revisit (iv) only on a written trigger from the (iii)
findings.

---

## 4. Gate class + authorization

- **Gate class: a P16-scale OpenSpec spec delta — explicitly NOT a thin packet.**
  Under the existing umbrella change `formal-ir-nbpolar-phase4-p0/` (which holds
  per-effort deltas `specs/nbpolar-phase4-pXX/`, incl. `nbpolar-phase4-p20s/`),
  (iv) would add a new delta spec (e.g. `specs/nbpolar-phase4-p2x/` + proposal /
  design / tasks entries) with P16-magnitude content: new construction/order/K
  derivation, new FROZEN_N runner + tests, new population freeze. It is NOT a
  new top-level change of class (i) (full operating-point redesign, NEXT-PHASE-PLAN
  §2 rank 3), but the branch-decision D1-B note governs verbatim: reduced-N
  reopening means "新 OpenSpec change，不是 packet" (a new OpenSpec change, not a
  packet) — i.e. it may not ride any existing packet freeze.
- **Required reviews/authorizations (named):** (1) OpenSpec delta authored +
  main-thread freeze review; (2) Stage-A-style implementation authorization
  (explicit pasted text; new runner/tests/derivation-program pin); (3)
  independent reviewer-go **Pre-EXECUTE** PASS (AGENTS.md §10.3: intended branch,
  scoped cleanliness, frozen contract, explicit user authorization,
  target-output absence, focused tests); (4) Stage-B single-execution
  authorization (explicit pasted text, separate from (2) per P20S gate
  discipline); (5) independent reviewer-go **Pre-RESULT** review on actual
  artifacts; (6) main-thread acceptance before any analysis use. FAIL at any
  gate blocks execution/solidification.
- **Inside or outside standing pre-authorization? OUTSIDE.** The standing
  pre-authorization covers continuing exploration and recommend-option picks of
  class (iii): analysis-only joins/mining under a frozen packet with zero
  decoder/RNG/tag calls and zero protected opens (NEXT-PHASE-PLAN §4). Tier-Y
  real-data execution — touching the never-decoded tail, opening the pairs
  parquet, spending the one-shot attempt — always needs its own freezes and
  explicit authorizations (AGENTS.md §§3, 10.3; P20S TASK_PACKET gate
  discipline: standing authorization does NOT collapse Tier-Y gates). This study
  itself fits the standing scope (analysis-only, additive single file); anything
  in §2 rows C1–C4/C9 does not.

---

## 5. Alternatives comparison (one paragraph each, evidence-based)

**(a) Analysis-only mining of the P20S/R1 full-block geometry archive.**
Already available at zero marginal cost: the accepted R1 root
(`l2_mechanism_probe_2m/`: jsonl + summary + `ir5_full_manifest.json` +
`report.md` + `frozen_plan.json` + identity pins; 9 `.bin` series
manifest/sha-pinned, byte-identical across the R1 delta per acceptance §2)
plus the 63-row post-R1 join (P20N 16 + P20O 20 + P20Q 20 + P20R 4 + P20S 3)
specified in NEXT-PHASE-PLAN §1. It decides H2e at full-block scope (IR-4
top-16 in-prefix 0/48 on all arms vs IR-2 mid-rank 0.4322 — the sharpest
available contrast), extracts the last value from the consumed merged block,
and is the only option inside standing pre-authorization. Its limit is that it
cannot create new operating-point evidence — but no other option creates
*comparable* new evidence either.

**(b) N=8192 new-construction packet.** Formable (exactly one 2M block,
3595..3626, §1) and stays in the high-information session, testing mechanism
persistence off the N=32768 point. But the cost is P16-scale (§2, ten items,
only formulas/paths reusable) while the information gain is capped: n=1 counts
non-discriminating (P20R precedent), geometry first-look without baseline, and
§3 severs every transferable conclusion — so it spends a P16-size effort plus
irreversibly consumes 32 of the last 50 high-information frames to produce
evidence that cannot update any accepted verdict. Justified only on the §3
trigger, not speculatively.

**(c) Wait for new acquisition.** Fresh 2M-session frames would reopen the
N=32768 ladder where all accepted geometry, orders, K, and H2 baselines live —
scientifically the highest-value path (it preserves comparability, unlike
(iv)). But acquisition is outside project control: no gate exists that we can
pass, no timeline to plan against (NEXT-PHASE-PLAN §2 rank 4). Correct handling
is to record it as a dependency and keep the project productive on (a) meanwhile,
not to burn the last 50 frames on (b) while waiting.

**(d) Closeout of the N=32768 real-data ladder with a documented stopping
reason.** Zero new information, but preserves the honesty of the record: the
ladder closes because the population is exhausted under the authorized rules
(0 full N=32768 blocks remain; largest same-session remainder 50 < 128;
1.5M↔2M mixing forbidden; D1-A spent the single authorized merge on P20S —
NEXT-PHASE-PLAN §3, branch-decision D1/D1-A execution note), not because of any
performance verdict. This is the fallback iff (iv) is declined and no new
hypothesis from (iii) warrants (i)-class rescoping (NEXT-PHASE-PLAN §2 rank 5).
It costs only a user decision plus the closeout note.

---

## 6. Recommendation + the ONE decision + ledger statement

**Recommendation:** run **(a)/(iii) now** (H2 v2 + geometry-archive mining under
standing pre-authorization); **decline (iv) now** per the §3 criterion (no named
unanswerable-from-archive question exists yet); hold **(d)/(v) closeout** as the
fallback; keep **(c) acquisition** as an external dependency. Revisit (iv) only
when a (iii) finding writes the trigger: the exact geometry quantity, its
N=8192 preregistration, and why no persisted series can answer it.

**The ONE decision to put to the user (concrete options):**

- **Option A (recommended):** authorize (iii) analysis-only packet freeze+run
  now; defer (iv) to the §3 trigger; defer (v) closeout to after (iii).
- **Option B:** authorize scoping of (iv) as a P16-scale OpenSpec delta
  (drafting only — still no execution, no tail contact) alongside (iii).
- **Option C:** decline both (iii) and (iv); authorize (v) N=32768 closeout now
  with the population-exhaustion stopping reason.

**Ledger statement (exact, post-P20S/R1; unchanged by this study):**
CONSUMED — 2M VAL 2827..2915 (89) + 2M HOLD 3556..3594 (39) = 128 frames = 1 ×
N=32768 block (P20S block consumed, R1 attempt spent; both roots immutable).
NEVER-DECODED — 1.5M VAL stub 2172..2212 (41 / 10,496 pr); 1.5M HOLD 2725..2766
(42 / 10,752 pr); 2M HOLD tail 3595..3644 (50 / 12,800 pr); total 133 fr /
34,048 pr. At N=8192 the 2M tail yields Block R1 = 3595..3626 (32 fr / 8192 pr)
+ remainder 3627..3644 (18 fr / 4608 pr). Authorizing (iv) would consume Block
R1 irreversibly (one-shot attempt, no rerun/tuning) and leave 18 + 41 + 42 =
101 never-decoded frames, from which no further same-session N=8192 2M block is
formable. Forward rule (unchanged): no real-data decode executes without a new
freeze + explicit authorization (NEXT-PHASE-PLAN §4).

---

## Tasks (ordered; verification of this study + conditional next steps — no coder tasks authorized by this study)

1. T1 — Main-thread check of §1 arithmetic against the cited ledger sources
   (NEXT-PHASE-PLAN §3, DELTA.md §2, R1 `frozen_plan.json` remainder/DEV pins):
   41/42/50 counts, inclusive ranges, 32-frame blocks, remainders 9/10/18,
   totals 133/34048. *Verify: every integer re-derivable from cited files; no
   protected open was performed (read list in header).*
2. T2 — Main-thread check of §2 pins (construction sha `055c9064…`, K
   (7080,334,6746), digests `b2255449…`/`98e25495…`/`139f34c3…`, H literals,
   `FROZEN_N` grep hits, `protocol.py:144`, `target_construction.py:1559`)
   and of the new-vs-reusable classification for C1–C10. *Verify: no K value
   presented as committable (≈1760 labelled estimate only, per AGENTS.md §5.5).*
3. T3 — Main-thread adjudication of the §3 comparability verdict and the
   two-conjunct trigger criterion (the study's load-bearing claim).
   *Verify: verdict consistent with D2/descriptive-only form and the
   cross-scope-pooling ban.*
4. T4 (conditional on user Option A) — Freeze + run the (iii) H2 v2 packet per
   NEXT-PHASE-PLAN §§1/4 (Tasks T1–T5 there); batch ledger/memory updates at the
   milestone. *Verify: standing-scope counters (zero decoder/RNG/tag/protected
   opens beyond the §1 ruling) hold.*
5. T5 (conditional on user Option B) — Draft the (iv) OpenSpec delta
   (`specs/nbpolar-phase4-p2x/` + proposal/design/tasks) with the C1–C10
   derivation plan, N=8192 preregistered geometry quantities, and the §4 gate
   sequence; explicitly no execution authorization. *Verify: delta states the
   §3 non-comparability disclaimer up front.*
6. T6 (conditional on user Option C) — Write the N=32768 closeout note with the
   §5(d) stopping reason; freeze further real-data execution. *Verify:
   decision recorded in `docs/decision-log.md`.*
7. T7 — Memory triage (mandatory per AGENTS.md §3) after the user decision:
   record the decision, the §1 ledger restatement, and the (iv) trigger
   criterion in durable memory; batch with the milestone.

*Small-task note for the orchestrator: this study is analysis-only and complete
as a document — there is no production-code task small enough to fast-path from
it. Any follow-on (T4/T5/T6) enters its own pipeline (packet freeze or OpenSpec
delta) after the user decision.*
