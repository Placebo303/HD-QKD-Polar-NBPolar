# Matching coding-agent prompt

In the current repository root (`.`), branch `codex/nbpolar-phase0`,
execute only the accepted Phase 0-2 tasks from
`openspec/changes/formal-ir-nbpolar-mvp/`. First read the review entrypoint,
packet, architecture and gates. Implement GF32/poly37/alpha2, the explicitly
ordered 2x2 transform, source-compression coordinate handling, log-domain
q-ary SC, and an independent tiny enumeration oracle. Public coordinates use
their actual symbol values, including zero when applicable; the decoder must
not access Alice truth.

Only modify files in the packet allowlist and focused tests. Do not touch Release,
frozen baseline code, historical outputs, Model-F, raw data, SCL, puncturing,
shortening, rate scans or real-data execution. Do not call an SC conditional
score a complete APP. Complete the Phase 0-2 checks or return one exact
`BLOCKED` reason. No result, qualification or promotion claim is authorized.
