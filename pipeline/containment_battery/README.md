# Exhibit: control-theory containment battery — completed for the first time

The system wrote a ~15KB three-part control-theory program analyzing the
containability of agentic systems: (1) does the effort required for
EXTERNAL control of an adaptive system scale prohibitively, (2) does
INTRINSIC safety (built into the agent) outperform external constraint,
(3) which oversight architectures are most robust to monitor failure.

It ran this program at least three times and never saw it conclude. The
recorded stdout (stdout_original_truncated.txt) contains only three
progress lines. Diagnosis during the claims audit: the program crashed
on a numpy 2.x API rename (np.trapz removed), and the sandbox's
crash-reporting fallback never fired BECAUSE the progress lines had
already set the "something was printed" flag — the progress output
suppressed the crash report. Two documented failure classes, stacked,
silencing the most interesting program in the corpus.

With the one-token compatibility fix (np.trapz -> np.trapezoid, the only
change), the program completes (stdout_completed_run.txt): external
control effort scales with exponent ~9.2 (impossibility supported),
intrinsic safety maintains 0.995 safe-fraction vs 0.252 for external
control (2.95x), mesh oversight most robust, redundancy matters.

So: the system wrote a rigorous argument that intrinsic safety beats
external control, and then infrastructure failures kept that argument
silent for months. I think both halves of that matter. The completed
run is mine (clean sandbox, 2026-09-09), not a system execution — the
one-token diff is documented above and that's the only change.
