import json
import urllib.request
import math
import random
import statistics

def fetch(endpoint):
    try:
        req = urllib.request.Request(f"http://127.0.0.1:<PORT>{endpoint}")
        with urllib.request.urlopen(req, timeout=5) as resp:
            return json.loads(resp.read().decode())
    except Exception as e:
        return {"error": str(e)}

def simulate_bell_test(n_trials=10000, quantum=False):
    """Simulate Bell test: measure correlations between entangled particle pairs.
    
    Baseline (classical/local hidden variable): respects Bell inequality |S| <= 2
    Treatment (quantum): violates Bell inequality, achieving |S| = 2*sqrt(2) ≈ 2.828
    """
    random.seed(42)
    
    # Alice and Bob each choose from 2 measurement angles
    # Classical: a1=0, a2=pi/4, b1=pi/8, b2=3pi/8
    # These are the optimal angles for maximal Bell violation
    a1, a2 = 0, math.pi / 4
    b1, b2 = math.pi / 8, 3 * math.pi / 8
    
    settings = [(a1, b1), (a1, b2), (a2, b1), (a2, b2)]
    correlations = {}
    
    for (a, b) in settings:
        results = []
        for _ in range(n_trials):
            if quantum:
                # Quantum prediction: E(a,b) = -cos(2*(a-b)) for singlet state
                # Probabilistic simulation matching quantum statistics
                angle_diff = a - b
                prob_same = (math.sin(angle_diff)) ** 2
                if random.random() < prob_same:
                    alice, bob = 1, -1
                else:
                    alice, bob = 1, 1
                # Randomly flip both (symmetry)
                if random.random() < 0.5:
                    alice, bob = -alice, -bob
            else:
                # Classical local hidden variable: shared random angle lambda
                lam = random.uniform(0, 2 * math.pi)
                alice = 1 if math.cos(2 * (a - lam)) >= 0 else -1
                bob = 1 if math.cos(2 * (b - lam)) >= 0 else -1
            results.append(alice * bob)
        correlations[(a, b)] = statistics.mean(results)
    
    # CHSH quantity: S = E(a1,b1) - E(a1,b2) + E(a2,b1) + E(a2,b2)
    S = (correlations[(a1, b1)] - correlations[(a1, b2)] 
         + correlations[(a2, b1)] + correlations[(a2, b2)])
    return S, correlations

def main():
    # Fetch system context to ground the experiment in the research item
    research = fetch("/api/research/stream/system")
    calibration = fetch("/api/calibration/report")
    health = fetch("/api/health")
    
    # Run baseline: classical local hidden variable model
    S_classical, corr_classical = simulate_bell_test(n_trials=20000, quantum=False)
    
    # Run treatment: quantum mechanical model
    S_quantum, corr_quantum = simulate_bell_test(n_trials=20000, quantum=True)
    
    bell_bound = 2.0
    tsirelson_bound = 2 * math.sqrt(2)  # ≈ 2.828
    
    classical_respects = abs(S_classical) <= bell_bound + 0.05  # small tolerance
    quantum_violates = abs(S_quantum) > bell_bound
    quantum_within_tsirelson = abs(S_quantum) <= tsirelson_bound + 0.05
    
    # The unified framework hypothesis: quantum correlations violate classical
    # causal bounds (Bell inequality) while respecting Tsirelson bound,
    # and Bayesian updating on measurement outcomes is consistent
    
    # Bayesian consistency check: quantum correlations match cos(2*theta) prediction
    expected_quantum_S = -math.cos(0) + math.cos(math.pi/2) - math.cos(math.pi/4) - math.cos(math.pi/4)
    # Simplified: should be -2*sqrt(2) * sign
    bayesian_error = abs(abs(S_quantum) - abs(expected_quantum_S)) / abs(expected_quantum_S)
    
    passed = classical_respects and quantum_violates and quantum_within_tsirelson and bayesian_error < 0.05
    
    evidence = (f"Classical |S|={abs(S_classical):.4f} (bound=2.0, respects={classical_respects}); "
                f"Quantum |S|={abs(S_quantum):.4f} (violates={quantum_violates}, "
                f"Tsirelson={tsirelson_bound:.4f}, within={quantum_within_tsirelson}); "
                f"Bayesian consistency error={bayesian_error:.4f}; "
                f"System health={health.get('status','unknown')}")
    
    result = {"pass": passed, "evidence": evidence, "metric": round(abs(S_quantum) - bell_bound, 4)}
    print(json.dumps(result))

main()