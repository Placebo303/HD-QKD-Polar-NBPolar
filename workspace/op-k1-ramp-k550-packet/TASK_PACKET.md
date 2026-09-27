# Task packet — `op-k1-ramp-k550` (operational k1 dose ramp, bounded 5 points)

- **Tier**: X (synthetic-only, descriptive, non-claim)
- **probe_id**: `op-k1-ramp-k550`
- **packet root**: `workspace/op-k1-ramp-k550-packet/`
- **probe root**: `workspace/probes/op-k1-ramp-k550/`
- **predecessor**: `workspace/probes/l2-singlefactor-c1-k550/` (`DESCRIPTIVE_TIER_X_REVIEWED_WITH_LIMITATIONS`)
- **driving plan**: `docs/nbpolar/OVERNIGHT_PLAN_20260927.md` §2 P1–P5
- **status**: `PACKET_PREPARED_AWAITING_FREEZE_REVIEW`

---

## 1. Scientific question (DP-K1)

C1 + `k2-dose-ramp` established a one-directional fact: on F4@q1024 + M2
two-layer GF32 SC, the **oracle** branch is highly sensitive to the L2
information set (C1 BASE 64/64 exact), while the **operational** branch is
`verify_failed` on every measured point (C1 0/64 at k1=10; `k2-dose-ramp` 0/32
at every k2 in {200,400,700,1024}). **k1 has never been varied as a single
factor in this series** (`K1_FROZEN=10` throughout).

⇒ This probe asks: **is the operational all-fail regime explained by an
insufficient L1 disclosure dose?** It is a *localisation* probe, not an
improvement attempt.

Per `AGENTS.md` §1.1 this is the informative next action; repeating the
already-observed "information-set sensitivity" result on the oracle branch is
not. Bounded-list candidates C2/C3/C4 (`NEXT_L2_PROBE_DESIGN_20260925.md` §4)
are **not consumed**.

## 2. Frozen design (DP-K2..K5)

See `STATUS.yaml` → `adjudications:` for the machine-readable form.

| Item | Value |
|---|---|
| variable | `k1 ∈ {10, 80, 160, 320, 450}` (5 bounded points, one run) |
| fixed | `k2 = 550`, no fallback |
| `d1` | `worst_k(H1, k1)` — **per config** |
| `d2` | `worst_k(H2, 550)` — shared; set-identical to C1 BASE |
| design seed / MC | `2026092600` / `128` — **unchanged from C1** |
| run seeds | `2026092701..2026092702` |
| blocks | 16 per seed ⇒ 32 per point, 160 total |
| arms | BASE only (single arm) |
| budget | wall ≤ 600 s, RSS ≤ 1 GiB |
| one-shot | `reruns=0` |

Bookkeeping reference (`disclosed = 5*(k1+k2)`, run-time arithmetic authoritative):

| k1 | disclosed | f_book (bookkeeping only) |
|---:|---:|---:|
| 10 | 2800 | ≈2.9344139789 (= C1 anchor) |
| 80 | 3150 | ≈3.3013 |
| 160 | 3550 | ≈3.7204 |
| 320 | 4350 | ≈4.5589 |
| 450 | 5000 | ≈5.2401 |

## 3. Allowed derivation delta vs the C1 runner

Only these five classes of change were made (P2):

1. `K1_FROZEN` → `K1_GRID=(10,80,160,320,450)`; `K2_SINGLE=550` unchanged;
   `K2_POINTS` → `K1_POINTS`.
2. `d1 = worst_k(H1,k1)` per config (the C1 `d1_shared` becomes per-config).
3. Identifiers `probe_id`, `SEEDS`, output path, `NUMBA_CACHE_DIR`.
4. CAND arm and the BASE/CAND `d2` overlap design gate removed (single arm ⇒
   not applicable). **`undetected` isolation STOP and the budget STOP are
   retained.**
5. Per-k1 result recording: operational/oracle outcome counts, observed
   `key_dependent_bits`, `disclosed_bits`, wall/RSS.

**Forbidden and not done**: channel change, prior change,
`toeplitz_master=2026091361` change, `tl.run_two_layer_block` call-semantics
change, any write to the read-only `qkd_recon.polar_core` dependency at
`/mnt/d/Code/qkd-reconciliation-lab/src`.

## 4. Write scope

- `workspace/probes/op-k1-ramp-k550/results.json`
- `workspace/probes/op-k1-ramp-k550/.numba_cache/`

Nothing else. No `results/`, no `comparison_bench/outputs_comparison/`.

## 5. Authorizations

Recorded in `STATUS.yaml` → `authorizations:`. Basis = the broad synthetic-work
authorization granted in the main conversation (as recorded in the C1 packet
`user_authorization`) **plus** a main-thread freeze-review PASS (P3).

**This packet touches no real or protected data.** Synthetic-only Tier-X; no
Tier-Y; no decode on real blocks.

## 6. Stop rules

- `undetected > 0` ⇒ immediate stop and isolation (never merged into success).
- wall > 600 s or RSS > 1 GiB ⇒ `status=incomplete`, stop, **no tuning**.
- unhandled exception ⇒ one record, **no retry**.

## 7. Claim boundary

Tier-X non-claim. No FER/efficiency/security claim, no significance wording, no
H-label conclusion, no R2 sizing input, no candidate/accepted token, no attempt
accounting, no automatic continuation.
**Every k1 point is a bookkeeping-only dose diagnostic and must never be called
an efficiency operating point.**
