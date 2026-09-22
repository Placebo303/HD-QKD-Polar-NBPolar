#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""g4_build_inventory.py — packet-local, READ-ONLY inventory builder for
NBPOLAR-M2-PRIOR-G4-INVENTORY (D6 gate G4; change openspec/changes/nbpolar-prior-rebaseline).

AUTHORIZED SCOPE (AUTHORIZATION_PROMPT.md A/B, operative: kai 2026-09-22,
g4_authorized / execution_one_shot / inventory_only_no_decode / raw_data_read=false):

  * Pure aggregation over already-frozen JSON/JSONL plus quoted markdown/yaml
    record rows. NO numeric re-derivation of anything (census sigma is quoted
    as a frozen string only; cross-artifact STRING consistency check allowed per
    Main-thread adjudication 2026-09-22 item 6).
  * NO decode, NO SC call, NO tag generation, NO raw SHG acquisition read,
    NO import of any project module (stdlib only), no production decoder path
    is reachable from this file.
  * Writes ONLY these four files, all inside this packet dir, never overwriting:
        g4_inventory.json, g4_inventory.md, g4_counts.json, g4_run_log.md
    (single output route, adjudication item 7). Nothing else, anywhere.
  * Budget (frozen): <= 300 s wall / 2 GiB RSS single-threaded. Exceeded => STOP.
  * One-shot: once ANY complete g4_inventory.json exists there is NO
    rebuild/patch/addendum (rebuild rule: only after a zero-output crash).
  * No claim sentences: no FER/efficiency/qualification/promotion/composable
    statements, no S9 citation. All verdicts are quoted as recorded.

Inline self-checks (ALL must pass BEFORE any output file is written;
a failure is a STOP -> return condition 2, nothing is written):

  SC1  input-path existence + non-empty locators for every manifest item
  SC2  g4_freeze_config.json TO-FREEZE pointers resolve and are non-null
  SC3  branch == codex/nbpolar-phase0; verbatim authorization recorded in STATUS.yaml
  SC4  target-output absence (none of the four outputs exists yet; no overwrite)
  SC5  CAL set-equality matrix (cal_ids*.json vs freeze configs vs closure copies;
       inventory CAL rows vs their source arrays)
  SC6  disclosure recount cross-check (per-stage sums == frozen recount ==
       summary disclosure_recount; incremental == mismatches[]; 42 rows; tags 42;
       undetected count agrees between per-block rows and summary arms)
  SC7  row schema validity (required fields, enums, unique sequential ids, mapping)
  SC8  countability: row_count == len(rows) == MD table rows ==
       sum(rows_by_stage) == sum(rows_by_message_class) ==
       sum(rows_by_release_handling); zero status=to_freeze rows;
       every expected class either has explicit rows or an explicit none_recorded row
  SC9  budget (wall s / RSS GiB) vs frozen limits, checked before writing
  SC10 constant-agreement + md-locator spot checks (recorded values equal the
       frozen constants; sigma STRING consistency across artifacts; no numeric work)

Usage:
  # Pre-EXECUTE focused test — runs every check + in-memory row build, writes NOTHING:
  /home/karel_303/.venvs/timetagger/bin/python g4_build_inventory.py --check-only

  # Phase-B ONE-SHOT build (only after independent Pre-EXECUTE PASS):
  /home/karel_303/.venvs/timetagger/bin/python g4_build_inventory.py
"""

import datetime
import json
import os
import re
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
FREEZE_PATH = os.path.join(HERE, "g4_freeze_config.json")
G4_STATUS_PATH = os.path.join(HERE, "STATUS.yaml")
OUT_PATHS = [
    os.path.join(HERE, "g4_inventory.json"),
    os.path.join(HERE, "g4_inventory.md"),
    os.path.join(HERE, "g4_counts.json"),
    os.path.join(HERE, "g4_run_log.md"),
]

AUTHORIZED_LINE = (
    "AUTHORIZED BY: kai —2026.09.22 — g4_authorized: true (precondition: G3 accepted "
    "NBPOLAR_M2_PRIOR_G3_SUCCESS, M2 VALIDATED_AT_FROZEN_CONTRACT) / execution_one_shot: true "
    "/ inventory_only_no_decode: true / raw_data_read: false"
)

# Frozen enums (packet-local freeze; extension requires a NEW freeze).
RELEASE_HANDLING = [
    "counted_in_leak_IR",
    "charged_0_labeled_public_ec_only_not_secure",
    "result_publication",
    "sacrificed_excluded_from_denominator",
    "diagnostic_only_never_lambda",
    "structural_public_parameter",
    "blocked_never_public",
]
MESSAGE_CLASSES = [
    "contract_param", "construction", "alignment_record", "ledger_allocation",
    "cal_frame_list", "fitted_prior", "reveal_bits_diagnostic", "disclosure_bits",
    "tag", "threshold_or_gate_record", "result_publication",
    "participation_disclosure", "blocked", "none_recorded",
]
# blocked/none_recorded are the last two classes; schema also lists "blocked" and "none_recorded".
ROW_STATUS = ["frozen", "quoted", "derived_read_only", "to_freeze"]
STAGES = ["CONTRACT", "G1", "G1R2", "G2", "G3"]

# message_class -> the ONE release_handling it may carry.
# Documented exceptions (both frozen in-packet): disclosure_bits may carry
# charged_0_labeled_public_ec_only_not_secure ONLY for the single Release
# in-sample comparison-record row (adjudication item 3).
CLASS_TO_HANDLING = {
    "contract_param": "structural_public_parameter",
    "construction": "structural_public_parameter",
    "alignment_record": "structural_public_parameter",
    "ledger_allocation": "structural_public_parameter",
    "cal_frame_list": "sacrificed_excluded_from_denominator",
    "fitted_prior": "structural_public_parameter",
    "reveal_bits_diagnostic": "diagnostic_only_never_lambda",
    "disclosure_bits": "counted_in_leak_IR",
    "tag": "structural_public_parameter",
    "threshold_or_gate_record": "structural_public_parameter",
    "result_publication": "result_publication",
    "participation_disclosure": "structural_public_parameter",
    "blocked": "blocked_never_public",
    "none_recorded": "structural_public_parameter",
}

# Repo-relative artifact roots (all READ-ONLY manifest inputs).
G1 = "workspace/m2_prior_validation/20260113_SHG_Type2PPLN_3s"
G1R2 = "workspace/m2_prior_validation/20260113_SHG_Type2PPLN_3s_g1r2"
G2 = "workspace/m2_prior_validation/20260113_SHG_Type2PPLN_3s_g2"
G3 = "workspace/m2_prior_validation/20260113_SHG_Type2PPLN_3s_2_g3"
PK1 = ".workbuddy/queue/NBPOLAR-M2-PRIOR-G1-REALDATA-NLL"
PK2 = ".workbuddy/queue/NBPOLAR-M2-PRIOR-G1R2-W200-CIRCULAR"
PK3 = ".workbuddy/queue/NBPOLAR-M2-PRIOR-G2-DECODE"
PK4 = ".workbuddy/queue/NBPOLAR-M2-PRIOR-G3-CONFIRM"
CONSTRUCTION = ".workbuddy/queue/NBPOLAR-PHASE4-P16-N32768-OPERATIONAL-F13/operational_f13_gate/construction_and_allocation.json"
SEC_MODEL = "docs/SECURITY_MODEL.md"
DECISION_LOG = "docs/decision-log.md"


class Blocker(Exception):
    """Concrete blocker -> return condition 2 (nothing is ever written)."""


CHECKS = []


def check(name, ok, detail=""):
    ok = bool(ok)
    CHECKS.append({"check": name, "ok": ok, "detail": str(detail)})
    if not ok:
        raise Blocker("%s: %s" % (name, detail))
    return ok


def rel(*parts):
    return "/".join(parts)


def abspath(repo_rel):
    return os.path.join(ROOT, *repo_rel.split("/"))


def read_text(repo_rel):
    with open(abspath(repo_rel), "r", encoding="utf-8") as fh:
        return fh.read()


def read_json(repo_rel):
    with open(abspath(repo_rel), "r", encoding="utf-8") as fh:
        return json.load(fh)


def read_jsonl(repo_rel):
    rows = []
    with open(abspath(repo_rel), "r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def must(container, key, ctx):
    """Locator resolution: absence/mismatch is a hard error, never a default."""
    if isinstance(container, dict):
        if key not in container:
            raise Blocker("locator miss: %s not in %s" % (key, ctx))
        return container[key]
    raise Blocker("locator miss: %s is not an object (%s)" % (ctx, key))


def jdump(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False)


def ranges_text(ids):
    if not ids:
        return "(empty)"
    out = []
    start = prev = ids[0]
    for x in ids[1:]:
        if x == prev + 1:
            prev = x
            continue
        out.append("%d-%d" % (start, prev) if start != prev else str(start))
        start = prev = x
    out.append("%d-%d" % (start, prev) if start != prev else str(start))
    return ", ".join(out)


def all_keys(obj, acc=None):
    if acc is None:
        acc = set()
    if isinstance(obj, dict):
        for k, v in obj.items():
            acc.add(str(k))
            all_keys(v, acc)
    elif isinstance(obj, list):
        for v in obj:
            all_keys(v, acc)
    return acc


def status_result_id(repo_rel):
    txt = read_text(repo_rel)
    idx = txt.find("\nresult:")
    if idx < 0:
        raise Blocker("locator miss: 'result:' block in %s" % repo_rel)
    m = re.search(r"\bid:\s*([A-Za-z0-9][A-Za-z0-9_\-]*)", txt[idx:idx + 4000])
    if not m:
        raise Blocker("locator miss: result.id in %s" % repo_rel)
    return m.group(1)


def line_contains(repo_rel, lineno_1based, needle):
    lines = read_text(repo_rel).splitlines()
    if len(lines) < lineno_1based:
        return False
    return needle in lines[lineno_1based - 1]


def rss_gib_hwm():
    try:
        with open("/proc/self/status", "r", encoding="utf-8") as fh:
            for line in fh:
                if line.startswith("VmHWM:"):
                    return int(line.split()[1]) / (1024.0 * 1024.0)
    except Exception:
        pass
    return None


# --------------------------------------------------------------------------------------
# row construction
# --------------------------------------------------------------------------------------
ROWS = []
ROW_LOG = []


def add(stage, cls, message, producer, key_dep, size_bits, count, seed_ref,
        source_artifact, source_locator, status):
    if stage not in STAGES:
        raise Blocker("stage not in frozen enum: %r" % stage)
    if cls not in MESSAGE_CLASSES:
        raise Blocker("message_class not in frozen enum: %r" % cls)
    if status not in ROW_STATUS:
        raise Blocker("status not in frozen enum: %r" % status)
    if not isinstance(key_dep, bool):
        raise Blocker("key_dependent must be bool in %s/%s" % (stage, cls))
    if not (isinstance(size_bits, int) or (isinstance(size_bits, str) and size_bits.startswith("N/A"))):
        raise Blocker("size_bits must be int or 'N/A ...' in %s/%s" % (stage, cls))
    if not isinstance(count, int):
        raise Blocker("count must be int in %s/%s" % (stage, cls))
    if not source_artifact or not source_locator:
        raise Blocker("empty source_artifact/source_locator in %s/%s" % (stage, cls))
    handling = CLASS_TO_HANDLING[cls]
    if cls == "disclosure_bits" and status == "quoted" and "Release baseline" in producer:
        handling = "charged_0_labeled_public_ec_only_not_secure"
    n = 1 + sum(1 for r in ROWS if r["stage"] == stage)
    row = {
        "id": "G4-%s-%03d" % (stage, n),
        "stage": stage,
        "message_class": cls,
        "message": message,
        "producer": producer,
        "key_dependent": key_dep,
        "size_bits": size_bits,
        "count": count,
        "seed_mask_code_ref": seed_ref,
        "source_artifact": source_artifact,
        "source_locator": source_locator,
        "release_handling": handling,
        "status": status,
    }
    ROWS.append(row)
    ROW_LOG.append("%s  ok  %s / %s" % (row["id"], cls, handling))
    return row


NONE_NOTES = {
    "disclosure_bits": (
        "no key_dependent_bits / public_control_bits field exists anywhere in this stage's "
        "JSON/JSONL artifacts (exhaustive key scan at build time)"),
    "tag": (
        "no tag / tag_invoked / tag_pass output field exists in this stage's output artifacts "
        "(exhaustive key scan at build time)"),
    "participation_disclosure": (
        "no participation_disclosure field exists in this stage's output artifacts "
        "(that statement is a G3 record)"),
    "reveal_bits_diagnostic": (
        "no reveal-bits value is recorded in this stage's artifacts; the only record is the "
        "SECURITY_MODEL.md skeleton row (CONTRACT stage row)"),
}


STAGE_DEFAULT_SOURCE = {
    "CONTRACT": CONSTRUCTION,
    "G1": rel(G1, "g1.json"),
    "G1R2": rel(G1R2, "g1.json"),
    "G2": rel(G2, "g2_summary.json"),
    "G3": rel(G3, "g3.json"),
}
SCAN_LOCATOR = "$ — exhaustive key scan over this stage's manifest JSON/JSONL artifacts " \
               "(expected-class matrix: g4_freeze_config.json expected_classes_by_stage)"


def add_none(stage, cls, source_artifact=None, source_locator=None, extra=""):
    note = NONE_NOTES.get(cls, "field class absent in this stage")
    msg = ("field class `%s`: none recorded — %s%s. Exhaustive-first publication: absence is "
           "stated explicitly, never silence." % (cls, note, ("; " + extra) if extra else ""))
    return add(stage, "none_recorded", msg, "G4 exhaustive field scan (read-only)",
               False, "N/A (no such message exists)", 0, "n/a",
               source_artifact or STAGE_DEFAULT_SOURCE[stage],
               source_locator or SCAN_LOCATOR, "derived_read_only")


def none_named_classes(stage):
    return {c for r in ROWS if r["stage"] == stage and r["message_class"] == "none_recorded"
            for c in MESSAGE_CLASSES if ("field class `%s`" % c) in r["message"]}


def cover_expected(stage, expected_classes):
    """SC8 exhaustiveness: every expected class has explicit rows or a none_recorded row."""
    present = {r["message_class"] for r in ROWS if r["stage"] == stage}
    named = none_named_classes(stage)
    for cls in expected_classes:
        if cls not in present and cls not in named:
            add_none(stage, cls)


def blocked_rows(stage, session_label):
    src = DECISION_LOG
    loc = "line 5327 (F3: exhaustive fail-closed public-message inventory, blocked_* statuses)"
    add(stage, "blocked",
        "%s: raw symbol/frame contents of the frames processed by this stage are NOT public — "
        "listed fail-closed, content never asserted by G4." % session_label,
        "Release fail-closed pattern (decision-log F3)", False,
        "N/A (fail-closed; content never asserted)", 0, "n/a", src, loc, "frozen")
    add(stage, "blocked",
        "%s: raw CAL frame payloads (a1_cal / cal32 contents) are NOT public — only the frame ID "
        "lists are published (see cal_frame_list rows)." % session_label,
        "Release fail-closed pattern (decision-log F3)", False,
        "N/A (fail-closed; content never asserted)", 0, "n/a", src, loc, "frozen")
    add(stage, "blocked",
        "%s: seed material before use is NOT public — only post-run tag_master contract values are "
        "published (see tag/contract rows)." % session_label,
        "Release fail-closed pattern (decision-log F3)", False,
        "N/A (fail-closed; content never asserted)", 0, "n/a", src, loc, "frozen")


def build_contract_rows(fc, construction_cell):
    n = fc["N"]
    add("CONTRACT", "contract_param", "N = %s (block length), recorded verbatim as contract context "
        "(inventory row, not re-derived)." % n,
        "P16 construction freeze", False, 0, 1, "n/a", CONSTRUCTION, "cell.n", "frozen")
    add("CONTRACT", "contract_param", "K1 = %s, recorded verbatim (frozen; D4 deferred, no re-split)."
        % fc["K1"], "P16 construction freeze", False, 0, 1, "n/a", CONSTRUCTION, "cell.k1", "frozen")
    add("CONTRACT", "contract_param", "K2 = %s, recorded verbatim (frozen; no increase)." % fc["K2"],
        "P16 construction freeze", False, 0, 1, "n/a", CONSTRUCTION, "cell.k2", "frozen")
    add("CONTRACT", "construction",
        "Frozen P16 orders l1_order and l2_order present, each of recorded length %s "
        "(presence + length recorded; never re-derived; G4 computes NO digest)."
        % len(construction_cell["l1_order"]),
        "P16 construction freeze", False, 0, 1, "n/a", CONSTRUCTION,
        "cell.l1_order, cell.l2_order", "frozen")
    add("CONTRACT", "construction",
        "P16 inner procedure digest %s quoted verbatim (inner digest of the canonical "
        "construction_and_allocation.json; the wrapper file's own sha256 differs — P17-established; "
        "G4 computes no digest)." % fc["p16_digest"],
        "P17-established record (quoted in G2/G3 summaries)", False, 0, 1, "n/a",
        rel(G2, "g2_summary.json"), "construction.inner_digest (agrees with %s $.construction.inner_digest)"
        % rel(G3, "g3_summary.json"), "quoted")
    add("CONTRACT", "contract_param", "W_P = %s (pairing_window_primary), recorded verbatim." % fc["W_P"],
        "G2/G3 freeze (inherited contract)", False, 0, 1, "n/a", rel(PK4, "g3_freeze_config.json"),
        "pairing_window_primary (agrees with %s)" % rel(PK3, "g2_freeze_config.json"), "frozen")
    add("CONTRACT", "contract_param", "W_S = %s (pairing_window_sensitivity), recorded verbatim "
        "(sensitivity readout only)." % fc["W_S"], "G2/G3 freeze (inherited contract)", False, 0, 1,
        "n/a", rel(PK4, "g3_freeze_config.json"), "pairing_window_sensitivity (agrees with %s)"
        % rel(PK3, "g2_freeze_config.json"), "frozen")
    add("CONTRACT", "contract_param", "MOD = %s, recorded verbatim." % fc["MOD"],
        "G2/G3 freeze (inherited contract)", False, 0, 1, "n/a", rel(PK4, "g3_freeze_config.json"),
        "mod_boundary (agrees with %s)" % rel(PK3, "g2_freeze_config.json"), "frozen")
    add("CONTRACT", "contract_param", "skip = %s, recorded verbatim (INHERITED_NOT_DERIVED)." % fc["skip"],
        "G2/G3 freeze (inherited contract)", False, 0, 1, "n/a", rel(PK4, "g3_freeze_config.json"),
        "skip_frames (agrees with %s and g1/g1r2 ledger records)" % rel(PK3, "g2_freeze_config.json"),
        "frozen")
    add("CONTRACT", "contract_param", "frame_pairs = %s, recorded verbatim." % fc["frame_pairs"],
        "G1 freeze (pairing frozen block)", False, 0, 1, "n/a", rel(G1, "g1.json"),
        "pairing.frozen.frame_pairs", "frozen")
    add("CONTRACT", "contract_param", "floor = %s, recorded verbatim." % fc["floor"],
        "G2 freeze (contract values)", False, 0, 1, "n/a", rel(PK3, "g2_freeze.md"),
        "line 91 ('chunk_rows 512; floor 1e-15')", "frozen")
    add("CONTRACT", "contract_param", "chunk = %s (chunk_rows), recorded verbatim." % fc["chunk"],
        "G2 freeze (contract values)", False, 0, 1, "n/a", rel(PK3, "g2_freeze.md"),
        "line 91 ('chunk_rows 512; floor 1e-15')", "frozen")
    add("CONTRACT", "contract_param",
        "bin = %s (pairing bin_width_ps=200 from the census frozen block; NOT the alignment-scan "
        "bin=100 ps — different constant; G4 derives neither)." % fc["bin"],
        "G1 freeze (pairing frozen block)", False, 0, 1, "n/a", rel(G1, "g1.json"),
        "pairing.frozen.bin_width_ps", "frozen")
    add("CONTRACT", "tag",
        "G2 tag_master = %s, recorded verbatim, labeled INHERITED (from G1R2; EVAL_SEED 2026093001 "
        "by frozen rule TAG_MASTER = EVAL_SEED + 10000). Contract seed record: 0 tags are emitted "
        "by this row." % fc["g2_tag_master"],
        "G1R2 freeze, inherited by G2", False, 0, 0, "tag_master %s" % fc["g2_tag_master"],
        rel(PK3, "g2_freeze_config.json"), "tag_master", "frozen")
    add("CONTRACT", "tag",
        "G3 tag_master = %s, recorded verbatim (EVAL_SEED 2026100101, same frozen rule). Contract "
        "seed record: 0 tags are emitted by this row." % fc["g3_tag_master"],
        "G3 freeze", False, 0, 0, "tag_master %s" % fc["g3_tag_master"],
        rel(PK4, "g3_freeze_config.json"), "tag_master", "frozen")
    add("CONTRACT", "contract_param",
        "census sigma = %s — frozen quoted value, not recomputed in G4 (citation carries its source "
        "artifact path; numeric re-derivation is forbidden)." % repr(fc["census_sigma"]),
        "2026-09-21 dual-rule census (quoted only)", False, 0, 1, "n/a",
        rel(G3, "g3_summary.json"),
        "$.align.peak_sigma_ps (string copies also in %s, %s, %s, docs/decision-log.md)"
        % (rel(PK4, "G3_ADJUDICATION.md"), rel(PK4, "G3_PROCESS_DEVIATION.md"),
           rel(PK4, "PRE_RESULT_REVIEW.md")), "quoted")
    add("CONTRACT", "fitted_prior",
        "Skeleton row (0-bit shape, docs/SECURITY_MODEL.md): fitted triple (q0, q+1, q-1) per "
        "session, derived from sacrificed CAL only, seed/mask = CAL frame IDs at freeze. Concrete "
        "per-session values live in the G1/G1R2/G2/G3 stage rows.",
        "estimator (skeleton record)", False, 0, 1, "CAL frame IDs",
        SEC_MODEL, "line 140 (§Public-message inventory skeleton table)", "quoted")
    add("CONTRACT", "reveal_bits_diagnostic",
        "Skeleton row (docs/SECURITY_MODEL.md): reveal bits (~18-22, params*log2(n) order-of-"
        "magnitude) are diagnostic-only and never enter lambda_total; size recorded 0 in the "
        "skeleton, descriptive status.",
        "estimator (skeleton record)", False, 0, 1,
        "params*log2(n) order-of-magnitude", SEC_MODEL,
        "line 141 (§Public-message inventory skeleton table)", "quoted")
    add("CONTRACT", "contract_param",
        "D4 K re-split record: NBPOLAR_M2_PRIOR_K_RESPLIT_D4_COMPLETE_REPORT_ONLY — report-only "
        "planning input, adopted neither branch; K1=319/K2=6492 unchanged (G4 records that D4 "
        "changed nothing).",
        "main-thread D4 record", False, 0, 1, "n/a",
        ".workbuddy/queue/NBPOLAR-M2-PRIOR-K-RESPLIT-D4/D4_RECORD.md", "line 3 (Label)", "frozen")
    add("CONTRACT", "disclosure_bits",
        "Release baseline in-sample estimation pattern: 0 bits charged, labeled "
        "public_ec_only_not_secure with composable_security_claim_flag=0 — COMPARISON RECORD ROW "
        "against the Release in-sample mode ONLY; never counted in NB-Polar's own accounting "
        "(NB-Polar accounts sacrificed CAL frames via sacrificed_excluded_from_denominator).",
        "Release baseline (comparison record)", False, 0, 1, "n/a",
        DECISION_LOG, "line 5327 (F3)", "quoted")


def build_stage_records(stage, session_label, g_json, g_json_rel, cal, cal_rel, closure_rel,
                        closure_field, freeze_cfg, freeze_cfg_rel, run_logs, status_rel, adj_rel,
                        tag_master_value, tag_master_art, tag_master_loc):
    """Shared per-stage record rows: contract/alignment/ledger/CAL/prior/gates/results/blocked."""
    pairing = must(g_json, "pairing", g_json_rel)
    add(stage, "contract_param",
        "as-executed pairing record (rule/window/n_pairs/frozen block) as recorded: " + jdump(pairing),
        "%s run" % stage, False, 0, 1, "n/a", g_json_rel, "$.pairing", "derived_read_only")
    ledger = must(g_json, "ledger", g_json_rel)
    add(stage, "ledger_allocation",
        "ledger/frame allocation as recorded: " + jdump(ledger),
        "%s run" % stage, False, 0, 1, "n/a", g_json_rel, "$.ledger", "derived_read_only")
    align = must(g_json, "align", g_json_rel)
    extra = ""
    if "offset_applied_to_alice" in g_json:
        extra = ("; offset_applied_to_alice=%s; convention '%s'; yield sweep recorded at $.yield_sweep"
                 % (g_json["offset_applied_to_alice"], g_json.get("offset_sign_convention", "")))
    add(stage, "alignment_record",
        "derived alignment record as recorded: " + jdump(align) + extra + " (G4 derives nothing; "
        "alignment reproduction is not re-evaluated)",
        "%s run (decoder-free closure/science)" % stage, False, 0, 1, "n/a", g_json_rel,
        "$.align, $.offset_applied_to_alice, $.yield_sweep (where present)", "derived_read_only")
    if "reproduction_gate" in g_json:
        add(stage, "threshold_or_gate_record",
            "alignment reproduction-gate record as recorded; values live in the source artifact — "
            "G4 does not restate or evaluate gate arithmetic (Wilson/B_tail/delta_min N/A for G4).",
            "%s run" % stage, False, 0, 1, "n/a", g_json_rel, "$.reproduction_gate",
            "derived_read_only")
    a1 = must(cal, "a1_cal_ids", cal_rel)
    c32 = must(cal, "cal_frame_ids", cal_rel)
    r1 = add(stage, "cal_frame_list",
             "sacrificed A1-CAL frame IDs as frozen: count=%d, ranges %s (listed exactly as "
             "recorded; never re-derived, re-allocated or edited)" % (len(a1), ranges_text(a1)),
             "operator freeze (segment layout rule)", False, 0, len(a1), "frame IDs at freeze",
             cal_rel, "$.a1_cal_ids", "frozen")
    r2 = add(stage, "cal_frame_list",
             "sacrificed CAL32 frame IDs as frozen: count=%d, ranges %s (listed exactly as "
             "recorded; never re-derived, re-allocated or edited)" % (len(c32), ranges_text(c32)),
             "operator freeze (segment layout rule)", False, 0, len(c32), "frame IDs at freeze",
             cal_rel, "$.cal_frame_ids", "frozen")
    # SC5: inventory CAL rows must be byte-identical to their source arrays (set equality).
    check("SC5_rows_match_source_%s" % stage,
          r1["message"].find(ranges_text(a1)) >= 0 and len(a1) == r1["count"]
          and r2["message"].find(ranges_text(c32)) >= 0 and len(c32) == r2["count"],
          "inventory CAL rows vs %s" % cal_rel)
    closure = read_json(closure_rel)
    res_ids = closure.get("reserve_frame_ids", [])
    add(stage, "ledger_allocation",
        "closure ledger/layout record: ledger_complete_frames=%s, reserve frames count=%d (ranges "
        "%s); layout rule '%s'; segment lists byte-equal to the stage cal_ids.json (SC5)."
        % (closure.get("ledger_complete_frames"), len(res_ids), ranges_text(res_ids) if res_ids else "(none recorded)",
           closure.get("layout_rule", "")),
        "%s closure run" % stage, False, 0, 1, "n/a", closure_rel,
        "$.ledger_complete_frames, $.reserve_frame_ids, $.layout_rule (companion: %s)" % closure_field,
        "frozen")
    freeze_keys = sorted(freeze_cfg.keys())
    add(stage, "threshold_or_gate_record",
        "freeze config published (TO-FREEZE windows/gates/CAL lists/thresholds as recorded; "
        "%d top-level keys: %s). Values are referenced by locator, never re-derived; gate VALUES "
        "are not restated by G4." % (len(freeze_keys), ", ".join(freeze_keys)),
        "%s freeze (packet)" % stage, False, 0, 1, "n/a", freeze_cfg_rel, "$ (all top-level keys)",
        "frozen")
    cal_field = must(g_json, "cal", g_json_rel)
    triple = must(cal_field, "m2_triple", g_json_rel + "$.cal")
    add(stage, "fitted_prior",
        "fitted M2 +/-1 parametric triple per session as recorded: " + jdump(triple) +
        " — fit on %s sacrificed CAL frames (%s pairs); accounted via CAL sacrifice and excluded "
        "from the key denominator; no lambda_prior term is asserted."
        % (cal_field.get("n_frames"), cal_field.get("n_pairs")),
        "estimator (CAL fit on sacrificed frames)", False, 0, 1, "CAL frame IDs at freeze",
        g_json_rel, "$.cal.m2_triple", "derived_read_only")
    for run_rel in run_logs:
        head = read_text(run_rel).splitlines()[0] if read_text(run_rel).strip() else ""
        check("SC10_runlog_heading_%s" % run_rel.split("/")[-1], "run log" in head.lower(),
              head[:80])
        add(stage, "result_publication",
            "public run log record: %s (first line: %s); gate/NLL/undetected lines quoted as "
            "recorded in the source." % (run_rel, head),
            "%s run" % stage, False, 0, 1, "n/a", run_rel, "lines 1-6", "derived_read_only")
    rid = status_result_id(status_rel)
    adj_txt = read_text(adj_rel)
    m_label = re.search(r"Label:\s*`([A-Za-z0-9_]+)`", adj_txt)
    label_part = ("; adjudication label = `%s`" % m_label.group(1)) if m_label else ""
    add(stage, "result_publication",
        "frozen adjudication result as recorded: result.id = %s%s (quoted verbatim as a public "
        "announcement from %s; G4 asserts nothing from it — no FER/efficiency/qualification "
        "claim)." % (rid, label_part, adj_rel),
        "main-thread adjudication", False, 0, 1, "n/a", status_rel, "$.result.id", "frozen")
    if "gates" in g_json:
        add(stage, "threshold_or_gate_record",
            "gate records (delta_tail / nll) as recorded; values live in the source artifact — "
            "G4 does not restate or evaluate gate arithmetic (Wilson/B_tail/delta_min N/A).",
            "%s run" % stage, False, 0, 1, "n/a", g_json_rel, "$.gates", "derived_read_only")
    blocked_rows(stage, session_label)
    # tag row: contract tag_master value from the stage freeze config (+ invocation count where recorded)
    add(stage, "tag",
        "tag_master = %s recorded in the stage freeze config (contract value). Tag invocation "
        "count for this stage: see disclosure_recount where present; where this stage executed no "
        "decoder the invocation count is 0 and no tag output field exists in the stage outputs."
        % tag_master_value,
        "verifier contract (Toeplitz tag from frozen TAG_MASTER)", False,
        "N/A (G4 records no tag bit charge; frozen artifacts record tag counts only)", 0,
        "tag_master %s" % tag_master_value, tag_master_art, tag_master_loc, "frozen")
    return rid


def build(freeze, check_only):
    t0 = time.time()
    fc = freeze["frozen_constants"]

    # ---- SC3: branch + authorization -------------------------------------------------
    head = read_text(".git/HEAD").strip()
    check("SC3a_branch", head == "ref: refs/heads/codex/nbpolar-phase0", head)
    g4_status = read_text(".workbuddy/queue/NBPOLAR-M2-PRIOR-G4-INVENTORY/STATUS.yaml")
    not_auth = re.search(r"^authorizations:\s*\[\]", g4_status, re.M)
    check("SC3b_authorization_recorded",
          not (not_auth is not None) and AUTHORIZED_LINE in g4_status,
          "authorizations empty" if not_auth else ("AUTHORIZED line present: %s"
                                                   % (AUTHORIZED_LINE in g4_status)))

    # ---- SC2: TO-FREEZE pointers resolve and are non-null ----------------------------
    pointers = freeze.get("to_freeze", [])
    check("SC2a_to_freeze_pointer_list", isinstance(pointers, list) and len(pointers) > 0,
          "%d pointers" % len(pointers))
    nulls = []
    for ptr in pointers:
        obj = freeze
        for part in ptr.split("."):
            if isinstance(obj, dict) and part in obj:
                obj = obj[part]
            else:
                obj = "<MISSING>"
                break
        if obj == "<MISSING>" or obj is None or obj == "" or obj == []:
            nulls.append(ptr)
    check("SC2b_to_freeze_non_null", not nulls, "null/empty: %s" % nulls)

    # ---- SC1: manifest path existence + locators -------------------------------------
    manifest = freeze["input_manifest"]
    missing = [it["path"] for it in manifest
               if not (it.get("exists") is True and os.path.exists(abspath(it["path"])))]
    no_loc = [it["path"] for it in manifest if not it.get("locators_used")]
    check("SC1a_input_paths_exist", not missing, "missing: %s" % missing)
    check("SC1b_locators_non_empty", not no_loc, "no locators: %s" % no_loc)
    check("SC1c_manifest_count", len(manifest) == freeze["manifest_count"],
          "%d vs manifest_count %s" % (len(manifest), freeze["manifest_count"]))

    # ---- SC4: target-output absence --------------------------------------------------
    existing = [p for p in OUT_PATHS if os.path.exists(p)]
    check("SC4_target_outputs_absent", not existing, "already exist: %s" % existing)

    # ---- SC10: constant agreement + md locator spot checks (string/record equality) ---
    construction = read_json(CONSTRUCTION)
    cell = must(construction, "cell", CONSTRUCTION)
    check("SC10a_N_K_agreement",
          (cell["n"] == fc["N"] and cell["k1"] == fc["K1"] and cell["k2"] == fc["K2"]),
          "cell n/k1/k2 vs frozen constants")
    check("SC10b_orders_len",
          isinstance(cell["l1_order"], list) and isinstance(cell["l2_order"], list)
          and len(cell["l1_order"]) == fc["N"] == len(cell["l2_order"]),
          "l1/l2 order presence + length (no digest computed)")
    g2s = read_json(rel(G2, "g2_summary.json"))
    g3s = read_json(rel(G3, "g3_summary.json"))
    check("SC10c_p16_digest_string",
          must(g2s, "construction", "g2_summary")["inner_digest"] == fc["p16_digest"]
          == must(g3s, "construction", "g3_summary")["inner_digest"],
          "inner_digest string equality vs frozen digest")
    g2f = read_json(rel(PK3, "g2_freeze_config.json"))
    g3f = read_json(rel(PK4, "g3_freeze_config.json"))
    check("SC10d_window_mod_skip_agreement",
          g2f["pairing_window_primary"] == g3f["pairing_window_primary"] == fc["W_P"]
          and g2f["pairing_window_sensitivity"] == g3f["pairing_window_sensitivity"] == fc["W_S"]
          and g2f["mod_boundary"] == g3f["mod_boundary"] == fc["MOD"]
          and g2f["skip_frames"] == g3f["skip_frames"] == fc["skip"],
          "w/mod/skip in g2/g3 freeze configs vs frozen constants")
    check("SC10e_tag_master_agreement",
          g2f["tag_master"] == fc["g2_tag_master"] and g3f["tag_master"] == fc["g3_tag_master"],
          "tag_master values vs frozen constants")
    g1j = read_json(rel(G1, "g1.json"))
    check("SC10f_frame_pairs_bin",
          must(g1j, "pairing", "g1.json")["frozen"]["frame_pairs"] == fc["frame_pairs"]
          and must(g1j, "pairing", "g1.json")["frozen"]["bin_width_ps"] == int(str(fc["bin"]).split()[0]),
          "frame_pairs/bin_width_ps vs frozen constants")
    check("SC10g_floor_chunk_line",
          line_contains(rel(PK3, "g2_freeze.md"), 91, "chunk_rows %d; floor %s"
                        % (fc["chunk"], str(fc["floor"]))),
          "g2_freeze.md line 91")
    # sigma STRING consistency (allowed: adjudication item 6; NO numeric work)
    sigma_str = repr(fc["census_sigma"])
    sigma_art = repr(g3s["align"]["peak_sigma_ps"])
    check("SC10h_sigma_string_consistency",
          sigma_str == sigma_art
          and sigma_str in read_text(rel(PK4, "G3_ADJUDICATION.md"))
          and sigma_str in read_text(DECISION_LOG),
          "sigma string across g3_summary / G3_ADJUDICATION / decision-log: %s" % sigma_str)
    check("SC10i_md_locators",
          line_contains(DECISION_LOG, 5327, "fail-closed public-message inventory")
          and line_contains(SEC_MODEL, 140, "fitted triple (q0, q+1, q−1)")
          and line_contains(SEC_MODEL, 141, "reveal bits (~18–22, diagnostic)")
          and line_contains(rel(PK1, "G1_ADJUDICATION.md"), 20, "G1 verdict: bounded negative")
          and ("NBPOLAR_M2_PRIOR_G1R2_COMPLETE_DESCRIPTIVE" in read_text(rel(PK2, "G1R2_ADJUDICATION.md")))
          and ("NBPOLAR_M2_PRIOR_G2_SUCCESS" in read_text(rel(PK3, "G2_ADJUDICATION.md")))
          and ("NBPOLAR_M2_PRIOR_G3_SUCCESS" in read_text(rel(PK4, "G3_ADJUDICATION.md"))),
          "markdown locator spot checks")

    # ---- SC5: CAL set-equality matrix ------------------------------------------------
    g1_cal = read_json(rel(G1, "cal_ids.json"))
    g1_closure = read_json(rel(G1, "cal_ids_closure.json"))
    g1_freeze = read_json(rel(PK1, "g1_freeze_config.json"))
    r2_cal = read_json(rel(G1R2, "cal_ids.json"))
    r2_closure = read_json(rel(G1R2, "cal_ids_closure.json"))
    r2_freeze = read_json(rel(PK2, "g1r2_freeze_config.json"))
    g2_cal = read_json(rel(G2, "cal_ids.json"))
    g3_cal = read_json(rel(G3, "cal_ids.json"))
    g3_input_freeze = read_json(rel(G3, "input/g3_freeze_config.json"))
    shg1_sources = {"g1": g1_cal, "g1_closure": g1_closure, "g1_freeze": g1_freeze,
                    "g1r2": r2_cal, "g1r2_closure": r2_closure, "g1r2_freeze": r2_freeze,
                    "g2": g2_cal, "g2_freeze": g2f}
    eq_fail = [k for k, v in shg1_sources.items()
               if v["a1_cal_ids"] != g1_cal["a1_cal_ids"]
               or v["cal_frame_ids"] != g1_cal["cal_frame_ids"]]
    check("SC5a_shg1_cal_set_equality", not eq_fail,
          "sources differing from g1 cal_ids.json: %s" % eq_fail)
    check("SC5b_g1_closure_common_lists",
          all(g1_cal[k] == g1_closure[k] for k in
              ("a1_cal_ids", "cal_frame_ids", "char_frame_ids", "heldout_frame_ids", "eval_frame_ids"))
          and all(r2_cal[k] == r2_closure[k] for k in
                  ("a1_cal_ids", "cal_frame_ids", "char_frame_ids", "heldout_frame_ids", "eval_frame_ids")),
          "cal_ids vs cal_ids_closure common list keys")
    check("SC5c_g2_eval_blocks", g2_cal["eval_blocks"] == g2f["eval_blocks"], "g2 eval_blocks")
    g3_cal_ids_ok = (g3_cal["a1_cal_ids"] == g3f["a1_cal_ids"] == g3_input_freeze["a1_cal_ids"]
                     and g3_cal["cal_frame_ids"] == g3f["cal_frame_ids"]
                     == g3_input_freeze["cal_frame_ids"])
    check("SC5d_shg2_cal_set_equality", g3_cal_ids_ok and g3_cal["eval_blocks"] == g3f["eval_blocks"],
          "shg_2 cal_ids vs packet freeze vs input freeze copy")
    exp = freeze["cal_frames_to_list"]
    check("SC5e_cal_counts_expected",
          len(g1_cal["a1_cal_ids"]) == exp["shg_1"]["a1_cal"]["expected_count"]
          and len(g1_cal["cal_frame_ids"]) == exp["shg_1"]["cal32"]["expected_count"]
          and len(g3_cal["a1_cal_ids"]) == exp["shg_2"]["a1_cal"]["expected_count"]
          and len(g3_cal["cal_frame_ids"]) == exp["shg_2"]["cal32"]["expected_count"],
          "cal list lengths vs frozen expectations")

    # ---- SC6: disclosure recount cross-check -----------------------------------------
    frozen_recount = freeze["recount_cross_check_frozen"]
    recount = {}
    for stage, d in (("G2", G2), ("G3", G3)):
        rows = read_jsonl(rel(d, "per_block_outcomes.jsonl"))
        summary = g2s if stage == "G2" else g3s
        key_sum = sum(r["key_dependent_bits"] for r in rows)
        pub_sum = sum(r["public_control_bits"] for r in rows)
        und = sum(1 for r in rows if r["undetected"] is True)
        rc = must(summary, "disclosure_recount", stage + "_summary")
        arms_und = sum(must(must(summary, "arms", stage + "_summary")[a], "outcomes", "arm")
                       ["undetected"] for a in must(summary, "arms", stage + "_summary"))
        ok = (len(rows) == frozen_recount["expected_block_rows"]
              and key_sum == frozen_recount["key_bits"]
              and pub_sum == frozen_recount["public_bits"]
              and rc["recount"]["key_dependent_bits"] == key_sum
              and rc["recount"]["public_control_bits"] == pub_sum
              and rc["incremental"] == rc["recount"]
              and rc["mismatches"] == []
              and rc["recount"]["tag_invocations"] == frozen_recount["tags"]
              and und == arms_und)
        check("SC6_recount_%s" % stage, ok,
              "rows=%d key=%d public=%d tags=%d undetected=%d mismatch_list=%s"
              % (len(rows), key_sum, pub_sum, rc["recount"]["tag_invocations"], und,
                 rc["mismatches"]))
        recount[stage] = {"rows": len(rows), "key": key_sum, "public": pub_sum,
                          "tags": rc["recount"]["tag_invocations"], "undetected": und}

    # ---- row construction -------------------------------------------------------------
    build_contract_rows(fc, cell)

    # G1 -------------------------------------------------------------------------------
    g1_tag_master = g1_freeze["tag_master"]
    build_stage_records(
        "G1", "SHG `_1`, G1 w=500/LINEAR contract", g1j, rel(G1, "g1.json"), g1_cal,
        rel(G1, "cal_ids.json"), rel(G1, "cal_ids_closure.json"),
        rel(G1, "g1_closure_reproduction.json"), g1_freeze, rel(PK1, "g1_freeze_config.json"),
        [rel(G1, "run_log.md"), rel(G1, "run_log_closure.md")],
        rel(PK1, "STATUS.yaml"), rel(PK1, "G1_ADJUDICATION.md"),
        g1_tag_master, rel(PK1, "g1_freeze_config.json"), "$.tag_master")
    add_none("G1", "tag", extra=
             "g1.json and the G1 output artifacts contain no tag/tag_invoked/tag_pass field "
             "(G1 was decoder-free: 0 tag invocations); the stage tag_master contract value %s is "
             "recorded separately in the G1 tag row from g1_freeze_config.json" % g1_tag_master)

    # G1R2 -----------------------------------------------------------------------------
    g1r2j = read_json(rel(G1R2, "g1.json"))
    g1r2_freeze_cfg = read_json(rel(PK2, "g1r2_freeze_config.json"))
    g1r2_tag_master = g1r2_freeze_cfg["tag_master"]
    build_stage_records(
        "G1R2", "SHG `_1`, G1R2 w=200/CIRCULAR contract", g1r2j, rel(G1R2, "g1.json"), r2_cal,
        rel(G1R2, "cal_ids.json"), rel(G1R2, "cal_ids_closure.json"),
        rel(G1R2, "g1_closure.json"), g1r2_freeze_cfg, rel(PK2, "g1r2_freeze_config.json"),
        [rel(G1R2, "run_log.md"), rel(G1R2, "run_log_closure.md")],
        rel(PK2, "STATUS.yaml"), rel(PK2, "G1R2_ADJUDICATION.md"),
        g1r2_tag_master, rel(PK2, "g1r2_freeze_config.json"), "$.tag_master")
    add_none("G1R2", "tag", extra=
             "g1.json and the G1R2 output artifacts contain no tag/tag_invoked/tag_pass field "
             "(G1R2 was decoder-free: 0 tag invocations); the stage tag_master contract value %s "
             "(later INHERITED by G2) is recorded separately in the G1R2 tag row from "
             "g1r2_freeze_config.json" % g1r2_tag_master)

    # G2 --------------------------------------------------------------------------------
    add("G2", "contract_param",
        "as-executed contract record as recorded: " + jdump(must(g2s, "contract", "g2_summary")),
        "G2 one-shot decode run", False, 0, 1, "n/a", rel(G2, "g2_summary.json"),
        "$.contract (freeze basis: %s §Contract values)" % rel(PK3, "g2_freeze.md"),
        "derived_read_only")
    add("G2", "ledger_allocation",
        "ledger/frame allocation as recorded: " + jdump(must(g2s, "ledger", "g2_summary")),
        "G2 closure/run", False, 0, 1, "n/a", rel(G2, "g2_summary.json"), "$.ledger",
        "derived_read_only")
    add("G2", "alignment_record",
        "alignment record as recorded: " + jdump(must(g2s, "align", "g2_summary")) +
        " (SHG `_1` alignment; G4 derives nothing)",
        "G1-derived alignment (recorded in G2 summary)", False, 0, 1, "n/a",
        rel(G2, "g2_summary.json"), "$.align", "derived_read_only")
    g2_a1 = g2_cal["a1_cal_ids"]
    g2_c32 = g2_cal["cal_frame_ids"]
    rr1 = add("G2", "cal_frame_list",
              "sacrificed A1-CAL frame IDs as frozen: count=%d, ranges %s (byte-equal membership "
              "to the SHG `_1` session lists — SC5)" % (len(g2_a1), ranges_text(g2_a1)),
              "operator freeze (segment layout rule)", False, 0, len(g2_a1),
              "frame IDs at freeze", rel(G2, "cal_ids.json"), "$.a1_cal_ids", "frozen")
    rr2 = add("G2", "cal_frame_list",
              "sacrificed CAL32 frame IDs as frozen: count=%d, ranges %s (byte-equal membership to "
              "the SHG `_1` session lists — SC5)" % (len(g2_c32), ranges_text(g2_c32)),
              "operator freeze (segment layout rule)", False, 0, len(g2_c32),
              "frame IDs at freeze", rel(G2, "cal_ids.json"), "$.cal_frame_ids", "frozen")
    check("SC5_rows_match_source_G2",
          rr1["count"] == len(g2_a1) and rr2["count"] == len(g2_c32), "g2 CAL rows vs source")
    add("G2", "ledger_allocation",
        "EVAL block layout as recorded: %d blocks, ranges %s (eval_blocks; COMPLETE-BLOCKS-ONLY "
        "rule quoted from the freeze, never re-allocated)" % (len(g2_cal["eval_blocks"]),
                                                              ranges_text([b[0] for b in g2_cal["eval_blocks"]])),
        "G2 freeze (block formation)", False, 0, len(g2_cal["eval_blocks"]), "n/a",
        rel(G2, "cal_ids.json"), "$.eval_blocks", "frozen")
    g2_triple = must(must(g2s, "arms", "g2_summary")["B_M2_32f_candidate"], "triple", "arm B")
    add("G2", "fitted_prior",
        "fitted M2 +/-1 triple (B arm) as recorded: " + jdump(g2_triple) +
        " — fit on 32 sacrificed CAL frames (8192 pairs); accounted via CAL sacrifice; no "
        "lambda_prior term is asserted.",
        "estimator (CAL fit on sacrificed frames)", False, 0, 1, "CAL frame IDs at freeze",
        rel(G2, "g2_summary.json"), "$.arms.B_M2_32f_candidate.triple", "derived_read_only")
    g2_rows = read_jsonl(rel(G2, "per_block_outcomes.jsonl"))
    rc2 = recount["G2"]
    add("G2", "disclosure_bits",
        "per-block key-dependent disclosure summed over the frozen per_block_outcomes.jsonl rows: "
        "key_dependent_bits total = %d over %d rows — equals the frozen recount %d "
        "(34119 x 42); counted to leakage (counted_in_leak_IR)."
        % (rc2["key"], rc2["rows"], frozen_recount["key_bits"]),
        "G2 one-shot decode run (verifier/accounting record)", True, rc2["key"], rc2["rows"],
        "n/a", rel(G2, "per_block_outcomes.jsonl"),
        "rows[*].key_dependent_bits (sum; cross-checked vs g2_summary $.disclosure_recount)",
        "derived_read_only")
    add("G2", "disclosure_bits",
        "per-block public control disclosure summed over the frozen rows: public_control_bits "
        "total = %d over %d rows — equals the frozen recount %d (327743 x 42); counted to leakage "
        "(counted_in_leak_IR)." % (rc2["public"], rc2["rows"], frozen_recount["public_bits"]),
        "G2 one-shot decode run (verifier/accounting record)", False, rc2["public"], rc2["rows"],
        "n/a", rel(G2, "per_block_outcomes.jsonl"),
        "rows[*].public_control_bits (sum; cross-checked vs g2_summary $.disclosure_recount)",
        "derived_read_only")
    add("G2", "result_publication",
        "disclosure recount record as published: incremental == recount, mismatches = [] "
        "(values in source; see the disclosure cross-check block).",
        "G2 accounting self-check", False, 0, 1, "n/a", rel(G2, "g2_summary.json"),
        "$.disclosure_recount", "frozen")
    add("G2", "tag",
        "Toeplitz tags: tag_invocations = %d recorded from tag_master %s (42 tags for the "
        "three-arm run; one 64-bit tag per block as frozen by D7). G4 records no tag bit charge — "
        "frozen artifacts record tag counts only; tags are NOT part of the key/public bit sums."
        % (rc2["tags"], fc["g2_tag_master"]),
        "verifier (per-block tag from frozen TAG_MASTER)", False,
        "N/A (tag bit charge not recorded in frozen artifacts; G4 counts invocations only)",
        rc2["tags"], "tag_master %s" % fc["g2_tag_master"], rel(G2, "g2_summary.json"),
        "$.disclosure_recount.recount.tag_invocations (contract: %s $.tag_master)"
        % rel(PK3, "g2_freeze_config.json"), "frozen")
    add("G2", "result_publication",
        "undetected outcomes: %d of %d rows as recorded — ISOLATED row, never merged into any "
        "success/FER number; G4 asserts no success, no FER, no efficiency."
        % (rc2["undetected"], rc2["rows"]),
        "G2 one-shot decode run (outcome record)", False, 0, rc2["rows"], "n/a",
        rel(G2, "per_block_outcomes.jsonl"),
        "rows[*].undetected (count; agrees with g2_summary $.arms.*.outcomes.undetected)",
        "derived_read_only")
    add("G2", "threshold_or_gate_record",
        "preregistered gate record as published; values live in the source artifacts — G4 does "
        "not restate or evaluate gate arithmetic (Wilson/B_tail/delta_min/g2_blocks N/A for G4).",
        "G2 freeze (gates preregistered before run)", False, 0, 1, "n/a",
        rel(G2, "g2_summary.json"), "$.gate (freeze basis: %s §Gates)" % rel(PK3, "g2_freeze.md"),
        "frozen")
    add("G2", "result_publication",
        "per-block outcome distribution as recorded: " +
        jdump({a: must(must(g2s, "arms", "g2_summary")[a], "outcomes", "arm")
               for a in must(g2s, "arms", "g2_summary")}) +
        " (quoted as recorded; G4 asserts nothing from it).",
        "G2 one-shot decode run", False, 0, 1, "n/a", rel(G2, "g2_summary.json"),
        "$.arms.*.outcomes", "derived_read_only")
    add("G2", "result_publication",
        "per-block NLL fields (nll_l2_trueH_bits, nll_l2_candH_bits) recorded for %d rows "
        "(values in source; domain labels are a G3 record)." % len(g2_rows),
        "G2 one-shot decode run", False, 0, len(g2_rows), "n/a",
        rel(G2, "per_block_outcomes.jsonl"), "rows[*].nll_l2_*_bits", "derived_read_only")
    g2_head = read_text(rel(G2, "run_log.md")).splitlines()[0]
    check("SC10j_runlog_heading_g2", "run log" in g2_head.lower(), g2_head[:80])
    add("G2", "result_publication",
        "public one-shot run log record: %s (first line: %s); arms/gate/undetected lines are "
        "quoted as recorded in the source." % (rel(G2, "run_log.md"), g2_head),
        "G2 one-shot decode run", False, 0, 1, "n/a", rel(G2, "run_log.md"), "lines 1-6",
        "derived_read_only")
    g2_rid = status_result_id(rel(PK3, "STATUS.yaml"))
    add("G2", "result_publication",
        "frozen adjudication result as recorded: result.id = %s; adjudication label = "
        "`NBPOLAR_M2_PRIOR_G2_SUCCESS` (quoted verbatim as a public announcement from %s; G4 "
        "asserts nothing from it — no FER/efficiency/qualification claim)."
        % (g2_rid, rel(PK3, "G2_ADJUDICATION.md")),
        "main-thread adjudication", False, 0, 1, "n/a", rel(PK3, "STATUS.yaml"), "$.result.id",
        "frozen")
    blocked_rows("G2", "SHG `_1`, G2 three-arm one-shot decode")
    cover_expected("G2", freeze["expected_classes_by_stage"]["G2"])

    # G3 --------------------------------------------------------------------------------
    add("G3", "contract_param",
        "as-executed contract record as recorded: " + jdump(must(g3s, "contract", "g3_summary")),
        "G3 one-shot decode run", False, 0, 1, "n/a", rel(G3, "g3_summary.json"),
        "$.contract (INHERITED from SHG `_1` frozen rules)", "derived_read_only")
    g3j = read_json(rel(G3, "g3.json"))
    add("G3", "ledger_allocation",
        "G3 closure/layout record as recorded: segments " + jdump(must(g3j, "segments", "g3.json")) +
        ", n_eval_blocks=%s, disjointness_all_disjoint=%s"
        % (g3j.get("n_eval_blocks"), g3j.get("disjointness_all_disjoint")),
        "G3 closure run", False, 0, 1, "n/a", rel(G3, "g3.json"),
        "$.segments, $.n_eval_blocks, $.disjointness_all_disjoint", "derived_read_only")
    add("G3", "ledger_allocation",
        "ledger/frame allocation as recorded: " + jdump(must(g3s, "ledger", "g3_summary")),
        "G3 closure/run", False, 0, 1, "n/a", rel(G3, "g3_summary.json"), "$.ledger",
        "derived_read_only")
    add("G3", "alignment_record",
        "alignment record as recorded: " + jdump(must(g3s, "align", "g3_summary")) +
        " (SHG `_2`; peak_sigma_ps is the frozen quoted census value, never recomputed in G4)",
        "G1-derived inherited alignment (recorded in G3 summary)", False, 0, 1, "n/a",
        rel(G3, "g3_summary.json"), "$.align", "derived_read_only")
    g3_a1 = g3_cal["a1_cal_ids"]
    g3_c32 = g3_cal["cal_frame_ids"]
    gr1 = add("G3", "cal_frame_list",
              "sacrificed A1-CAL frame IDs as recorded: count=%d, ranges %s (byte-equal membership "
              "to g3_freeze_config.json and its input copy — SC5)" % (len(g3_a1), ranges_text(g3_a1)),
              "operator freeze (segment layout rule)", False, 0, len(g3_a1),
              "frame IDs at freeze", rel(G3, "cal_ids.json"), "$.a1_cal_ids", "frozen")
    gr2 = add("G3", "cal_frame_list",
              "sacrificed CAL32 frame IDs as recorded: count=%d, ranges %s (byte-equal membership "
              "to g3_freeze_config.json and its input copy — SC5)" % (len(g3_c32), ranges_text(g3_c32)),
              "operator freeze (segment layout rule)", False, 0, len(g3_c32),
              "frame IDs at freeze", rel(G3, "cal_ids.json"), "$.cal_frame_ids", "frozen")
    check("SC5_rows_match_source_G3",
          gr1["count"] == len(g3_a1) and gr2["count"] == len(g3_c32), "g3 CAL rows vs source")
    add("G3", "ledger_allocation",
        "EVAL block layout as recorded: %d blocks, ranges %s (eval_blocks; COMPLETE-BLOCKS-ONLY "
        "quoted from the freeze, never re-allocated)"
        % (len(g3_cal["eval_blocks"]), ranges_text([b[0] for b in g3_cal["eval_blocks"]])),
        "G3 freeze (block formation, INHERITED)", False, 0, len(g3_cal["eval_blocks"]), "n/a",
        rel(G3, "cal_ids.json"), "$.eval_blocks", "frozen")
    g3_triple = must(must(g3s, "arms", "g3_summary")["B_M2_32f_candidate"], "triple", "arm B")
    add("G3", "fitted_prior",
        "fitted M2 +/-1 triple (B arm) as recorded: " + jdump(g3_triple) +
        " — fit on 32 sacrificed CAL frames (8192 pairs); accounted via CAL sacrifice; no "
        "lambda_prior term is asserted.",
        "estimator (CAL fit on sacrificed frames)", False, 0, 1, "CAL frame IDs at freeze",
        rel(G3, "g3_summary.json"), "$.arms.B_M2_32f_candidate.triple", "derived_read_only")
    rc3 = recount["G3"]
    add("G3", "disclosure_bits",
        "per-block key-dependent disclosure summed over the frozen per_block_outcomes.jsonl rows: "
        "key_dependent_bits total = %d over %d rows — equals the frozen recount %d "
        "(34119 x 42); counted to leakage (counted_in_leak_IR)."
        % (rc3["key"], rc3["rows"], frozen_recount["key_bits"]),
        "G3 one-shot decode run (verifier/accounting record)", True, rc3["key"], rc3["rows"],
        "n/a", rel(G3, "per_block_outcomes.jsonl"),
        "rows[*].key_dependent_bits (sum; cross-checked vs g3_summary $.disclosure_recount)",
        "derived_read_only")
    add("G3", "disclosure_bits",
        "per-block public control disclosure summed over the frozen rows: public_control_bits "
        "total = %d over %d rows — equals the frozen recount %d (327743 x 42); counted to leakage "
        "(counted_in_leak_IR)." % (rc3["public"], rc3["rows"], frozen_recount["public_bits"]),
        "G3 one-shot decode run (verifier/accounting record)", False, rc3["public"], rc3["rows"],
        "n/a", rel(G3, "per_block_outcomes.jsonl"),
        "rows[*].public_control_bits (sum; cross-checked vs g3_summary $.disclosure_recount)",
        "derived_read_only")
    add("G3", "result_publication",
        "disclosure recount record as published: incremental == recount, mismatches = [] "
        "(values in source; see the disclosure cross-check block).",
        "G3 accounting self-check", False, 0, 1, "n/a", rel(G3, "g3_summary.json"),
        "$.disclosure_recount", "frozen")
    add("G3", "tag",
        "Toeplitz tags: tag_invocations = %d recorded from tag_master %s (42 tags for the "
        "three-arm run; one 64-bit tag per block as frozen by D7). G4 records no tag bit charge — "
        "frozen artifacts record tag counts only; tags are NOT part of the key/public bit sums."
        % (rc3["tags"], fc["g3_tag_master"]),
        "verifier (per-block tag from frozen TAG_MASTER)", False,
        "N/A (tag bit charge not recorded in frozen artifacts; G4 counts invocations only)",
        rc3["tags"], "tag_master %s" % fc["g3_tag_master"], rel(G3, "g3_summary.json"),
        "$.disclosure_recount.recount.tag_invocations (contract: %s $.tag_master)"
        % rel(PK4, "g3_freeze_config.json"), "frozen")
    add("G3", "result_publication",
        "undetected outcomes: %d of %d rows as recorded — ISOLATED row, never merged into any "
        "success/FER number; G4 asserts no success, no FER, no efficiency."
        % (rc3["undetected"], rc3["rows"]),
        "G3 one-shot decode run (outcome record)", False, 0, rc3["rows"], "n/a",
        rel(G3, "per_block_outcomes.jsonl"),
        "rows[*].undetected (count; agrees with g3_summary $.arms.*.outcomes.undetected)",
        "derived_read_only")
    add("G3", "threshold_or_gate_record",
        "preregistered gate record as published; values live in the source artifacts — G4 does "
        "not restate or evaluate gate arithmetic (Wilson/B_tail/delta_min/g3_blocks N/A for G4).",
        "G3 freeze (gates preregistered before run)", False, 0, 1, "n/a",
        rel(G3, "g3_summary.json"), "$.gate (packet freeze basis: %s)" % rel(PK4, "g3_freeze_config.json"),
        "frozen")
    add("G3", "result_publication",
        "per-block outcome distribution as recorded: " +
        jdump({a: must(must(g3s, "arms", "g3_summary")[a], "outcomes", "arm")
               for a in must(g3s, "arms", "g3_summary")}) +
        " (quoted as recorded; G4 asserts nothing from it).",
        "G3 one-shot decode run", False, 0, 1, "n/a", rel(G3, "g3_summary.json"),
        "$.arms.*.outcomes", "derived_read_only")
    add("G3", "result_publication",
        "per-block NLL fields with frozen domain labels as recorded: nll_l2_trueH_bits / "
        "nll_l2_candH_bits + nll_l2_*_domain strings for %d rows (values and labels in source)."
        % len(read_jsonl(rel(G3, "per_block_outcomes.jsonl"))),
        "G3 one-shot decode run", False, 0, rc3["rows"], "n/a",
        rel(G3, "per_block_outcomes.jsonl"),
        "rows[*].nll_l2_*_bits, rows[*].nll_l2_*_domain; g3_summary $.nll_domains", "derived_read_only")
    part = must(g3s, "participation_disclosure", "g3_summary")
    add("G3", "participation_disclosure",
        "participation-disclosure statement as a listed public message (verbatim): \"" + part + "\"",
        "G3 packet (recorded verbatim in every G3 output)", False, 0, 1, "n/a",
        rel(G3, "g3_summary.json"), "$.participation_disclosure (also in g3.json, cal_ids.json, "
        "per_block_outcomes.jsonl rows, and %s §5)" % rel(PK4, "G3_ADJUDICATION_PREWRITE.md"),
        "frozen")
    g3_head = read_text(rel(G3, "run_log.md")).splitlines()[0]
    check("SC10j_runlog_heading_g3", "run log" in g3_head.lower(), g3_head[:80])
    add("G3", "result_publication",
        "public one-shot run log record: %s (first line: %s; participation line quoted as "
        "recorded in the source); arms/gate lines are quoted as recorded."
        % (rel(G3, "run_log.md"), g3_head),
        "G3 one-shot decode run", False, 0, 1, "n/a", rel(G3, "run_log.md"), "lines 1-6",
        "derived_read_only")
    g3_rid = status_result_id(rel(PK4, "STATUS.yaml"))
    add("G3", "result_publication",
        "frozen adjudication result as recorded: result.id = %s; adjudication label = "
        "`NBPOLAR_M2_PRIOR_G3_SUCCESS` (quoted verbatim as a public announcement from %s; G4 "
        "asserts nothing from it — no FER/efficiency/qualification claim)."
        % (g3_rid, rel(PK4, "G3_ADJUDICATION.md")),
        "main-thread adjudication", False, 0, 1, "n/a", rel(PK4, "STATUS.yaml"), "$.result.id",
        "frozen")
    blocked_rows("G3", "SHG `_2`, G3 three-arm confirmation decode")
    cover_expected("G3", freeze["expected_classes_by_stage"]["G3"])

    # coverage for CONTRACT / G1 / G1R2 (G2/G3 handled above) ---------------------------
    cover_expected("CONTRACT", freeze["expected_classes_by_stage"]["CONTRACT"])
    cover_expected("G1", freeze["expected_classes_by_stage"]["G1"])
    cover_expected("G1R2", freeze["expected_classes_by_stage"]["G1R2"])

    # ---- SC7: schema validity ----------------------------------------------------------
    ids = [r["id"] for r in ROWS]
    check("SC7a_unique_ids", len(ids) == len(set(ids)), "duplicate ids")
    schema_fields = ["id", "stage", "message_class", "message", "producer", "key_dependent",
                     "size_bits", "count", "seed_mask_code_ref", "source_artifact",
                     "source_locator", "release_handling", "status"]
    manifest_paths = {it["path"] for it in manifest}
    failures = []
    for r in ROWS:
        if sorted(r.keys()) != sorted(schema_fields):
            failures.append("%s: field set" % r["id"])
        if not (r["release_handling"] in RELEASE_HANDLING
                and r["message_class"] in MESSAGE_CLASSES
                and r["status"] in ROW_STATUS and r["stage"] in STAGES):
            failures.append("%s: enum membership" % r["id"])
        allowed = {CLASS_TO_HANDLING[r["message_class"]]}
        if r["message_class"] == "disclosure_bits" and r["status"] == "quoted":
            allowed.add("charged_0_labeled_public_ec_only_not_secure")
        if r["release_handling"] not in allowed:
            failures.append("%s: %s -> %s not in %s"
                            % (r["id"], r["message_class"], r["release_handling"], sorted(allowed)))
        if r["source_artifact"] not in manifest_paths:
            failures.append("%s: source outside manifest: %s" % (r["id"], r["source_artifact"]))
    check("SC7b_schema_enums_mapping_sources", not failures, "; ".join(failures[:10]))
    check("SC7c_zero_to_freeze_rows",
          all(r["status"] != "to_freeze" for r in ROWS), "rows still to_freeze")
    # expected-class completeness: every expected class has explicit rows or a none row
    for stage in STAGES:
        expected = freeze["expected_classes_by_stage"][stage]
        explicit = {r["message_class"] for r in ROWS if r["stage"] == stage}
        unmet = [c for c in expected
                 if c not in explicit and c not in none_named_classes(stage)]
        check("SC7d_expected_coverage_" + stage, not unmet, "unmet classes: %s" % unmet)

    # ---- SC8: countability -------------------------------------------------------------
    md = render_md(freeze, recount, g1_cal, g3_cal, t0)
    row_count = len(ROWS)
    by_stage = {s: sum(1 for r in ROWS if r["stage"] == s) for s in STAGES}
    by_class = {c: sum(1 for r in ROWS if r["message_class"] == c) for c in MESSAGE_CLASSES}
    by_handling = {h: sum(1 for r in ROWS if r["release_handling"] == h) for h in RELEASE_HANDLING}
    md_rows = md.count("| G4-")
    check("SC8a_row_count_agreement",
          row_count == sum(by_stage.values()) == sum(by_class.values())
          == sum(by_handling.values()) == md_rows,
          "json=%d stage=%d class=%d handling=%d md=%d"
          % (row_count, sum(by_stage.values()), sum(by_class.values()),
             sum(by_handling.values()), md_rows))
    check("SC8b_ids_sequential", all(
        [r["id"] for r in ROWS if r["stage"] == s]
        == ["G4-%s-%03d" % (s, i + 1) for i in range(by_stage[s])] for s in STAGES),
        "per-stage id sequences")

    inventory = {
        "packet": "NBPOLAR-M2-PRIOR-G4-INVENTORY",
        "generated_by": "g4_build_inventory.py (packet-local read-only builder; Phase-B one-shot)",
        "row_count": row_count,
        "rows": ROWS,
    }
    counts = build_counts(freeze, by_stage, by_class, by_handling, recount)
    check("SC8c_counts_sums",
          sum(counts["rows_by_stage"].values()) == row_count
          and sum(counts["rows_by_message_class"].values()) == row_count
          and sum(counts["rows_by_release_handling"].values()) == row_count,
          "counts sums vs row_count")

    # ---- SC9: budget ------------------------------------------------------------------
    elapsed = time.time() - t0
    rss = rss_gib_hwm()
    check("SC9a_wall_budget", elapsed <= freeze["budget"]["wall_s_max"],
          "%.2fs / %ss" % (elapsed, freeze["budget"]["wall_s_max"]))
    if rss is not None:
        check("SC9b_rss_budget", rss <= freeze["budget"]["rss_gib_max"],
              "%.3f GiB / %s GiB" % (rss, freeze["budget"]["rss_gib_max"]))

    if check_only:
        print("CHECK_ONLY_OK  checks=%d  rows=%d  by_stage=%s  wall=%.2fs  (nothing written)"
              % (len(CHECKS), row_count, by_stage, elapsed))
        still_there = [p for p in OUT_PATHS if os.path.exists(p)]
        if still_there:
            raise Blocker("check-only wrote files: %s" % still_there)
        return None

    # ---- write (only reached when ALL checks passed) -----------------------------------
    run_log = render_run_log(freeze, recount, elapsed, rss, row_count, by_stage)
    with open(OUT_PATHS[0], "w", encoding="utf-8") as fh:
        json.dump(inventory, fh, ensure_ascii=False, indent=2)
        fh.write("\n")
    with open(OUT_PATHS[1], "w", encoding="utf-8") as fh:
        fh.write(md)
    with open(OUT_PATHS[2], "w", encoding="utf-8") as fh:
        json.dump(counts, fh, ensure_ascii=False, indent=2)
        fh.write("\n")
    with open(OUT_PATHS[3], "w", encoding="utf-8") as fh:
        fh.write(run_log)

    # post-write verification (read-back arithmetic; same data, no rebuild semantics)
    back = json.load(open(OUT_PATHS[0], encoding="utf-8"))
    md_back = open(OUT_PATHS[1], encoding="utf-8").read()
    check("SC8d_postwrite_readback",
          back["row_count"] == len(back["rows"]) == md_back.count("| G4-")
          == sum(json.load(open(OUT_PATHS[2], encoding="utf-8"))["rows_by_stage"].values()),
          "read-back row_count agreement")
    with open(OUT_PATHS[3], "a", encoding="utf-8") as fh:
        fh.write("\n## Post-write read-back\n\n- SC8d_postwrite_readback: PASS — row_count == "
                 "len(JSON rows) == MD table rows == counts rows_by_stage sum, after re-reading "
                 "the written files.\n")
    print("BUILD_COMPLETE rows=%d wall=%.2fs outputs=%s"
          % (row_count, elapsed, ", ".join(os.path.basename(p) for p in OUT_PATHS)))
    return counts


def build_counts(freeze, by_stage, by_class, by_handling, recount):
    frozen = freeze["recount_cross_check_frozen"]
    key_sum = sum(r["size_bits"] for r in ROWS
                  if r["release_handling"] == "counted_in_leak_IR"
                  and r["key_dependent"] and isinstance(r["size_bits"], int))
    pub_sum = sum(r["size_bits"] for r in ROWS
                  if r["release_handling"] == "counted_in_leak_IR"
                  and not r["key_dependent"] and isinstance(r["size_bits"], int))
    tags_total = sum(r["count"] for r in ROWS if r["message_class"] == "tag")
    g1_cal = read_json(rel(G1, "cal_ids.json"))
    g3_cal = read_json(rel(G3, "cal_ids.json"))
    return {
        "rows_by_stage": by_stage,
        "rows_by_message_class": by_class,
        "rows_by_release_handling": by_handling,
        "key_bits_sum": key_sum,
        "public_bits_sum": pub_sum,
        "tags_total": tags_total,
        "cal_frames_listed": {
            "shg_1": len(g1_cal["a1_cal_ids"]) + len(g1_cal["cal_frame_ids"]),
            "shg_2": len(g3_cal["a1_cal_ids"]) + len(g3_cal["cal_frame_ids"]),
        },
        "cross_check": {
            "key": {"computed": {s: recount[s]["key"] for s in ("G2", "G3")},
                    "frozen": frozen["key_bits"],
                    "match": all(recount[s]["key"] == frozen["key_bits"] for s in ("G2", "G3"))},
            "public": {"computed": {s: recount[s]["public"] for s in ("G2", "G3")},
                       "frozen": frozen["public_bits"],
                       "match": all(recount[s]["public"] == frozen["public_bits"] for s in ("G2", "G3"))},
            "tags": {"computed": {s: recount[s]["tags"] for s in ("G2", "G3")},
                     "frozen": frozen["tags"],
                     "match": all(recount[s]["tags"] == frozen["tags"] for s in ("G2", "G3"))},
        },
        "sc_calls": 0,
        "tag_invocations": 0,
        "g4_runs": freeze["expected_counters"]["g4_runs"],
        "reruns": freeze["expected_counters"]["reruns"],
    }


def md_escape(text):
    return str(text).replace("|", "\\|").replace("\n", " ")


def render_md(freeze, recount, g1_cal, g3_cal, t0):
    fc = freeze["frozen_constants"]
    L = []
    A = L.append
    A("# G4 public-message inventory — NBPOLAR-M2-PRIOR-G4-INVENTORY (Release pattern, CAL frames listed)")
    A("")
    A("- packet: `NBPOLAR-M2-PRIOR-G4-INVENTORY` | change: `%s` | branch: `%s`"
      % (freeze["change"], freeze["branch"]))
    A("- generated by: `%s` at %s (budget: wall <= %s s, RSS <= %s GiB, single-threaded)"
      % (freeze["builder"], datetime.datetime.now().isoformat(timespec="seconds"),
         freeze["budget"]["wall_s_max"], freeze["budget"]["rss_gib_max"]))
    A("- authorization: recorded in this packet's `STATUS.yaml` `authorizations` before the build; "
      "independent Pre-EXECUTE review is a separate gate (this document is NOT self-approved).")
    A("")
    A("## Scope and no-claim statement")
    A("")
    A("G4 is a RECORD/AUDIT inventory only: it reads already-executed, already-adjudicated public "
      "messages of the frozen M2 track (G1 / G1R2 / G2 / G3), lists the sacrificed CAL frame IDs, "
      "and maps every row to one frozen Release-pattern handling class. G4 runs no decoder, makes "
      "no SC/tag call, reads no raw acquisition data, recomputes nothing (the census sigma is a "
      "**frozen quoted value, not recomputed in G4**), computes no lambda, no disclosure cap, no "
      "Wilson/B_tail/delta_min arithmetic, and no FER/efficiency/qualification/promotion/"
      "composable-key statement. S9 is never cited as FER/efficiency evidence.")
    A("")
    A("Closure domain — IN: every public message already emitted by G1 / G1R2 / G2 / G3, the CAL "
      "frame-ID detail per session, and the Release-pattern mapping. OUT: S8/S9 synthetic probe "
      "parameters, Stage-1 test outputs, and the Stage-3 measurement set (separate future packet, "
      "own freeze, own authorization). The census enters only as the quoted-sigma source.")
    A("")
    A("## Enumeration rule (frozen before the build)")
    A("")
    A("> %s" % freeze["enumeration_rule"])
    A("")
    A("Rows are entries with the frozen schema: %s. Every expected field class per stage is either "
      "covered by explicit rows or carries an explicit `none_recorded` row — never silence "
      "(exhaustive-first, adjudication item 4)." % ", ".join("`%s`" % f for f in freeze["row_schema_fields"]))
    A("")
    A("## Frozen constants (recorded verbatim; any change requires a NEW freeze)")
    A("")
    A("| # | key | value | handling |")
    A("|---|-----|-------|----------|")
    notes = freeze["frozen_constant_notes"]
    for i, (k, v) in enumerate(fc.items(), start=1):
        A("| %d | `%s` | `%s` | %s |" % (i, k, v, md_escape(notes.get(k, "recorded verbatim"))))
    A("")
    A("## CAL frames listed (sacrificed; excluded from the key denominator)")
    A("")
    A("Listed exactly as frozen in the `cal_ids*.json` artifacts — never re-derived, re-allocated "
      "or edited. Set-equality (SC5) holds across `cal_ids.json`, `cal_ids_closure.json`, the "
      "packet freeze configs and the inventory rows.")
    A("")
    for label, cal in (("SHG `_1` (session 20260113_SHG_Type2PPLN_3s)", g1_cal),
                       ("SHG `_2` (session 20260113_SHG_Type2PPLN_3s_2)", g3_cal)):
        a1 = cal["a1_cal_ids"]
        c32 = cal["cal_frame_ids"]
        A("### %s" % label)
        A("")
        A("- A1-CAL (%d frames): ranges `%s`" % (len(a1), ranges_text(a1)))
        A("- A1-CAL explicit IDs: %s" % ", ".join(str(x) for x in a1))
        A("- CAL32 (%d frames): ranges `%s`" % (len(c32), ranges_text(c32)))
        A("- CAL32 explicit IDs: %s" % ", ".join(str(x) for x in c32))
        A("- handling: `sacrificed_excluded_from_denominator` (label per spec.md `sacrificed small "
          "CAL`: \"excluded from key denominators and listed in the public-message inventory\")")
        A("")
    A("## Release-pattern mapping summary")
    A("")
    A("| release_handling | rows | key bits (counted) | public bits (counted) |")
    A("|-------------------|------|--------------------|-----------------------|")
    for h in RELEASE_HANDLING:
        rows = [r for r in ROWS if r["release_handling"] == h]
        kb = sum(r["size_bits"] for r in rows
                 if r["key_dependent"] and isinstance(r["size_bits"], int))
        pb = sum(r["size_bits"] for r in rows
                 if not r["key_dependent"] and isinstance(r["size_bits"], int))
        A("| `%s` | %d | %s | %s |" % (h, len(rows), kb, pb))
    A("")
    A("Mapping conventions (frozen in-packet): `none_recorded` rows and structural records map to "
      "`structural_public_parameter`; exactly ONE row carries "
      "`charged_0_labeled_public_ec_only_not_secure` (the Release in-sample comparison record; "
      "never counted in NB-Polar's own accounting, adjudication item 3); NB-Polar accounts its "
      "sacrificed CAL via `sacrificed_excluded_from_denominator`; `result_publication` rows carry "
      "size 0 / N-A (adjudication item 4).")
    A("")
    A("## Disclosure cross-check block (frozen recount; mismatch => STOP, frozen numbers stand)")
    A("")
    frozen = freeze["recount_cross_check_frozen"]
    A("| stage | rows | computed key bits | computed public bits | frozen key/public | tags | match |")
    A("|-------|------|-------------------|----------------------|-------------------|------|-------|")
    for s in ("G2", "G3"):
        rc = recount[s]
        A("| %s | %d | %d | %d | %d / %d | %d | %s |"
          % (s, rc["rows"], rc["key"], rc["public"], frozen["key_bits"], frozen["public_bits"],
             rc["tags"],
             "MATCH" if (rc["key"] == frozen["key_bits"]
                         and rc["public"] == frozen["public_bits"]
                         and rc["tags"] == frozen["tags"]) else "MISMATCH"))
    A("")
    A("Frozen identities as recorded: key %d = 34119 x 42; public %d = 327743 x 42; tags 42 per "
      "stage (G2 `tag_master %s` INHERITED, G3 `tag_master %s`). `incremental == recount`, "
      "`mismatches == []` in both summaries (SC6)."
      % (frozen["key_bits"], frozen["public_bits"], fc["g2_tag_master"], fc["g3_tag_master"]))
    A("")
    A("## `undetected` isolation")
    A("")
    A("G2 `undetected` = %d/%d as recorded; G3 `undetected` = %d/%d as recorded. These are listed "
      "as isolated rows and are NEVER merged into any success/FER number. G4 asserts no success, "
      "no FER, no efficiency, no qualification, no promotion and no composable key; no verdict in "
      "this document is G4's own — every verdict is quoted as recorded in its source artifact."
      % (recount["G2"]["undetected"], recount["G2"]["rows"],
         recount["G3"]["undetected"], recount["G3"]["rows"]))
    A("")
    A("## G3 participation-disclosure statement (quoted wherever G3 is cited)")
    A("")
    part = must(read_json(rel(G3, "g3_summary.json")), "participation_disclosure", "g3_summary")
    A("> %s" % md_escape(part))
    A("")
    A("Participation disclosure means decoder/model independence, NOT no-prior-contact.")
    A("")
    A("## Inventory tables")
    A("")
    header = ("| id | message_class | message | producer | key_dependent | size_bits | count | "
              "seed/mask/code | source_artifact | source_locator | release_handling | status |")
    sep = "|---|---|---|---|---|---|---|---|---|---|---|---|"
    for stage in STAGES:
        rows = [r for r in ROWS if r["stage"] == stage]
        A("### stage %s (%d rows)" % (stage, len(rows)))
        A("")
        A(header)
        A(sep)
        for r in rows:
            A("| %s | %s | %s | %s | %s | %s | %d | %s | `%s` | %s | `%s` | `%s` |"
              % (r["id"], r["message_class"], md_escape(r["message"]), md_escape(r["producer"]),
                 r["key_dependent"], md_escape(r["size_bits"]), r["count"],
                 md_escape(r["seed_mask_code_ref"]), r["source_artifact"],
                 md_escape(r["source_locator"]), r["release_handling"], r["status"]))
        A("")
    A("## Completeness declaration")
    A("")
    A("- Machine-countable arithmetic: `row_count` = %d = number of JSON rows = number of MD table "
      "rows = sum(`rows_by_stage`) = sum(`rows_by_release_handling`) = sum(`rows_by_message_class`) "
      "(self-check SC8, read-back verified)." % len(ROWS))
    A("- Every row carries a resolvable `source_artifact` + `source_locator`; every cited artifact "
      "is inside the frozen input manifest; zero rows remain `status: to_freeze`.")
    A("- Expected-but-absent field classes carry explicit `none_recorded` rows (G1/G1R2 tag-output "
      "and disclosure fields verified absent by exhaustive key scan; participation/reveal fields "
      "absent where noted).")
    A("- Disclosure sums equal the frozen recount; `undetected` is isolated; CAL lists are "
      "byte-identical to their source arrays.")
    A("- Acceptance IDs: this document supplies the G4-0..G4-4 evidence. R1 (independent "
      "Pre-RESULT review) and R2 (main-thread adjudication) remain PENDING — this builder and its "
      "operator do not self-approve, and no acceptance ID is asserted PASS here.")
    A("- Outcome strings (frozen before the build): `%s` / `%s` (applied only by the reviewed "
      "return, not by this document)."
      % (freeze["outcome_strings_preregistered"]["complete"],
         freeze["outcome_strings_preregistered"]["incomplete"]))
    A("")
    A("## Inputs (verbatim from `g4_freeze_config.json`)")
    A("")
    for it in freeze["input_manifest"]:
        A("- [%s] `%s` — exists: %s; locators: %s"
          % (it["id"], it["path"], it["exists"], "; ".join(it["locators_used"])))
    A("")
    A("Excluded explicitly (never read, never cited):")
    for x in freeze["excluded_inputs"]:
        A("- %s" % x)
    A("")
    return "\n".join(L) + "\n"


def render_run_log(freeze, recount, elapsed, rss, row_count, by_stage):
    L = []
    A = L.append
    A("# G4 run log — NBPOLAR-M2-PRIOR-G4-INVENTORY")
    A("")
    A("- built_at: %s" % datetime.datetime.now().isoformat(timespec="seconds"))
    A("- command: `/home/karel_303/.venvs/timetagger/bin/python g4_build_inventory.py`")
    A("- python: %s" % sys.version.split()[0])
    A("- branch: %s | authorization: recorded in STATUS.yaml before build" % freeze["branch"])
    A("- budget: wall %.2f s / %s s, RSS peak %s / %s GiB, single-threaded"
      % (elapsed, freeze["budget"]["wall_s_max"],
         ("%.3f GiB" % rss) if rss is not None else "n/a",
         freeze["budget"]["rss_gib_max"]))
    A("- counters: sc_calls 0, tag_invocations 0, g4_runs 1, reruns 0, rebuilds 0")
    A("- resources: read-only aggregation over frozen JSON/JSONL; no decode, no SC, no tags, "
      "no raw-data read, no sigma re-derivation (string consistency check only)")
    A("")
    A("## Self-checks (all ran BEFORE any output file was written)")
    A("")
    A("| check | ok | detail |")
    A("|-------|----|--------|")
    for c in CHECKS:
        A("| %s | %s | %s |" % (c["check"], "PASS" if c["ok"] else "FAIL", md_escape(c["detail"])))
    A("")
    A("## Rows built (%d; by stage %s)" % (row_count, by_stage))
    A("")
    for line in ROW_LOG:
        A("- %s" % line)
    A("")
    A("## Disclosure recount (frozen cross-check)")
    A("")
    for s in ("G2", "G3"):
        A("- %s: rows=%d key=%d public=%d tags=%d undetected=%d"
          % (s, recount[s]["rows"], recount[s]["key"], recount[s]["public"],
             recount[s]["tags"], recount[s]["undetected"]))
    A("")
    A("## Acceptance IDs")
    A("")
    A("- G4-0..G4-4: evidence produced in `g4_freeze_config.json`, `g4_inventory.json`, "
      "`g4_inventory.md`, `g4_counts.json`; reviewed by R1 (independent Pre-RESULT) and R2 "
      "(main-thread adjudication) — both PENDING, no self-approval in this log.")
    A("- outcome strings frozen BEFORE this build; the state string is applied only by the "
      "reviewed return.")
    A("")
    return "\n".join(L) + "\n"


def main():
    if not os.path.exists(FREEZE_PATH):
        print("BLOCKER (return condition 2): g4_freeze_config.json missing — Phase A not done; "
              "run the Phase-A freeze first.")
        return 2
    with open(FREEZE_PATH, "r", encoding="utf-8") as fh:
        freeze = json.load(fh)
    try:
        build(freeze, "--check-only" in sys.argv[1:])
    except Blocker as exc:
        print("BLOCKER (return condition 2): %s" % exc)
        print("No output file was written (all checks run before any write).")
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
