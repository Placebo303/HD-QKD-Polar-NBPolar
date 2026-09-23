# Stage-3 deferral: discriminative-power note (paper-only — authorizes nothing)

- `EXPLORATION_ONLY / DOCS_ONLY` — this note performs **no computation** and
  **authorizes no code, no run, no freeze change, no frozen-constant change, no
  data access, no Tier-X probe run, and no Tier-Y decision gate**.
- Subject: the Stage-3 gate of the archived change
  (`openspec/changes/archive/2026-09-22-nbpolar-prior-rebaseline/`, design D6
  measurement set; drafted packet
  `.workbuddy/queue/NBPOLAR-M2-PRIOR-STAGE3-MEASUREMENT/`, stage PACKET_DRAFT,
  `authorizations: []` — reference only, never modified).
- Any Stage-3 re-entry needs its own freeze, its own packet, independent
  Pre-EXECUTE/Pre-RESULT reviews, and verbatim user authorization (see §4).

## §1 Cap structure as drafted

- The drafted cap is a closed-form scalar bound `cap = f_scalar · N · H_total`
  tied to frozen constants (N=32768; f(6811)=1.2747449 as the scalar source;
  H_total from a frozen entropy source), compared per-block against frozen
  accounting columns under a TO-FREEZE comparison caliber.
- The per-block accounting columns are the frozen disclosure decomposition
  (key-dependent / public-control / CAL-handling / reveal-bits diagnostic /
  tag record, with `undetected` 0/42 isolated and never summed).

## §2 Degeneracy derivation (paper-only; no computation performed)

- Per-block `key_dependent_bits = 34,119 = 5·(K1+K2)+64` with K1=319, K2=6492
  is a per-row constant with zero variance; `public_control_bits = 327,743`
  is likewise a per-row constant; `undetected` 0/42 is isolated and never
  enters any total.
- With λ per-row constant, the cap comparison degenerates into a construction
  identity: the two sides differ only by the frozen arithmetic, so the gate's
  output carries zero bits of hypothesis information (zero discriminative
  power).
- Running the gate now would produce a verdict-shaped artifact that cannot
  discriminate any hypothesis. Deferral is therefore the minimal action: no
  gate edit, no constant move.

## §3 Conditions that restore discriminative power (stated; none selected)

- (i) Non-constant λ: the per-block disclosure would need to vary
  block-to-block (e.g. a disclosure component that is genuinely
  block-dependent rather than fixed by the frozen arithmetic), so that the
  comparison has something to discriminate. This would require a future design
  whose accounting columns carry real per-block variation under their own
  freeze — a different measurement object from the drafted one, not an edit
  to it.
- (ii) A non-identical construction comparison: the cap would need to be
  constructed independently of the accounting arithmetic it is compared
  against (e.g. a bound from a separate frozen source with its own
  provenance), so that agreement or disagreement is informative rather than
  algebraic. This would require a future design that names the independent
  source, its derivation path, and the comparison caliber under its own
  freeze — again a new object, not a patch to the drafted packet.

## §4 Deferral is not abolition: re-entry conditions

- Re-entry needs its own freeze, its own packet, independent
  Pre-EXECUTE/Pre-RESULT reviews, and verbatim user authorization.
- The drafted packet stays PACKET_DRAFT with `authorizations: []`; it is
  reference only and is never modified by this note.

## §5 No-claim box

- No computation performed, no constant moved, no gate edited.
- No FER statement, no efficiency statement, no promotion statement, no
  qualification statement, no composable-key statement.
- Frozen numbers above (N=32768; K1=319; K2=6492; 34,119 = 5·(K1+K2)+64;
  327,743; undetected 0/42; f(6811)=1.2747449) are verbatim provenance
  context, not results.
