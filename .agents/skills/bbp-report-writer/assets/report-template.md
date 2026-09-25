# Bug Bounty Report Template (HackerOne-style)

Fill every `<placeholder>`, delete inapplicable lines. For YesWeHack use the
metadata mapping at the bottom instead of restructuring the body.

---

## Title

```text
<Vulnerable component> lets <attacker type> <security impact>
```

Example shape: `IDOR on /api/v2/orders allows any authenticated user to read other tenants' invoices`

## Metadata (fill in submission form)

```text
Asset:        <exact in-scope asset, e.g. api.target.com>
Weakness/CWE: CWE-639: Authorization Bypass Through User-Controlled Key
Severity:     <High>
CVSS v3.1:    CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:N  (<6.4>)
```

## Summary

<3-4 sentences: what the bug is, where it lives (exact endpoint/component),
who can trigger it and with what access level, and the direct consequence.
No company background, no discovery story.>

## Affected Component

```text
Endpoint:  <METHOD /path>
Component: <file/function or service name if known from response headers/source>
Parameter: <name(s)>
Version:   <only if disclosed by the target itself and relevant>
```

## Reproduction

Prerequisites:

```text
- account A: <role/setup>
- account B: <role/setup> (if multi-account proof)
```

Steps (transcribed from frozen command log):

```bash
# Step 1 - authenticate as user A
curl -sk https://<host>/api/v2/login -d '...' | jq .token

# Step 2 - request resource owned by user B using only A's session
curl -sk "https://<host>/api/v2/orders/<B-order-id>" \
  -H "Authorization: Bearer $TOKEN_A"
```

Result:

```http
HTTP/1.1 200 OK
Content-Type: application/json

{"order_id":"<B-order-id>","owner":"<B-user-id-redacted>", ...}
```

[!] Redaction rule applied to all evidence: real IDs/tokens masked to first/last 4 chars.

## Impact

<Attacker-path chain with honest math:>

```text
1. Any registered user obtains a valid session token.            [proven]
2. The token authorizes reads of arbitrary order objects by ID.  [proven above]
3. Exposed fields include billing address and email.             [proven, N=5 samples]
4. Likely enables bulk enumeration via sequential IDs; automated
   enumeration was NOT performed against production.             [not validated]
```

<No claim beyond what steps show. If a stronger impact exists but was not tested,
name it as untested hypothesis, never as fact.>

## Suggested Fix

- Enforce object-level authorization: check `resource.owner == session.user` server-side for every object read/write.
- Use non-enumerable identifiers (UUIDv4) as defense-in-depth; do not treat them as the authorization control.
- Add regression test covering cross-tenant access attempt.

## Validation Boundary

```text
Validated against live in-scope host with authenticated GET requests only,
using researcher-owned test accounts. No other users' data retained; no
modification, no automated enumeration. Total requests made: <N>.
```

## Notes

- Duplicate search performed: see `duplicate-check.md` (closest related report: <link or none found>).
- Attachments: `request.txt`, `response.txt`, `poc.png`, `MANIFEST.txt`.

---

# YesWeHack Mapping (do not restructure body for YWH)

Fill form metadata fields:

| YWH field | Value from this template |
|-----------|--------------------------|
| Scope | Asset |
| Host | Endpoint host |
| Bug Type | Weakness/CWE |
| Vulnerable Part | Affected Component endpoint/path |
| Parameter | Parameter |
| Payload | Step 2 request line |
| CVSS | CVSS vector + score |

Free-text body sections: Summary -> DESCRIPTION, Reproduction -> EXPLOITATION,
Affected Component + Result -> POC, Impact -> RISK, Suggested Fix -> REMEDIATION.
