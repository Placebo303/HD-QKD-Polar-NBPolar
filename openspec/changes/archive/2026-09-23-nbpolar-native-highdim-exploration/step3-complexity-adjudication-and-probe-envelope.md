# Step-3 d=1024 paper-complexity adjudication + split-dimension probe envelope (design artifact — authorizes nothing)

## 0. Status

- `EXPLORATION_ONLY / DOCS_ONLY` — this file is an **envelope/skeleton** for the
  future Step-3 paper-complexity adjudication. It **authorizes no code, no run,
  no freeze change, no frozen-constant change, no data access, no Tier-X probe
  run, and no Tier-Y decision gate**.
- Parent scope: `openspec/changes/nbpolar-native-highdim-exploration/`,
  specifically proposal §Step 3 ("d=1024 paper-complexity adjudication +
  split-dimension probe design") and design §D5 (Step-3 complexity adjudication
  + split-dimension probe envelope), both **post-OQ3 as amended**.
- The actual paper adjudication happens at a future freeze under separate
  authorization per AGENTS.md §10.1–10.4. Nothing is computed in this file:
  structure is fixed now; numbers are future-freeze items.
- Any future adjudication execution needs its own freeze document plus separate
  verbatim user authorization. Nothing here satisfies that requirement.
- Output path + tier label (clarified at milestone close, per T8 V-2/V-3): the
  future one-page paper adjudication is a **paper-only, tier-N/A** artifact —
  it is neither a Tier-X probe run nor a Tier-Y gate (it computes nothing and
  touches no data) — and its output, if ever authorized, lands under
  `workspace/exploration/nbpolar-native-highdim/step3/` (at most `prereg.md` /
  `results.json` / `notes.md` per design §D1; a paper-only artifact may use a
  subset) under its own freeze plus verbatim user authorization. This envelope
  creates nothing.
- Minimalism (AGENTS.md §5.7): plain markdown only. No code, no checksums, no
  atomic writes, no schema validators, no retry frameworks, no defensive
  machinery (see §11).

### User-adjudicated decision OQ3 (2026-09-23; recorded verbatim, not re-opened)

- Proposal adjudication note (2026-09-23): "(3) Other factorizations ARE
  pre-allowed — GF(32) is the baseline candidate, not the sole locked family,
  and the Step-3 adjudication compares within the pre-allowed set (T6 and
  `design.md` D5 carry this delta)."
- `tasks.md` OQ section (2026-09-23): "OQ3：Step-3 是否确认 GF(32)
  为裂维探针，还是预允许其他因式分解。Decision: DECIDED 2026-09-23（用户裁决）——预允许其他因式分解；GF(32)
  为基线候选而非唯一锁定族，Step-3 裁决在预允许因式分解集合内比较。T6 与 design.md D5 按此调整。"
- Consequence: GF(32) = 32×32 is the **baseline candidate, NOT the sole locked
  family**. Factorizations other than GF(32) are **pre-allowed** for the
  Step-3 split-dimension probe within the set defined in §6. The future
  adjudication compares within that pre-allowed set. The set is **CLOSED at
  design time** — no post-hoc additions (§6).

## 1. Scientific question, success criterion, stop-loss, not-doing list

(Substance identical to proposal §Step 3 as amended for OQ3 and design §D5;
neither weakened nor extended.)

- **Scientific question:** even if Steps 0–2 look promising, does a native
  d=1024 decoder survive the complexity wall on paper (RS-kernel / SCL scaling
  as cited in §2), and is a split-dimension probe (GF(32) baseline; other
  factorizations pre-allowed per OQ3) the right bounded next object?
- **Read-only inputs:** the cited complexity formulas as stated (§2 — no
  re-derivation claimed here); sibling GF(32) history as negative-result
  record (§8 — constraints, not reusable code).
- **Design outputs (later, under separate authorization):** a one-page
  complexity adjudication (ops/memory vs block budget, with explicit
  assumptions, §3–§4) plus a bounded split-dimension probe envelope
  (GF(32) baseline candidate; other factorizations pre-allowed per OQ3 —
  what is asked, what would falsify it, what it cannot claim; §5–§7).
- **Success:** a future freeze document exists fixing every assumption in §3
  and every table cell in §4 before any adjudication reading, and the reading
  records exactly one of SCALE / PROBE-ONLY / STOP (§5) against its stated
  falsifier.
- **Stop-loss:** if the paper adjudication shows orders-of-magnitude overrun
  with no credible reduction path, the recommendation is to stop scaling and
  record the negative — not to launch code (per proposal §Step 3; see §9).
- **Not doing:** no decoder implementation, no GF(32) graph work, no
  complexity-figure tuning to justify a preferred answer, no claim of any
  kind — no FER claim, no efficiency claim, no promotion claim, no
  qualification claim, no composable-key or security claim (§10).

## 2. Complexity inputs, CITED AS-IS

Every figure below carries its source and assumption label. Nothing is
re-derived, re-computed, or arithmetically combined in this file. Any number
appearing in the future adjudication belongs to the future freeze document,
not here.

- **C1 — RS-kernel scaling.** Formula as cited: RS-kernel `O(q^l·l)`.
  Source: Trifonov-2018 (as cited in proposal §Frozen facts). Status: cited
  as-is; no re-derivation. Assumption refs: §3 (kernel width `l`, alphabet
  size `q` per configuration row).
- **C2 — SCL scaling.** Formula as cited: SCL multiplications
  `(q²+q)·L·n·log n/2`. Source: Chen–Bai–Ma-2022
  (DOI 10.1016/j.jiixd.2022.10.002, as cited in proposal §Frozen facts).
  Status: cited as-is; no re-derivation. With the cited scale point q=1024
  the source discussion notes ≈ 1e6 multiplications/node scale. Status of
  that scale point: cited as-is from the literature anchor; not computed here.
  Assumption refs: §3 (list size `L`, block length `n`, alphabet size `q`
  per configuration row).
- **C3 — Block-budget assumption from the frozen point.** `N=32768` symbols
  per block with a `d=1024` alphabet (frozen numbers verbatim; see §12).
  Source: proposal §Frozen facts. Status: frozen context, not an adjudication
  result; assumption refs: §3.
- **C4 — Per-decode budget.** `~20 s` per decode. Status: **INFERRED
  ASSUMPTION — never a frozen constant.** Provenance: G2/G3 wall telemetry
  ≈ 855–858 s across 3 arms × 14 blocks ⇒ ≈ 20 s per decode (as stated in
  the task scope; no arithmetic performed here). This figure must never be
  presented as a frozen constant; the future freeze re-states it as an
  assumption with this provenance or replaces it with its own stated budget
  assumption.

## 3. Assumption list (structure fixed now; values are future-freeze items)

The future freeze must fix one value per item before any adjudication
reading. This file fixes the item list only; no value is set here.

- **A1 — Alphabet size `q` per configuration row** (full native d=1024 row;
  one `q`-set/factorization per probe row within the pre-allowed set, §6).
- **A2 — Kernel/list parameters** (`L`, `l` / kernel width, iterations where
  applicable) per row.
- **A3 — Block length `n`** used in the SCL formula per row.
- **A4 — Memory model** (what is counted: messages, lists, kernel tables;
  units stated) per row.
- **A5 — Budget** (block budget from C3; per-decode budget from C4 as an
  explicitly labeled inferred assumption unless the freeze states its own).
- **A6 — Reduction-path claims admitted** (which hypothesized reductions, if
  any, the adjudication may credit, and under what stated condition — §5
  falsifiers govern whether they rescue a verdict).
- **A7 — Probe-cost bound** (what "bounded cost" means for the
  split-dimension probe rows; fixed before the reading, never tuned after).

## 4. Ops/memory-vs-budget table SKELETON (zero invented numbers)

Rows = candidate configurations: the full native d=1024 row plus one row per
split-dimension probe candidate within the pre-allowed set (§6). Columns are
fixed below. Every numeric cell is a **future-freeze item**; this file
contains no arithmetic and no invented values.

| Row (configuration) | q | q-set / factorization | Kernel/list params (L, l) | Ops estimate (formula as cited) | Memory estimate | Budget comparison | Assumption refs |
|---|---|---|---|---|---|---|---|
| Full native d=1024 | TBD (future freeze) | TBD — native, no split (future freeze) | TBD (future freeze) | TBD — C1/C2 formula as cited (future freeze) | TBD (future freeze) | TBD (future freeze) | A1–A6 |
| Split-dimension probe, GF(32) baseline (32×32) | TBD (future freeze) | TBD — GF(32) = 32×32 baseline (future freeze) | TBD (future freeze) | TBD — C1/C2 formula as cited (future freeze) | TBD (future freeze) | TBD — incl. A7 bound (future freeze) | A1–A7 |
| Split-dimension probe, other pre-allowed factorization (one row per candidate admitted under §6) | TBD (future freeze) | TBD — within pre-allowed set only (future freeze) | TBD (future freeze) | TBD — C1/C2 formula as cited (future freeze) | TBD (future freeze) | TBD — incl. A7 bound (future freeze) | A1–A7 |

- No additional rows may be added post-hoc beyond the pre-allowed set closed
  in §6. A candidate outside the closed set is not an extra row; it is out
  of scope for the future adjudication.
- The future freeze fills every TBD cell before the reading; no cell may be
  filled by assumption, placeholder, or inference in this skeleton.

## 5. Trifurcation with falsifiers

The future adjudication records exactly one verdict. Each verdict carries its
falsifier stated below; a verdict whose falsifier is met is not recorded.

- **SCALE** — recorded only under conditions where full native d=1024 is
  declared viable on paper: the full-native row's ops/memory sit within
  budget under the frozen §3 assumptions with no post-hoc assumption change.
  Falsifier: ops/memory over budget by orders of magnitude with no credible
  reduction path (per the A6 paths admitted at freeze time) ⇒ SCALE is not
  recorded.
- **PROBE-ONLY** — recorded only where the split-dimension probe within the
  pre-allowed set is the bounded next object: at least one probe row sits
  within the A7 cost bound while the full-native row does not survive its
  falsifier. The probe asks only whether the split-dimension object preserves
  the Step-1 separation signal (cf. sibling artifact
  `step1-screening-design.md`: the native-vs-bit-plane separation signal at
  small q) at bounded cost; it cannot claim d=1024 native performance.
  Falsifier: the probe cannot preserve the Step-1 separation signal at
  bounded cost ⇒ PROBE-ONLY is not recorded.
- **STOP** — the negative is recorded: scaling stops, no code is launched.
  Falsifier: a credible reduction path exists (among the A6 paths admitted at
  freeze time) that keeps a configuration within budget ⇒ STOP is not
  recorded on complexity grounds alone.

## 6. Pre-allowed factorization set (OQ3)

- **Baseline:** GF(32) = 32×32 — the baseline candidate, not the sole locked
  family.
- **Admissibility criteria** for any other factorization (all must hold):
  1. the factor product is 1024;
  2. preference for factors with existing repo algebra support;
  3. both factors bounded so probe cost stays bounded (under the A7 bound).
- **Closure rule:** the set is CLOSED at design time. Membership is fixed by
  the future freeze from within the admissible envelope above; no post-hoc
  additions after the reading. A factorization admitted at freeze time is
  compared within the set — it never promotes the probe into a d=1024
  native-performance claim (§5 PROBE-ONLY).
- **Repo-internal GF(32) context (recorded, not authorized for reuse):**
  Phase-1 GF(32) poly37/α2 + butterfly transform, independent 17/17. Noted
  here as admissibility context for the baseline only; nothing in this file
  opens a GF(32) graph-work or implementation path (§10).

## 7. Sibling-negative constraints (recorded as CONSTRAINTS, not reusable code)

- **V7R3** — GF(32)×GF(32) multilayer: on record as a wrong route
  (per proposal §Frozen facts). Constraint: any future probe touching a
  multilayer structure in this shape must distinguish itself from V7R3 in its
  own freeze; V7R3 code is not reused here and no reuse path is opened.
- **V54** — Q_SUB=32 production shell: on record as a wrong route
  (per proposal §Frozen facts). Constraint: a Q_SUB=32-shaped probe envelope
  must distinguish itself from the V54 shell in its own freeze; the V54
  shell is not reused here and no reuse path is opened.
- **V13R3** — native q=1024 (n=256, rate 0.336): on record as a wrong route
  (per proposal §Frozen facts). Constraint: the full-native row (§4) is
  adjudicated on paper against this negative history; V13R3 is not re-run,
  re-derived, or reused here.
- **Current d=1024 NB-LDPC position as frozen-facts context** (read-only
  numerical reference, not an adjudication input): `f≈12.1`, leakage
  6.64 bits/symbol, target `f≈1.1` (values as stated in proposal §Frozen
  facts; not altered, not re-derived, not claimed here).

## 8. Step-1 separation-signal preservation question

- The probe-preservation question refers to the Step-1 separation signal
  defined in the sibling artifact `step1-screening-design.md` (paired FER–f
  separation of native-symbol vs ordered-MSD bit-plane arms across the locked
  ladder q ∈ {4, 8, 16}).
- The Step-3 probe asks only whether a split-dimension object within the
  pre-allowed set preserves that signal at bounded cost (A7). A positive
  preservation reading motivates freezing further designs; it does not assert
  anything about d=1024 native performance or about real-data FER (sim/real
  firewall per design §D1; no sim→real generalization claim).

## 9. Stop-loss

- If the future paper adjudication shows orders-of-magnitude overrun with no
  credible reduction path (among the A6 paths admitted at freeze time), the
  recommendation is to **stop scaling and record the negative — not to launch
  code** (per proposal §Step 3).
- The stop-loss is a design requirement, not a post-hoc judgment: the future
  freeze states the numeric no-go reading rule before any adjudication
  reading; no assumption (A1–A7) may be moved after the table is filled to
  rescue a preferred verdict (§10: no complexity-figure tuning).

## 10. Not doing

- No decoder implementation (no q-ary polar / HD-Cascade / list-decoder code).
- No GF(32) graph work (no multilayer construction, no shell reuse, no
  algebra implementation).
- No complexity-figure tuning to justify a preferred answer (assumptions
  A1–A7 freeze before the reading; §9 stop-loss applies as written).
- No claim of any kind: no FER claim, no efficiency claim, no promotion
  claim, no qualification claim, no composable-key or security claim. Any
  future claim-bearing gate is Tier-Y and needs its own change, freeze,
  independent Pre-EXECUTE/Pre-RESULT reviews, and explicit user authorization.

## 11. Minimalism (§5.7)

- Plain markdown: this file plus the future one-page adjudication and probe
  envelope only. No code, no checksums, no atomic writes, no schema
  validators, no retry frameworks, no caching layers, no hardening beyond the
  concrete failure modes named here (wrong-ledger citation, frozen-file
  touch, raw-data read, post-hoc assumption tuning — each guarded in
  §4–§5, §8–§9).
- Each future packet names its single realistic failure mode or omits the
  mechanism.

## 12. Frozen-number box (verbatim provenance; not adjudication results)

d=1024; N=32768 (=128 frames × 256 pairs); K1=319; K2=6492; P16
construction; W_P=200 / W_S=500 / CIRCULAR / skip=702; frame_pairs=256;
floor=1e-15; chunk=512; bin=200 ps; f(6811)=1.2747449;
key_dependent_bits=34,119 (=5·(K1+K2)+64, per-row constant);
public_control_bits=327,743; undetected 0/42 isolated (never merged into
success/FER); EVAL 14 blocks (frames 2398–4189); RESERVE SHG_1 29 frames /
SHG_2 99 frames; never pad/reuse/shrink, COMPLETE-BLOCKS-ONLY else
INSUFFICIENT; already-decoded segments = DEVELOPMENT data, never a
confirmation sample.

(No number in this box is moved by this envelope; all values match proposal
§Frozen facts verbatim. They are provenance context, not adjudication inputs
or results. The ~20 s per-decode figure is NOT part of this box — it is the
inferred assumption C4 with its provenance in §2.)
