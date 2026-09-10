# Exhibit: 3-SAT phase transition — alpha_c ~ 4.25 (literature: 4.267)

One experiment, exactly as the system recorded it. The system wrote a DPLL
SAT solver from scratch with two branching heuristics (VSIDS-style activity
scoring vs. random selection), generated random 3-SAT instances across
clause-to-variable ratios alpha = 3.5 to 5.0, and located the
satisfiability phase transition by peak search + power-law fit.

Result: alpha_c ~ 4.25 against the published critical ratio of ~4.267
(Mezard, Parisi, Zecchina 2002 and successors). The heuristic-scaling
difference (VSIDS exponent 0.302 vs random 0.073, t-test p=0.0101) was the
actual hypothesis under test; the phase-transition recovery is the
literature check that says the apparatus works.

| file | what it is |
|---|---|
| code.py | the solver + sweep the system wrote |
| meta.json | execution record (see _redaction_note) |
| stdout.txt | the result line, verbatim |

The solver is ~160 lines, self-contained, stdlib + numpy/scipy only.
Correctness is checkable: run it yourself.
