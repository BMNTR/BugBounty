---
name: bbp-program-triage
description: Triage bug bounty programs before research. Use when evaluating HackerOne, YesWeHack, Bugcrowd, or similar bounty programs to decide whether an asset is worth working, whether accounts are required, what is in scope, what testing is forbidden, and what route is likely to be lowest-risk and highest-signal.
---

# BBP Program Triage

## Workflow

1. Read the program policy before touching assets.
2. Extract and summarize only operational facts:
   - in-scope assets
   - out-of-scope findings
   - account or KYC requirements
   - allowed testing methods
   - forbidden testing methods
   - bounty range and response SLA
   - required headers, aliases, or test account labels
3. Classify each asset by research fit:
   - source code: best for static review and low-noise validation
   - executable/mobile app: best for local reverse engineering and safe dynamic tests
   - domain/API: requires careful rate-limited manual testing only
   - smart contract/blockchain: requires local/testnet reproduction
   - hardware: skip unless physical device is available
4. Prefer work that can be validated locally without touching real users or production data.
5. Do not start active testing when the policy forbids the technique or when the scope is ambiguous.

## Decision Rules

- If the user has already asked about a program, say so before starting new work.
- If a program requires an account, tell the user exactly what account step they must do and what the agent can do after that.
- If a program requires Signal, KYC, invitation, or unavailable access, say that it is blocked.
- If the likely route needs real payments, bookings, abuse of third-party users, DoS, spam, brute force, social engineering, or leaked credentials, do not perform it.
- For source code programs, start with repository cloning, commit pinning, and local-only analysis.
- For mobile apps, prefer manifest/exported component review, local emulator/device validation, and non-destructive PoC.

## Output Format

Always answer with:

```text
Verdict:
Best target:
Needs account:
Safe first checks:
Do not test:
Next action:
```

Keep the recommendation practical and do not overpromise payouts.
