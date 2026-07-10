---
name: bbp-cloud-security-audit
description: Review cloud infrastructure configurations in authorized bug bounty targets. Use when the target exposes cloud services (AWS S3, GCP buckets, Azure storage), misconfigured DNS, open databases, exposed metadata services, or insecure CI/CD pipelines.
---

# BBP Cloud Security Audit

## External-Facing Checks

Only test assets reachable without provider credentials:

### Storage Buckets
- Enumerate common bucket names: `<target>-assets`, `<target>-backup`, `<target>-config`.
- Check public listing/reading: `https://<bucket>.s3.amazonaws.com`, `https://storage.googleapis.com/<bucket>`.
- Check bucket policy for unauthenticated write.

### DNS & Subdomain
- `dig <target> ANY` — DNS zone transfer, wildcard, SPF/DMARC records.
- `dig TXT <target>` — check for secrets in TXT records.
- CNAME to cloud service — check for takeover.

### Exposed Services
- Open Elasticsearch/Kibana: `https://<target>:9200`.
- Open MongoDB: port 27017 exposure.
- Open Redis, Memcached, Cassandra.
- Jenkins, Grafana, Prometheus without auth.

### Metadata Service
- SSRF to cloud metadata: `http://169.254.169.254/latest/meta-data/` (AWS).
- Same for GCP (`metadata.google.internal`) and Azure (`169.254.169.254/metadata/instance`).

### CI/CD Leaks
- GitHub Actions: check for secrets in workflow logs, `.github/workflows/*.yml`.
- npm package: check `postinstall` scripts in package.json.
- Environment file exposure: `.env`, `.env.prod`, `config.*.json`.

### Docker / Kubernetes
- Check exposed Docker daemon socket: `http://<target>:2375/version` — open Docker API = RCE.
- Registry exposure: `https://registry.<target>/v2/_catalog`, `https://<target>:5000/v2/_catalog`.
- K8s API server: `https://<target>:6443/api/v1/namespaces` — cek anonymous auth.
- K8s Dashboard: `https://<target>:30000` atau path `/api/v1/namespaces/kube-system` — default creds / skip login.
- etcd: `http://<target>:2379/version` — no auth = full cluster access.
- Container breakout via privileged mode / hostPath mount — cuma bisa validasi kalo ada akses shell ke container.

## Tools

```bash
# Bucket enumeration
nuclei -t exposures/ -l alive.txt
s3scanner scan -bucket <target>

# Subdomain takeover
nuclei -t takeovers/ -l alive.txt
```

## Evidence

Save as:

```text
C:\BugBounty\programs\<program>\evidence\<finding>/
```

Include: exact URL/command used, response excerpt, impact.
