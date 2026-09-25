# RSocket Finding — Report Template

```markdown
## RSocket Authorization Bypass: privileged route callable by anonymous peer

**Severity**: High/Critical (CVSS 8.x+)
**Asset**: wss://target.example.com/rsocket (route `payments.refund`)
**Type**: CWE-285 Improper Authorization on messaging route

### Discovery

Route enumeration via response oracle:

```
$ rsc ws://... --request --route payments.refund --data '{"id":1}'
-> {"status":"queued"}          # executed, no auth metadata attached
```

Control routes correctly return AccessDenied (user.profile with no auth).

### Interaction model abuse

Same destination reachable via REQUEST_FNF (no response channel):

```
$ rsc ... --fnf --route payments.refund --data '{...}'
Server-side state diff proves execution (refund queue length +1 observed
via legitimate status route).
```

### Impact

Any unauthenticated WebSocket peer can invoke payment operations and
bypass audit logging partially (FNF path skips some handlers).

### Remediation

1. Enforce authorization interceptor on ALL interaction models including
   fire-and-forget (setup + rsocket interceptors at connection level).
2. Deny-by-default route registry; explicit role mapping per destination.
3. Rate-limit frames per connection; cap metadata size.
4. Add integration tests asserting anonymous FNF is rejected.
```
