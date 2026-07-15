param(
    [Parameter(Mandatory = $true, Position = 0)]
    [string]$Domain
)

$ErrorActionPreference = "Continue"
$bbDir = "C:\BugBounty"
$toolsDir = "$bbDir\tools"
$env:Path = "$toolsDir;" + [Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [Environment]::GetEnvironmentVariable("Path", "User")

function Write-Step { param([string]$s) Write-Output "`n[+] CRYPTO AUDIT: $s" }

if (-not $Domain) {
    Write-Error "Please provide a domain to audit."
    exit 1
}

Write-Step "Starting Cryptography Audit for $Domain"

# 1. TLS/SSL Configuration Scan
Write-Step "Scanning TLS/SSL configuration..."
nuclei -u https://$Domain -tags ssl,tls,crypto -c 50

# 2. JWT Endpoint Discovery
Write-Step "Hunting for JWT endpoints and weak signatures..."
nuclei -u https://$Domain -tags jwt -c 50

# Note: Further deep crypto audit (e.g., testssl.sh or custom padding oracle attacks) 
# requires manual verification based on the endpoints discovered above.

Write-Step "Cryptography Audit completed for $Domain."
