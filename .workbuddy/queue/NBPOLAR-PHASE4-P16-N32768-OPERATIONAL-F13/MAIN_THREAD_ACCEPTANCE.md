# Main-thread acceptance — Phase 4-P16 N=32768 operational f=1.3

Decision: accept `TARGET_EMPIRICAL_OPERATIONAL_F13_N32768_CANDIDATE` as a
model-sampled operational development signal, with zero count margin.

All integrity gates passed; exact recovery was 62/64, undetected was zero and
the one-sided Wilson lower bound was 0.9098711859. The one artifact read and
attempt were consumed without rerun or tuning; both independent reviews
support the frozen classification. The result sits exactly at the count
threshold: 61/64 would have failed both recovery gates. It is therefore not
accepted as a stable rate point, qualification, promotion or real-data FER.

The next gate is an independent 128-block replication at the same N, K,
orders, channel model and protocol. It reuses the accepted P16 construction
and spends no new TRAIN/genie work. P16 observations are not pooled into the
replication decision.

Route principle: channel/construction or asymptotic evidence determines a
candidate rate/order, but never establishes finite-length decoder usability.
Finite-length backoff and actual decoder/graph behavior remain separate gates.

