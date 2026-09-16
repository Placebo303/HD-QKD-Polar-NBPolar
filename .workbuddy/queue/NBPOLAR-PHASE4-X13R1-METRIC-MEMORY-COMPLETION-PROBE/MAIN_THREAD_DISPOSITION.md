# Main-thread disposition — X13-R1 metric-memory completion

Decision: record `X13R1_COMPLETE_DESCRIPTIVE_ONLY`.

The completed four-cell evidence shows that both frozen alternatives finish
6/6 injected blocks under the 2 GiB virtual-memory limit, including two
N=262144 blocks per alternative. Small-N parity was inherited and replayed;
X13 remained immutable. This is sufficient to establish that release at last
use removes the specific P12 allocation blocker in the injected setting. It
does not select `lifetime_only` versus `owned_log`, prove target-channel
recovery, or justify a P12 rerun.

The machine record says that no separate reviewer was available during the
execution. The independent reviewer-go review subsequently supplied to the
main thread is accepted as the focused post-run review; this timing/provenance
distinction is retained rather than rewriting the probe record.

Route decision: do not promote either memory alternative yet. The next gate
first measures target-model empirical genie residuals at N=4096, 8192 and
16384. If the f=1.3 crossing occurs there, the N=262144 profile is unnecessary.

