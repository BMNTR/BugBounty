# Business Logic Finding — Report Template

```markdown
## Business Logic: <one-line flaw summary>

**Severity**: High (CVSS 7.5) / adjust to actual monetary & reach
**Asset**: https://target.example.com/api/...
**Type**: Improper Authorization / Race Condition / Payment Logic Flaw

### Broken invariant

App assumes: <e.g., "a coupon code can be redeemed exactly once per user">
Reality:    <e.g., "N concurrent redeems all pass the used-check">

### Minimal reproduction

1. Login as test account A (owned by researcher).
2. Capture redeem request:
```
POST /api/coupons/redeem HTTP/1.1
Cookie: session=...
{"code":"SAVE10","cart_id":987}
```
3. Fire 30 concurrent copies (Turbo Intruder gate / race_probe.py).
4. Observe 27x HTTP 200 with `"applied": true`; final cart total -270.

### Evidence table

| Req# | Status | Response | Effect |
|---|---|---|---|
| 1 | 200 | {"applied":true} | discount row #1 |
| 2 | 200 | {"applied":true} | discount row #2 |
| ... | ... | ... | ... |

Screenshot(s): evidence/race_results.png, evidence/final_total.png.

### Impact (honest math)

- Per iteration an attacker gains $10 x N discount against their own order.
- At scale (scripted), unlimited store credit -> direct financial loss.
- No special privilege required; any registered user can execute.

### Cleanup statement

All test mutations were performed on researcher-owned account A.
Orders #90001-#90003 canceled; balances restored via [sandbox reset /
support ticket]. No third-party data touched.

### Remediation

1. Enforce atomic redemption: `INSERT INTO redemptions ... ON CONFLICT DO NOTHING`
   and treat affected-rows==0 as already-used.
2. Wrap check+write in one transaction with row lock (SELECT ... FOR UPDATE).
3. Require server-generated idempotency keys on money endpoints.
4. Add alerting on same-code redeem rate > X/sec per account.
```
