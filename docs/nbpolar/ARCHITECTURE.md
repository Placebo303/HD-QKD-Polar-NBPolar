# NB-Polar software and data architecture

## Algorithm objects

Use a few explicit records rather than a framework:

```text
PolarSpec:
    q, m, primitive_polynomial, alpha, N, index_order

SymbolMetric:
    logp: float64[N,q], normalized on the last axis
    conditioning: Bob/context declaration
    provenance: prior or posterior declaration

Construction:
    entropy_bits[N], error_risk[N], disclosure_order[N], train_provenance

SCResult:
    u_hat[N], x_hat[N], status, decision_logp[N] (optional)
    metric_provenance, known_coordinate_count
```

`FrameBatch` remains the outer input. The decoder receives Bob data and an
explicit metric; it must not receive Alice truth through metadata or a closure.

## Module layout

```text
comparison_bench/src/comparison_bench/
  formal_ir/nbpolar/
    algebra.py          # Polar-neutral GF field adapter and symbol packing
    transform.py        # F_alpha butterfly and inverse/reference transform
    prior.py            # Model-F and synthetic metric adapters
    construction.py     # genie Monte Carlo reliability order
    sc.py               # reference log-domain q-ary SC
    protocol.py         # source disclosure, result and verification flow
  methods/nbpolar.py    # thin IRMethod adapter
```

The first change may keep `algebra.py` thin and import the existing field
arithmetic. Do not move all historical field code merely for naming symmetry.

## Field and transform contract

For row vectors:

```text
[x0, x1] = [u0, u1] F_alpha
x0 = u0 + alpha*u1
x1 = u1
```

Use GF32 polynomial basis, polynomial `37`, and `alpha=2`. The non-zero cycle
has length 31. In characteristic two, `F_alpha` is its own inverse. Use
`G_N = F_alpha tensor_power n` with `N=2**n` and an explicitly tested natural
order; do not inherit Release's hidden bit-reversal convention.

The recursive symbol metric is:

```text
L_minus(u) = logsumexp_v [ L0(u + alpha*v) + L1(v) ]
L_plus(v)  = L0(u_hat + alpha*v) + L1(v)
```

All rows are normalized after each operation. The `plus` recursion uses the
left subtree's encoded partial sums, not an untransformed vector of left-side
decisions.

## Mathematical references

The finite-field polarization condition for the 2x2 kernel is the one stated
by Mori and Tanaka: the kernel parameter must generate the extension field
over its prime field. A primitive alpha=2 in GF32 with polynomial 37 satisfies
that condition; the implementation still proves the claim with the tiny
conditional-entropy tests in the validation packet. See
[Mori and Tanaka, arXiv:1211.5264](https://arxiv.org/abs/1211.5264).

The direct q-ary source/channel formulation and likelihood-ratio-vector SC
decoding follow the source-polarization treatment in
[Bravo-Santos, arXiv:1511.03881](https://arxiv.org/abs/1511.03881). These
references justify the MVP definition, not any finite-length QKD performance
claim.

Phase 0 therefore relies on exactly these two references. Park-Barg is not a
Phase 0 dependency; if Phase 3 construction work later needs it, that review
must add the exact paper identifier and a specific use statement.

## Source reconciliation contract

Alice computes `U = A G_N`. A construction labels coordinates with high
conditional entropy as disclosed coordinates `D`; low-entropy coordinates are
SC-decoded coordinates `I`. Alice sends the actual values `U[D]`. Bob knows
`U[D]`, runs SC in index order, and reconstructs `A_hat = U_hat G_N`.

This is source polarization with side information. It is not channel coding
with zero frozen bits, and it is not a syndrome decoder.

## Prior contract

The only operational metric representation is a normalized float64 log vector
with shape `(N,q)` and probability axis last:

```text
logp[j,a] = ln P(A_j=a | Bob/context)
logsumexp(logp[j,:]) = 0
```

Natural logs are used internally; entropy and disclosure are in bits. Exact
zero support is `-inf`; numerical floors are declared separately from
statistical smoothing. A scalar LLR is insufficient for a GF32 symbol.
Every `1e-12` or `1e-9` numerical gate in the NB-Polar plan is an absolute
maximum-error tolerance, with no relative-tolerance or averaged-norm reading.

For the first Model-F-aligned experiment:

```text
P1 = P(high | B)
P2 = P(low | high, B)
```

L1 uses `P1`. L2 uses a candidate-conditioned prior built from the L1 hard
candidate. An oracle L2 prior using the true high symbol is diagnostic only.
No q-ary SC path metric is relabelled as a complete APP.

## Construction contract

Use a genie traversal on training samples. At coordinate `i`, provide the true
prefix `U_<i` and Bob's full side information, compute the exact conditional
symbol distribution, and record:

```text
h_i = E[-log2 P(U_i_true | U_<i_true, B^N)]
e_i = E[1 - max_a P(U_i=a | U_<i_true, B^N)]
```

Sort disclosure candidates by a frozen risk rule (initially descending `e_i`,
then coordinate index), produce nested sets, and evaluate on disjoint data.
No fixed PW order, rate grid search, or self-trained/self-evaluated sidecar is
accepted as the NB-Polar construction.

## Protocol and leakage

The first protocol publishes one static coordinate set. For GF32:

```text
L_static = 5 * number_of_disclosed_coordinates
L_keydep = L_static + 64
```

Random Toeplitz seed and other public control bits are recorded separately. A
full physical-symbol packing is used for final verification, not a decoder
metric. A verification failure rejects the candidate; it does not select a
new SC/SCL path in the MVP.

## Boundary to existing methods

`methods/nbpolar.py` may implement `IRMethod.run` and wrap the stable
`IRRunResult`, but it must not change the core dataclasses. Existing
`IRRunConfig.max_iter` cannot silently mean Polar list size or depth, and the
comparison default `verify_mode="crc32"` cannot silently become the formal
Toeplitz protocol. Use a dedicated NB-Polar configuration.
