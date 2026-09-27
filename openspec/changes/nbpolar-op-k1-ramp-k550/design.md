# Design: operational k1 dose ramp (five bounded points, single arm)

## Frozen object and route

- Tier-X synthetic-only probe; `N=q=1024`, `n_log=10`, `R=10`.
- F4 channel: `p0=0.75`, `p(+1)=0.24`, `p(-1)=0.005`, residual mass `0.005`
  spread uniformly over the other 1021 offsets; `x` is uniform and
  `y=(x+delta) mod 1024`. **Unchanged from C1.**
- Reuse the C1 predecessor's M2 prior, two-layer GF32 SC/oracle and operational
  decode semantics, `toeplitz_master=2026091361`, and disclosure accounting.
  No decoder, channel, or `tl.run_two_layer_block` call-semantics change.
- Preserve the predecessor's read-only runtime import of `qkd_recon.polar_core`
  through `/mnt/d/Code/qkd-reconciliation-lab/src`; this code dependency is not
  a data input and receives no writes.
- **Variable**: `K1_GRID = (10, 80, 160, 320, 450)`. **`k2 = 550` fixed**, no
  fallback.
- `d1 = worst_k(H1, k1)` — computed **per grid point**; the `d1_shared`
  semantics of C1 becomes per-config.
- `d2 = worst_k(H2, 550)` — identical rule, design seed and `DESIGN_MC` as C1,
  therefore **the same set as C1's BASE**.
- Single arm (BASE only). C1 already established BASE as the effective and
  current information set; the variable here is k1, not the arm.

## Bookkeeping reference (run-time arithmetic is authoritative)

`disclosed_bits = 5*(k1 + k2)`; `f_book` is **bookkeeping only**, never an
efficiency point. `HN ≈ 954.18`.

| k1 | disclosed = 5·(k1+550) | f_book (bookkeeping only) |
|---:|---:|---:|
| 10 | 2800 | ≈2.9344139789 (= C1 anchor) |
| 80 | 3150 | ≈3.3013 |
| 160 | 3550 | ≈3.7204 (cross-checks the 3550 point of `k2-dose-ramp`) |
| 320 | 4350 | ≈4.5589 |
| 450 | 5000 | ≈5.2401 |

The 64-bit tag remains **excluded** from `f` and included in the observed
key-dependent bits.

## Frozen sampling and pairing

- Design seed `2026092600`; `DESIGN_MC=128`. **Unchanged from C1** (this is
  what makes `d2` set-identical to C1's BASE).
- Run seeds `2026092701..2026092702`, 16 blocks per seed ⇒ **32 blocks per k1
  point**, 160 blocks total.
- Per `(seed,block)`, use `default_rng([seed,block])`, draw `x` then `delta`,
  and reuse the resulting `(x,y)` across the grid within that block.
- Only `k1` varies. `k2` stays 550 at every point.

## Gates, stops and result

- The C1 `identical / overlap ≥ 495` design gate is **not applicable** (single
  arm). It is removed together with the CAND arm.
- **Retained STOP rules**: `undetected > 0` ⇒ immediate stop and isolation;
  wall or RSS breach ⇒ `status=incomplete`, no tuning; unhandled exception ⇒
  one record, no retry.
- Per-k1 descriptive readout: operational outcome counts, oracle outcome
  counts, `key_dependent_bits`, wall and peak RSS, and the point's
  `disclosed_bits`.

## Runtime limits and writes

- Wall limit **600 s**; peak RSS limit **1 GiB**. Check after every design
  chunk of 32 samples and after each measurement block; stop on breach with an
  honest incomplete status.
- One shot, `reruns=0`. No seed change, tuning, extra samples, or fallback.
- Probe output is confined to `workspace/probes/op-k1-ramp-k550/`, with one
  result record. The Numba cache path, if used, is inside that probe root.
- No other project files are written during execution. Preparation writes only
  the enumerated OpenSpec, probe, and packet files.

## Execution gate

The user has granted broad authorization for continued synthetic work. The
packet records `user_authorization` and the main-thread freeze review as its
authority basis. This design does not itself authorize execution: the exact
prereg command, source delta, target-output absence, budget, and write scope
require main-thread freeze review (`FREEZE_REVIEW.md`, P3) first. No design or
decoder execution is part of this preparation task.
