# Advanced Fuzzing — Deep Workflows

Companion to SKILL.md. ffuf mastery, parameter discovery, header fuzzing.

## ffuf core patterns

```bash
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64)"

# Directory discovery with jitter (WAF-friendly):
ffuf -u https://target.example.com/FUZZ -w $WL/common.txt \
  -H "User-Agent: $UA" -p "0.1-0.5" -ac -c \
  -o programs/<slug>/recon/ffuf_dirs.json -of json

# Filter by size/status instead of blind -mc 200:
-fs <baseline_size> -fc 403,500   # subtract noise
-mr "regex"                        # match response REGEX (e.g., api version)

# Multiple wordlists = cluster bomb:
ffuf -u https://target.example.com/api/FUZZ1/FUZZ2 \
  -w users.txt:FUZZ1 -w actions.txt:FUZZ2 -mode clusterbomb

# Recursion for API trees:
-recursion -recursion-depth 2 -recursion-strategy greedy

# Vhost discovery:
ffuf -u https://internal-host -H "Host: FUZZ.target.com" \
  -w $WL/subdomains-top1million-5000.txt -fs <default-vhost-size>

# Method fuzzing:
-X FUZZ -w methods.txt   (TRACE PATCH PROPFIND ...)
```

## Parameter name discovery

```bash
# arjun (single request per param batch — very WAF-safe):
arjun -u https://target.example.com/api/orders -m JSON \
  --stable --rate 15 -o programs/<slug>/recon/arjun.json
# Then TEST each discovered param manually: hidden params often accept
# debug=true, admin=true, internal=true, include=*, expand=all.
```

## Value fuzzing on known params

```bash
ffuf -u "https://target.example.com/api/v2/users/FUZZ" \
  -w ids.txt -H "Authorization: Bearer $T" -ac
# ids.txt built from: seq ranges, leaked UUIDs from JS bundles,
# wayback URLs (gau target.example.com | grep -oE '[0-9]{3,8}')
```

## Header fuzzing

```bash
for h in X-Originating-IP X-Forwarded-For X-Real-IP Client-IP; do :; done
ffuf -u https://target.example.com/admin \
  -H "FUZZ: 127.0.0.1" -w headers.txt -fs <blocked-size>
# A size change = admin panel trusts internal IPs -> access control gap.
```

## Wordlist selection (local SecLists)

```bash
WL=C:/BugBounty/wordlists/SecLists   # verify actual mount under /mnt/c in WSL
Discovery/Web-Content/common.txt          -> first pass always
Discovery/Web-Content/raft-large-*.txt    -> deep pass
Discovery/Web-Content/api/*.txt           -> API paths
Discovery/DNS/deepmine.txt                -> vhosts
Fuzzing/SQLi/ + Fuzzing/XSS/              -> payload lists
Usernames/Names/top-*                     -> user enumeration
```

## Rate discipline

```text
-p "0.1-0.5" jitter default ON for all runs above.
If 429/403 appears: STOP the run, switch to slower (-p "1-3") or rotate.
Never exceed ~30 req/s against unknown infra without WAF check first.
```

## False-positive elimination

1. `-ac` auto-calibration helps but ALWAYS eyeball outliers once.
2. Soft-404 SPA catch-alls return 200 — filter by unique content length
   AND content regex (`-mr "\"title\":\"Not Found\""` inverse).
3. Re-validate every hit manually before queueing deeper testing.
