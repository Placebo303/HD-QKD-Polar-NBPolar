# NB-Polar static reconciliation protocol requirements

## Requirement: Static disclosure is explicit

The implementation SHALL publish one frozen set of GF32 coordinate/value
pairs. Zero SHALL be a valid disclosed value and SHALL remain distinguishable
from an undisclosed coordinate.

## Requirement: Reconstruction and verification are fail closed

The implementation SHALL reconstruct the complete source label vector before
one final 64-bit Toeplitz verification. Verification SHALL NOT choose, retry or
modify a decoder path. A verified non-exact result SHALL be `undetected` and
SHALL NOT count as success.

## Requirement: Disclosure is independently recountable

The transcript SHALL separate key-dependent GF32 values, the key-dependent
verification tag and public Toeplitz seed material. The persisted total SHALL
equal an independent event recount exactly.

## Requirement: Evidence stays synthetic and bounded

The first development run SHALL contain exactly 300 frozen synthetic blocks
and SHALL make no real-data, FER-qualification, leakage-efficiency, key-rate or
performance claim.
