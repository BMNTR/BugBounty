---
name: bbp-waf-bypass
description: Specialized skill for bypassing Web Application Firewalls (WAF) using HTTP Request Smuggling, encoding techniques, and origin IP discovery.
---

# WAF Bypass Skill

This skill provides techniques to evade Web Application Firewalls (WAF) such as Cloudflare, Akamai, and AWS WAF.

## Workflow

### 1. Origin IP Discovery
The most effective way to bypass a WAF is to avoid it entirely by finding the backend server's true IP address.
- **Censys / Shodan:** Search for the target domain's SSL certificate (`parsed.names: "target.com"`) to find IPs directly exposing the certificate.
- **DNS History:** Use SecurityTrails to view historical A records from before the WAF was implemented.
- **SSRF:** Trigger an SSRF vulnerability to make the server ping your interactsh client. The source IP of the ping is the origin IP.
- **Email Headers:** Trigger an email from the application (e.g., password reset, welcome email). Analyze the `Received` headers to find the originating server's IP.

### 2. HTTP Request Smuggling (HTTP Desync)
Exploit discrepancies in how the front-end (WAF) and back-end servers parse the `Content-Length` (CL) and `Transfer-Encoding` (TE) headers.
- **CL.TE:** The WAF uses `Content-Length`, the backend uses `Transfer-Encoding: chunked`.
- **TE.CL:** The WAF uses `Transfer-Encoding: chunked`, the backend uses `Content-Length`.
- **TE.TE:** Both support `Transfer-Encoding`, but one can be tricked into ignoring it by obfuscating the header (e.g., `Transfer-Encoding: xchunked`).
- **Exploitation:** Smuggle a malicious request (e.g., exploiting a vulnerable endpoint or XSS) inside the body of a seemingly benign request. The WAF inspects the benign outer request, while the backend processes the smuggled inner request.

### 3. Payload Encoding & Obfuscation
- **URL Encoding:** Double URL encoding (`%2522` instead of `%22`), Unicode encoding, or null byte injection (`%00`).
- **HTTP Parameter Pollution (HPP):** Send multiple parameters with the same name. Some WAFs inspect the first, while the backend processes the second: `?id=safe&id=malicious`.
- **JSON Obfuscation:** Add spaces, newlines, or use Unicode escapes (`\u003c` instead of `<`) within JSON payloads.

### 4. Header Manipulation
- Modify the `Content-Type` header (e.g., change `application/x-www-form-urlencoded` to `multipart/form-data`) to bypass WAF regex rules that only inspect specific content types.
- Inject headers to spoof the source: `X-Originating-IP: 127.0.0.1`, `X-Forwarded-For: 127.0.0.1`, `X-Remote-IP: 127.0.0.1`.
