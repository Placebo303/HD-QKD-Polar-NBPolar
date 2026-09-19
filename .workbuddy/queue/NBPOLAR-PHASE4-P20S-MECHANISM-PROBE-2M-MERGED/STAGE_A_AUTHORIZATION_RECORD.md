# Stage-A authorization record — NBPOLAR-PHASE4-P20S-MECHANISM-PROBE-2M-MERGED

- Date: 2026-09-20
- Source: user standing pre-authorization message, quoted verbatim:
  - "我预授权给你向下自主探索与推进的权力… 需要授权的地方都标注我已预授权"
- Scope: Stage-A implementation ONLY, exactly as frozen in `TASK_PACKET.md`
  §§2–7, §12, with the frozen DECIDED 2026-09-20 F-median8 formula:
  - "F-median8: score[i] = h[i] − median(h over the R=8 clipped natural
    neighborhood of i), where h[i] is the frozen arm-table hazard atom
    (-log2 true-cell mass, same recipe as the IR recorders); rank all 32768
    L2 positions by descending score; take the first K2=6746 positions as
    arm B's disclosed L2 set; tie-break by ascending natural block
    coordinate; deterministic, zero sampling, zero genie calls, zero
    protected reads (inputs: worktree `raw_prior_2m.npz` arrays only); arm
    A's set stays the frozen incumbent-order first-K2 prefix."
- Explicitly NOT authorized by this record:
  - Stage-B execution (needs independent Pre-EXECUTE review + separate
    pasted Stage-B authorization);
  - any real-data decoder execution;
  - any protected open (counts 0/0, merged-DEV 0/1, 1M 0, 1.5M 0,
    2M-non-DEV 0 at Stage-A close);
  - any commit or push.
- Operator rule: the operator never self-accepts and never authorizes
  Stage B. Return follows packet §15 (R1..R9 stage-appropriately, or a
  concrete blocker with the ONE decision needed).

# Stage-B authorization record — NBPOLAR-PHASE4-P20S-MECHANISM-PROBE-2M-MERGED

- Date: 2026-09-20
- Source: user standing pre-authorization message, quoted verbatim:
  - "我预授权给你向下自主探索与推进的权力，允许你往下推进至少十轮，需要抉择的地方都自动选择recommend项，需要授权的地方都标注我已预授权"
- Independent Pre-EXECUTE: PASS (reviewer-go, session ses_f44e12d50ffeGf5QnxJNUQg4eU, 12/12).
- Scope: EXACTLY ONE Stage-B attempt, byte-identical frozen command per
  `P20S_FREEZE.md` §10 (module `FROZEN_COMMAND`), ONLY the frozen output
  files under the Stage-B root
  `.workbuddy/queue/NBPOLAR-PHASE4-P20S-MECHANISM-PROBE-2M-MERGED/l2_mechanism_probe_2m/`.
- Explicitly NOT authorized by this record:
  - rerun/tuning (one attempt only; a repeat is allowed solely as a
    recorded identical-freeze repeat of an execution error, never tuning);
  - any prior/alt/construction/K/order/formula/IR-threshold change;
  - any protected open beyond merged-DEV 1/1 (counts 0/0, 1M 0, 1.5M 0,
    2M-non-DEV 0 stay fail-closed);
  - any H2 verdict;
  - any recovery-rate reading;
  - any commit or push;
  - any self-acceptance.
- Operator rule: the operator never self-accepts. Return follows packet §15.
