# Web Recon Skill

Step-by-step pipeline for web reconnaissance on bug bounty targets. Runs before manual testing.

## Pipeline

### Phase 1: Surface Expansion
```bash
# subdomain enumeration + DNS resolution
subfinder -d $DOMAIN -all -o subs.txt
assetfinder --subs-only $DOMAIN >> subs.txt
sort -u subs.txt -o subs.txt

# DNS resolution
cat subs.txt | dnsx -silent -a -resp-only -o resolved.txt
```

### Phase 2: Live Host Probing
```bash
cat subs.txt | httpx -silent -title -status-code -tech-detect -o alive.txt

# screenshot all live
gowitness file -f alive.txt -P screens/ --no-http
```

### Phase 3: URL Collection
```bash
# wayback + commoncrawl + alienvault
gau --subs $DOMAIN | sort -u > urls.txt
echo $DOMAIN | waybackurls >> urls.txt
sort -u urls.txt -o urls.txt

# extract js paths, endpoints, params
cat urls.txt | grep -E '\.js($|\?)' | sort -u > js.txt
cat urls.txt | unfurl paths | sort -u > endpoints.txt
cat urls.txt | unfurl keys | sort -u > params.txt
```

### Phase 4: Content Discovery
```bash
# directory brute (focused wordlist)
ffuf -u https://$TARGET/FUZZ -w /usr/share/seclists/Discovery/Web-Content/common.txt \
  -ac -t 100 -o ffuf.json

# api endpoint brute
ffuf -u https://$TARGET/FUZZ -w /usr/share/seclists/Discovery/Web-Content/api/objects.txt
```

### Phase 5: Vulnerability Scanning
```bash
# nuclei — cve + exposures + misconfigs
nuclei -l alive.txt -t cves/ -t exposures/ -o nuclei-critical.txt
nuclei -l alive.txt -t misconfiguration/ -o nuclei-misconfig.txt

# tech-specific
nuclei -l alive.txt -t technologies/ -t takeovers/
```

### Phase 6: Manual Signal Collection
```
For each live host, record:
- tech stack (from httpx / wappalyzer)
- auth mechanisms (JWT, OAuth, session cookie)
- upload endpoints
- API routes (look for graphql, swagger, /api/v1)
- interesting params (id, file, url, redirect, callback)
- template engines (Jinja2, Twig, Freemarker, Velocity, Pug/Jade, Handlebars)
```

**SSTI quick check** — input `{{7*7}}`, `#{7*7}`, `${{7*7}}`, `{{7*'7'}}` di params. Kalo response mengandung `49` atau `777`, kemungkinan SSTI. Lanjut detection per engine di SKILL.md §4.9.

## Output Structure
```
programs/<target>/
  recon/
    subs.txt
    resolved.txt
    alive.txt
    urls.txt
    js.txt
    endpoints.txt
    params.txt
    screens/
    ffuf.json
    nuclei-*.txt
    notes.md
```

## When to Stop & Switch Skills
| Signal | Switch To |
|--------|-----------|
| SSRF parameter found (`url=`, `file=`) | manual test (SKILL.md §4.3) |
| Upload endpoint | manual test (SKILL.md §4.8) |
| GraphQL endpoint | `bbp-api-testing` or SKILL.md §5.2 |
| JWT found | manual test (SKILL.md §4.5, JWT section) |
| OpenAPI/Swagger doc | `bbp-api-testing` |
| auth bypass pattern (IDOR, race) | manual test (SKILL.md §4.5-4.6) |
| SSTI candidate (`{{7*7}}` reflected) | SKILL.md §4.9 (SSTI per-engine payloads) |
| nothing interesting after full recon | move to next target |

## Reference

Deep command reference in `SKILL.md §2` (Reconnaissance) and `SKILL.md §4` (Web Vulnerabilities). This skill is the workflow — SKILL.md has the encyclopedia.
