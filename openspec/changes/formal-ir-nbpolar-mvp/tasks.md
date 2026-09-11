# Tasks: NB-Polar MVP

## Freeze and review

- [x] Review `docs/nbpolar/README.md`, `ASSET_MAP.md`, `ARCHITECTURE.md`,
  `ROADMAP.md` and this change as one packet.
- [x] Confirm no Release, frozen baseline, result root or raw input is in
  scope.
- [x] Record one independent numerical review before implementation.

## Phase 0

- [ ] Add the Polar-neutral GF32 spec adapter and explicit 5+5 packing helpers.
- [ ] Add pure-array tests for mapping, field identity, concentration smoothing,
  axes and normalization.

## Phase 1

- [x] Add the GF(q) 2x2 butterfly transform and dense reference comparison.
- [x] Add source-compression coordinate extraction with actual known values,
  including arbitrary zero and non-zero symbols.
- [x] Add exhaustive GF4 and GF32-N=2 transform tests.

## Phase 2

- [x] Add log-domain q-ary SC with partial sums and metric provenance.
- [x] Add independent tiny enumeration for SC conditionals.
- [x] Add noiseless, asymmetric, one-hot, exact-zero and arbitrary frozen-value
  tests.
- [x] Report the stable Phase 0-2 operator return or one exact blocker. Do not
  start Model-F, real data, SCL or performance scans automatically.

## Acceptance

- [ ] Mapping and prior checks meet `1e-12` absolute tolerance.
- [x] Transform and inverse have zero mismatches.
- [x] Noiseless SC exact recovery is 100%.
- [x] Tiny SC conditional metrics meet `1e-12`; finite log-score checks meet
  `1e-9`; no Alice truth reaches the decoder.
- [x] Independent review passes; no result or qualification claim is made.
