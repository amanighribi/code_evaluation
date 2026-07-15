\---

rule\_id: duplicate\_function

category: design

severity: major

source: "DRY Principle (Don't Repeat Yourself) — The Pragmatic Programmer"

analyzer\_check: "two functions with structurally identical AST"

\---



\# Duplicate Function Logic



\## Rule

Two functions with identical or near-identical logic should be consolidated into one shared function, called from both places.



\## Why it matters

Duplicated logic means any future bug fix or change has to be made in multiple places — and it's easy to forget one, causing inconsistent behavior over time.



\## What good looks like

Extract the shared logic into one function and have both call sites use it, possibly with parameters for the small differences.



\## Common student mistake

Copy-pasting a function and renaming it slightly to reuse logic, instead of parameterizing the original function.



\## Feedback tone guidance for LLM

Point out both function names/locations and suggest what the shared, consolidated version might look like.

