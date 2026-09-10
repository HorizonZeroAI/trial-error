# Autonomous Research System — public samples

Sample output and selected modules from an autonomous research system
I've been building and running for the past year. It ran continuously
for 25 weeks on a single CPU-only cloud server. It's frozen right now
while I fix what my own audits found.

Quick context: a year ago I had never written code. I designed the
architecture, directed AI coding agents to implement it, and built the
verification process that checks their output. The verification turned
out to be the hard part, and honestly most of this repo is evidence of
that.

The core architecture is not public and isn't going to be. What's here
is enough to judge whether the system does real work. I'm happy to talk
about how any of it functions at the conceptual level.

## Where to start
- `ARCHITECTURE.md` — the shape and the design decisions, not the
  implementation
- `CODEBASE_SHAPE.md` — measured size and structure. 385 code files,
  94,908 lines, and the largest file in the codebase is the verifier
- `METRICS.md` — every number I've claimed, tagged by how far it's
  been checked
- `FAILURE_TAXONOMY.md` — seven ways a healthy-looking autonomous
  system lied to itself, each with a receipt in this repo

## `pipeline/` — complete experiments, exactly as recorded
Each folder is one experiment end to end: the code the system wrote,
the execution record, and the verbatim stdout. Nothing cleaned up
beyond redacting paths.

| exhibit | result |
|---|---|
| `riemann_zeta/` | 500 zeros at 25-decimal precision via mpmath; N(T)/Gram's Law suite passes 5/5 criteria, Lehmer phenomenon confirmed |
| `sat_phase_transition/` | from-scratch DPLL solver finds the 3-SAT phase transition at alpha_c ~ 4.25 against the literature's ~4.267 |
| `chsh_tsirelson/` | Bell test sim: classical arm respects the bound of 2, quantum arm hits 2.824 under Tsirelson's 2.828. Recorded pass=false because a second bundled criterion failed — the ledger keeps it that way, and I left it that way |
| `arrow_of_time/` | classifier distinguishes time-forward from time-reversed trajectories at accuracy 1.000 over reversible microdynamics |
| `containment_battery/` | the system's own control-theory analysis of whether agentic systems can be externally contained. Silenced for months by two stacked infrastructure failures; completed for the first time during my claims audit. Read this one |

## `engines/` — programs the system wrote and validated itself
Textbook algorithms on purpose — correctness is checkable against known
results instead of taken on faith. All self-contained; run them.
- `tarjan_scc.py` — correct Tarjan implementation. Fair warning: the
  property it tests is close to true-by-construction, so weigh
  "1000/1000" accordingly
- `hash_chain_tamper_detect.py` — hash chain + modular-inverse tamper
  detection, 2500/2500
- `ipf_max_entropy.py` — iterative proportional fitting max-entropy
  solver, matches the product distribution to 4.4e-16
- `persistent_homology.py` — kept with a review note in the header: its
  bottleneck approximation is too loose for the stability figure to
  mean much. It's what the system actually wrote, so it stays

## `system/` — one module from the system itself
- `stats_engine.py` — Cohen's d with CIs, JZS Bayes factors, power
  analysis. Feeds the hypothesis pipeline's promote/reject decisions.
  The system later packaged this into a standalone loopback-only API
  service on its own (deployed 2026-03-11)

## `rerun/`
Two of my original public claims failed when I traced them back to raw
artifacts. I re-ran both experiments with clean implementations and
both hold. Scripts and results are in there, runnable in minutes, with
provenance labels — these are my runs, not system output, and I'm not
pretending otherwise.

## The claims audit
Before publishing this repo I traced every public claim I'd made back
to the artifact that produced it. Two of four literature checks needed
correction, and the full trace — including exactly how each one went
wrong — is in `CLAIMS_AUDIT.md`. The whole premise of the system is
that any result can be walked backward to its origin. I don't get an
exemption from that.

## Who I'm hoping hears about this
I built this alone, and the hardest part hasn't been the engineering —
it's having nobody to talk to about any of it. So, plainly:
- If you run long-horizon or autonomous agents, I want to compare
  notes. Especially if you've measured your own
  infrastructure-failure-as-result rate, or your verifier's actual
  coverage, or anything else in `FAILURE_TAXONOMY.md`
- If you work on AI safety or evaluation: the evaluator-confabulation
  receipt and the containment battery are the two things here I most
  want someone to challenge
- If you just find this interesting, that's enough. I genuinely can't
  tell if I'm on a path worth continuing or reinventing wheels badly,
  and I'd like to be told either way
- If any of this is useful to something you're building and you think
  I could help, I'm open to that conversation too

DMs open, issues open. I'd rather be corrected than agreed with.

## Known weaknesses, so you don't have to dig for them
Single machine. Single operator. No peer review. Experiments run at
sandbox scale, not cluster scale. The corpus is mid-repair — the
failure taxonomy is why — and the system stays frozen until that's
done. And two of my own original claims failed their trace; they're
corrected in `CLAIMS_AUDIT.md`, not deleted.
