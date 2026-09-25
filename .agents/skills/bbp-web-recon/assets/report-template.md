# Finding Report Template (Recon-Originated)

Fill every `<placeholder>`. Delete sections that do not apply.
One finding per file. Save as `programs/<slug>/reports/<finding-slug>.md`.

---

# <Vulnerable component> lets <attacker type> <security impact>

**Severity:** <Critical|High|Medium|Low>
**CVSS v3.1:** `CVSS:3.1/<AV>/<AC>/<PR>/<UI>/<S>/<C>/<I>/<A>` (<score>)
**Asset:** `<exact in-scope host or URL>`
**Discovered via:** <nuclei template id / ffuf path / katana crawl URL>
**Date:** <YYYY-MM-DD>

## Summary

<2-4 sentences. What is exposed, on which asset, and what an unauthenticated or
low-privilege attacker can do with it. No background history of the company.>

## Affected Component

```text
URL:      https://<host><path>
Method:   <GET|POST>
Param(s): <name> (if applicable)
Version:  <server/framework version header if disclosed and relevant>
```

## Reproduction

Exact commands, in order, copy-paste runnable:

```bash
curl -sk "https://<host><path>" \
  -H "User-Agent: Mozilla/5.0" \
  | head -50
```

Observed response (trimmed to the relevant part):

```http
HTTP/1.1 200 OK
Content-Type: <type>

<response excerpt proving the issue, secrets redacted to first/last 4 chars>
```

[!] Redact any real credentials, tokens, or user data in this section. Show
    structure and proof markers (`AKIA****`, `eyJhbGciOi...`), not full values.

## Impact

<Concrete attacker path: step A gives B, B enables C. Use only what the PoC
actually demonstrates. If a further step was not tested, write it as
"likely enables X; not validated".>

## Suggested Fix

- <Primary fix, e.g. remove endpoint / require authN+authZ / restrict CORS>
- <Defense-in-depth, e.g. WAF rule, log alerting on the path>

## Validation Boundary

<e.g. "Validated against production host with read-only GET requests only.
No data modification, no account access, no automated scanning against
this specific endpoint beyond the single verification request.">

## Attachments

```text
programs/<slug>/evidence/<finding-slug>/
  request.txt        <- exact raw HTTP request
  response.txt       <- exact raw HTTP response
  screenshot.png     <- if visual proof applies
  duplicate-check.md <- from bbp-duplicate-guard
```
