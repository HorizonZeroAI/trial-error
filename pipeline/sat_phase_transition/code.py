import json as _json
_results = {"pass": False, "evidence": "", "metric": 0}
_pv_printed = False
_orig_print = print
def print(*a, **kw):
    global _pv_printed
    _pv_printed = True
    _orig_print(*a, **kw)
try:
    import json, math, random, time
    import numpy as np
    from scipy import stats
    from scipy.optimize import curve_fit
    
    results = {}
    
    def make_random_3sat(n, alpha, rng):
        m = int(alpha * n)
        clauses = []
        for _ in range(m):
            vs = rng.choice(n, 3, replace=False) + 1
            clause = [int(v) * (1 if rng.random() > 0.5 else -1) for v in vs]
            clauses.append(clause)
        return clauses
    
    def dpll_solve(clauses, n, heuristic, max_conflicts=2000):
        assign = {}
        activity = {v: 1.0 for v in range(1, n+1)}
        conflicts = [0]
        decisions = [0]
    
        def unit_prop(clauses, assign):
            changed = True
            while changed:
                changed = False
                for cl in clauses:
                    unset = [l for l in cl if abs(l) not in assign]
                    sat = any(assign.get(abs(l)) == (l > 0) for l in cl)
                    if sat:
                        continue
                    if len(unset) == 0:
                        return None
                    if len(unset) == 1:
                        l = unset[0]
                        assign[abs(l)] = (l > 0)
                        changed = True
            return assign
    
        def choose_var(assign, activity, heuristic, n):
            unset = [v for v in range(1, n+1) if v not in assign]
            if not unset:
                return None
            if heuristic == 'vsids':
                return max(unset, key=lambda v: activity.get(v, 0))
            elif heuristic == 'lrb':
                return max(unset, key=lambda v: activity.get(v, 0) * (1 + random.random() * 0.1))
            else:
                return random.choice(unset)
    
        def solve(assign, depth):
            if conflicts[0] > max_conflicts:
                return None
            a2 = dict(assign)
            a2 = unit_prop(clauses, a2)
            if a2 is None:
                conflicts[0] += 1
                for cl in clauses:
                    for l in cl:
                        activity[abs(l)] = activity.get(abs(l), 1.0) * 1.05
                for v in activity:
                    activity[v] *= 0.99
                return None
            if len(a2) == n:
                return a2
            v = choose_var(a2, activity, heuristic, n)
            if v is None:
                return a2
            decisions[0] += 1
            for val in [True, False]:
                a3 = dict(a2)
                a3[v] = val
                res = solve(a3, depth+1)
                if res is not None:
                    return res
            return None
    
        result = solve(assign, 0)
        return conflicts[0], decisions[0]
    
    try:
        rng = np.random.RandomState(42)
        random.seed(42)
    
        # Sweep alpha for random 3-SAT, two heuristics, small n for speed
        n = 50
        alphas = np.linspace(3.5, 5.0, 15)
        n_inst = 8
        heuristics = ['vsids', 'random']
        sat_results = {h: [] for h in heuristics}
    
        for alpha in alphas:
            for h in heuristics:
                confs = []
                for _ in range(n_inst):
                    clauses = make_random_3sat(n, alpha, rng)
                    c, d = dpll_solve(clauses, n, h, max_conflicts=1500)
                    confs.append(c)
                sat_results[h].append(np.median(confs))
    
        results['sat_medians'] = {h: sat_results[h] for h in heuristics}
    
        # Fit power law near peak
        def power_law(x, ac, gamma, A):
            denom = np.abs(x - ac)
            denom = np.where(denom < 1e-6, 1e-6, denom)
            return A * denom ** (-gamma)
    
        exponents = {}
        peak_idx = np.argmax(sat_results['vsids'])
        alpha_c_est = float(alphas[peak_idx])
    
        for h in heuristics:
            y = np.array(sat_results[h], dtype=float)
            y = np.where(y < 1, 1, y)
            try:
                popt, _ = curve_fit(power_law, alphas, y,
                                    p0=[alpha_c_est, 0.5, float(np.max(y))],
                                    bounds=([3.0, 0.01, 0.1], [5.5, 5.0, 1e7]),
                                    maxfev=3000)
                exponents[h] = float(popt[1])
            except Exception:
                exponents[h] = float(np.nan)
    
        results['exponents'] = exponents
    
        # Statistical test: are heuristic conflict distributions different near peak?
        near_peak = (alphas > alpha_c_est - 0.4) & (alphas < alpha_c_est + 0.4)
        vsids_peak = np.array(sat_results['vsids'])[near_peak]
        rand_peak = np.array(sat_results['random'])[near_peak]
    
        if len(vsids_peak) > 1 and len(rand_peak) > 1:
            t_stat, p_val = stats.ttest_ind(vsids_peak, rand_peak)
        else:
            t_stat, p_val = 0.0, 1.0
    
        results['t_stat'] = float(t_stat)
        results['p_value'] = float(p_val)
    
        exp_vsids = exponents.get('vsids', np.nan)
        exp_rand = exponents.get('random', np.nan)
        exp_diff = abs(exp_vsids - exp_rand) if (not math.isnan(exp_vsids) and not math.isnan(exp_rand)) else 0.0
        results['exponent_diff'] = float(exp_diff)
    
        passed = bool(p_val < 0.05 or exp_diff > 0.1)
        evidence = (f"VSIDS exponent={exp_vsids:.3f}, random exponent={exp_rand:.3f}, "
                    f"diff={exp_diff:.3f}, t-test p={p_val:.4f}, alpha_c~{alpha_c_est:.2f}")
    
        print(json.dumps({"pass": passed, "evidence": evidence, "metric": float(exp_diff)}))
    
    except Exception as e:
        results['error'] = str(e)
        print(json.dumps({"pass": False, "evidence": f"Error: {str(e)}", "metric": 0.0}))
except Exception as _e:
    _results["evidence"] = f"Experiment crashed: {_e}"
    _results["pass"] = False
finally:
    if not _pv_printed:
        _orig_print(_json.dumps(_results))
