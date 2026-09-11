# EXPLORATION_NOTES — NBPOLAR-PHASE2-SC-ORACLE

## 1. Recursion/data-structure alternatives considered

- **Alt A (selected): pure recursive segment function.** `decode_segment(block, offset)`
  operates on contiguous `(m, q)` metric blocks: split into halves, vectorized
  minus over pairs `(row_j, row_{j+m})`, recurse left, re-encode left decisions
  with the accepted `polar_transform`, vectorized plus conditioned on the
  result, recurse right. Leaf decisions in natural index order; known
  coordinates forced through a position→value dict at the leaf only.
- **Alt B (rejected): explicit node-object tree** with parent/child pointers,
  per-node cached metric buffers and combination-index tables, iterative stack
  traversal. Same algebra, roughly 3× the code, manual stack discipline risks
  stage-order bugs, and zero benefit at reference scale (N≤64). Failure
  attribution still lands on the same five layers, so the objects add no
  diagnostic value.
- **Index-table alternative:** per-element `field.add/mul` calls inside the
  `q×q` inner loops vs one precomputed `(q,q)` combination index
  `index[u,v] = u + alpha*v` per decode. Selected the single table (O(q²)
  validated field ops once); all inner loops are NumPy. Per-element calls
  were rejected (noisier, slower, no readability gain).

## 2. Selected design and natural-order match

`G_N = F_alpha^{⊗n}` with the row-vector kernel `x0 = u0 + alpha*u1`,
`x1 = u1` factors contiguous halves: top node pairs `(row_j, row_{j+m})`,
left subtree decodes the first-half U segment, right the second half, and
the node result is their concatenation in natural order — no permutation,
no bit reversal. A throwaway probe (60 random GF4 N=4 + 25 random GF32 N=2
metrics, `/tmp/opencode/p2_probe.py`, not a repo file) matched every leaf
decision row against brute-force enumeration to ≤4.5e-16 probability /
≤3.6e-15 log error with zero support mismatches before any production file
was written, confirming orientation, kernel direction, and concat order.

## 3. Partial sums: representation and proof

Partial sums are the re-encoded left decision segment
`beta = polar_transform(u_hat[offset:offset+half])` (length-m vector over
the same field/alpha), used as `plus[v] = L0[beta_j + alpha*v] + L1[v]`.
Using raw left U decisions instead is a demonstrated-wrong variant, not an
equivalent one: the frozen GF4 N=4 discriminator
(`test_partial_sum_discriminator`) has `u_left = [0,3]` but
`beta = [1,3]`; the raw-beta U_2 conditional misses the oracle by 0.32 in
probability and picks symbol 2 instead of 1, while the production row
matches to 1.1e-16. Correctness also follows from the end-to-end oracle
agreement (221 comparisons, max 3.4e-16) plus 831/831 noiseless loopback.

## 4. Oracle independence argument

`oracle.py` imports only `polar_transform_reference` (accepted Phase 1)
plus `numpy`/`itertools`. It shares no code with `sc.py`: no recursion,
no minus/plus helpers, no partial-sum helpers, no validation/normalization
routines, no decision logic. Its logsumexp is max-subtraction with an
explicit `-inf` guard; production uses `np.logaddexp.reduce`. Enumeration
is literal — every full U candidate is transformed with the dense
reference and scored `sum_j logp_x[j, X_j]`, then aggregated by candidate
`U_i`. The forbidden-coupling test asserts the absence of `sc` imports
and of `_minus_block`/`_plus_block` in the oracle source. Enumeration is
capped at 4096 candidates so N=64 can never enter it accidentally.

## 5. Numerical normalization and exact-zero policy

Production validates (2-D, `(N,q)` with `N = 2**k`, `q == field.q`, no
NaN, no `+inf`, every row with finite support) then explicitly normalizes
each row with `logsumexp == 0`; every internal minus/plus output is
re-normalized. `-inf` is exact-zero support end to end: preserved through
gather/add/`logaddexp`, never floored, never uniform-filled. Invalid rows
raise (`metric contract`); a forced value landing on `-inf` raises
`ImpossibleDisclosedValueError`; internal NaN raises
`NumericNonfiniteError`. Support-consistency note: a forced leaf that
passes (finite conditional) implies positive joint mass for its prefix,
so all later exact conditionals are normalizable — through the public API
a support contradiction always surfaces as impossible-disclosed-value,
and the numeric category guards internal arithmetic (unit-tested
directly). No `final_beliefs`/`APP` field exists anywhere.

## 6. First meaningful mismatch and layer identification

During probing, an intermediate plus-input row was compared directly
against the U-coordinate oracle row and differed by 0.56 — briefly
suspecting a kernel-orientation bug. Classification per packet §7 showed
production and oracle already agreed at every leaf (240/240 cases); the
error was probe-side: plus outputs feed the right subtree, which applies
its own minus recursion before reaching a U coordinate, so internal node
inputs are never comparable to leaf conditionals. No production edit was
needed; the final suite compares only leaf decision rows. A second
incident was test-side: the suite helper used max-normalization while the
surprisal test needs the packet's logsumexp contract (chain −7.848 vs
block −4.964, exactly the missing global log-partition). Fixed by giving
the helper true logsumexp normalization. A third was a wrong hand-derived
test expectation (one-hot X=[1,1,1,1] decodes to U=[2,1,3,1], not
[1,1,1,1]); corrected to compute the expectation with the accepted
transform. A 0/20000 correction-search drought was cleared the same way:
oracle agreement on the failing trials proved the decoder exact and the
construction merely hard (packet §7: poor hard decode is not a Phase 2
defect), then a wider-contrast search froze the T1-06 witness.

## 7. Phase 1 issues

None found. `algebra.py` and `transform.py` are unmodified (verified via
`git status`: only `__init__.py` gains Phase 2 exports). N=1 (documented
Phase 1 limitation, identity code path) is now exercised by
`test_n1_identity` through the SC/oracle pair. The generic-alpha note
stands: production accepts any valid symbol alpha but every test uses the
frozen alpha=2.

## 8. N=64 sanity and why no optimization was added

GF32 N=64: one-hot noiseless decode 0.004 s, finite asymmetric decode
0.009 s (plain-Python runner, WSL venv). Shapes: `decision_metrics`
`(64,32)` throughout, peak extra block `(32,32,32)` ≈ 256 KiB. Reference
complexity `O(N q² log N)` NumPy ops plus `O(N log² N)` field ops for
partial sums. No optimization added: 30 s warning threshold is cleared by
three orders of magnitude and any table/convolution work belongs to a
later phase behind reference-equivalence tests.
