\---

rule\_id: unused\_import

category: cleanliness

severity: minor

source: "PEP 8 — imports should be used; Pyflakes/Flake8 convention"

analyzer\_check: "imported name never referenced"

\---



\# Unused Import



\## Rule

Every imported module or name should actually be used somewhere in the file. Unused imports should be removed.



\## Why it matters

Unused imports add noise, can mislead readers into thinking a dependency is used when it isn't, and in larger projects can slow down startup time or hide genuinely unused dependencies.



\## What good looks like

Only import what you use, and remove imports as soon as the code that needed them is deleted.



\## Common student mistake

Leaving imports behind after refactoring code that used to need them.



\## Feedback tone guidance for LLM

Keep this feedback brief and factual — it's a simple cleanup issue, not a design problem.

