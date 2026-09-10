# Architecture Overview

Structural overview of an autonomous research system built and run over the past
year. This describes shape and design decisions, not implementation. The core
architecture is not public.

## Scale

~80,000 lines of Python across 321+ modules, running as 24 background services
on a single cloud server — 8 vCPUs, 31GB RAM, no GPU. Thirty-minute cognition
cycle. 25 weeks continuous uptime.

Module distribution:

```
api           78   HTTP surface — every faculty has an interface
research      24   replication, foundry, causal, provenance, calibration
entity        13   self layer
cognitive      8   reflection, self-audit, self-diagnosis
security       8   egress, red team, containment, policy
planner        6   active inference, global workspace, goal generation
llm            4   tiered model routing
improvement    4   program evolution, reflexion, skill distillation
product        4   commercialization
sandbox        3   isolated execution + output contracts
safe_apply     3   gated self-modification
voice          3   speech synthesis
stats          1   statistical engine (included here)
```

Plus bus, ledgers, metrics, data, ops, optimization, modules, agents, utils.

## Data model

**146 append-only JSONL ledgers, ~580MB.** Nothing is ever overwritten. A
correction is a new row referencing the row it corrects.

This is the decision everything else depends on. It was built for rollback
safety, and the consequence I didn't anticipate is that any result the system
produces can be walked backward completely — the exact code, the process
metadata, stdout, stderr, the environment, the dependency versions, the
reasoning that produced the hypothesis. All resolvable by ID.

It's also what made auditing possible. I could reconstruct twenty-five weeks of
behavior because nothing had been discarded.

## Layers

**Self.** Reads live data sources and surfaces the contradictions between them
rather than reconciling them. Tracks novelty, forms cross-domain associations,
maintains layered memory (short-term / episodic / semantic) with continuous
consolidation. Snapshots its own behavior so a modified version can be compared
against how it behaved before the change.

**Reflection.** Recursive self-audit, self-diagnosis, hindsight synthesis,
detection of capabilities that emerged rather than being designed.

**Research.** Pulls papers from arXiv through a gated egress path (~31,000
fetches, all logged) and reproduces published results — with `rejected` as a
legitimate verdict. A hypothesis foundry running preregistration -> sandboxed
execution -> Bayesian effect sizes -> promote or reject. Causal inference,
lineage, provenance, a p-hacking immune system, calibration tracking.

**Safety.** Four properties verified nightly by an automated scan (kept private).
Adversarial verification. Network egress off by default, every call allowlisted
and logged. Self-modification passes six gates — syntax validation, signature
preservation, AST splice, CI baseline, candidate run, verifier approval — plus
operator approval before anything applies.

## Sandbox and the output contract

Experiments run isolated under resource limits. Every result declares its own
provenance: whether it ran on real or synthetic data, and how many real records
it actually read. The wrapper defaults those fields to `unknown` rather than
assuming, so an undeclared result stays visible instead of passing as real.

That contract exists because of a specific failure. Crashes were being wrapped
and emitted in the same shape as legitimate negative results — from outside,
"the experiment ran and found nothing" and "the experiment died" were
indistinguishable. In one audited sample of 2,458 findings, 1,354 turned out to
be the second thing recorded as the first.

## Model routing

Four tiers with explicit gating. A local model handles anything identity-bearing;
cloud models are tools the system uses, never the thing producing its own
outputs. Every call is logged to a corpus intended for eventually training a
local replacement.

Under a freeze flag, cloud tiers fail fast and the sandbox refuses jobs. The
system keeps thinking and consolidating memory but stops doing research.

## Current state

Frozen. Research stopped in August; the system is kept alive — thinking,
consolidating, running its safety checks — while I repair what the audits found
and wire components that were built and never connected, which turned out to be
the largest single category of defect.

The reason for the freeze: I want to fine-tune a local model on the system's own
corpus. If the mislabeling rate across the rest of it resembles what I found in
the audited sample, training on it as-is would make that permanent.
