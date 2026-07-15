---
name: bbp-edoverflow-cheatsheet
description: Curated payloads, tips, tools, and technique references from EdOverflow's bug bounty cheatsheet. Covers XSS, SQLi, SSRF, LFI, XXE, RCE, recon, template injection, and more.
---

# EdOverflow Bug Bounty Cheatsheet

A curated reference of payloads, tips, and tricks from [EdOverflow/bugbounty-cheatsheet](https://github.com/EdOverflow/bugbounty-cheatsheet).

## Reference

| Category | Files |
|----------|-------|
| **Recon** | [recon.md](https://github.com/EdOverflow/bugbounty-cheatsheet/blob/master/cheatsheets/recon.md) |
| **Platforms** | [bugbountyplatforms.md](https://github.com/EdOverflow/bugbounty-cheatsheet/blob/master/cheatsheets/bugbountyplatforms.md) |
| **Practice** | [practice-platforms.md](https://github.com/EdOverflow/bugbounty-cheatsheet/blob/master/cheatsheets/practice-platforms.md) |
| **Tools** | [special-tools.md](https://github.com/EdOverflow/bugbounty-cheatsheet/blob/master/cheatsheets/special-tools.md) |
| **Tips** | [bugbountytips.md](https://github.com/EdOverflow/bugbounty-cheatsheet/blob/master/cheatsheets/bugbountytips.md) |
| **Books** | [books.md](https://github.com/EdOverflow/bugbounty-cheatsheet/blob/master/cheatsheets/books.md) |
| **XSS** | [xss.md](https://github.com/EdOverflow/bugbounty-cheatsheet/blob/master/cheatsheets/xss.md) |
| **SQLi** | [sqli.md](https://github.com/EdOverflow/bugbounty-cheatsheet/blob/master/cheatsheets/sqli.md) |
| **SSRF** | [ssrf.md](https://github.com/EdOverflow/bugbounty-cheatsheet/blob/master/cheatsheets/ssrf.md) |
| **LFI** | [lfi.md](https://github.com/EdOverflow/bugbounty-cheatsheet/blob/master/cheatsheets/lfi.md) |
| **XXE** | [xxe.md](https://github.com/EdOverflow/bugbounty-cheatsheet/blob/master/cheatsheets/xxe.md) |
| **RCE** | [rce.md](https://github.com/EdOverflow/bugbounty-cheatsheet/blob/master/cheatsheets/rce.md) |
| **Open Redirect** | [open-redirect.md](https://github.com/EdOverflow/bugbounty-cheatsheet/blob/master/cheatsheets/open-redirect.md) |
| **CRLF Injection** | [crlf.md](https://github.com/EdOverflow/bugbounty-cheatsheet/blob/master/cheatsheets/crlf.md) |
| **CSV Injection** | [csv-injection.md](https://github.com/EdOverflow/bugbounty-cheatsheet/blob/master/cheatsheets/csv-injection.md) |
| **Template Injection** | [template-injection.md](https://github.com/EdOverflow/bugbounty-cheatsheet/blob/master/cheatsheets/template-injection.md) |
| **Crypto** | [crypto.md](https://github.com/EdOverflow/bugbounty-cheatsheet/blob/master/cheatsheets/crypto.md) |
| **XSLT Injection** | [xslt.md](https://github.com/EdOverflow/bugbounty-cheatsheet/blob/master/cheatsheets/xslt.md) |
| **Content Injection** | [content-injection.md](https://github.com/EdOverflow/bugbounty-cheatsheet/blob/master/cheatsheets/content-injection.md) |

## Key Highlights

### Recon
- Certspotter API (`curl https://certspotter.com/api/v0/certs\?domain\=target.com | jq`)
- Sublist3r one-liner across multiple domains
- Apktool → LinkFinder for Android APK endpoint extraction
- Aquatone one-liner (discover → scan → takeover → gather)

### XSS Payloads
- Chrome XSS-Auditor bypasses (pre-2017)
- Safari XSS vector via `location.href`
- **XSS Polyglot**: `jaVasCript:/*-/*`/*\`/*'/*"/**/(/* */oNcliCk=alert() )//%0D%0A%0d%0a//</stYle/</titLe/</teXtarEa/</scRipt/--!>\x3csVg/<sVg/oNloAd=alert()//>\x3e`
- WAF bypasses: Kona, ModSecurity, Wordfence, Incapsula
- Markdown XSS via `javascript:` protocol in link syntax
- Flash SWF XSS for 15+ common SWF files
- AngularJS expression sandbox escape (v1.0.1 → v1.6.0+)
- CSP bypass via JSONP endpoints: `site:example.com inurl:callback`

### SQLi
- Akamai Kona WAF bypass: `444/**/OR/**/MID(CURRENT_USER,1,1)/**/LIKE/**/"p"/**/#`
- 15+ blog/article references for deeper SQLi techniques

### SSRF
- IPv4 bypasses: octal (`0177.1`), hex (`0x7f.1`), integer (`520968996`)
- Exotic handlers: `gopher://`, `dict://`, `php://`, `jar://`, `tftp://`
- IPv6 loopback: `http://[::1]`, `http://[::]`
- Wildcard DNS: `xip.io`, `nip.io`
- AWS EC2 metadata: `http://169.254.169.254/latest/meta-data/`
- IAM role credential extraction

### Bug Bounty Tips
- Git as recon tool — clone repos, check logs
- GitLab `/explore` bypass — misconfigured instances leak internal projects
- Test paid/manual-setup apps — fewer testers = more bugs
- IDOR → XSS → ATO chain
- Hackathon assets — temporary credentials left exposed
- Save dirbust results for future CVE retro hunting
- Change POST → GET to improve CVSS (CSRF via `<img>` tag)

### Tools
- Resolution: dnsbin.zhack.ca, pingb.in, mockbin.org
- Recon: spyse.com, dnsdumpster.com, crt.sh, Google CT, VirusTotal, wayback machine
- Wildcard DNS: xip.io, nip.io
- Report templates: fransr/template-generator, ZephrFish/BugBountyTemplates

## Usage
Before testing any target, verify scope. Reference the appropriate cheatsheet for your vulnerability class. Combine recon techniques for surface area expansion, then use payloads from the vulnerability-specific sheets for validation.
