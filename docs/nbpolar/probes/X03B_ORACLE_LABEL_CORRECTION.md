# X03b — oracle-label correction (Tier-X delta successor)

Question: with accepted P5 oracle semantics restored, how much of the
hard-to-oracle exact-recovery gap is closed by the Bob-marginal L2 prior?

## Inherited unchanged from X03

GF32/N256; epsilon1=0.05; strong
`epsilon2(u1)=0.02+0.36*u1/31`; K1=45; K2=140; seeds
`2026091490..2026091494`; 128 common blocks/seed; public master=`seed+10000`;
the same sampling order, P1/P2 tables, D1/D2, tag/accounting, hard arm,
Bob-marginal formula and `PRIOR_ONLY` truth-isolation contract.

## Only semantic delta

- hard final label: `low_hat_hard + 32*high_hat`;
- marginal final label: `low_hat_marginal + 32*high_hat`;
- oracle final label: **`low_hat_oracle + 32*high_true`**.

The oracle L2 metric remains `ORACLE_CONDITIONED`. Alice `high_true` is allowed
only in this labelled diagnostic arm and scoring. It must not enter hard or
marginal metrics, decisions or labels.

## Output and reporting

Write exactly `prereg.md` and `results.json` under
`workspace/probes/nbpolar_x03b_oracle_label_correction/`. The preregistration
must precede every decoder call and contain the complete executed body.

Persist one scalar record per `(seed,block)` containing only: seed, block index,
`high_candidate_correct`, exact/outcome for hard/marginal/oracle, the three
paired-cell labels, key-dependent/public-control counts, truth-isolation flags,
and metric-difference scalars. Persist no source/candidate/decoded vectors,
labels, tags or raw seed bits.

Report per seed and pooled:

- all three outcome totals;
- hard-vs-marginal, hard-vs-oracle and marginal-vs-oracle four-cell tables;
- `gap_closed=(marginal_exact-hard_exact)/(oracle_exact-hard_exact)`, null only
  when its denominator is zero;
- `max|P2_marginal-direct_joint_marginal|`;
- `max|P2_marginal-P2_true_conditioned|` and fraction of rows differing by
  more than 1e-12;
- disclosure/control recount and truth-isolation violations.

One independent reviewer-go focused review must reconstruct the oracle label
contract, all paired cells, gap arithmetic and at least one full seed.

This is a Tier-X correction, not a rerun of or edit to X03. No production edit,
threshold/pass-fail, candidate/accepted token, attempt, artifact/real data,
APP/SCL/FWHT, old-root modification, per-probe ledger/memory update,
qualification/promotion, commit or push. Record all execution errors without
changing inherited parameters or the single delta.
