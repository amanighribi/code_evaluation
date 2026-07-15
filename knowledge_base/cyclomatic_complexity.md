\---

rule\_id: high\_cyclomatic\_complexity

category: maintainability

severity: major

source: "McCabe, T.J. (1976). A Complexity Measure. IEEE Transactions on Software Engineering."

analyzer\_check: "cyclomatic\_complexity > 5"

\---



\# High Cyclomatic Complexity



\## Rule

Cyclomatic complexity counts the number of independent execution paths through a function (each `if`, loop, or exception handler adds one path). A complexity above 5-10 is generally considered hard to test and understand.



\## Why it matters

High complexity means more test cases are needed for full coverage, and more mental effort is needed to trace through all possible branches. It strongly correlates with defect rates in real-world studies.



\## What good looks like

Break a highly branching function into smaller functions, each handling one condition or responsibility, and compose them.



\## Common student mistake

Nesting many `if/elif/else` blocks instead of using early returns or extracting helper functions.



\## Feedback tone guidance for LLM

Point to the specific branching structure causing the complexity (e.g. "the nested if inside your for loop") rather than a vague "simplify this function."

