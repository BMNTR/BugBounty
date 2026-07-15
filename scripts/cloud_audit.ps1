param(
    [Parameter(Mandatory = $true, Position = 0)]
    [string]$Domain
)

$ErrorActionPreference = "Continue"
$bbDir = "C:\BugBounty"
$toolsDir = "$bbDir\tools"
$env:Path = "$toolsDir;" + [Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [Environment]::GetEnvironmentVariable("Path", "User")

function Write-Step { param([string]$s) Write-Output "`n[+] CLOUD AUDIT: $s" }

if (-not $Domain) {
    Write-Error "Please provide a domain to audit."
    exit 1
}

Write-Step "Starting Cloud Audit for $Domain"

# 1. Subdomain Takeover & CNAME analysis
Write-Step "Checking for dangling DNS and CNAME takeovers..."
nuclei -u https://$Domain -tags takeover -c 50 

# 2. S3 Bucket Enumeration
Write-Step "Scanning for exposed S3 buckets and GCP storage..."
nuclei -u https://$Domain -tags cloud,s3,aws,gcp,azure -c 50

# 3. Cloud Metadata SSRF Probing (Requires SSRF vector, but we can check known endpoints)
Write-Step "Checking for exposed cloud metadata endpoints..."
nuclei -u https://$Domain -tags ssrf,metadata -c 50

Write-Step "Cloud Audit completed for $Domain."
