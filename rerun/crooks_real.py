"""Crooks fluctuation theorem, verified honestly.

Overdamped Langevin particle in a harmonic trap dragged from 0 to L
(forward) and L to 0 (reverse). Same trap stiffness at both ends, so
Delta F = 0 and Crooks reads: log[P_F(W)/P_R(-W)] = beta * W.

Preregistered criteria:
  1. Crooks slope: fit of log[P_F(W)/P_R(-W)] vs W gives slope beta
     within 15% (beta = 1).
  2. Jarzynski: <exp(-beta W)> = exp(-beta dF) = 1 within 10%.
  3. Second law on average: <W_F> > 0.
Result printed no matter what.
"""
import json
import math

import numpy as np

rng = np.random.default_rng(7)

beta = 1.0          # 1/kT
k = 2.0             # trap stiffness
gamma = 1.0         # friction
L = 1.5             # drag distance
tau = 2.0           # protocol duration
dt = 0.002
steps = int(tau / dt)
n_traj = 40000

sigma = math.sqrt(2 * dt / (beta * gamma))


def run_protocol(forward: bool) -> np.ndarray:
    """Return work values for n_traj trajectories."""
    centers = np.linspace(0, L, steps) if forward else np.linspace(L, 0, steps)
    # Sample initial positions from equilibrium at the starting trap center
    x = centers[0] + rng.normal(0, math.sqrt(1 / (beta * k)), n_traj)
    W = np.zeros(n_traj)
    for i in range(steps - 1):
        c, c_next = centers[i], centers[i + 1]
        # Work = energy change from moving the trap with particle fixed
        W += 0.5 * k * ((x - c_next) ** 2 - (x - c) ** 2)
        # Overdamped Langevin step in the (already moved) trap
        x += -(k / gamma) * (x - c_next) * dt + sigma * rng.normal(0, 1, n_traj)
    return W


W_F = run_protocol(forward=True)
W_R = run_protocol(forward=False)

# Criterion 1: Crooks slope via histogram ratio on overlapping support
bins = np.linspace(-2, 4, 41)
centers_b = 0.5 * (bins[:-1] + bins[1:])
pf, _ = np.histogram(W_F, bins=bins, density=True)
pr, _ = np.histogram(-W_R, bins=bins, density=True)
mask = (pf > 1e-4) & (pr > 1e-4)
log_ratio = np.log(pf[mask] / pr[mask])
slope, intercept = np.polyfit(centers_b[mask], log_ratio, 1)
crit_slope = bool(abs(slope - beta) / beta < 0.15)

# Criterion 2: Jarzynski equality (dF = 0)
jarzynski = float(np.mean(np.exp(-beta * W_F)))
crit_jarz = bool(abs(jarzynski - 1.0) < 0.10)

# Criterion 3: second law on average
crit_2nd = bool(np.mean(W_F) > 0)

passed = crit_slope and crit_jarz and crit_2nd
evidence = (
    f"{n_traj} forward + {n_traj} reverse Langevin trajectories. "
    f"Crooks slope={slope:.4f} (theory {beta:.1f}, {'OK' if crit_slope else 'FAIL'}, "
    f"{mask.sum()} overlap bins). Jarzynski <e^-bW>={jarzynski:.4f} (theory 1.0, "
    f"{'OK' if crit_jarz else 'FAIL'}). <W_F>={np.mean(W_F):.4f} "
    f"({'OK' if crit_2nd else 'FAIL'})."
)
print(json.dumps({"pass": passed, "evidence": evidence,
                  "metric": round(1 - abs(slope - beta), 4)}))
