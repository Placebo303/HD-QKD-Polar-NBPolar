# Tasks: L2 Representation & Disclosure-Placement Redesign (all NOT AUTHORIZED — scoping skeleton only)

Every box is unchecked. Every task carries `[GATE — NOT AUTHORIZED]`.
No task may execute, freeze, or authorize anything under this scoping.

- [ ] B1 — Proposal review (this change). Confirm proposal/design/tasks encode the strategy
  stop rule (no add-N), the honest-scope boundaries (synthetic-only descriptive; real-data
  gate not reopened; no FER/reliability claims), the ranked axes (i)–(iv), and the SCL-lock
  posture. [GATE — NOT AUTHORIZED]
- [ ] B2 — Axis-selection decision (main thread). Select the FIRST axis and candidate for the
  freeze: default C-P1 (axis i, placement minimum-delta at the G3 triple); alternatives C-P2
  (axis ii, tiered amount/structure) or C-P3 (axis iii, structured prior re-estimation with
  Q5 as the first Tier-X probe). Record the selection reason. [GATE — NOT AUTHORIZED]
- [ ] B3 — Freeze review. Independent review of the frozen first-axis packet: selected
  candidate with differ-from-all-proven-pointless proof (X14 flat/N=256, X15 d=0.75/N=256,
  X16 d=0.75/N=32768 first-natural, G3 d=0.90/N=16384 first-natural); ceiling-margin
  arithmetic re-shown at freeze (M ≥ 50 × recorded max |Δ|, currently 0.00099 → M ≥ 0.0495);
  disclosure-set / tier / prior freeze; seed/tag grep proof; 3-line prereg text; stop tokens
  incl. ceiling-hugging stop and wiring stops. [GATE — NOT AUTHORIZED]
- [ ] B4 — Implementation authorization. Explicit user authorization to create the probe body
  only (new files under `workspace/probes/<id>/` and the packet dir; caller-side disclosure
  placement/amount injection; zero edits to `formal_ir/nbpolar/` existing modules incl.
  `sc.py`; zero protected opens; zero data contact). [GATE — NOT AUTHORIZED]
- [ ] B5 — Focused tests. T0/T1 green: placement-injection smoke (disclosed-set sizes exact),
  order-identity under shuffled `known_positions`, ceiling-arithmetic assert, wiring/gate
  asserts, path-refusal asserts (no protected imports); full NB-Polar suite green. T2 at
  milestones only. [GATE — NOT AUTHORIZED]
- [ ] B6 — Single synthetic execution. One frozen-command Tier-X run under single-thread pins;
  probe-root-only writes; `results.json` scalar-only (< 2 MB) with per-seed values +
  mean/sample-std(n−1)/range; `decoder_calls`/`rng_calls`/`tag_calls` recorded; zero protected
  opens; execution-error-only single recorded rerun. [GATE — NOT AUTHORIZED]
- [ ] B7 — Focused numerical review. Independent reviewer-go Tier-X review (commands,
  completeness, arithmetic, truth isolation, write scope, ceiling-band reading against the
  frozen edges). No Pre-EXECUTE/Pre-RESULT (Tier-X rule). [GATE — NOT AUTHORIZED]
- [ ] B8 — Acceptance + axis decision. Main-thread acceptance of descriptive readings; apply
  design (c): in-band → next ranked question on the axis + SCL-track re-freeze candidacy
  (never automatic); above-high → retire axis, forced switch at 2 probes/axis; below-low →
  degenerate note; record Q5 disposition (activated as this route's first Tier-X probe only
  if axis (iii) was selected at B2; otherwise stays retired-conditional). If all axes (i)–(iii)
  retire within budget → forced return to the user-owned exhaustion-route decision. No
  FER/reliability/efficiency claim; no real-data follow-on; SCL lock status re-stated.
  [GATE — NOT AUTHORIZED]

Notes: B1 is this scoping. B2 is the single main-thread decision this scoping hands back.
B3..B8 are placeholders for the separately-gated future route. Small-task fast path is NOT
claimed: an axis freeze plus probe body needs the full gate sequence above.
