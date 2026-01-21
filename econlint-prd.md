# econlint: Product Requirements Document

## One-sentence description

A static analysis tool that flags Python code patterns which create hidden or runaway economic cost in production systems.

---

## Core idea

Most static analysis focuses on correctness, security, or style. econlint answers a different question: "If this code misbehaves at scale, how does it cost money?"

**This is economic risk detection, not cost optimization.**

**Critical differentiation:** Detection logic is table stakes—tools like Semgrep can already flag loops containing external calls. The value is in the *framing* and *explanation quality*. Every warning must make the engineer *feel* the cost implication. If the output looks like any other linter, the project fails.

---

## Problem statement

In cloud-metered systems, small code decisions create nonlinear cost. Failures amplify spend rather than halt execution. Engineers notice after the bill arrives.

Patterns like retries without caps, API calls inside loops, and unbounded concurrency are common, reviewable, and statically detectable—yet rarely flagged as economic risk.

### Target user

**Primary:** Senior engineers, staff/principal engineers, owner-operators, PE-backed or cloud-metered teams

**Not targeted:** Beginners, frontend-only developers, teams wanting style enforcement

---

## Product goals

1. Surface economic failure modes, not bugs
2. Tie each warning explicitly to a cost mechanism
3. Make warnings *feel* expensive—the explanation is the product
4. Remain fast, readable, and non-intrusive

### Non-goals

- General linting
- Configuration framework (except inline ignores)
- Severity levels
- Dashboards or runtime instrumentation
- AI-generated explanations
- Multi-language support

If it drifts into these areas, it loses credibility.

---

## v1 scope

### The four rules

| Rule | Pattern | Economic risk |
|------|---------|---------------|
| ECON001 | External calls inside loops | Cost scales with iteration count; retries multiply under failure |
| ECON002 | Retry logic without hard cap | Transient failures become runaway spend |
| ECON003 | N+1 patterns against paid systems | Linear cost growth tied to data size |
| ECON004 | Unbounded fan-out | Bursty cost spikes and vendor throttling penalties |

### Output

Each warning includes: rule ID, location, pattern detected, economic risk explanation, and mitigation guidance.

The explanation quality is the differentiating feature. Each must:
- State what was found concretely
- Connect to a specific cost mechanism
- Explain how small becomes large
- Suggest mitigation

### Inline suppression

`# econlint: ignore` syntax prevents abandonment when the tool flags legitimate patterns.

---

## Success criteria

**Succeeds if:** A senior engineer runs it, understands the warnings without documentation, and says "yes, that would get expensive."

**Fails if:** It feels generic, overclaims precision, or becomes configurable noise.

---

## Positioning intent

This project signals operator-level thinking, comfort with production failure modes, technical judgment over novelty, and restraint in scope.

It is intentionally small.

---

## Out of scope for v1

- Multi-language support
- Configuration files
- Severity levels
- IDE integrations
- Pre-commit hooks (users can add themselves)
- Cost estimation in dollars

These are reasonable v2 features.
