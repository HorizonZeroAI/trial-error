"""Montgomery pair correlation on GENUINE Riemann zeta zeros (mpmath).

The honest version of the experiment: real zeros, preregistered criteria,
result printed no matter what.
"""
import json
import math
import time

import mpmath
import numpy as np
from scipy.stats import kstest

t0 = time.time()
mpmath.mp.dps = 15
TIME_BUDGET_S = 420

# 1. Compute genuine zeros (imaginary parts) until N or time budget
zeros = []
n = 1
N_TARGET = 600
while n <= N_TARGET and (time.time() - t0) < TIME_BUDGET_S:
    zeros.append(float(mpmath.zetazero(n).imag))
    n += 1
g = np.array(zeros)
N = len(g)

# 2. Unfold: w_n = g_n/(2pi) * log(g_n/(2pi*e))  (mean spacing -> 1)
w = g / (2 * math.pi) * np.log(g / (2 * math.pi * math.e))

# 3. Nearest-neighbor spacings vs Wigner GUE surmise
s = np.diff(w)
s = s / np.mean(s)


def wigner_gue_cdf(x):
    # p(s) = (32/pi^2) s^2 exp(-4 s^2 / pi); CDF numerically
    xs = np.atleast_1d(x)
    out = []
    for xx in xs:
        grid = np.linspace(0, max(xx, 1e-9), 400)
        pdf = (32 / math.pi**2) * grid**2 * np.exp(-4 * grid**2 / math.pi)
        out.append(np.trapezoid(pdf, grid))
    return np.array(out)


ks_stat, ks_p = kstest(s, wigner_gue_cdf)

# 4. Montgomery pair correlation R2(x) = 1 - (sin(pi x)/(pi x))^2 on [0.25, 3]
diffs = []
for i in range(N):
    for j in range(i + 1, N):
        d = w[j] - w[i]
        if d > 3.0:
            break
        diffs.append(d)
diffs = np.array(diffs)
bins = np.linspace(0.25, 3.0, 12)
centers = 0.5 * (bins[:-1] + bins[1:])
width = bins[1] - bins[0]
counts, _ = np.histogram(diffs, bins=bins)
# Empirical R2: pair density per unit length per zero
emp_R2 = counts / (N * width)
theory_R2 = 1 - (np.sin(math.pi * centers) / (math.pi * centers)) ** 2
mean_abs_err = float(np.mean(np.abs(emp_R2 - theory_R2)))

# 5. Preregistered criteria
crit_ks = bool(ks_p > 0.05)          # spacings consistent with GUE surmise
crit_pc = bool(mean_abs_err < 0.15)  # pair correlation tracks Montgomery R2
passed = crit_ks and crit_pc

evidence = (
    f"{N} genuine mpmath zeros (dps=15). "
    f"Wigner-GUE spacing KS={ks_stat:.4f}, p={ks_p:.4f} ({'consistent' if crit_ks else 'REJECTED'}). "
    f"Montgomery R2 mean abs error={mean_abs_err:.4f} over [0.25,3] "
    f"({'tracks GUE' if crit_pc else 'FAILS'}). elapsed={time.time()-t0:.1f}s"
)
print(json.dumps({"pass": passed, "evidence": evidence, "metric": round(1 - mean_abs_err, 4)}))
