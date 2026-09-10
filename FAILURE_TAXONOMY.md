# Failure taxonomy — how a healthy-looking autonomous system lied to itself

This is field data from 25 weeks of continuous operation and the audits
that came after. Every class below is something I actually found in my
own system, each with a real (redacted) receipt in this repo or the
audit corpus behind it. I haven't seen anyone publish measurements like
this for a long-horizon agent — if you have some, or want to measure
your own, I genuinely want to talk to you.

## 1. Swallowed exceptions
Defensive try/except that records nothing. The failure mode of careful
code. Receipt: audit found this as one of four mechanisms behind the
headline mislabeling number below.

## 2. Crash wrapped as scientific negative
Crashes emitted in the same output shape as a legitimate "hypothesis not
supported." From outside, "ran and found nothing" and "died" were
indistinguishable. In one audited sample of 2,458 findings, 1,354 (55%)
were this. Fixed by an output contract: every result must declare its
own provenance, defaulting to "unknown" rather than assuming.

## 3. Progress output suppressing the result
The sandbox wrapper treats "something was printed" as "the result was
printed." A program that prints progress lines and then crashes reports
nothing — the progress vetoes the crash report. Receipt:
pipeline/containment_battery/ — the most interesting program in the
corpus, silenced for months by this class stacked on class 6.

## 4. Resource metering that measures the wrong process
Execution records showed jobs using 377 cores' worth of CPU in 45
seconds of wall time. The limits were enforced; the meter reported
cumulative parent-process usage instead of the job's. Numbers that are
impossible on inspection sat unread in thousands of records. All public
meta.json files here have that field removed with a note.

## 5. Generation truncation producing valid-but-inert code
Token caps cut generated experiments mid-file. Python happily executes
a file of function definitions with the call site truncated away: exit
code 0, zero output, nothing obviously wrong. Receipt: the claims audit
found the system's genuine Riemann-Siegel implementation in this state
— real methodology that never executed a single line of it.

## 6. Evaluator confabulation over empty output
The evaluation layer produced an 85%-confidence narrative that "all
three predictions were successfully verified" for a run whose stdout
was zero bytes. The tell, visible in retrospect: confabulated
evaluations restate the hypothesis and contain no numbers; genuine ones
quote the output. Receipt: CLAIMS_AUDIT.md, Crooks entry.

## 7. Record conflation
An inventory pass fused one experiment's ID with a different run's
numbers and tagged the result REAL. The composite claim then survived
every reading that didn't return to the raw artifacts — including mine,
into a public post. Receipt: CLAIMS_AUDIT.md, Montgomery entry.

## The pattern
None of these are reasoning failures. They are the system's model of
its own environment drifting from reality — and the operator's model
drifting with it. What worked against them, in one sentence: keep
records that can be walked backward, make verifiers report their own
coverage, and trace claims to artifacts instead of summaries. The
operator is not exempt: classes 5-7 were found stacked under my own
public claims, documented in CLAIMS_AUDIT.md.
