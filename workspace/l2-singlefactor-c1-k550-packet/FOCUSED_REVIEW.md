# C1 Tier-X focused numerical review and main-thread adjudication — 2026-09-26

Independent luna_worker verdict: **PASS_WITH_LIMITATIONS**. The reviewer read the frozen packet, preregistration, runner, result, and execution transcript without rerunning the probe.

- The recorded command matches the preregistered C command; the transcript records one launch, direct exit code 0, and zero reruns.
- BASE and CAND each contain 550 positions. Intersection 76 implies union 1024 and Jaccard 76/1024 = 0.07421875, below the frozen 495 overlap stop. All 8 measurement cells and 64 paired blocks were completed.
- Recounting per-block records gives BASE oracle exact 64/64, CAND oracle exact 0/64, and operational exact 0/64 for both arms. Paired oracle discordance is 64 BASE-only exact and 0 CAND-only exact. Every seed has the same 16/16 versus 0/16 pattern; recorded means, sample standard deviations, and ranges agree.
- `undetected`, `decode_failed`, and `resource_abort` are zero in all four arm/mode totals. Disclosure is 2800 bits; the 64-bit tag is excluded from the bookkeeping f and included in the 2864 observed key-dependent bits. Wall 99.9065 s <= 200 s; peak RSS 215662592 bytes <= 1 GiB.

Limitations: `results.json` itself does not contain the literal command, UTC timestamps, or process exit code required by the probe template; they are retained in `EXECUTION_TRANSCRIPT.md`. The runner's preparation-only comment is stale. Neither issue changes the result arithmetic, but the JSON alone is not a complete provenance record. The operator's complete filesystem write history is not independently established.

Main-thread adjudication: accept the result **only as a descriptive Tier-X contrast at this frozen synthetic point**. The C1 reverse-Shannon set is a deliberate low-information control, not an improved algorithm. The oracle-conditioned split shows information-set sensitivity; operational recovery remains absent in both arms. This does not estimate real-data FER, efficiency, security, a general construction effect, or an R2 sample-size input. No candidate/accepted scientific token, promotion, attempt accounting, or automatic continuation follows.
