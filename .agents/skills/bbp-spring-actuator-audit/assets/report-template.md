# Spring Boot Actuator Finding — Report Template

```markdown
## Exposed Spring Actuator: heapdump leaks database credentials

**Severity**: Critical (CVSS 9.1)
**Asset**: https://target.example.com/actuator/
**Type**: CWE-200 Exposure of Sensitive Information / CWE-16 Configuration

### Exposure inventory

```
GET /actuator/mappings     -> 200 (full route map)
GET /actuator/env          -> 200 (property sources; secrets masked)
GET /actuator/heapdump     -> 200 (~214MB hprof)
```

### Credential extraction proof

Heapdump analyzed offline (Eclipse MAT). One credential proven:

```
spring.datasource.username = app_rw
spring.datasource.password = ********(redacted, 24 chars)
jdbc:mysql://internal-db:3306/prod
```
Validity confirmed by successful authenticated SELECT 1 from a READ-ONLY
query through an internal jump host permitted by program scope.
Screenshot with value redacted: evidence/heapdump_creds.png.

Full dump NOT retained; deleted after evidence capture (sha256 noted).

### Impact

Production DB credentials retrievable by anyone with network access ->
full customer data compromise path.

### Remediation

1. `management.server.port` on isolated interface; never public ingress.
2. Expose only health,info; require auth + mTLS for anything else.
3. Network ACL management endpoints to ops CIDR.
4. Rotate ALL credentials present in the captured dump immediately.
```
