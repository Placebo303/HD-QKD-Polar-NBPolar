# Proposal: Phase 6-R1 decode-reject advancement

The accepted Phase 6 strict-stop schedule saved 28.17% disclosure but lost 29
blocks when K29 SC raised `ImpossibleDisclosedValueError` before verification.
Keep K=(29,33,37,41,45), construction, channel, thresholds, tag domain and
accounting unchanged. At K<45, only this exception advances to the immediate
next level after one public feedback request and a restart-from-scratch SC. At
K45 it remains terminal `decode_failed`.

No exception swallowing, SC change, new K, tuning, warm start, tag-based
candidate selection, real data, SCL, Phase 7, qualification or promotion.
