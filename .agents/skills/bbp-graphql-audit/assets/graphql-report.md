# GraphQL Finding — Report Template

```markdown
## GraphQL <BOLA / Batching Rate-Limit Bypass / Info Disclosure>: <summary>

**Severity**: High (CVSS 7.5)
**Asset**: https://target.example.com/api/graphql
**Type**: Broken Object Level Authorization (API1:2023) / API4 Resource Limits

### Endpoint & engine

- Endpoint: POST /api/graphql
- Engine: <graphw00f result, e.g., Apollo Server 4>
- Introspection: enabled/disabled (<method used>)

### Finding 1 — BOLA on query `user(id)`

Request as User A (id 101):
```json
{"query":"query { user(id: 102) { id email phone ssn } }"}
```
Response:
```json
{"data":{"user":{"id":102,"email":"victim@x.com","phone":"+62...","ssn":"..."}}}
```
Expected: error/ownership check. Actual: full PII of User B returned.

### Finding 2 — Alias multiplexing bypasses login rate limit

Single request:
```graphql
mutation { l1:login(u:"admin",p:"g1"){token}
           l2:login(u:"admin",p:"g2"){token} }
```
Both operations processed independently; per-request rate limit defeated
(evidence: 3 attempts, not a brute-force run).

### Impact

- Any registered user can enumerate and read all user profiles (PII).
- Authentication controls can be sidestepped via alias batching.

### Reproduction steps

(numbered, with exact curl commands and both accounts' roles stated)

### Remediation

1. Enforce object ownership inside every resolver (not just top-level).
2. Disable introspection in production or gate it behind auth.
3. Enforce per-operation rate limits; reject JSON-array batching or cap it.
4. Add depth limiting + alias count limiting at the engine level.
```
