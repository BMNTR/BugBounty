# Cloud Misconfiguration Report Template

Save filled copy as `programs/<slug>/reports/<finding-slug>.md`.
One finding per file. Redact all real secrets before submission.

---

# Publicly accessible <S3 bucket|Azure container|GCS bucket> <name-pattern> exposes <data class>

**Severity:** <High|Medium|Critical depending on data sensitivity>
**CVSS v3.1:** `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N` (<score>)
**Asset:** `<exact in-scope asset this bucket belongs to>`
**Cloud provider:** AWS S3 | Azure Blob | GCP Storage
**Date:** <YYYY-MM-DD>

## Summary

<2-4 sentences: which storage resource, how it was discovered (in-scope asset
reference only), what anonymous access allows, and the data classes visible.
Do not include actual third-party or user content in the report body.>

## Affected Resource

```text
Endpoint:  https://<resource-endpoint>
Provider:  <AWS|Azure|GCP>
Region:    <region if disclosed by response headers>
Discovery: <recon source, e.g. leaked URL in JS bundle on in-scope host>
```

## Proof of Concept

Anonymous listing request and response:

```bash
curl -sk "https://<resource-endpoint>" | head -40
```

```xml
<!-- response excerpt: structure only, object names truncated -->
<ListBucketResult>
  <Contents><Key>2024/<redacted>...</Key></Contents>
</ListBucketResult>
```

Anonymous object read (if applicable):

```bash
aws s3 cp s3://<bucket>/<key> /tmp/probe.bin --no-sign-request --region <region>
```

[!] Evidence hygiene rules applied:
- Object names truncated to directory level where they contain usernames/IDs.
- Any downloaded sample deleted after classification; hash recorded below.
- No writes performed; no ACLs modified; no deletion of any object.

## Impact

<Honest attacker path: what an unauthenticated internet user can list/read,
what data classes that exposes (PII / credentials / internal configs),
and realistic downstream abuse. If deeper impact was not tested, say
"likely enables X; not validated against live data".>

## Data Classification Summary

```text
Visible prefixes: <e.g. backups/, logs/, uploads/>
Data classes:     <e.g. SQL dump files, application config>
Sampled objects:  <N> objects inspected for classification only
SHA256 of probe artifact: <hash> (if a sample was saved)
```

## Suggested Fix

- Remove public access at the account/policy level (`BlockPublicAccess`, equivalent).
- Grant least-privilege read via signed URLs or CloudFront/OIDC instead of open policy.
- Rotate any credentials observed in readable material (assume compromised).
- Audit access logs for prior anonymous access.

## Validation Boundary

<e.g. "Verified anonymous LIST and GET on <N> objects to classify exposure.
No modification, upload, or deletion attempted. No third-party data retained.">

## Attachments

```text
programs/<slug>/evidence/cloud-<provider>-<slug>/
  command.txt      <- exact commands with target substituted
  response.txt     <- raw response excerpts proving access
  impact-notes.md  <- data classes visible (types, not contents)
```
