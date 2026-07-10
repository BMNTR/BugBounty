---
name: bbp-api-audit
description: Test authorized API endpoints for security vulnerabilities. Use for in-scope REST, GraphQL, or gRPC APIs to find IDOR, BOLA, mass assignment, rate limiting issues, injection, SSRF, and auth bypass through structured request/response analysis.
---

# BBP API Audit

## Setup

1. Identify base URL, auth mechanism, and API docs (OpenAPI, GraphQL schema, Postman collection).
2. Record: auth type (JWT, OAuth, session cookie, API key), rate limits, content types.
3. Set up a proxy (Burp, Caido, or mitmproxy) if interactive testing is needed.

## Endpoint Inventory

For each endpoint, record:

```text
METHOD /path
Auth required: yes/no
Params: query, path, body
Response codes: 200, 4xx, 5xx
Content-Type: JSON, XML, form
```

## Test Categories

### BOLA / IDOR
- Replace object IDs in path/body with other users' IDs.
- Test both numeric and UUID identifiers.
- Check if authorization is checked before data access.

### Mass Assignment
- Add unexpected fields to JSON body.
- Check if extra fields are accepted and persisted.

### Rate Limiting & Bruteforce
- Send repeated requests to auth endpoints.
- Check for rate limit headers (Retry-After, X-RateLimit-*).
- Test password reset, OTP, and invite endpoints.

### Injection
- SQLi: `'`, `"`, `--`, `sleep(1)` in params.
- NoSQLi: `$gt`, `$ne`, `$where` in JSON bodies.
- SSTI: `{{7*7}}`, `${7*7}` in template-rendered fields.

### Auth Bypass
- Remove/modify auth header.
- Downgrade from authenticated to anonymous.
- Test forced browsing to admin endpoints.

## Reporting

Save findings under:

```text
C:\BugBounty\programs\<program>\evidence\<finding>/
```

Include: request/response pairs, curl commands, and impact analysis.
