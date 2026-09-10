# Metrics

Every number I've claimed publicly, with an honest tag on how far it's
been checked. I'd rather undersell with tags than oversell without
them.

Tags:
- [verified] — I re-derived it from raw records specifically for this
  repo.
- [audited] — established during my system audits earlier this year;
  the audit corpus exists but I haven't re-derived it fresh for the
  repo.
- [claimed] — comes from the system's own ledgers/counters and hasn't
  been independently re-checked yet. Treat accordingly.

| metric | value | tag |
|---|---|---|
| First-party code | 385 files / 94,908 lines (321 Python / 80,382, plus dashboard JS/CSS and shell) | [verified] — see CODEBASE_SHAPE.md |
| Continuous operation | 25 weeks on one 8-vCPU CPU-only server | [claimed] |
| Append-only ledgers | 146 files, ~580MB, nothing ever overwritten | [claimed] |
| Research records | 19,391 across 3,575 subjects | [claimed] |
| Gated arXiv fetches | ~31,000, all logged | [claimed] |
| Self A/B evaluations | 10,516 recorded keep/discard decisions | [audited] — see composition note below |
| Findings audit | of 2,458 findings sampled, 1,354 (55%) were infrastructure failures recorded as scientific negatives | [audited] — this is the finding that started everything |
| Verifier coverage | 33 of 475 criteria (7%) actually tested while reporting "passed"; it now self-reports coverage nightly | [audited] |
| Standalone stats service | generated, packaged and deployed by the system; loopback-only; deployed 2026-03-11 | [verified] deploy date from service records; the exact continuous-uptime figure is pending a re-check, so I'm not quoting one here |

## What "10,516 A/B tests" actually means
I went and sampled the decision records rather than just repeating the
number. Of 55 sampled: 23 carried full baseline-vs-candidate
measurements, 25 were CI-skipped with null measurements, the rest were
metadata-only decisions. So "10,516" counts recorded decisions, not
uniformly rigorous experiments — I want that distinction on the record.

Three real records, paths redacted:

1. baseline 2946ms rc=0 vs candidate 229ms rc=1 -> KEEP=false,
   reason=candidate_failed. It rejected a 12.8x speedup because the
   candidate failed correctness. This is my favorite record in the
   whole corpus.
2. baseline 2254ms rc=0 vs candidate 1139ms rc=0 -> KEEP=true, on one
   of its own core planning modules.
3. baseline 6252ms vs candidate 7928ms -> KEEP=false,
   reason=candidate_slower.

Honest summary: the keep/discard machinery is real and makes correct
calls when it measures. A substantial fraction of its history skipped
measurement, and that fraction is itself now a tracked number.
