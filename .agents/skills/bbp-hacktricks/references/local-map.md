# Local Resource Map — HackTricks

## What lives where (verified)

```
No HackTricks repo clone found under:
  C:\BugBounty\wordlists\  (SecLists, PayloadsAllTheThings, nuclei-templates)
  C:\BugBounty\tools\      (apktool, jadx, sqlmap, hashcat, xsstrike...)
```

Nearest LOCAL equivalents that exist:
- `C:\BugBounty\SKILL.md` — your 95KB encyclopedia with per-service commands
  (ports 6379/27017/8080, Jenkins, Tomcat methodologies)
- `C:\BugBounty\wordlists\PayloadsAllTheThings\` — payload-level depth
- `C:\BugBounty\bbcore\` — orchestrator implementing recon methodology
- Per-service skills: `.agents\skills\bbp-spring-actuator-audit\`,
  `.agents\skills\bbp-wpscan\`, etc.

## When you need actual HackTricks content

```bash
# Clone (optional, ~large repo):
git clone --depth 1 https://github.com/carlospolop/hacktricks \
  C:\BugBounty\tools\hacktricks
# Then read specific pages as markdown:
# tools\hacktricks\network-services-pentesting-pentesting\<service>\
```

Online quick paths:
- book.hacktricks.xyz/network-services-pentesting-pentesting/<port>
- book.hacktricks.xyz/pentesting-web/<vuln-class>

## Decision guide: which local reference first?

| Situation | Open first |
|---|---|
| Odd open port/service | SKILL.md encyclopedia section |
| Need exact payloads | PayloadsAllTheThings clone |
| Service-specific methodology | matching bbp-* skill if present |
| Still stuck | clone/read HackTricks page |
