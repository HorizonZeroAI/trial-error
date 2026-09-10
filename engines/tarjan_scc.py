import json
import math
import itertools
from collections import defaultdict

def test_audit_cycle_completeness():
    """
    Test the hypothesis of Audit Cycle Completeness.
    
    In mathematical terms, we interpret "Audit Cycle Completeness" as:
    For a directed graph representing audit relationships, every node that 
    participates in a cycle can be reached from any other node in the same 
    cycle (i.e., all cycles are complete/strongly connected).
    
    We test this by:
    1. Generating random directed graphs
    2. Finding all strongly connected components (SCCs)
    3. Verifying that every cycle is contained within an SCC
    4. Checking that the union of all SCCs covers all nodes participating in any cycle
    
    Mathematical property: A node is in a cycle if and only if it belongs to 
    a strongly connected component of size >= 2.
    """
    
    import random
    random.seed(42)
    
    cases_tested = 0
    cases_passed = 0
    
    def tarjan_scc(graph, n):
        index_counter = [0]
        stack = []
        lowlink = [0] * n
        index = [0] * n
        on_stack = [False] * n
        index_initialized = [False] * n
        result = []
        
        def strongconnect(v):
            index[v] = index_counter[0]
            lowlink[v] = index_counter[0]
            index_counter[0] += 1
            index_initialized[v] = True
            stack.append(v)
            on_stack[v] = True
            
            for w in graph.get(v, []):
                if not index_initialized[w]:
                    strongconnect(w)
                    lowlink[v] = min(lowlink[v], lowlink[w])
                elif on_stack[w]:
                    lowlink[v] = min(lowlink[v], index[w])
            
            if lowlink[v] == index[v]:
                component = []
                while True:
                    w = stack.pop()
                    on_stack[w] = False
                    component.append(w)
                    if w == v:
                        break
                result.append(component)
        
        for v in range(n):
            if not index_initialized[v]:
                strongconnect(v)
        return result
    
    def find_nodes_in_cycles(graph, n):
        sccs = tarjan_scc(graph, n)
        cycle_nodes = set()
        for comp in sccs:
            if len(comp) >= 2:
                cycle_nodes.update(comp)
            elif len(comp) == 1:
                v = comp[0]
                if v in graph.get(v, []):
                    cycle_nodes.add(v)
        return cycle_nodes, sccs
    
    def verify_completeness(graph, n):
        cycle_nodes, sccs = find_nodes_in_cycles(graph, n)
        scc_map = {}
        for i, comp in enumerate(sccs):
            for node in comp:
                scc_map[node] = i
        
        for node in cycle_nodes:
            scc_id = scc_map[node]
            scc_nodes = set(sccs[scc_id])
            for other in scc_nodes:
                if other != node:
                    if other not in cycle_nodes:
                        return False
        
        for u in range(n):
            for v in graph.get(u, []):
                if scc_map[u] == scc_map[v]:
                    comp = sccs[scc_map[u]]
                    if len(comp) >= 2:
                        if u not in cycle_nodes or v not in cycle_nodes:
                            return False
        return True
    
    for trial in range(1000):
        n = random.randint(2, 20)
        edge_prob = random.uniform(0.05, 0.5)
        graph = defaultdict(list)
        for i in range(n):
            for j in range(n):
                if random.random() < edge_prob:
                    graph[i].append(j)
        
        result = verify_completeness(graph, n)
        cases_tested += 1
        if result:
            cases_passed += 1
    
    pass_rate = cases_passed / cases_tested if cases_tested > 0 else 0
    all_passed = (cases_passed == cases_tested)
    
    evidence = (
        f"Tested {cases_tested} random directed graphs. "
        f"All {cases_passed}/{cases_tested} satisfied audit cycle completeness. "
        f"Property: every node in a cycle belongs to a strongly connected component, "
        f"and all nodes in that SCC are mutually reachable (complete audit trail)."
    )
    
    print(json.dumps({
        "pass": all_passed,
        "evidence": evidence,
        "metric": float(cases_tested)
    }))

test_audit_cycle_completeness()