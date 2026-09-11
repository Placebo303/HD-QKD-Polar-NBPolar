# Main-thread adjudication — P2 attempt 1

Disposition: `BLOCKED_REVIEWED_ATTEMPT_EXHAUSTED`.

The sole authorized artifact-content attempt reached and passed the frozen
artifact loader, then failed in newly written diagnostic indexing before any
output was created. The accepted sibling artifact and P1 loader/formula are not
implicated. `f3` has layout `[U1,B,U2]`; `f3[u1,:,nz]` applies advanced indexing
to U2 and moves that indexed axis ahead of B, producing `(32,1024)` against Bob
weights `(1024,1)`. The intended selection is on Bob:
`f3[u1, nz_b, :] -> (n_nonzero_B,32)`.

Attempt 1/1 remains consumed. The absent target stays absent. No rerun is
authorized here. A successor P2-R1 packet may correct and test the diagnostic,
then request one new artifact-content attempt on the same immutable input.
