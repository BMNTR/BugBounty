# WPScan — Deep Workflows

Companion to SKILL.md. Enumeration depth, xmlrpc abuse, plugin exploits.

## Step 1: Confirm WordPress + version

```bash
curl -s https://target.example.com/ | grep -oE 'wp-content|wp-includes'
# Version leaks:
curl -s https://target.example.com/feed/ | grep -oE '<v:[a-z]+>[^<]+'
curl -s https://target.example.com/readme.html | head -5
curl -s -I https://target.example.com/wp-links-opml.php
```

## Step 2: Full enumeration pass (WAF-aware)

```bash
wsl wpscan --url https://target.example.com \
  --api-token "$WPSCAN_TOKEN" \
  -e vp,vt,tt,cb,dbe,u,m \
  --plugins-detection aggressive \
  --themes-detection passive \
  --random-user-agent \
  --throttle 300 \
  -o programs/<slug>/recon/wpscan.txt
```

Flag meanings: vp= vulnerable plugins, vt= vulnerable themes,
tt= timthumbs, cb= config backups, dbe= db exports, u= users, m= media.

## Step 3: User enumeration fallbacks (when blocked)

```bash
# REST API:
curl -s "https://target.example.com/wp-json/wp/v2/users?per_page=100" | jq '.[].slug'
# ?author scan on classic installs:
for i in $(seq 1 20); do
  curl -s -o /dev/null -w "%{redirect_url}\n" \
    "https://target.example.com/?author=$i"
done | grep -oE 'author/[a-z0-9_-]+'
# Login error diffing via xmlrpc or wp-login.php wording.
```

## Step 4: XML-RPC capabilities check

```bash
curl -s -X POST https://target.example.com/xmlrpc.php \
  -d '<?xml version="1.0"?><methodCall><methodName>system.listMethods</methodName>
<params></params></methodCall>'
# pingback.ping -> SSRF probe (one internal URL max, document only):
# <methodName>pingback.ping</methodName> with target internal URL param.
# system.multicall exists? -> credential testing AMPLIFICATION vector.
# Report amplification capability; do NOT brute-force real accounts.
```

## Step 5: Plugin/theme exploit workflow

```bash
1. wpscan lists plugin X version Y with known advisory.
2. searchsploit "plugin X"            # local exploit-db mirror
3. Verify EXACT version fingerprint:
   curl -s .../wp-content/plugins/X/readme.txt | grep -i stable
4. Manual PoC per advisory type:
   - unauthenticated upload  -> test file landing path
   - LFI/RFI                 -> include parameter probe
   - SQLi                    -> boolean/time single proof
   - IDOR ajax actions       -> two-account replay (admin-ajax.php action=...)
5. Screenshot impact; never run destructive payloads from public PoCs.
```

## Step 6: Backup & export hunting

```bash
for f in wp-config.php.bak wp-config.php~ wp-config.old .env backup.zip \
         wp-content/backup-db/ wp-content/uploads/database.sql; do :; done
# Probe each; a hit = credentials exposure (High).
dbe flag in step 2 automates common names.
```

## False-positive elimination

1. Plugin listed != vulnerable: match exact version against advisory.
2. REST users list may be disabled while author-scan still works.
3. Confirm xmlrpc methods actually execute (some return faults for all).
