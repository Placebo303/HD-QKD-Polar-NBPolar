Implement and execute the complete authorized Tier-Y task in `TASK_PACKET.md`.
Add the OpenSpec delta first, then make only the frozen allocation change in
`sc.py`: exact row chunks with default 512 and `None` golden direct mode. Do not
alter public SC semantics or any adjacent module.

Run focused and predecessor tests, freeze the exact command/root/schema, and
obtain independent reviewer-go Pre-EXECUTE PASS before the first formal
`sc_decode`. That call consumes attempt 1/1. Execute once, never rerun or tune,
then obtain independent Pre-RESULT review before return. No artifact access,
commit or push. Return only complete candidate evidence or a concrete blocker.
