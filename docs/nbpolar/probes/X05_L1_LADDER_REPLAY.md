# X05 — L1 ladder replay and schedule Pareto (Tier X)

Question: which adaptive hard-L1 disclosure schedule gives the best observed
end-to-end recovery/leakage tradeoff on the already decoded X04 blocks?

## Frozen input and scope

Read only
`workspace/probes/nbpolar_x04_l1_disclosure_pareto/results.json`. Do not call a
decoder, generate blocks/tags, or alter X04. Require its recorded shape to be
five streams x 128 blocks x six K1 values, with
`K1=[45,52,60,72,88,112]`, `K2=140`, no duplicate `(stream,block,K1)` rows,
and its recorded undetected/nonfinite/decode-failure/resource-abort and
truth-isolation violation totals all zero. A mismatch stops the replay.

Enumerate every increasing schedule that starts at K1=45 and ends at any member
of the frozen grid. Intermediate grid points are optional. This gives exactly
32 schedules. A block visits stages in order and stops at its first recorded
hard-arm exact outcome; otherwise it exhausts the schedule and fails. This is
a deterministic planning replay of X04 scalar outcomes, not a new protocol
execution or evidence that skipped stages would reproduce identical tags.

## Frozen accounting

For a block stopping/exhausting at stage `j` with terminal prefix `K_j`:

- L1+L2 disclosure: `5*(K_j+140)` key-dependent bits;
- verification: `64*j` key-dependent bits, where stages are one-based and
  every visited X04 row had a tag invocation;
- feedback: `j-1` public bits;
- tag seed/control: `2623*j` public bits;
- total public control: `2623*j+(j-1)`.

Thus key-dependent bits are `5*(K_j+140)+64*j`. Count the L2 disclosure only
once. Independently recount every schedule from its per-block replay records.
Use the exact X04 frozen entropy value for planning-only average
`f=mean_key_dependent/(256*(H1+H2))`.

## Required output

Before reading X04 records, write `prereg.md` containing the complete
postprocessor body. Write exactly `prereg.md` and `results.json` under
`workspace/probes/nbpolar_x05_l1_ladder_replay/`.

Persist, for each schedule and each `(stream,block)`, only the schedule ID,
terminal K1, levels/tags/feedback invoked, exact/failure outcome and the four
accounting totals. Also report:

- per-stream and pooled exact/failure counts for all 32 schedules;
- mean/total key-dependent and public-control bits, planning-only f, terminal
  K1 histogram, levels/tag histogram and feedback totals;
- static one-stage schedules `[45]`, `[52]`, `[60]`, `[72]`, `[88]`, `[112]`
  reconstructed directly from X04 as named comparison rows (only `[45]` is
  part of the 32 adaptive schedules);
- the nondominated frontier under maximizing exact and minimizing mean
  key-dependent bits; ties must remain visible;
- for schedules ending at 112, the minimum-mean-key schedule and its absolute
  and percentage savings versus static `[112]`;
- record-count, input-integrity and independent-recount mismatches.

Do not impose a success threshold or select a production schedule. The next
main-thread decision will use this frontier to either freeze a Tier-Y adaptive
hard-L1 gate or decline it in favor of a separately proposed soft/list route.

An independent reviewer-go focused review must independently parse X04,
reconstruct all 32 schedules and static rows, verify the frontier and accounting
formula, and report any mismatch. Its result is trusted under AGENTS.md section
4.1.

This is decoder-free Tier X: no production edit, decoder/RNG/tag invocation,
attempt/seed consumption, threshold/pass-fail/candidate/accepted token,
artifact/real data, APP/SCL/FWHT, old-root modification, per-probe
decision-log/index/memory update, qualification/promotion, commit or push.
