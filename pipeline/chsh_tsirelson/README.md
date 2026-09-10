# Exhibit: CHSH / Tsirelson bound — |S| = 2.824 (bound: 2*sqrt(2) ~ 2.828)

One experiment, exactly as the system recorded it. The system simulated a
Bell test: classical local-hidden-variable correlations vs quantum
correlations at the standard CHSH measurement angles.

Result: classical |S| = 2.0095 (respects the classical bound of 2),
quantum |S| = 2.8238 — violating the Bell inequality and landing under the
Tsirelson bound of 2.8284, as quantum mechanics requires.

Two things worth noticing:

1. The overall record is marked "pass": false. The experiment bundled the
   CHSH test with a second criterion (Bayesian-consistency against a live
   system metric) that failed. The physics succeeded; the composite
   experiment did not, and the ledger says so. Results are recorded as
   they happened, not as they'd look best.

2. The code fetches one value from the system's own local API
   (loopback-only; endpoint genericized in this copy). This experiment was
   the system testing a hypothesis about itself using quantum correlations
   as the comparison class.

| file | what it is |
|---|---|
| code.py | the CHSH simulation the system wrote |
| meta.json | execution record (see _redaction_note) |
| stdout.txt | the result line, verbatim |
