# NB-Polar track

## Status

This worktree is the independent NB-Polar planning and implementation checkout.
Phases 1-2 are implementation-accepted and Phase 3-R1 has one bounded accepted
synthetic diagnostic (O3, eps=0.05, K45, seed 2026091213, 299/300 exact).
Phase 4-P0 is prepared but not authorized; no Model-F run, real-data run,
qualification, or promotion exists here.

The first implementation target is a native GF(32) source-polarization code:

```text
q = 32
polynomial basis, primitive polynomial 0b100101 = 37
alpha = 2
F_alpha = [[1, 0], [alpha, 1]] over GF(32)
G_N = F_alpha tensor_power n, N = 2**n
log metric shape = (N, 32), probability axis last
decoder = q-ary SC, log-domain, ordinary hard decision
```

The QKD symbol dimension and Polar alphabet are deliberately separate:

```text
d = 1024 physical labels
A = 32*high + low, high/low in GF(32)
N = Polar symbols per block
physical input size = 10*N bits
```

`high` and `low` are the current Model-F packing control. They do not define a
GF(1024) field multiplication and do not inherit the old two-layer NB-LDPC
mother or BP graph.

## Ownership boundary

All new NB-Polar code, tests, configurations, comparison adapters, and future
results belong in this worktree's `comparison_bench/` layer. Do not modify the
binary Polar implementation or result roots in
`../HD-QKD_Polar_Release`. Do not turn the historical NB-LDPC matrices,
graphs, schedules, or decoder results into NB-Polar dependencies.

The Comparison checkout remains the source of historical NB-LDPC evidence and
durable route decisions. Its old `formal-ir-future-nbpolar-app-transfer`
proposal is archived as a superseded draft because it made a hybrid NB-LDPC
dependency the entry gate. The new track starts with an independent native
GF32 Polar golden path. A hybrid NB-LDPC adapter is outside the MVP and
requires a separate change after the native route has passed its gates.

## Core scientific contract

Alice has `A^N` and Bob has `B^N`. Alice computes `U^N = A^N G_N` and reveals
the selected high-conditional-entropy coordinates with their actual
symbol values, including zero when that is the disclosed value. Bob runs SC
using `P(A_j | B_j)` or an explicitly conditioned
metric, reconstructs `A_hat^N`, and only then performs one independent full-
symbol verification tag. A disclosed coordinate is not a communication-code
zero frozen bit.

The operational metric is a normalized log probability:

```text
logp_x[j,a] = ln P(A_j=a | Bob/context)
shape       = (N,q)
logsumexp(logp_x[j,:]) = 0
```

SC decision scores are path-conditionals. They must carry provenance and must
not be relabelled as a full symbol APP or fed into the old NB-LDPC `q @ P`
bridge.

## What is already known

- `GF2mField`, GF32 polynomial-37 arithmetic, field preflight, empirical
  `counts_ab`, Model-F concentration smoothing, and `(N,q)` probability
  conventions are valuable Comparison assets.
- Release supplies arbitrary frozen-value handling, ordinary SCL path-state
  ideas, sidecar statistics, leakage accounting, and random Toeplitz
  verification.
- D7-A's independent arithmetic oracle and D7-B/C metric/provenance separation
  are reusable validation patterns.
- D5/D6/D7 do not justify transferring an LDPC graph, BP schedule, mother,
  row-prefix disclosure, or a conclusion that NB-LDPC/GF32 is generally
  ineffective.

The detailed mapping and the phase gates are in `ASSET_MAP.md`,
`ARCHITECTURE.md`, and `ROADMAP.md`.
