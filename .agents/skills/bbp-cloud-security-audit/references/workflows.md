# Cloud Security Audit Workflows (Authorized, External-Facing)

Scope rules for every workflow in this file:

- External-facing checks only. No provider credentials, no authenticated cloud console access.
- Read-only verification. Never write to a bucket, never delete, never modify ACLs.
- Stop and report at proof of exposure. Do not enumerate or download third-party/user data
  beyond the minimal sample needed to demonstrate impact.
- Every command below is safe PoC syntax; run it only against assets confirmed in scope.

Output layout:

```text
C:\BugBounty\programs\<slug>\recon\cloud-*.txt      raw enumeration output
C:\BugBounty\programs\<slug>\evidence\<finding>\    promoted PoCs + responses
```

---

## Workflow 1: AWS S3 Bucket Enumeration and Misconfiguration Checks

### Step 1 - Generate candidate bucket names

Buckets live in a global namespace; names usually follow org patterns. Build a list:

```text
<org>            <org>-assets       <org>-backup       <org>-backups
<org>-config     <org>-dev          <org>-staging      <org>-prod
<org>-static     <org>-media        <org>-cdn          <org>-data
<org>-logs       <org>-uploads      <org>-images       <org>-files
<org>-terraform-state               <org>-deploy       <org>-release
```

Also harvest real bucket names from recon data before guessing:

```bash
# JS files and HTTP responses often leak full bucket URLs
grep -rhoiE "[a-z0-9.-]+\.s3[.-][a-z0-9-]*\.?amazonaws\.com" /mnt/c/BugBounty/programs/<slug>/recon/ | sort -u > s3-found.txt
grep -rhoiE "s3://[a-z0-9][a-z0-9.-]{2,62}" /mnt/c/BugBounty/programs/<slug>/recon/ | sort -u >> s3-found.txt
grep -rhoiE "[a-z0-9.-]+\.s3\.amazonaws\.com|[a-z0-9.-]+\.s3-[a-z0-9-]+\.amazonaws\.com" /mnt/c/BugBounty/wordlists/SecLists 2>/dev/null | head -1 >/dev/null  # sanity check pattern only

# Subdomain CNAMEs pointing at S3 (from dnsx output)
grep -iE "s3[.-](website\.)?(us|eu|ap|sa|ca|af)-[a-z0-9-]+\.amazonaws\.com" dnsx-resolved.txt > s3-cnames.txt
```

### Step 2 - Probe candidate buckets anonymously

HTTP probing (fast first pass, works from any host with curl):

```bash
while read -r b; do
  for url in "https://${b}.s3.amazonaws.com" ; do
    code=$(curl -sk -o /tmp/s3resp.xml -w "%{http_code}" --max-time 10 "$url")
    case "$code" in
      200) echo "[+] LISTABLE : $url" ;;
      403) echo "[~] EXISTS   : $url (403 = exists but listing denied)" ;;
      404) ;; # does not exist - stay quiet
      *)   echo "[?] $code $url" ;;
    esac
  done
done < candidates.txt | tee "$OUT/cloud-s3-probe.txt"
```

Key decision rule: **403 proves existence** (S3 returns 404 for nonexistent buckets,
403 when it exists but anonymous access is denied). A 403 bucket is worth a targeted
policy review only if you have another way in - do not brute force.

Anonymous AWS CLI listing (only on hosts found LISTABLE above):

```bash
aws s3 ls s3://<bucket> --no-sign-request --region us-east-1 | head -20
# Region matters: wrong region gives NoSuchBucket. Try the region from the
# x-amz-bucket-region response header if the first attempt fails:
curl -skI "https://<bucket>.s3.amazonaws.com" | grep -i x-amz-bucket-region

# Check whether individual objects are readable even when listing is denied:
aws s3 cp s3://<bucket>/<known-or-guessed-key> /tmp/probe.bin --no-sign-request
```

Website-enabled buckets respond on the regional website endpoint instead:

```bash
curl -sk "http://<bucket>.s3-website-<region>.amazonaws.com" -o /dev/null -w "%{http_code}\n"
```

### Step 3 - What counts as reportable

| Observation | Reportable? |
|-------------|-------------|
| Anonymous `ListBucket` succeeds on prod-data bucket | Yes, High |
| Listing denied (403) but specific objects readable via direct key | Yes, if keys contain sensitive data |
| Public bucket containing only public static assets (CSS/JS/images) | No - intended design |
| Bucket name disclosure alone (403) | No - not a vulnerability by itself |

## Workflow 2: Azure Storage Account / Container Checks

```bash
# Public container listing (REST API, no auth):
curl -sk "https://<account>.blob.core.windows.net/<container>?restype=container&comp=list&maxresults=20"

# Interpret codes:
#   200 + XML <Blobs> -> anonymous list enabled (misconfig if container holds private data)
#   409 / AuthorizationFailure -> exists, listing denied
#   404 -> container or account unknown

# The special $web static-site container often allows public read by design:
curl -sk "https://<account>.blob.core.windows.net/\$web?restype=container&comp=list&maxresults=10"

# Blob-level read without container-level listing (direct key guess on known files):
curl -skI "https://<account>.blob.core.windows.net/<container>/backup.bak"
curl -skI "https://<account>.blob.core.windows.net/<container>/web.config"

# Harvest account/container names from recon corpus:
grep -rhoiE "[a-z0-9]{3,24}\.blob\.core\.windows\.net(/[a-z0-9$-]+)?" \
  /mnt/c/BugBounty/programs/<slug>/recon/ | sort -u
```

Reportable: anonymous listing or readable blobs on containers that hold non-public
material (backups, configs, user uploads). `$web` serving static site content = normal.

## Workflow 3: GCP Cloud Storage Bucket Checks

```bash
# Anonymous listing via JSON API:
curl -sk "https://storage.googleapis.com/storage/v1/b/<bucket>/o?maxResults=20"

# Or the simpler XML endpoint:
curl -skI "https://storage.googleapis.com/<bucket>/"

# Individual object read:
curl -skI "https://storage.googleapis.com/<bucket>/<object-key>"
```

Interpretation mirrors S3: public listing on a bucket holding private material is
reportable; public static asset hosting is not. GCS returns 403 for existing-but-private
buckets in most configurations - same existence-vs-access distinction as AWS.

## Workflow 4: Metadata Service Exposure via SSRF

Cloud instance metadata endpoints are only reachable from inside the instance. They
become findings when an SSRF primitive lets you reach them. Patterns to test once an
SSRF parameter (`url=`, `dest=`, `fetch=`, `webhook=`, `redirect=`) is confirmed:

AWS IMDSv1 (no token needed - this is the misconfigured version):

```text
http://169.254.169.254/latest/meta-data/
http://169.254.169.254/latest/meta-data/iam/security-credentials/
http://169.254.169.254/latest/meta-data/iam/security-credentials/<role-name>
```

If credentials JSON comes back, you have demonstrated role credential theft - Critical.
Redact all token values in evidence; show structure only.

AWS IMDSv2 (token required - blocks simple GET-based SSRF):

```text
PUT http://169.254.169.254/latest/api/token   header: X-aws-ec2-metadata-token-ttl-seconds: 21600
then GET metadata with header X-aws-ec2-metadata-token: <token>
```

Only reachable from SSRF primitives that allow method/header control (e.g. blind
SSRF via gopher-like schemes or full HTTP client control). If v2 is enforced,
simple GET SSRF is NOT exploitable against metadata - state that honestly.

GCP:

```text
http://metadata.google.internal/computeMetadata/v1/
requires header: Metadata-Flavor: Google
```

Azure:

```text
http://169.254.169.254/metadata/instance?api-version=2021-02-01
requires header: Metadata: true
```

Both GCP/Azure require specific headers - plain SSRF that cannot set headers fails;
that failure mode is expected, not a finding.

## Workflow 5: CI/CD Leak Locations

Check these paths during content discovery (ffuf) and JS review:

```text
/.git/HEAD                      exposed repo (follow up: dump via git-dumper locally)
/.github/workflows/*.yml        workflow definitions (public repos: check secrets usage)
/.circleci/config.yml
/Jenkinsfile
/.gitlab-ci.yml
/bitbucket-pipelines.yml
/buildkite/pipeline.yml
azure-pipelines.yml
```

What is actually reportable in CI configs:

- Hard-coded secrets/tokens committed in plaintext (verify revocation impact honestly).
- Pull-request-triggered workflows leaking secrets to fork PRs (self-hosted runners).
- Publicly readable artifact/logs endpoints containing env dumps.

Not reportable: presence of `${{ secrets.X }}` references - that is correct usage.

## Decision Tree

```text
Found bucket/storage URL in recon?
  -> probe anonymously (Workflow 1/2/3)
       -> 200 listing on non-public data  -> capture sample, promote to evidence/
       -> 403                              -> record existence only, move on
       -> 404                              -> next candidate

Confirmed SSRF primitive anywhere?
  -> test metadata endpoints per Workflow 4
       -> credentials returned             -> Critical, redact tokens
       -> header-required service blocked  -> note honestly, no claim

Exposed CI config found?
  -> contains real secret? -> validate format only, never USE the secret
  -> no secret             -> not a finding, move on
```

## Evidence Capture Standard

For every promoted cloud finding save into `evidence/<finding-slug>/`:

1. `command.txt` - exact commands used (with target substituted).
2. `response.txt` - raw server response excerpt proving access.
3. `impact-notes.md` - what data classes were visible (types, not contents).
4. Redaction applied to any real secret: keep first 4 + last 4 characters max.
