# Codebase shape

People reasonably ask whether "80,000 lines" means a real system or a
pile of generated filler. Fair question. So instead of asserting, I
counted it, directly from a point-in-time mirror of the source tree.
First-party source only — no virtualenvs, no caches, no backups, no
data files (the ledgers and experiment artifacts are separate and much
larger).

## Totals
| category | files | lines |
|---|---|---|
| Python | 321 | 80,382 |
| dashboard (JavaScript) | 23 | 8,971 |
| shell | 33 | 3,267 |
| CSS / HTML | 8 | 2,288 |
| **code total** | **385** | **94,908** |
| docs, configs, service units | 192 | 39,911 |
| **everything** | **577** | **134,819** |

There's also an off-box companion toolchain (an MCP server I use for
operator diagnostics, plus audit harnesses) — roughly another 80 Python
files / 20,000 lines. I count that as tooling around the system, not
the system, so it's not in the table.

## Size distribution (all 321 Python files)
| file size | count |
|---|---|
| under 100 lines | 155 |
| 100-300 | 86 |
| 300-600 | 47 |
| 600-1,000 | 24 |
| over 1,000 | 9 |

Median file is 115 lines. That shape is what I'd defend: most of the
system is small single-purpose modules, and nine cores over 1,000
lines do the heavy lifting.

## The biggest file in the codebase is the verifier
The single largest source file (5,617 lines) is the nightly harness
that checks the rest of the system against its acceptance criteria.
Counting all the verification and ops tooling together, about one line
in seven exists to check the other six. It reports its own coverage
every night now — because at one point it was genuinely testing 33 of
475 criteria while reporting "passed," and I only found that out by
auditing the auditor.

## Where the Python lives (files / lines)
Same granularity as the module table in ARCHITECTURE.md, with line
counts. Sums to the 321 / 80,382 above.
| layer | files | lines |
|---|---|---|
| HTTP API surface | 79 | 13,918 |
| verification & ops tooling | 31 | 13,810 |
| self layer | 31 | 10,021 |
| research | 24 | 9,477 |
| generated standalone services | 49 | 6,573 |
| planner | 7 | 5,459 |
| cognitive | 9 | 5,344 |
| tests | 18 | 1,102 |
| everything else (security, llm routing, improvement, product, sandbox, metrics, bus, data) | 73 | 14,678 |

The thing I notice in that table: verification is the second-biggest
investment in the whole system, and the self layer is about the same
size as the research layer. It studies itself about as hard as it
studies anything else. That wasn't the plan — it's just where a year
of fixing what the audits found ends up.
