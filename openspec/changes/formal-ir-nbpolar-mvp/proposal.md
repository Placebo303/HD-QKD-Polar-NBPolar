# NB-Polar MVP source-reconciliation track

## Status

`PLAN_CANDIDATE / IMPLEMENTATION_NOT_AUTHORIZED / EXECUTE_NOT_AUTHORIZED`

## Problem

The repository has useful GF32 arithmetic, empirical QKD symbol statistics,
prior adapters, and binary Polar protocol patterns, but no native q-ary Polar
transform, construction, or decoder. The earlier APP-transfer draft made a
hybrid NB-LDPC dependency the entry gate and did not isolate transform,
construction, prior, decoder, and protocol failures.

## Proposal

Create an independent Comparison-layer NB-Polar method beginning with a
GF(32), alpha=2, 2x2 kernel and a reference log-domain q-ary SC source decoder.
The first implementation covers the mathematical contract, transform, tiny
oracle and synthetic loopback only. Model-F, reconciliation and performance
runs are later phases with separate gates.

## Scope

- GF32 polynomial-basis arithmetic adapter, `poly=37`;
- `F_alpha=[[1,0],[2,1]]` and `G_N=F_alpha**tensor n`;
- source-polarization coordinate semantics and actual disclosed values,
  including arbitrary zero or non-zero symbols;
- normalized `(N,q)` log metrics and metric provenance;
- independent tiny enumerator and reference SC;
- documentation, focused tests and no production result output.

Out of scope: Release changes, LDPC graph/mother reuse, CRC-aided SCL,
puncturing/shortening, adaptive real-data runs, joint APP decoding and any
qualification or promotion claim.

## Source of truth

The detailed contracts are in `docs/nbpolar/ARCHITECTURE.md` and the phase
gates in `docs/nbpolar/ROADMAP.md`. This change is not an authorization to run
decoder or real-data work.
