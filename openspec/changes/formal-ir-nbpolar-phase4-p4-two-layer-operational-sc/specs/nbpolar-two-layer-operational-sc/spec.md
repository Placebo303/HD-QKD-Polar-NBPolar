# Two-layer operational SC requirements

## Requirement: causal candidate conditioning

Operational L2 SHALL condition only on Bob and the hard source-domain L1
candidate returned by L1 SC. Alice truth SHALL NOT affect this metric.

## Requirement: isolated oracle comparator

True-L1 conditioning SHALL exist only in a labelled diagnostic arm and scoring.
Oracle and operational arms SHALL use identical blocks and frozen public sets.

## Requirement: full-symbol terminal decision

Success SHALL require exact reconstructed 10-bit labels plus the final tag.
Layer failures and undetected verification outcomes SHALL remain distinct.

## Requirement: bounded claim

The result SHALL be described only as synthetic two-layer interface and
cross-layer-propagation evidence, not efficiency or empirical performance.
