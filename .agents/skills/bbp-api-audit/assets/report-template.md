# API Finding — Report Template

```markdown
## API BOLA: <endpoint> returns other users' objects

**Severity**: High (CVSS 8.1)
**Asset**: GET https://target.example.com/api/v1/orders/{id}
**Type**: CWE-639 Authorization Bypass Through User-Controlled Key (API1:2023)

### Reproduction (two owned accounts)

1. Account A (id 101) creates order 90001.
2. Account B (id 102) requests it:

```
GET /api/v1/orders/90001
Authorization: Bearer <token_B>
```

3. Response 200 with full order payload of A (JSON excerpt attached).
4. Control: expired token -> 401 (authn enforced; authz missing).

Evidence: evidence/bola_pair.png (both responses side by side).

### Impact

Any registered user can read every order on the platform by iterating ids
(demonstrated range 90000-90004 only). Exposure includes name, address,
phone, last4 card.

### Remediation

1. Enforce ownership check inside handler using authenticated principal,
   not client-supplied user_id.
2. Prefer scoped queries (`WHERE owner = :principal`).
3. Add regression tests per endpoint for cross-tenant access.
4. Alert on sequential id access patterns per token.
```
