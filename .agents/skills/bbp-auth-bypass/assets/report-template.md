# Auth Bypass Finding — Report Template

```markdown
## Authentication Bypass: <JWT/OAuth/session> <summary>

**Severity**: Critical (CVSS 9.1)
**Asset**: https://target.example.com/api/auth/verify
**Type**: CWE-287 Improper Authentication

### Root cause

Server accepts tokens signed with `alg: none` when header algorithm is
omitted from signature validation branch.

### Reproduction

1. Obtain valid token for Account A.
2. Modify payload `{"sub":"102","role":"user"}` -> role admin, keep alg none:

```
Authorization: Bearer eyJhbGciOiJub25lIiwidHlwIjoiSldUIn0.<payload>.
```

3. GET /api/admin/users returns full user list (screenshot:
   evidence/none_alg_admin.png).

Control test: tampered HS256 signature without key -> 401 (proves the
none-alg branch is the bypass).

### Impact

Any unauthenticated attacker can mint arbitrary-principal tokens and
assume administrative identity across the API.

### Remediation

1. Pin allowed algorithms server-side; reject alg none and mixed-key
   families explicitly.
2. Use a maintained JWT library with algorithm allowlist config.
3. Reject unsigned tokens at gateway; log+alert on alg anomalies.
4. Rotate signing keys; shorten token TTL; bind tokens to session where
   high assurance is required.
```
