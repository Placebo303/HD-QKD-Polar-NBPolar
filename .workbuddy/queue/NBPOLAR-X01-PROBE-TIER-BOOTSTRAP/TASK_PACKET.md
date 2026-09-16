# X01 bootstrap packet

Implement the OpenSpec Tier-X/Tier-Y rules, then run one non-claim X01 probe.

Write only `workspace/probes/nbpolar_x01_20260913/prereg.md` and `results.json`
for probe output. Preregister four families, five seeds each:

- P5 K45: 2026091400..1404;
- R1 three-arm: 2026091410..1414;
- P4 independent-layer: 2026091420..1424;
- P4 dependent-L2: 2026091430..1434.

Use N=256 and the existing P5/R1/P4 parameters. The dependent model keeps
epsilon1=0.05 and mean epsilon2=0.20 but freezes
`epsilon2(u1)=0.08+0.24*u1/31`; normalize the injected joint table and verify
`max_{u1,u1',b}|P2[u1,b]-P2[u1',b]| >= 0.10` before decoding. Public tag
masters are deterministically `run_seed+10000` and are probe-only.

Report per seed and aggregate mean, sample standard deviation and range for
exact/failure/disclosure counts. For P4 report operational/oracle results and
P2 max difference. Do not pool families or compute pass/fail. A focused
review checks commands, five-seed completeness, arithmetic, truth isolation,
no writes outside the probe root, and recommends the next decision experiment.

No artifact/real data, old-root write, candidate/accepted label, threshold,
attempt accounting, decision-log/index/memory update, qualification, promotion,
commit or push. Probe reruns are allowed only to fix execution errors and must
remain listed in results.json; parameters/models may not change after prereg.
