#!/bin/bash

# program.sh - Program orchestrator (Bash version)

# Parse arguments
URL=""
PROGRAM_NAME=""

usage() {
    echo "Usage: $0 -u <url> [-n <program_name>]"
    exit 1
}

while getopts "u:n:" opt; do
    case "$opt" in
        u) URL="$OPTARG" ;;
        n) PROGRAM_NAME="$OPTARG" ;;
        *) usage ;;
    esac
done

if [ -z "$URL" ]; then
    usage
fi

# Configuration
BB_DIR="/mnt/c/BugBounty"
SCRIPTS_DIR="$BB_DIR/scripts"

# Resolve target name
if [ -n "$PROGRAM_NAME" ]; then
    SLUG=$(echo "$PROGRAM_NAME" | sed -E 's/[^a-zA-Z0-9-]/_/g')
else
    # Simple URL to slug conversion
    SLUG=$(echo "$URL" | sed -E 's|^https?://||; s|/.*||; s/[^a-zA-Z0-9-]/_/g')
fi

PROG_DIR="$BB_DIR/programs/$SLUG"

echo ">>> PHASE 0: Setup"
echo "  Program:     $SLUG"
echo "  Workspace:   $PROG_DIR"

# Create directories
mkdir -p "$PROG_DIR"/{policy,source,downloads,evidence,reports,attachments,notes,recon,scripts,temp}

# Create policy file
cat <<EOF > "$PROG_DIR/policy/README.md"
# Program: $SLUG

- URL: $URL
- Created: $(date '+%Y-%m-%d %H:%M:%S')

Review the program policy at $URL for:
- In-scope assets
- Out-of-scope findings
- Allowed testing methods
EOF

echo ">>> PHASE 1: Initialization complete. Workspace created."
echo "Note: The bash version of program.sh is a minimal wrapper. Advanced fetching and classification requires parsing platform APIs or using the original program.ps1."
