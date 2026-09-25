---
name: bbp-business-logic
description: Specialized skill for identifying and exploiting business logic flaws, race conditions, and payment manipulation vulnerabilities. Use during authorized bug bounty work to abuse checkout flows, coupons, workflow state, and TOCTOU windows with safe PoCs and a full finding report.
version: "2.0"
---

# Business Logic & Race Condition Skill

Targets flaws in intended application behavior rather than injection
vectors: payment manipulation, coupon/limit races, workflow-state bypass,
and verification-flow abuse.

## When to Use

- App has money flows: cart, checkout, wallet, refunds, gift cards, payouts
- Single-use resources: coupons, invite codes, OTPs, password reset tokens
- Multi-step workflows: registration, KYC, checkout, approval chains
- Limits exist that should be enforced server-side (votes, redemptions,
  transfer caps, free-tier quotas)

## Prerequisites

- **Two or more test accounts you own** (never test against real customers)
- Burp Suite Pro (Repeater + Turbo Intruder) or the bundled race_probe.py
- Written authorization; program policy on payment testing READ FIRST —
  most programs require using 100%/sandbox test amounts only
- Baseline captures of every request in each flow (Proxy history)

## Workflow

### Step 1: Model the Intended Logic First

For each flow write down the invariant the developer assumes:

```text
Flow: checkout
Invariants assumed by app:
  I1 price comes from trusted source
  I2 quantity >= 1 and <= stock
  I3 coupon applied once per user
  I4 payment confirmed BEFORE order status = paid
  I5 shipping step cannot be skipped
Attack surface = every way to violate I1..I5
```

### Step 2: Parameter-Level Abuse (I1/I2)

```bash
# Negative / zero values
curl -X POST https://target.example.com/api/cart/items \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"sku":"SKU123","quantity":-1}'          # credit instead of charge

-d '{"price":0.001,"quantity":1}'              # sub-cent rounding abuse
-d '{"price":"1e-9"}'                          # exponent notation parsing
-d '{"quantity":2147483648}'                   # int32 overflow / wrap

# Currency confusion
-d '{"amount":100,"currency":"IDR"}'           # was USD; amount kept at 100
-d '{"amount":100,"currency":"usd"}'           # case-handling bugs
```

### Step 3: Coupon / Single-Use Races (I3)

```bash
# Capture the exact redeem request first (Burp), then either:
# a) Turbo Intruder script -> references/workflows.md
# b) bundled helper:
python scripts/race_probe.py \
  --url "https://target.example.com/api/coupons/redeem" \
  --method POST \
  --header "Cookie: session=<yours>" \
  --header "Content-Type: application/json" \
  --data '{"code":"SAVE10","cart_id":987}' \
  --threads 30 --requests 60
# Success signal: balance/discount applied more than once in responses,
# or final order total reflects N>1 applications.
```

Other race targets: OTP consumption, password-reset single-use tokens,
gift-card load, vote/like counters, referral bonus payout, withdrawal vs
balance debit.

### Step 4: Workflow-State Bypass (I4/I5)

```bash
# Skip payment: call confirmation directly with your own session
curl -X POST https://target.example.com/api/checkout/confirm \
  -H "Authorization: Bearer $TOKEN" -d '{"order_id":90001}'

# Replay a completed flow with a modified earlier step
#   complete checkout normally for $5 item, then replay confirm for $500 order id
# Hidden field tampering
-d '{"status":"paid"}'
-d '{"is_verified":true}'
-d '{"discount_applied":100}'
-d '{"role":"premium"}'      # mass assignment via workflow params
```

### Step 5: Verification-Flow Abuse

```text
Email/phone verify: submit code from account A against account B session;
  try code reuse after success; try predictable codes (000000, 123456);
  test response-body leaks of the code (debug flags).
Password reset: token not invalidated after use/re-request; host-header
  poisoning of reset link (see bbp skill harvested: testing-for-host-header-injection).
OTP: response comparison across wrong/right codes; missing expiry window.
```

### Step 6: Quantify Impact Honestly

- Compute actual monetary delta achievable per attack iteration.
- State whether it is self-enrichment (wallet credit), fraud against other
  users (requires their consent in-lab: use ONLY your own accounts), or
  availability/quota abuse.
- Never leave altered state behind: cancel orders, restore balances where
  the platform provides test/sandbox mode; note every mutation made.

## Key Concepts

| Concept | Description |
|---------|-------------|
| TOCTOU | Time-of-check to time-of-use gap enabling races |
| Invariant | Assumption developers rely on; breaking one = logic bug |
| Idempotency | Whether repeating a request changes outcome twice |
| Client-trust | Server trusting client-sent price/status/role fields |
| State machine bypass | Reaching later workflow states without prior steps |

## Common Scenarios

1. Coupon redeemed concurrently N times -> total discount exceeds limit
2. Refund requested while item still ships -> double compensation
3. Withdrawal + transfer raced so combined outflow > balance
4. Checkout confirm reachable pre-payment via direct API call
5. Free-tier signup repeated with same card but normalized emails

## Output Format

Use `assets/logic-report.md`: include invariant broken, minimal repro,
monetary impact math, race timing evidence (response table), and cleanup
statement of what state was restored.
