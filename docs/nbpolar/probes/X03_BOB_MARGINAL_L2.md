# X03 — Bob-marginal L2 prior (Tier X)

Question: does a truth-free Bob-marginal prior reduce the accepted P5
hard-candidate penalty enough to justify a later production/Tier-Y change?

Freeze: GF32/N256, epsilon1=0.05, strong
`epsilon2(u1)=0.02+0.36*u1/31`, K1=45, K2=140; seeds
`2026091490..2026091494`; 128 common blocks/seed; public master=`seed+10000`.
Run three arms: hard candidate, Bob-marginal, true-L1 oracle.

Define `P2_marginal[b,u2]=sum_u1 P1[u1,b]*P2[u1,b,u2]` and compare it with
direct marginalization of the injected joint table within 1e-12. Provenance is
`PRIOR_ONLY`; it receives Bob only, never candidate, truth, oracle or APP.

Write exactly `prereg.md` and `results.json` under
`workspace/probes/nbpolar_x03_bob_marginal_l2/`. Report per-seed and aggregate
outcomes, paired cells, accounting, formula error, truth isolation, and the
fraction of the hard-to-oracle exact gap closed by marginal. No pass/fail.

Use only a preregistered in-memory probe body; no production edits. Perform one
focused review. No artifact/real data, old-root write, attempt, threshold,
ledger/memory update, APP/SCL/FWHT, qualification/promotion, commit or push.
