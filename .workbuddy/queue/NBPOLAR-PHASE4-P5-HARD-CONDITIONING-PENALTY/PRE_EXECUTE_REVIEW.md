# Pre-EXECUTE review — NBPOLAR-PHASE4-P5-HARD-CONDITIONING-PENALTY

Rev 1 (2026-09-13). Independent reviewer session; did not write the code under review.
Read-only except this file. The real 384-pair gate command was NOT run; no commit/push;
no Model-F/artifact/parquet/TTBin/real-data access; old evidence roots not modified.
Repository `/mnt/d/Code/HD-QKD_Polar_Comparison-nbpolar`; HEAD
`ab173f2a5e17336383a897b941080b731ba3dd9e` (unchanged; `git reflog` holds only the clone
entry). Pinned interpreter `/mnt/d/Code/HD-QKD_Polar_Comparison/.venv/bin/python`
(Python 3.12.3, numpy 2.5.3). Review date 2026-09-13, session window 17:2x-17:4x.

## Verdict: NEEDS_CHANGES

One blocking issue, documentation-only: `P5_FREEZE.md` (and
`P5_IMPLEMENTATION_NOTES.md`) enumerate the public tag masters as
`2026092470..2026092472`, which is `seed + 1000`, while the frozen definition
(packet, user authorization, freeze §5 first sentence, delta spec, module constant) is
`seed + 10000`, i.e. `2026101470..2026101472`. The executable contract (derived master)
is unambiguous and consistent; only the explicit enumeration in the two docs is wrong.
Everything else passes, including the full scientific math, gates, tests and scope.
No code/test/command/root change is required.

## Blocking Issues

- **B-1 (docs-only).** Master enumeration mismatch vs frozen definition.
  - `P5_FREEZE.md:100-102`: "`stream_seed + 10000` = **2026092470, 2026092471,
    2026092472**". Arithmetic: `2026091470 + 10000 = 2026101470`.
  - `P5_IMPLEMENTATION_NOTES.md:121-122`: repeats `2026092470..2026092472` in the
    freshness claim.
  - The module (`penalty_gate.py:79` `PUBLIC_TAG_MASTER_OFFSET = 10000`; `:912`
    `master = stream_seed + PUBLIC_TAG_MASTER_OFFSET`) and the packet/authorization
    both specify `seed+10000`; the emitted `frozen_plan.json`/`aggregate_summary.json`
    will record `[2026101470, 2026101471, 2026101472]`, contradicting the freeze doc.
  - Freeze §15.1 itself requires "this freeze doc matches the implemented constants
    ... (point, profile, D1/D2, seeds, masters, ...)" — it does not for masters.

Smallest in-scope repair (docs only; do not change code, constants, command, sets,
seeds or root):
1. `P5_FREEZE.md:102` → `**2026101470, 2026101471, 2026101472**`.
2. `P5_IMPLEMENTATION_NOTES.md:122` → `2026101470..2026101472`.
3. Optionally re-cite the freshness evidence: the reviewer independently ran
   `git grep -l <v> HEAD` and a worktree scan for all nine values
   (1470..1472 seeds, 2026092470..72 and 2026101470..72): HEAD has zero matches for
   all nine; the worktree matches only the P5 files. The corrected values are clean.
Then a focused re-review of the two corrected lines (no re-run of any check needed; all
other evidence below stands unchanged because the code was not modified).

## Non-Blocking Suggestions

- **N-1 (freeze wording).** Freeze §11:208-209 says "on expiry the remaining planned
  blocks are `resource_abort`". The implementation only marks the remaining blocks of
  the *current* stream; remaining streams emit no records (`_integrity_gates`
  `pairing_coverage_complete`/`attempt_accounting_at_frozen_point` then fail). Verified
  with a multi-stream microsecond budget: len(results)=4 vs planned 8, 5 gates fail,
  label `BLOCKED`, five files still written. Fail-closed either way; no verdict impact.
- **N-2 (notes rounding).** Notes §3.1 "within `2.1e-15`" for the literal P2 formula:
  exact max over all 32x32 coordinates is `2.1094237467877974e-15`
  (marginally > 2.1e-15 before rounding; test tolerance 1e-12 passes).
- **N-3 (power context, main-thread information only).** Fresh non-frozen reviewer
  smoke at the same frozen point (seeds 2026091500-1502, 96 pairs) gives operational
  exact 62/96 (64.6%) vs X02's 47/96 (49%); projected X at 384 pairs ~132-134, close
  to the pre-registered first-pass X=131. Both discriminator outcomes are reachable and
  this sensitivity is inherent to a single pre-registered attempt; it changes no
  threshold and blocks nothing.
- **N-4 (STATUS shape).** `STATUS.yaml` omits some closed-flag keys present in the
  P3/P4 templates (e.g. `raw_data_authorized`, `empirical_construction_authorized`,
  `phase7_authorized`); absent keys are not grants and the four open flags are exactly
  the authorized set. Informational.
- **N-5 (declaration source).** Unlike P3's authorization prompt, the P5
  `AUTHORIZATION_PROMPT.md` does not enumerate `state:`/`next_gate:` strings; the
  STATUS values follow the established naming pattern and match the lifecycle stage.
- **N-6 (sibling attribution).** Sibling-checkout files (e.g.
  `../HD-QKD_Polar_Comparison/AGENT_PROJECT_MEMORY.md` 17:19:25) were modified during
  the same wall-clock window, but their content is formal-IR/D7 work from that
  project's concurrent sessions, and this P5 session's only sibling use is the
  read-only pinned interpreter. No P5 content found in the sibling diff; recorded as
  an attribution observation, not a P5 finding.
- **N-7 (accepted module nuance).** Accepted `tl.validate_run_seed` accepts
  2026091360/2026091361 by design (P4's own frozen seeds); P5 layers them into
  `pg.BANNED_SEEDS` and refuses them (CLI exit 2). Correct layering, no defect.

## Required checks (PASS/FAIL)

### 1. STATUS edit exactness — PASS

Exact command: `cat .workbuddy/queue/NBPOLAR-PHASE4-P5-HARD-CONDITIONING-PENALTY/STATUS.yaml`.
Raw content: `documentation_authorized: true`, `implementation_authorized: true`,
`decoder_execution_authorized: true`, `development_gate_authorized: true`;
`artifact_read_authorized: false`, `real_data_authorized: false`,
`scalable_decoder_authorized: false`, `scl_authorized: false`,
`scientific_promotion: false`; `attempts_allowed: 1`, `attempts_used: 0`;
`state: AUTHORIZED_FOR_AUTONOMOUS_PHASE4_P5_HARD_CONDITIONING_PENALTY`;
`next_gate: IMPLEMENTATION_THEN_INDEPENDENT_PRE_EXECUTE_REVIEW`.
The user authorization text ("只开放 documentation、implementation、decoder_execution
和 development_gate") opens exactly those four; no other flag is `true`. The
`state`/`next_gate` pair matches the packet lifecycle (implementation complete, this
review in progress). See N-4/N-5 for shape/declaration notes.

### 2. Frozen identity — FAIL (single docs-only defect B-1); all operative items PASS

- Constants (`penalty_gate.py:65-107`): N=256, epsilon1=0.05, profile `strong`,
  formula `0.02 + 0.36*u1/31` (mean exactly 0.20), K1=45, K2=140,
  seeds `(2026091470, 2026091471, 2026091472)`, 128 blocks/seed, 384 pairs,
  offset 10000, floor 0.30, oracle-exact min 365, L threshold 0.30, target 0.05,
  tag 64 bits, `FULLY_INVOKED_ARM_BITS=989`, RSS 2147483648, wall 3600.0.
- Exact command identity: extracted code block from `TASK_PACKET.md` (lines 18-22),
  `P5_FREEZE.md` (lines 245-249) and the module constant are byte-identical:
  `packet==freeze: True`, `packet==module: True`, 414 bytes each, sha256
  `a5b66f7ffc479bb2b252266f9b0d3bfd487bc46bf30304ce07305b8803116ed8`.
  Parses: `build_parser().parse_args` accepts the exact token tail; my CLI smoke ran
  the same `-m` path under `ulimit -v 2097152` (exit 0).
- Output root `.workbuddy/queue/NBPOLAR-PHASE4-P5-HARD-CONDITIONING-PENALTY/paired_penalty_gate/`
  `test -e ... => ABSENT` before and after this review; parent contains only the 7
  packet docs (now 8 with this review).
- Seed validator: `pg.BANNED_SEEDS` == the 29 declared values
  (`2026091200..2026091213`, `2026091314..2026091321`, `2026091330`, `2026091340`,
  `2026091341`, `2026091350`, `2026091351`, `2026091360`, `2026091361`) exactly;
  frozen seeds and their masters are not banned; CLI refuses 2026091360/2026091200
  (exit 2, root not created); `tl.validate_run_seed` accepts 1470..1472.
- Freshness: `for v in 2026091470 2026091471 2026091472 2026092470 2026092471
  2026092472 2026101470 2026101471 2026101472; do git grep -l "$v" HEAD; done` →
  zero matches for all nine. Worktree scan (`rg -l` same set, excluding .git) → only
  the P5 packet docs, `penalty_gate.py`, `test_nbpolar_penalty_gate.py`, and the P5
  delta spec.
- D1/D2: independently recomputed `sorted(analytic_order(0.05,256)[:45])` and
  `sorted(analytic_order(0.20,256)[:140])`; both exactly equal `tl.frozen_disclosure_sets`
  and the two lists printed in `P5_FREEZE.md:75-91` (45/140 entries, strictly
  increasing). D2 uses the profile mean 0.20 as declared.
- B-1: masters. Code/derived = `[2026101470, 2026101471, 2026101472]` (my smoke run
  with seed 2026091490 recorded `toeplitz_masters: [2026101490]`); corrected masters
  pass `tl.validate_toeplitz_master` and generate 2623-bit seeds. Freeze/notes list
  `2026092470..72` (seed+1000) — wrong; see Blocking Issues.

### 3. Dependent model — PASS

- Table construction (`penalty_gate.py:231-254`): literal per-high kernel
  `ph[high,bh] * pl_{e2(high)}[al,bl]`; independent rebuild (own kernel loops and own
  1024x1024 assembly) is **bitwise identical** to the module table; max column-sum
  deviation `3.774758283725532e-15 <= 1e-12` (module and independent agree exactly;
  freeze states the same value; never renormalized).
- `p2_maxdiff`: module `pg.p2_cross_u1_maxdiff(tl.layer_metric_tables(table)[1])` =
  `0.34875000000000267` (hex `0x1.651eb851eb882p-2`), exactly equal to X02's persisted
  strong value. Independent all-pairs double loop over 496 (u1,u1') pairs →
  `0.34875000000000267` (difference 0.0). Closed form `0.36*31/32 = 0.34875`.
  Floor: `require_p2_maxdiff(0.34875)` passes; `0.2999999` raises before any decode;
  weak/medium `0.11625000000000252` / `0.2325000000000006` `< 0.30` (both X02-exact).
- Literal formula: `P2[u1,32*bh+bl,u2] == Pl_{e2(u1)}[u2,bl]` max deviation
  `2.1094237467877974e-15` (test tolerance 1e-12 passes; see N-2).
- Sampler (`penalty_gate.py:282-309`): literal independent reimplementation of the
  documented draw order (high, low, `B_high` mask + replacements, `B_low` mask with
  `e2[high]` + replacements) is exactly array-equal for a fresh seed (4x256 positions);
  determinism exact; different seed differs. Distribution vs generative kernel over
  196,608 positions (24 blocks x 8192): empirical `P(high erased)=0.050308` (z=+0.63
  vs 0.05), per-high low erasure max |z|=1.68 over 32 bins, empirical mean 0.1998 vs
  e2 mean 0.2000; replacements always in GF32 (95-97% differ from the old value as
  expected for uniform replacement). No global RNG (`default_rng` only; source scan).

### 4. Four-cell statistic — PASS

- `classify_cell` (`:312-320`) maps (T,T)->both_exact, (F,T)->oracle_only,
  (T,F)->operational_only, (F,F)->neither; set equals `CELLS`.
- Structural argument: `labels_true = low + 32*high` with digits in 0..31, so
  operational `exact` (tag pass AND label match) implies `op_high_hat == high`.
  Independently verified on 48 op-exact blocks (0/48 violations) in a 64-pair smoke
  and 62/96 in the 96-pair smoke: every op-exact block had
  `p2_hat_probs == p2_true_probs` bitwise and `high_hat == true high`; the accepted
  runner then gives both arms identical L2 SC arguments (same d2/u2_disclosed) and
  same-input determinism, so oracle exact follows. `operational_only == 0` observed in
  4-, 64- and 96-pair smokes; manual `classify_cell` counts equal the summary cells.
- Provenance sets at the frozen point: operational arms `CANDIDATE_CONDITIONED`
  (4/4, 64/64), oracle arms `ORACLE_CONDITIONED` (4/4, 64/64).
- Per-block records are scalar-only: 0 non-scalar fields across block and arm levels;
  arm keys are exactly the 19 frozen keys (`outcome, exact, label_match, tag_pass,
  l1_provenance, l2_provenance, l1_executed, l1_decode_failed, l2_invoked,
  l2_skipped_by_l1_failure, l2_decode_failed, tag_invoked, key_dependent_bits,
  public_control_bits, nonfinite, truth_leak_violation, l1_error_type, l2_error_type,
  wall_s`); no symbols/labels/disclosed values/seed bits anywhere in the five files.

### 5. Discriminator math — PASS

Independent implementation: direct product-sum tail with `math.fsum` and a 200-step
bisection on `P[Bin(384,L) >= X] = 0.05` (tail increasing in L), entirely separate from
`pg.binomial_tail_probability`/`exact_lower_bound`.

```
 X    independent root        coded root              |diff|     tail(coded)-0.05
 1    0.00013356736655250224  0.00013356736655250473  2.5e-18    +9.4e-16
 100  0.22374652237568871     0.22374652237568876     5.6e-17    +9.4e-16
 130  0.2985480937864875      0.2985480937864875      0.0        -2.6e-16
 131  0.30106362808316556     0.30106362808316567     1.1e-16    +2.2e-16
 196  0.46720267271103788     0.46720267271103777     1.1e-16    -1.6e-16
 250  0.6089569617345576      0.6089569617345576      0.0        -3.5e-16
 384  0.99222896570364538     0.99222896570364538     0.0        (root 0.05**(1/384))
```
- Boundary: first X with `L > 0.30` is **131** (L(130)=0.2985480937864875 < 0.30,
  L(131)=0.30106362808316567 > 0.30); tail(0.30,384,131)=0.045430... < 0.05 confirms
  the root sits just above 0.30. Coded monotone nondecreasing in X over X=1..384.
- Edge handling: `exact_lower_bound(0,384) == 0.0`;
  `exact_lower_bound(384,384) == 0.05**(1.0/384)` exactly (0.9922289657036454).
- Thresholds: `oracle_exact >= 365`, `operational_only == 0`, `L > 0.30`, shape 384;
  outcome label logic in `_build_summary` (`:705-710`) matches the packet, with the
  documented shape guard (non-384 runs can never emit CANDIDATE; verified on 2- and
  4-pair smokes -> NOT_CONFIRMED). No binomial interval is applied to the marginal
  difference.

### 6. Integrity gates + accounting — PASS

- All ten gates (`INTEGRITY_GATE_ORDER`, `:110-121`) are persisted as booleans and were
  `true` in every clean smoke (4-, 64-, 96-pair). Failure semantics exercised
  independently: patching `tl._truth_isolation_sentinel -> False` turns
  `operational_truth_leak_zero` false and the label `BLOCKED`; a microsecond budget
  marks `resource_abort`, fails `resource_abort_zero` (multi-stream also fails
  coverage/attempt gates) and yields `BLOCKED` with five files; `p2_maxdiff` below the
  floor raises before any decode (patched `tl.sc_decode` never called); a doctored
  transcript event produces exactly the incremental-vs-recount mismatch
  (`total:key_dependent_bits:1978!=1983`, `operational:...:989!=994`) and an untagged
  event id raises `ValueError`. `undetected` is never success by the accepted outcome
  logic (tag pass and label mismatch -> `undetected`); `nonfinite` and
  `resource_abort` are outcome/flag based.
- Accounting: per fully invoked arm `5*(45+140)+64 = 989`
  (`DISCLOSED_BITS_PER_COORDINATE*(k1+k2)+TAG_BITS`); each tag consumes
  `seed_bits_for(256) = 10*256+63 = 2623` public control bits. Clean 4-pair smoke:
  8 arms, key-dependent total 7912 = 8x989, public total 20984 = 8x2623, 8 tag
  invocations, 24 events; incremental == independent literal recount (0 mismatch).
  Frozen-run projection: 768 arms -> 759552 key-dependent bits, 2014464 public bits,
  768 tags, 2304 events.
- Refusals before any decoder call (patched `tl.sc_decode` raiser, in-process):
  existing root (FileExistsError), banned seeds 1360/1200/1351, duplicate seeds,
  profile `weak`/`bogus`, k1=46, k2=141, n=128, epsilon1=0.10, blocks=0, budget=0 —
  all refuse and never create the target root. CLI: existing root / banned seed /
  wrong profile / wrong k1 / wrong n all exit 2 with explicit stderr and no root
  created; the pre-existing root was left byte-for-byte untouched.

### 7. Bounded re-measurement (non-frozen seed, temp root) — PASS

- CLI under the frozen envelope `bash -c 'ulimit -v 2097152; timeout 300 <pinned
  python> -m ...penalty_gate --n 256 --epsilon1 0.05 --profile strong --k1 45 --k2 140
  --seeds 2026091494 --blocks-per-seed 2 --out-dir /tmp/opencode/p5_review_cli'`:
  exit 0, exactly five files (`frozen_plan.json`, `per_block_paired_outcomes.json`,
  `transcript_accounting.json`, `aggregate_summary.json`, `report.md`), gates all
  true, label NOT_CONFIRMED, X=1, L=0.000133567...
- Module smoke (seed 2026091490, 4 pairs): five files, all ten gates true, 989/2623
  accounting exact, per-block records scalar-only (0 non-scalar fields).
- Cost margin: 64-pair run 6.79 s and 96-pair run 9.79 s -> 0.102-0.106 s/pair ->
  projected 384-pair wall ~39-41 s vs 3600 s (~88x margin). Peak RSS 126-137 MB vs
  2 GiB. No `resource_stop` path is expected at the frozen shape.
- Reviewer risk smoke at the frozen point (fresh seeds 2026091500-1502, 96 pairs,
  temp root): cells `{both_exact: 62, oracle_only: 33, operational_only: 0,
  neither: 1}`; op outcomes {exact 62, verify_failed 34}, oracle {exact 95,
  verify_failed 1}; zero L1/L2 decode failures, zero provenance gaps, zero leak/
  nonfinite; all ten gates true, label NOT_CONFIRMED (96-shape). See N-3.

### 8. Tests — PASS

Pinned interpreter, `-q -p no:cacheprovider`, fresh `/tmp` basetemps, `PYTHONDONTWRITEBYTECODE=1`:
- `pytest comparison_bench/tests/test_nbpolar_penalty_gate.py -q -p no:cacheprovider
  --basetemp=/tmp/opencode/p5_bt_focused` -> **9 passed** (6.51 s).
- All 14 `comparison_bench/tests/test_nbpolar_*.py` files ->
  **201 passed** (102.70 s), i.e. 9 new + 192 predecessors, as frozen.
- Test file inspection: 9 `test_*` functions cover table/normalization/`p2_maxdiff`/
  floor refusal; sampler determinism + literal draw order; four-cell classifier +
  structural impossibility; exact lower bound vs independent direct product-sum,
  residuals, monotonicity, edges; integrity gates and failure paths (truth-leak,
  budget abort, pre-decoder floor refusal); CLI refusals without decoder calls;
  five-file scalar-only schema and accounting; frozen constants/seed sets; forbidden
  markers/import-time effects. Test draws use fresh seeds 2026091480..85 only; the
  frozen seeds appear only in argparse/constant assertions (grep), and no
  `default_rng(<frozen seed>)` exists.

### 9. Scope / premises — PASS

- `git status --porcelain` = 55 entries before and after review (unchanged).
  Operator-window writes (`find ... -newermt 17:12:00 ! -newermt 17:22:00`) are exactly:
  `penalty_gate.py`, `test_nbpolar_penalty_gate.py`, `P5_FREEZE.md`,
  `P5_IMPLEMENTATION_NOTES.md`, `p0/specs/nbpolar-phase4-p5/spec.md`, `p0/tasks.md`,
  and `STATUS.yaml` — the declared set. The other dirty files were written earlier
  (pre-implementation packet prep 17:04-17:06: packet docs, `AGENT_PROJECT_MEMORY.md`,
  `CURRENT_TASK.md`, `docs/decision-log.md`, `DOCUMENT_INDEX.md`, X01 STATUS) or are
  pre-existing changes from prior sessions; none attributable to the operator outside
  the declared set.
- Accepted modules untouched: mtimes of `two_layer.py` (12:59), `prior.py`, `sc.py`,
  `transform.py`, `construction.py` (2026-09-12), `protocol.py` (02:13),
  `__init__.py` (10:41), `test_nbpolar_two_layer.py` (13:06) all predate the P5
  implementation window; no import-time mutation.
- No writes: `find results comparison_bench/outputs_comparison workspace/probes
  -newermt "2026-09-13 16:55"` -> nothing; all five named old evidence roots ->
  0 files newer. Sibling: only read-only interpreter use by P5 (see N-6).
- HEAD unchanged (`ab173f2a...`), no commit/push (`git reflog` single clone entry).
  Gate root still ABSENT; `attempts_used` still 0; no gate seed was ever passed to the
  runner.

## Frozen record (verified)

| item | value |
|---|---|
| point | GF32 poly basis (poly 37, alpha 2, natural), N=256, epsilon1=0.05, strong `epsilon2(u1)=0.02+0.36*u1/31` (mean 0.20), K1=45, K2=140 |
| model | `P(B|A)=Ph(B_high|high)*Pl(B_low|low,high)`, q=32 marked erasure, column dev 3.774758283725532e-15 <= 1e-12; `p2_maxdiff=0.34875000000000267` (floor 0.30; X02-identical) |
| D sets | D1=45 coords, D2=140 coords, both byte-identical to freeze lists and `tl.frozen_disclosure_sets` (D2 at mean epsilon2=0.20) |
| seeds | streams 2026091470..2026091472, 128 paired blocks each, 384 pairs, one attempt; public masters `seed+10000` = 2026101470..2026101472 (freeze doc lists 2026092470..72 -> B-1) |
| command | 3 lines, 414 bytes, sha256 a5b66f7ffc479bb2b252266f9b0d3bfd487bc46bf30304ce07305b8803116ed8; byte-identical TASK_PACKET / P5_FREEZE / module constant; parses; ulimit/timeout envelope smoke-tested |
| root | `.workbuddy/.../paired_penalty_gate/` ABSENT now; CLI refuses existing roots before any decoder call; five files created only after the run |
| budget | wall 3600 s internal + external `timeout 3600`, 2 GiB address space (`ulimit -v 2097152`), rss cap 2147483648; projected 384-pair wall ~40 s |
| schema | exactly 5 compact files; per-block records scalar-only; no symbols/labels/disclosed values/seed bits persisted |
| gates | ten gates persisted as booleans in `INTEGRITY_GATE_ORDER`; all pass in clean smokes; fail-closed semantics verified |
| discriminator | `oracle_exact>=365`, `operational_only==0`, `L>0.30` with X=oracle_only and L the exact one-sided 95% lower bound root (X=0 -> 0.0, X=384 -> 0.05**(1/384)); first discriminating X=131; `CANDIDATE` iff all gates + discriminator + shape 384 |

## Closure statements

- The real 384-pair gate command was **not run**; no execution with the frozen seeds
  occurred in this review (only non-frozen seeds 2026091490-1502 in `/tmp` roots and
  the focused/full test suites).
- `attempts_used` is still **0**; the single attempt remains unconsumed.
- The gate output root `.workbuddy/queue/NBPOLAR-PHASE4-P5-HARD-CONDITIONING-PENALTY/paired_penalty_gate/`
  is still **ABSENT** after this review (checked last at review close).
- No commit, no push, no staging; HEAD `ab173f2a...` unchanged; nothing outside this
  review file was written by the reviewer.
- After the docs-only B-1 repair, re-review is limited to `P5_FREEZE.md:102` and
  `P5_IMPLEMENTATION_NOTES.md:122`; all other items above remain valid because no code
  or test file changes.
