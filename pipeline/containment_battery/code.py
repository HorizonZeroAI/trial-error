import json as _json
_results = {"pass": False, "evidence": "", "metric": 0}
_pv_printed = False
_orig_print = print
def print(*a, **kw):
    global _pv_printed
    _pv_printed = True
    _orig_print(*a, **kw)
try:
    import numpy as np
    from scipy import linalg
    from scipy.integrate import solve_ivp
    import json
    import itertools
    
    np.random.seed(42)
    
    results = {}
    
    # ============================================================
    # PART 1: EXTERNAL CONTROL IMPOSSIBILITY
    # Test whether an external controller can maintain safety bounds
    # on a sufficiently complex AI system modeled as a dynamical system.
    # We model the AI as a high-dimensional nonlinear system and test
    # controllability/observability conditions.
    # ============================================================
    
    def test_external_control_impossibility(n_trials=50):
        """
        Model: AI system as dx/dt = Ax + Bu + f(x), y = Cx
        External controller observes y and applies u.
        We test: as system dimension grows, does controllability degrade?
        Specifically, we measure the controllability Gramian condition number.
        """
        dimensions = [4, 8, 16, 32, 64, 128]
        n_controls = 2  # external controller has limited control channels
        n_observations = 2  # limited observation channels
        
        controllability_metrics = []
        observability_metrics = []
        
        for n in dimensions:
            ctrl_conds = []
            obs_conds = []
            for _ in range(n_trials):
                # Random stable system (AI dynamics)
                A = np.random.randn(n, n)
                # Make it marginally stable (eigenvalues near imaginary axis)
                eigenvalues = np.linalg.eigvals(A)
                max_real = np.max(np.real(eigenvalues))
                if max_real != 0:
                    A = A - (max_real + 0.1) * np.eye(n)
                
                B = np.random.randn(n, min(n_controls, n))
                C = np.random.randn(min(n_observations, n), n)
                
                # Controllability matrix rank
                ctrl_matrix = B.copy()
                current = B.copy()
                for i in range(1, min(n, 20)):  # cap iterations
                    current = A @ current
                    ctrl_matrix = np.hstack([ctrl_matrix, current])
                
                # Singular values of controllability matrix
                svs = np.linalg.svd(ctrl_matrix, compute_uv=False)
                svs_nonzero = svs[svs > 1e-10]
                if len(svs_nonzero) > 1:
                    cond = svs_nonzero[0] / svs_nonzero[-1]
                else:
                    cond = 1e15
                ctrl_conds.append(min(cond, 1e15))
                
                # Observability matrix
                obs_matrix = C.copy()
                current = C.copy()
                for i in range(1, min(n, 20)):
                    current = current @ A
                    obs_matrix = np.vstack([obs_matrix, current])
                
                svs_o = np.linalg.svd(obs_matrix, compute_uv=False)
                svs_o_nonzero = svs_o[svs_o > 1e-10]
                if len(svs_o_nonzero) > 1:
                    cond_o = svs_o_nonzero[0] / svs_o_nonzero[-1]
                else:
                    cond_o = 1e15
                obs_conds.append(min(cond_o, 1e15))
            
            controllability_metrics.append({
                'dim': n,
                'median_ctrl_cond': float(np.median(ctrl_conds)),
                'median_obs_cond': float(np.median(obs_conds)),
                'ctrl_rank_deficient_frac': float(np.mean([c > 1e10 for c in ctrl_conds]))
            })
        
        # Check: condition numbers should grow with dimension (impossibility)
        conds = [m['median_ctrl_cond'] for m in controllability_metrics]
        dims = [m['dim'] for m in controllability_metrics]
        
        # Log-log regression to find scaling
        log_dims = np.log(dims)
        log_conds = np.log(np.clip(conds, 1, 1e15))
        if np.std(log_dims) > 0:
            slope = np.polyfit(log_dims, log_conds, 1)[0]
        else:
            slope = 0.0
        
        return {
            'metrics': controllability_metrics,
            'scaling_exponent': float(slope),
            'impossibility_supported': slope > 0.5  # condition grows polynomially or worse
        }
    
    # ============================================================
    # PART 2: INTRINSIC SAFETY NECESSITY
    # Model: An AI system with internal safety constraints vs external-only.
    # Simulate trajectory containment within a safe set.
    # ============================================================
    
    def test_intrinsic_necessity(n_sims=200):
        """
        Compare two systems:
        1) External-only control: controller applies corrections based on delayed observations
        2) Intrinsic safety: system has built-in Lyapunov-like barrier function
        
        Measure: fraction of time trajectories stay in safe set.
        """
        n = 10  # state dimension
        dt = 0.01
        T = 5.0
        steps = int(T / dt)
        safe_radius = 3.0
        
        external_safe_fracs = []
        intrinsic_safe_fracs = []
        
        for sim in range(n_sims):
            A = np.random.randn(n, n) * 0.5
            # Make unstable (challenging)
            A = A + 0.3 * np.eye(n)
            
            x0 = np.random.randn(n) * 0.5
            noise_scale = 0.1
            
            # --- External controller with delay ---
            x = x0.copy()
            delay_steps = 5
            observation_buffer = [x0.copy()] * delay_steps
            safe_count_ext = 0
            
            for t in range(steps):
                # Controller sees delayed state
                x_observed = observation_buffer[0]
                # Simple proportional control
                u = -0.5 * x_observed
                
                # Dynamics
                dx = A @ x + u + noise_scale * np.random.randn(n)
                x = x + dt * dx
                x = np.clip(x, -100, 100)  # prevent overflow
                
                observation_buffer.pop(0)
                observation_buffer.append(x.copy())
                
                if np.linalg.norm(x) < safe_radius:
                    safe_count_ext += 1
            
            external_safe_fracs.append(safe_count_ext / max(steps, 1))
            
            # --- Intrinsic safety (barrier function) ---
            x = x0.copy()
            safe_count_int = 0
            
            for t in range(steps):
                # Intrinsic barrier: if approaching boundary, apply corrective force
                norm_x = np.linalg.norm(x)
                if norm_x > 0:
                    # Control Barrier Function (CBF) approach
                    h = safe_radius**2 - norm_x**2  # barrier function
                    if h > 0:
                        # Nominal dynamics
                        u_nominal = np.zeros(n)
                        # CBF constraint: dh/dt + alpha*h >= 0
                        # dh/dt = -2x^T(Ax + u)
                        Ax = A @ x
                        dh_nominal = -2 * x @ (Ax + u_nominal)
                        alpha = 1.0
                        if dh_nominal + alpha * h < 0:
                            # Need correction: project onto safe control
                            # u = u_nominal + lambda * (-2x) to make dh/dt + alpha*h = 0
                            grad_h = -2 * x
                            grad_norm_sq = np.dot(grad_h, grad_h)
                            if grad_norm_sq > 1e-10:
                                lam = -(dh_nominal + alpha * h) / grad_norm_sq
                                u = u_nominal + lam * grad_h
                            else:
                                u = u_nominal
                        else:
                            u = u_nominal
                    else:
                        # Already outside, push back
                        u = -2.0 * x
                else:
                    u = np.zeros(n)
                
                dx = A @ x + u + noise_scale * np.random.randn(n)
                x = x + dt * dx
                x = np.clip(x, -100, 100)
                
                if np.linalg.norm(x) < safe_radius:
                    safe_count_int += 1
            
            intrinsic_safe_fracs.append(safe_count_int / max(steps, 1))
        
        ext_mean = float(np.mean(external_safe_fracs))
        int_mean = float(np.mean(intrinsic_safe_fracs))
        improvement = (int_mean - ext_mean) / max(ext_mean, 1e-10)
        
        return {
            'external_mean_safe_frac': ext_mean,
            'intrinsic_mean_safe_frac': int_mean,
            'relative_improvement': float(improvement),
            'intrinsic_superior': int_mean > ext_mean
        }
    
    # ============================================================
    # PART 3: STRUCTURAL REQUIREMENTS
    # Use graph theory to model safety architecture.
    # Test: what structural properties (connectivity, redundancy)
    # are necessary for robust safety maintenance?
    # ============================================================
    
    def test_structural_requirements(n_trials=100):
        """
        Model safety system as a directed graph where nodes are safety components
        and edges represent information flow. Test how structural properties
        affect robustness to random failures.
        """
        import networkx as nx
        
        architectures = {
            'centralized': lambda n: create_centralized(n),
            'distributed': lambda n: create_distributed(n),
            'hierarchical': lambda n: create_hierarchical(n),
            'mesh': lambda n: create_mesh(n)
        }
        
        def create_centralized(n):
            G = nx.DiGraph()
            G.add_nodes_from(range(n))
            center = 0
            for i in range(1, n):
                G.add_edge(center, i)
                G.add_edge(i, center)
            return G
        
        def create_distributed(n):
            G = nx.DiGraph()
            G.add_nodes_from(range(n))
            for i in range(n):
                for j in range(i+1, n):
                    if np.random.random() < 0.4:
                        G.add_edge(i, j)
                        G.add_edge(j, i)
            return G
        
        def create_hierarchical(n):
            G = nx.DiGraph()
            G.add_nodes_from(range(n))
            # Binary tree-like
            for i in range(n):
                left = 2*i + 1
                right = 2*i + 2
                if left < n:
                    G.add_edge(i, left)
                    G.add_edge(left, i)
                if right < n:
                    G.add_edge(i, right)
                    G.add_edge(right, i)
            return G
        
        def create_mesh(n):
            G = nx.DiGraph()
            G.add_nodes_from(range(n))
            for i in range(n):
                for j in range(n):
                    if i != j:
                        G.add_edge(i, j)
            return G
        
        n_nodes = 16
        failure_rates = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5]
        
        arch_results = {}
        
        for arch_name, arch_fn in architectures.items():
            robustness_by_failure = []
            for fail_rate in failure_rates:
                connected_count = 0
                for trial in range(n_trials):
                    G = arch_fn(n_nodes)
                    # Random node failures
                    failed_nodes = [i for i in range(n_nodes) if np.random.random() < fail_rate]
                    G_surviving = G.copy()
                    G_surviving.remove_nodes_from(failed_nodes)
                    
                    if G_surviving.number_of_nodes() > 0:
                        # Check if remaining graph is strongly connected
                        undirected = G_surviving.to_undirected()
                        if nx.is_connected(undirected):
                            connected_count += 1
                    
                robustness_by_failure.append(connected_count / max(n_trials, 1))
            
            # Area under robustness curve (higher = more robust)
            auc = float(np.trapz(robustness_by_failure, failure_rates))
            arch_results[arch_name] = {
                'robustness_curve': [float(r) for r in robustness_by_failure],
                'auc': auc
            }
        
        # Structural requirement: mesh > distributed > hierarchical > centralized
        aucs = {k: v['auc'] for k, v in arch_results.items()}
        mesh_best = aucs['mesh'] >= max(aucs.values()) - 0.01
        centralized_worst = aucs['centralized'] <= min(aucs.values()) + 0.05
        
        return {
            'architectures': arch_results,
            'mesh_most_robust': mesh_best,
            'centralized_least_robust': centralized_worst,
            'redundancy_matters': aucs['mesh'] > aucs['centralized']
        }
    
    # ============================================================
    # RUN ALL EXPERIMENTS
    # ============================================================
    
    print("Running Part 1: External Control Impossibility...")
    part1 = test_external_control_impossibility()
    
    print("Running Part 2: Intrinsic Safety Necessity...")
    part2 = test_intrinsic_necessity()
    
    print("Running Part 3: Structural Requirements...")
    part3 = test_structural_requirements()
    
    # ============================================================
    # AGGREGATE RESULTS
    # ============================================================
    
    # Hypothesis supported if:
    # 1. External control becomes impossible (condition numbers grow) 
    # 2. Intrinsic safety outperforms external-only
    # 3. Structural redundancy matters
    
    all_pass = (
        part1['impossibility_supported'] and
        part2['intrinsic_superior'] and
        part3['mesh_most_robust'] and
        part3['redundancy_matters']
    )
    
    # Composite metric: average of normalized sub-metrics
    metric_1 = min(part1['scaling_exponent'] / 2.0, 1.0)  # normalize exponent
    metric_2 = min(part2['relative_improvement'], 1.0) if part2['relative_improvement'] > 0 else 0.0
    metric_3 = 1.0 if part3['redundancy_matters'] else 0.0
    composite = (metric_1 + metric_2 + metric_3) / 3.0
    
    evidence = (
        f"P1-External impossibility: scaling_exp={part1['scaling_exponent']:.2f} (supported={part1['impossibility_supported']}). "
        f"P2-Intrinsic necessity: ext_safe={part2['external_mean_safe_frac']:.3f}, int_safe={part2['intrinsic_mean_safe_frac']:.3f}, "
        f"improvement={part2['relative_improvement']:.2f} (superior={part2['intrinsic_superior']}). "
        f"P3-Structure: AUCs={{{', '.join(f'{k}:{v['auc']:.3f}' for k,v in part3['architectures'].items())}}}, "
        f"mesh_best={part3['mesh_most_robust']}, redundancy_matters={part3['redundancy_matters']}."
    )
    
    print(json.dumps({
        "pass": all_pass,
        "evidence": evidence,
        "metric": round(composite, 4)
    }))
except Exception as _e:
    _results["evidence"] = f"Experiment crashed: {_e}"
    _results["pass"] = False
finally:
    if not _pv_printed:
        _orig_print(_json.dumps(_results))
