---
name: bbp-source-code-audit
description: Perform authorized source-code bug bounty review. Use for in-scope open-source repositories or source-code assets to find security bugs through local static analysis, code tracing, tests, and reproducible proof-of-concept creation without fabricating impact.
---

# BBP Source Code Audit

## Setup

1. Create a clean folder under `C:\BugBounty\programs\<program>\source`.
2. Clone the repository or copy the source.
3. Record:
   - repository URL
   - branch
   - commit SHA
   - dependency/runtime versions
4. Build or run tests if practical.

## Discovery Passes

Run focused searches first:

- authz/authn bypass: `auth`, `authorize`, `permission`, `role`, `owner`, `tenant`
- token/session issues: `jwt`, `sign`, `verify`, `secret`, `nonce`, `session`
- request trust boundary: `header`, `origin`, `redirect`, `callback`, `webhook`
- filesystem/process: `exec`, `spawn`, `open`, `path`, `upload`, `download`
- crypto/signature misuse: `serialize`, `deserialize`, `verify`, `digest`, `hmac`
- dangerous catches: `catch`, `Throwable`, `Exception`, `panic`, `recover`
- business logic: `balance`, `withdraw`, `transfer`, `refund`, `payment`

## Validation

For every candidate:

1. Trace source to sink.
2. Identify attacker control.
3. Identify missing or broken security check.
4. Prove the behavior locally with a unit test, script, or minimal reproduction.
5. Confirm impact is security-relevant and in scope.
6. Check duplicates before preparing a report.

## Integrity Rules

- Never invent runtime output, screenshots, server behavior, customer data, or bounty impact.
- If only source review was performed, say so clearly.
- If no live service was tested, say so clearly.
- Prefer a failing regression test or local PoC over narrative-only claims.

## Evidence

Save all evidence under:

```text
C:\BugBounty\programs\<program>\evidence\<finding-slug>
```

Include:

- reproduction script or test
- command log
- relevant source excerpts
- version/commit metadata
- expected vs actual behavior

## Report Readiness

A finding is report-ready only when:

- the asset is in scope
- the root cause is clear
- the PoC is reproducible
- the impact is not hypothetical
- duplicate risk was checked
- the report states the exact validation boundary
