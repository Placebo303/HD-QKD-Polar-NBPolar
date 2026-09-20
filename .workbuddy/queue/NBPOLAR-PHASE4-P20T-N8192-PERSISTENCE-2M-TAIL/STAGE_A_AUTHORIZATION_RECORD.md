# P20T Stage-A Authorization Record (STEP 0)

- Date: 2026-09-20
- Source: user standing pre-authorization 2026-09-20 for autonomous推進
  (preauthorization scheme: autonomous推进, recommend picks auto-selected,
  authorization points marked pre-authorized by the user), renewed 2026-09-20
  for continued 推進. Applied by the main thread to Stage-A implementation ONLY.
- Scope: Stage-A implementation ONLY, exactly as frozen in the packet
  `TASK_PACKET.md` §§2–7 and §12 (new `FROZEN_N = 8192` runner or
  thin-importer + new frozen constants; N=8192 construction/allocation +
  fresh L1/L2/spike-order derivation under the frozen TRAIN seeds
  2026092410..2026092413 × 16 blocks; worktree-file reuse verification;
  focused injected tests; Stage-A freeze supplement + implementation notes;
  existing RN OpenSpec delta only).
- Explicitly NOT authorized by this record: Stage-B execution under any
  circumstances; real-data decoder execution on DEV; protected opens beyond
  the Stage-A budget (counts 0/0, DEV 0/1, VAL-DEV/HOLD-DEV otherwise 0,
  1M/1.5M/2M-non-DEV 0); commit/push.
- RN-1 freeze review: PASSED 2026-09-20 (main thread; decision-log entry).
- Operator rule: the operator never self-accepts; acceptance belongs to the
  main thread after independent Pre-EXECUTE / Pre-RESULT review.

# P20T Stage-B Authorization Record (STEP 0, Stage-B operator)
- Date: 2026-09-20
- Source: user standing pre-authorization 2026-09-20 for autonomous推進
  (preauthorization scheme: autonomous推进, recommend picks auto-selected,
  authorization points marked pre-authorized by the user), renewed 2026-09-20
  for continued 推進. Applied by the main thread to this Stage-B execution.
  Independent Pre-EXECUTE is PASS (reviewer-go, session
  ses_f4313eceaffebVIFYfTW0Iz1xj, 13/13, incl. spike-h reading
  WITHIN-CONTRACT). The filled STEP-2 in AUTHORIZATION_PROMPT.md names the
  exact frozen command.
- Scope: EXACTLY ONE attempt of the byte-identical frozen Stage-B command
  producing ONLY the frozen output files under
  `.workbuddy/queue/NBPOLAR-PHASE4-P20T-N8192-PERSISTENCE-2M-TAIL/n8192_persistence_probe_2m/`
  (fifteen files per §9: frozen_plan.json,
  input_and_predecessor_identity.json, per_block_arm_outcomes.jsonl,
  aggregate_summary.json, report.md, ir5_full_manifest.json + nine IR-5 .bin
  series). Single attempt (1/1 consumed at first DEV content open); DEV 1/1;
  envelope 1200 s / 2 GiB / single thread; within-N descriptive reading only.
- Explicitly NOT authorized by this record: any rerun/tuning after the one
  attempt (execution-error repeat only as a recorded identical-freeze repeat,
  never tuning); any prior/construction/K/order/formula/IR-threshold change;
  any protected opens beyond DEV 1/1 (counts 0/0, 1M/1.5M/2M-non-DEV 0);
  any H2 verdict; any recovery-rate reading; any commit/push; any
  self-acceptance.
- Operator rule: the operator never self-accepts; acceptance belongs to the
  main thread after independent Pre-RESULT review.
