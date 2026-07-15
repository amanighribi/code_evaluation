\---

rule\_id: unused\_variable

category: cleanliness

severity: minor

source: "General code cleanliness convention (Pyflakes/Flake8)"

analyzer\_check: "variable assigned but never read"

\---



\# Unused Variable



\## Rule

A variable that is assigned a value but never used afterward is dead code and should be removed (or prefixed with `\_` if intentionally unused).



\## Why it matters

Unused variables clutter the code and can indicate an incomplete thought, a leftover from debugging, or a genuine logic mistake (e.g. forgetting to return or use a computed value).



\## What good looks like

Remove genuinely unused variables; if a value is intentionally discarded (e.g. in unpacking), prefix it with `\_`.



\## Common student mistake

Computing an intermediate value for debugging (`print`-style) and forgetting to remove the variable afterward.



\## Feedback tone guidance for LLM

Ask whether the variable was meant to be used somewhere (e.g. in a return statement) — this is often a sign of an incomplete implementation, not just style.

