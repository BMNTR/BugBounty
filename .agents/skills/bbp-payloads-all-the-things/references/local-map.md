# Local Resource Map — PayloadsAllTheThings

## What lives where (verified)

```
C:\BugBounty\wordlists\PayloadsAllTheThings\          <- full repo clone
  Account Takeover\  API Key Leaks\  Business Logic Errors\
  Command Injection\  Directory Traversal\  File Inclusion\
  GraphQL Injection\  Insecure Deserialization\  Insecure Direct Object References\
  Server Side Request Forgery\  SQL Injection\  XSS Injection\  XXE Injection\
  Upload\  Web Cache Poisoning\  ... (60+ categories, one dir each)
Each dir contains README.md (methodology + payloads) and sometimes an
Intruderc/ folder of ready-to-load Burp Intruder payload lists.
```

WSL path equivalent: `/mnt/c/BugBounty/wordlists/PayloadsAllTheThings`

## Fast lookups by task

| Task | Open |
|---|---|
| Command injection bypass ideas | `Command Injection\README.md` |
| SSRF filter bypass table | `Server Side Request Forgery\README.md` |
| LFI wrappers (php:// etc) | `File Inclusion\README.md` |
| Upload magic bytes | `Upload\README.md` |
| IDOR patterns | `Insecure Direct Object References\` |
| GraphQL attacks | `GraphQL Injection\README.md` |

## Usage recipes

```bash
# Load PATTH intruder list straight into ffuf:
wsl ffuf -u https://target/FUZZ -w "/mnt/c/BugBounty/wordlists/PayloadsAllTheThings/SQL Injection/Intruder/SQLi.txt"
```

Cross-link: this skill is the deep reference for bbp-* hunter skills;
each hunter's references/payloads.md summarizes the top payloads here.

## When nothing is local

Upstream: `git clone https://github.com/swisskyrepo/PayloadsAllTheThings`
Update existing clone:
```bash
cd C:\BugBounty\wordlists\PayloadsAllTheThings && git pull --ff-only
```
