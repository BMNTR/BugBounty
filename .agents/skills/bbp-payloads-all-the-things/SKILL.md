---
name: bbp-payloads-all-the-things
description: Comprehensive payload and bypass collection from swisskyrepo/PayloadsAllTheThings for web application security testing and CTF. Covers 60+ vulnerability categories with ready-to-use payloads.
---

# Payloads All The Things

Reference: [swisskyrepo/PayloadsAllTheThings](https://github.com/swisskyrepo/PayloadsAllTheThings) (79k stars)

## Coverage (60+ categories)

| Category | Key Techniques |
|----------|---------------|
| **SQL Injection** | Time-based, error-based, UNION, stacked queries, out-of-band, WAF bypasses |
| **XSS Injection** | Reflected, stored, DOM, polyglots, WAF bypass, CSP bypass, mXSS |
| **SSRF** | Cloud metadata, IP bypass (octal/hex/integer), gopher/dict, DNS rebinding |
| **SSTI** | Jinja2, Twig, Freemarker, Velocity, Mako, Jade, Smarty, ERB |
| **XXE** | File read, SSRF, blind exfil, error-based, parameter entities, XInclude |
| **Command Injection** | Blind/out-of-band, filtering bypass, charset bypass (wildcards, $(), backticks) |
| **File Inclusion** | LFI → RCE via log poisoning, php://input, expect wrapper, /proc/self/environ |
| **Upload** | MIME bypass, magic bytes, extension filter bypass, .htaccess, zip slip |
| **Insecure Deserialization** | PHP, Python, Java, .NET, Ruby, Node.js, ysoserial, gadget chains |
| **JWT** | none algorithm, weak HMAC, kid injection, JWK injection, JKU bypass |
| **GraphQL** | Introspection, batching, DoS, CSRF, injection, depth queries |
| **CORS** | Origin reflection, wildcard, preflight bypass, credentialed requests |
| **IDOR** | UUID enumeration, parameter pollution, mass assignment |
| **Request Smuggling** | CL.TE, TE.CL, TE.TE, HTTP/2 downgrade, connection reuse |
| **Race Condition** | TOCTOU, concurrent requests, time-of-check bypass |
| **NoSQLi** | MongoDB ($ne, $regex, $where), parameter pollution |
| **OAuth** | CSRF, redirect_uri bypass, state leakage, code injection |
| **LDAP Injection** | AND/OR injection, blind extraction, filter bypass |
| **Web Cache Poisoning** | Unkeyed headers, cache key injection, X-Forwarded-Host |
| **Prototype Pollution** | Client-side, server-side, key injection, merge bypass |
| **XXE via XLSX/Office** | XML inside ZIP, SSRF via OOXML |
| **CVE Exploits** | Real-world exploits: Log4j, Spring4Shell, Drupalgeddon, etc. |

## Structure Per Section
Each vulnerability directory contains:
- `README.md` — description, exploitation techniques, payloads
- Intruder files — ready-to-import payload lists for Burp Intruder
- Images — diagrams and screenshots
- Files — referenced binaries, configs, scripts

## Web Version
Online searchable version: [swisskyrepo.github.io/PayloadsAllTheThings/](https://swisskyrepo.github.io/PayloadsAllTheThings/)
