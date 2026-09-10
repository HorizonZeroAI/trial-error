import json
import math
import itertools
import collections
import functools
from collections import Counter

def max_entropy_distribution(marginals_list, categories_list, n_iter=100, lr=0.01):
    """
    Find maximum entropy distribution over joint space subject to 
    multi-way cardinality (marginal) constraints using iterative proportional fitting (IPF).
    
    marginals_list: list of dicts, each mapping category -> required proportion
    categories_list: list of lists of categories for each dimension
    """
    # Build joint space
    joint_keys = list(itertools.product(*categories_list))
    n_cells = len(joint_keys)
    
    # Initialize uniform distribution (maximum entropy starting point)
    dist = {k: 1.0 / n_cells for k in joint_keys}
    
    # IPF (Iterative Proportional Fitting) to satisfy marginal constraints
    for iteration in range(n_iter):
        for dim_idx, marginals in enumerate(marginals_list):
            # Compute current marginal for this dimension
            current_marginal = collections.defaultdict(float)
            for k, v in dist.items():
                current_marginal[k[dim_idx]] += v
            
            # Adjust
            for k in dist:
                cat = k[dim_idx]
                target = marginals.get(cat, 0)
                current = current_marginal[cat]
                if current > 1e-15:
                    dist[k] *= target / current
        
        # Normalize
        total = sum(dist.values())
        if total > 1e-15:
            dist = {k: v / total for k, v in dist.items()}
    
    return dist

def entropy(dist):
    """Compute Shannon entropy of a distribution (dict of probabilities)."""
    h = 0.0
    for p in dist.values():
        if p > 1e-15:
            h -= p * math.log(p)
    return h

def check_marginals(dist, marginals_list, categories_list, tol=1e-4):
    """Check if distribution satisfies all marginal constraints within tolerance."""
    for dim_idx, marginals in enumerate(marginals_list):
        current_marginal = collections.defaultdict(float)
        for k, v in dist.items():
            current_marginal[k[dim_idx]] += v
        for cat, target in marginals.items():
            actual = current_marginal[cat]
            if abs(actual - target) > tol:
                return False, dim_idx, cat, target, actual
    return True, None, None, None, None

def test_hypothesis():
    results = []
    
    # Test Case 1: 2-way constraints (age x gender)
    age_cats = ['young', 'middle', 'old']
    gender_cats = ['M', 'F']
    age_marginals = {'young': 0.3, 'middle': 0.5, 'old': 0.2}
    gender_marginals = {'M': 0.48, 'F': 0.52}
    
    dist = max_entropy_distribution(
        [age_marginals, gender_marginals],
        [age_cats, gender_cats]
    )
    
    h = entropy(dist)
    max_possible_h = math.log(len(age_cats) * len(gender_cats))
    satisfied, *details = check_marginals(dist, [age_marginals, gender_marginals], [age_cats, gender_cats])
    
    # Verify max entropy property: the solution should have higher entropy than random feasible solutions
    # The IPF solution should be close to the product of marginals (independence = max entropy under marginal constraints)
    product_dist = {}
    for a in age_cats:
        for g in gender_cats:
            product_dist[(a, g)] = age_marginals[a] * gender_marginals[g]
    product_h = entropy(product_dist)
    
    results.append({"test": "2way_marginals_satisfied", "pass": satisfied, "entropy": h, "max_entropy": max_possible_h})
    results.append({"test": "2way_matches_product_dist", "pass": abs(h - product_h) < 1e-6, "ipf_entropy": h, "product_entropy": product_h})
    
    # Test Case 2: 3-way constraints (age x gender x income)
    income_cats = ['low', 'medium', 'high']
    income_marginals = {'low': 0.4, 'medium': 0.35, 'high': 0.25}
    
    dist3 = max_entropy_distribution(
        [age_marginals, gender_marginals, income_marginals],
        [age_cats, gender_cats, income_cats]
    )
    h3 = entropy(dist3)
    sat3, *_ = check_marginals(dist3, [age_marginals, gender_marginals, income_marginals], [age_cats, gender_cats, income_cats])
    
    # Check it equals product of marginals
    product3 = {}
    for a in age_cats:
        for g in gender_cats:
            for i in income_cats:
                product3[(a, g, i)] = age_marginals[a] * gender_marginals[g] * income_marginals[i]
    product3_h = entropy(product3)
    
    results.append({"test": "3way_marginals_satisfied", "pass": sat3, "entropy": h3})
    results.append({"test": "3way_matches_product", "pass": abs(h3 - product3_h) < 1e-5, "diff": abs(h3 - product3_h)})
    
    # Test Case 3: Verify entropy is maximized - perturb and check entropy decreases
    n_perturbations_tested = 0
    n_entropy_lower = 0
    for _ in range(1000):
        perturbed = dict(dist3)
        keys = list(perturbed.keys())
        i, j = keys[_ % len(keys)], keys[(_ * 7 + 3) % len(keys)]
        delta = 0.001 * ((_ % 10) + 1)
        if perturbed[i] > delta:
            perturbed[i] -= delta
            perturbed[j] += delta
            total = sum(perturbed.values())
            perturbed = {k: v/total for k, v in perturbed.items()}
            hp = entropy(perturbed)
            n_perturbations_tested += 1
            if hp <= h3 + 1e-10:
                n_entropy_lower += 1
    
    frac_lower = n_entropy_lower / max(n_perturbations_tested, 1)
    results.append({"test": "perturbation_entropy_check", "pass": frac_lower > 0.95, 
                     "fraction_not_higher": frac_lower, "n_tested": n_perturbations_tested})
    
    all_pass = all(r["pass"] for r in results)
    n_cases = len(results)
    
    print(json.dumps({"pass": all_pass, "evidence": json.dumps(results, default=str), "metric": n_cases}))

test_hypothesis()