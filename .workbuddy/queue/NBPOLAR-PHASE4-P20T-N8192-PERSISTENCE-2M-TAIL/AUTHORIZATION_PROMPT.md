# P20T authorization prompts — STEP-1 (copyable now) + STEP-2 (template)

Packet: `NBPOLAR-PHASE4-P20T-N8192-PERSISTENCE-2M-TAIL` (`TASK_PACKET.md`).
State: `FROZEN_AWAITING_EXPLICIT_AUTHORIZATION`. RN-1 PASSED 2026-09-20.
Standing pre-authorization 2026-09-20 covers the freeze; Stage A and Stage B
each still need their own explicit pasted authorization below.

---

## STEP-1 — Stage-A implementation + N=8192 derivation authorization (COPYABLE NOW)

> I authorize Stage A ONLY of packet
> `NBPOLAR-PHASE4-P20T-N8192-PERSISTENCE-2M-TAIL` per `TASK_PACKET.md` §§3/12
> and `PROMPT.md`: implement the new `FROZEN_N = 8192` runner (or thin-importer
> + new frozen constants with justification) + focused injected tests
> (`comparison_bench/tests/test_nbpolar_n8192_persistence_probe_2m.py`,
> `pytest -p no:cacheprovider`, fresh additive `workspace/p20t/<uuid>/` roots,
> test seeds `2026092401..2026092407`); verify the §3 reuse pins by
> worktree-file digest recomputation ONLY (prior canonical digest
> `b16f52165d9f7ef28884df270f921ce07c2a743f4f4b39c3435838809ae1c587`, H
> literals `0.02566204884275839 / 0.8069006731309893 / 0.8325627219737477`
> within 1e-12, floor pins); run the frozen N=8192 derivation (synthetic TRAIN
> sampling from the worktree prior arrays ONLY, TRAIN seeds
> `2026092410..2026092413` × 4 blocks per stream = 16 blocks, P16 4×4 pattern;
> K via `floor((1.3·8192·H−64)/5)` from recomputed H with (K1,K2) by
> TRAIN-residual selection; fresh L1/L2/spike orders at length 8192 under
> formula-id `F_MEDIAN8_CARRIED_20260920_H_MINUS_LOCAL_MEDIAN_W8_R8_REFROZEN_8192`
> with R=8 re-frozen for 8192-geometry); confirm the §4 population integers
> (DEV HOLD 3595..3626, remainder 3627..3644) by JSON-manifest metadata only;
> grep-verify tag master `2026092400` / prefix
> `nbpolar-p20t-n8192-persistence-2m-seed` / test-seed freshness.
> Hard limits for Stage A: counts-calibration opens 0/0 at every stage (the V25
> counts NPZ is never opened/statted/listed); DEV 0/1; VAL-DEV/HOLD-DEV
> otherwise 0; 1M/1.5M/2M-non-DEV 0 in every form; zero scoring-time
> sampling/genie (derivation sampling ONLY under the frozen 16-block
> budget+seeds); no DEV contact; no decoder on real data; no Stage-B output
> root (`n8192_persistence_probe_2m/` must remain ABSENT); full reuse/digest
> pins (§3), K-rule/cap/command pins (§§5/10), envelope 1200 s / 2 GiB / single
> thread (§8). No N=32768 K/order/tag/leakage literal is carried; no H2 input;
> no cross-N reading; no commit/push; no self-acceptance. Return per §15(a)
> stage-appropriately (P20T-R1..R9) plus the split open audit, or §15(b) with
> the ONE decision needed.

STEP-1 status: COPYABLE NOW (all Stage-A input pins frozen in-packet; only
Stage-A OUTPUT digests — construction, fresh-order, spike digests, program pin,
K literals — are filled at Stage-A close into `<FROZEN_AT_STAGE_A>`).

---

## STEP-2 — Stage-B single-execution authorization (FILLED 2026-09-20 — standing pre-authorization applied)

> I authorize Stage B ONLY of packet
> `NBPOLAR-PHASE4-P20T-N8192-PERSISTENCE-2M-TAIL`: exactly one execution of the
> frozen Stage-B command (byte-identical to the module FROZEN_COMMAND;
> `--prior-digest b16f52165d9f7ef28884df270f921ce07c2a743f4f4b39c3435838809ae1c587`, `--construction-digest
> d77466eca5b80840ba114ba76500d73d472a5f2818e1fc00b28abbd86d352bb6`, `--order-digest
> 66aefea8d88ef0160906ea37575aa4c4c0dbc0dda6fcd67513a61458198ade93`,
> `--spike-order-digest 355a32d3551c065088da6627dc1ad4ec07b004b73d322567eddaf8cadf03352a`, `--spike-formula
> F_MEDIAN8_CARRIED_20260920_H_MINUS_LOCAL_MEDIAN_W8_R8_REFROZEN_8192`,
> `--k1 84`, `--k2 1676`, `--tag-master
> 2026092400`, `--chunk-rows 128`, `--n 8192`, DEV HOLD 3595..3626, out-dir
> `n8192_persistence_probe_2m/`) with the new construction digest
> `d77466eca5b80840ba114ba76500d73d472a5f2818e1fc00b28abbd86d352bb6`, fresh-order digest
> `66aefea8d88ef0160906ea37575aa4c4c0dbc0dda6fcd67513a61458198ade93`, spike digest
> `355a32d3551c065088da6627dc1ad4ec07b004b73d322567eddaf8cadf03352a`, derivation-program pin
> `n8192_persistence_probe_2m:run_derive_stage_a` (frozen rule per P20T_FREEZE.md §4 + B-1 F-median8 text), and K
> literals `84 / 1676` as pinned at Stage-A close. Requires: Stage-A
> return complete, independent Pre-EXECUTE PASS recorded, target-output root
> ABSENT. Single attempt (1/1 consumed at first DEV content open); DEV 1/1; no
> rerun/seed/parameter/arm change; envelope 1200 s / 2 GiB / single thread.
> Within-N descriptive reading only; no recovery-rate/FER/H2/cross-N claim.

STEP-2 status: FILLED 2026-09-20 from P20T_FREEZE.md (construction d77466…, fresh-order 66aefe…, spike 355a32…, K 84/1676, program pin §4). Executed under the standing pre-authorization 2026-09-20 after Stage-A return + independent Pre-EXECUTE PASS + target-output absence.

(End of file)
