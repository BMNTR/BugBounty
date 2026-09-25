#!/usr/bin/env bash
# check_dangling.sh - detect dangling DNS records that may allow subdomain takeover.
# Usage: wsl ./check_dangling.sh <subs_file> [output_dir]
# Input: text file, one subdomain per line. Requires dig + curl inside WSL.

set -u

SUBS_FILE="${1:-}"
OUT_DIR="${2:-dangling_out}"

if [ -z "$SUBS_FILE" ]; then
  echo "[!] Usage: $0 <subs_file> [output_dir]" >&2
  exit 1
fi

if [ ! -f "$SUBS_FILE" ]; then
  echo "[!] Input file not found: $SUBS_FILE" >&2
  exit 2
fi

if ! command -v dig >/dev/null 2>&1; then
  echo "[!] dig not found. Install dnsutils (apt-get install dnsutils)." >&2
  exit 3
fi

mkdir -p "$OUT_DIR"
CNAME_OUT="$OUT_DIR/cnames.txt"
DANGLING_OUT="$OUT_DIR/dangling.txt"
FINGERPRINT_OUT="$OUT_DIR/fingerprints.txt"

: > "$CNAME_OUT"
: > "$DANGLING_OUT"
: > "$FINGERPRINT_OUT"

# Vendor error signatures (subset of references/fingerprints.md)
SIGS=(
  "NoSuchBucket"
  "There isn't a GitHub Pages site here"
  "No such app"
  "404 Web Site not found"
  "Help Center Closed"
  "There is no app configured at that hostname"
  "Site Not Found"
  "Fastly error: unknown domain"
  "project not found"
  "DEPLOYMENT_NOT_FOUND"
  "Not Found - Request ID"
  "The gods are wise"
  "Project doesnt exist"
  "No settings were found for this company"
  "We could not find what you're looking for"
  "This page is reserved for artistic dogs"
  "The requested content does not exist"
)

count=0
while IFS= read -r sub; do
  [ -z "$sub" ] && continue
  count=$((count + 1))
  cname=$(dig +short +time=3 +tries=1 CNAME "$sub" 2>/dev/null | head -n1)
  arec=$(dig +short +time=3 +tries=1 A "$sub" 2>/dev/null | head -n1)

  if [ -n "$cname" ]; then
    echo "$sub -> $cname" >> "$CNAME_OUT"
    # CNAME exists but no A record resolves anywhere on the chain: dangling candidate
    if [ -z "$arec" ]; then
      echo "[+] DANGLING (no A): $sub -> $cname" | tee -a "$DANGLING_OUT"
      continue
    fi
  fi

  # Probe HTTP body for vendor signatures regardless of resolution
  body=$(curl -s -m 8 -L -A "Mozilla/5.0 (Windows NT 10.0; Win64; x64)" \
    "https://$sub/" 2>/dev/null || true)
  if [ -z "$body" ]; then
    body=$(curl -s -m 8 -L -A "Mozilla/5.0 (Windows NT 10.0; Win64; x64)" \
      "http://$sub/" 2>/dev/null || true)
  fi

  if [ -n "$body" ]; then
    for sig in "${SIGS[@]}"; do
      if printf '%s' "$body" | grep -qF "$sig"; then
        echo "[+] FINGERPRINT $sig at $sub (cname: ${cname:-none})" \
          | tee -a "$FINGERPRINT_OUT"
        break
      fi
    done
  fi

  sleep 0.3
done < "$SUBS_FILE"

echo ""
echo "[*] Scanned: $count hosts"
echo "[*] CNAME map:      $CNAME_OUT ($(wc -l < "$CNAME_OUT") lines)"
echo "[*] Dangling:       $DANGLING_OUT ($(wc -l < "$DANGLING_OUT") lines)"
echo "[*] Fingerprints:   $FINGERPRINT_OUT ($(wc -l < "$FINGERPRINT_OUT") lines)"
echo "[*] Verify every hit manually with dig + curl before claiming impact."
