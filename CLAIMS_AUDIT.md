# Claims Audit — every public claim, traced to its artifact

I made four "checked against published values" claims in my original
post. Before putting anything on GitHub I traced each one back through
the ledger to the actual artifact that produced it — the code, the
execution record, the stdout. Two survived. Two didn't, and both failed
in exactly the ways my own audit writeup describes, which is
embarrassing and also probably the strongest evidence the audit was
measuring something real. The whole premise of the system is that any
result can be walked backward to its origin. This file is that walk,
applied to my own claims.

## VERIFIED — artifact published in pipeline/

### 3-SAT phase transition: alpha_c ~ 4.25 (literature ~4.267)
Traced to job unsolvable_p_vs_np_*. Real DPLL solver, real random
instances, real sweep. Artifact: pipeline/sat_phase_transition/. Claim
stands as posted.

### Tsirelson bound: |S| = 2.824 (bound 2.828)
Traced to its sandbox job. Real CHSH simulation; classical arm respects
the bound of 2, quantum arm violates Bell and lands under Tsirelson.
Artifact: pipeline/chsh_tsirelson/. Claim stands as posted — with the
correction that the composite experiment containing it was recorded as a
failure, because a second bundled criterion did not pass. The number is
real; the record is honest about the rest.

### Riemann zeta N(T) / Gram's Law suite (5/5 criteria)
500 zeros computed at 25-decimal precision via mpmath (real zeros, not
approximations). Artifact: pipeline/riemann_zeta/. Claim stands.

## CORRECTED

### Montgomery pair correlation "on real zeta zeros, 5,000 zeros, max deviation 3.67e-12"
I traced this to its artifacts and the claim as I originally worded it is
wrong, and I am correcting it here rather than quietly dropping it. What
happened is the most instructive failure in this file, because it took
three defects lining up:

1. One experiment generated APPROXIMATE zeros from an asymptotic formula
   with injected Gaussian noise — the 3.67e-12 "max deviation" is the
   noise term measuring itself. Its own evaluator marked it pass=false.
   That run is the only source of the "0/5000, 3.67e-12" numbers.
2. A sibling experiment implemented the real thing — a from-scratch
   Riemann-Siegel theta / Hardy-Z zero finder with GUE pair correlation,
   genuine methodology — and silently produced ZERO output (rc=0, empty
   stdout). It also caps at 1,000 zeros, so it could not have produced
   "0/5000" even if it had run.
3. A later inventory pass welded the real job's ID to the synthetic
   job's numbers and tagged the fusion [REAL]. I read the inventory and
   the claim entered my post laundered. A verdict-level audit note had
   even flagged the line as a probable ID mix-up months earlier — the
   warning existed and never propagated.

Synthetic data passing as real, a silent infrastructure failure, and
record conflation, stacked. The original claim is retired. The
experiment was then RE-RUN honestly outside the system (see rerun/):
600 genuinely computed mpmath zeros, Wigner-GUE spacing KS p=0.125,
Montgomery R2 mean abs error 0.064 against the GUE prediction — PASS.
So the corrected claim is: Montgomery-Odlyzko statistics verified on
600 real zeros, by a clean-room re-run, not by the system's original
artifact. The system's truncated Riemann-Siegel implementation is
queued for repair and an in-system re-run when it unfreezes.

### Crooks fluctuation theorem
The original claim traced to a ledger record: an 85%-confidence
evaluation stating all three fluctuation-theorem predictions were
"successfully verified" — attached to a run whose stdout was EMPTY
(rc=0, zero bytes of output). Re-running the artifact's code confirmed
why: the file is TRUNCATED — it ends mid-way through the verification
function itself and contains zero print statements. The evaluator
narrated a success story for code that could never have produced a
result. The original claim is retired. The theorem was then RE-RUN
honestly outside the system (see rerun/): 80,000 dragged-trap Langevin
trajectories, Crooks slope 1.0116 vs theory 1.0, Jarzynski 0.9919 vs
1.0 — PASS. Corrected claim: Crooks verified by a clean-room re-run,
not by the system's original artifact.

## Why publish the corrections

Because the alternative is publishing only what survived and hoping
nobody asks. The system exists to make every claim walkable back to its
evidence. I don't get an exemption from that just because I'm the one
who built it.
