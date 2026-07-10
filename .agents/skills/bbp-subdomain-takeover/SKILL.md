---
name: bbp-subdomain-takeover
description: Specialized skill for identifying and exploiting dangling DNS records to perform subdomain takeovers on cloud services.
---

# Subdomain Takeover Skill

This skill provides methodologies for identifying and exploiting misconfigured DNS records that point to unclaimed or deprovisioned third-party services.

## Workflow

### 1. Discovery (Identifying Dangling Records)
- Use tools like `subfinder`, `amass`, and `assetfinder` to enumerate subdomains.
- Use `dnsx -cname -resp` or `dig` to identify CNAME records pointing to external services (e.g., `github.io`, `s3.amazonaws.com`, `herokudns.com`).
- Use `nuclei -t takeovers/` to automate the detection of known vulnerable service signatures.

### 2. Validation & Service Identification
- Visit the subdomain in a browser or use `curl`. Look for specific error messages indicating an unclaimed resource:
  - **GitHub Pages:** "There isn't a GitHub Pages site here."
  - **AWS S3:** "NoSuchBucket"
  - **Heroku:** "No such app"
  - **Zendesk:** "Help Center Closed"

### 3. Exploitation (Claiming the Resource)
- Register an account with the identified third-party service provider.
- Attempt to create a resource (e.g., a bucket, an app, or a repository) using the exact name specified in the dangling CNAME record.
- **Proof of Concept (PoC):** Upload a benign `index.html` file containing a clear message demonstrating control (e.g., `<h1>Subdomain Takeover PoC by [YourName]</h1>`).
- Ensure the PoC is visible when navigating to the vulnerable subdomain.

### 4. Edge Cases & Bypasses
- **A Record Takeovers:** If an A record points to a specific IP address associated with a cloud provider (e.g., Elastic IP in AWS), and that IP is released but the DNS record remains, an attacker might be able to claim that IP address.
- **Edge-Rule Takeovers (e.g., Cloudflare):** If a subdomain points to Cloudflare, but the domain is not registered in any Cloudflare account, an attacker can add the domain to their own Cloudflare account and control the routing.
