# Clean-room re-runs — operator-side, NOT system-generated

PROVENANCE: The two experiments here were written and executed by the
operator's build assistant in a clean sandbox (2026-09-09) AFTER the
original system artifacts for these claims were found defective (see
CLAIMS_AUDIT.md). They are deliberately labeled as such. Nothing in this
folder was produced by the autonomous system; that distinction is the
entire point of the claims audit, and it cuts both ways.

Both scripts are self-contained (numpy/scipy/mpmath), print a result no
matter what, and take minutes on a laptop. Run them yourself.

| script | claim re-tested | result |
|---|---|---|
| montgomery_real.py | Montgomery pair correlation on genuine zeta zeros | PASS — 600 mpmath zeros, Wigner-GUE spacing KS p=0.125, R2 mean abs error 0.064 |
| crooks_real.py | Crooks fluctuation theorem | PASS — slope 1.0116 vs 1.0, Jarzynski 0.9919 vs 1.0, 80k Langevin trajectories |

The corrected public claims are therefore: Montgomery-Odlyzko statistics
hold on 600 genuinely computed zeros (not "5,000" — that number came
from a synthetic run and is retired), and the Crooks fluctuation theorem
verifies cleanly in a dragged-trap Langevin system (the system's own
attempt was truncated code that never printed a byte).
