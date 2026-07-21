#!/bin/bash

# recon.sh - Bug bounty recon pipeline (Bash version)

# Parse arguments
DOMAIN=""
QUICK=0
RUN_NUCLEI=0

usage() {
    echo "Usage: $0 -d <domain> [--quick] [--nuclei]"
    exit 1
}

while [[ "$#" -gt 0 ]]; do
    case $1 in
        -d|--domain) DOMAIN="$2"; shift ;;
        --quick) QUICK=1 ;;
        --nuclei) RUN_NUCLEI=1 ;;
        *) usage ;;
    esac
    shift
done

if [ -z "$DOMAIN" ]; then
    usage
fi

BB_DIR="/mnt/c/BugBounty"
SLUG=$(echo "$DOMAIN" | sed -E 's/[^a-zA-Z0-9-]/_/g')
PROG_DIR="$BB_DIR/programs/$SLUG"
RECON_DIR="$PROG_DIR/recon"
TEMP_DIR="$PROG_DIR/temp"

mkdir -p "$RECON_DIR" "$TEMP_DIR"

echo ">>> PHASE 1: Subdomain Enumeration for $DOMAIN"

if ! command -v subfinder &> /dev/null; then
    echo "[-] subfinder not found. Run setup-linux.sh first."
    exit 1
fi

subfinder -d "$DOMAIN" -all -o "$TEMP_DIR/subs.txt"

echo ">>> PHASE 2: Live Host Discovery"
cat "$TEMP_DIR/subs.txt" | httpx -silent -title -tech -status-code -o "$RECON_DIR/alive_hosts.txt"
cat "$RECON_DIR/alive_hosts.txt" | awk '{print $1}' > "$TEMP_DIR/alive_urls.txt"

if [ "$RUN_NUCLEI" -eq 1 ]; then
    echo ">>> PHASE 3: Vulnerability Scanning (Nuclei)"
    if ! command -v nuclei &> /dev/null; then
        echo "[-] nuclei not found. Run setup-linux.sh first."
        exit 1
    fi
    nuclei -l "$TEMP_DIR/alive_urls.txt" -severity low,medium,high,critical -o "$RECON_DIR/nuclei_results.txt"
fi

echo ">>> RECON COMPLETE"
echo "Results saved to $RECON_DIR"
