---
name: bbp-wpscan
description: WordPress vulnerability scanning and enumeration methodologies. Use this when the target is running WordPress to enumerate plugins, themes, users, and execute wpscan commands.
---

# WPScan & WordPress Auditing

When you detect WordPress running on a target (e.g., `/wp-login.php`, `wp-content/`), use this methodology.

## 1. Automated Scanning (wpscan)
Always use an API token (if available) to detect vulnerabilities associated with identified plugins.
```bash
wpscan --url https://target.com/ -e vp,vt,tt,cb,dbe,u,m --plugins-detection aggressive --api-token YOUR_API_TOKEN
```
- `-e vp` : Vulnerable plugins
- `-e vt` : Vulnerable themes
- `-e u`  : User enumeration
- `--plugins-detection aggressive` : Force exhaustive plugin discovery

## 2. Manual Verification
- **XML-RPC**: Check `https://target.com/xmlrpc.php`. If enabled, test for pingback SSRF or brute force amplification.
- **REST API**: Check `https://target.com/wp-json/wp/v2/users` to enumerate users directly if `wpscan` fails.
- **wp-config.php**: Look for backups or exposed `wp-config.php.bak`, `wp-config.php~`.

## 3. Exploit Known Flaws
If a vulnerable plugin is found:
1. Note the version.
2. Search exploit databases (`searchsploit`, HackTricks, CVE databases).
3. Validate manually before reporting. Many plugins have unauthenticated XSS, SQLi, or File Upload flaws.
