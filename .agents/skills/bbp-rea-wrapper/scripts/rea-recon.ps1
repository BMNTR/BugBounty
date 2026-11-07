<# 
.SYNOPSIS
    REA Reverse Engineering recon wrapper for BugBounty workflow
.DESCRIPTION
    Runs static analysis on in-scope mobile/desktop/native targets using REA (morluto/rea)
    Outputs evidence to programs/<slug>/recon and programs/<slug>/evidence
.PARAMETER TargetPath
    Path to target binary: .apk, .ipa, .app, .asar, .exe, ELF, Mach-O, PE
.PARAMETER Slug
    Program slug (folder under programs/)
.PARAMETER Provider
    Deep analysis provider: hopper, ghidra, auto (default: auto)
#>

param(
    [Parameter(Mandatory=$true)]
    [string]$TargetPath,

    [Parameter(Mandatory=$true)]
    [string]$Slug,

    [string]$Provider = "auto"
)

# Resolve paths
$programDir = "C:\BugBounty\programs\$Slug"
$reconDir   = "$programDir\recon"
$evidenceDir = "$programDir\evidence"
$scriptsDir = "$programDir\scripts"

# Ensure directories exist
foreach ($d in @($reconDir, $evidenceDir, $scriptsDir)) {
    if (-not (Test-Path $d)) { New-Item -ItemType Directory -Force -Path $d | Out-Null }
}

# Validate target exists
if (-not (Test-Path $TargetPath)) {
    Write-Error "Target not found: $TargetPath"
    exit 1
}

$targetName = [System.IO.Path]::GetFileNameWithoutExtension($TargetPath)
$timestamp  = Get-Date -Format "yyyyMMdd-HHmmss"
$baseName   = "${targetName}_${timestamp}"

Write-Host "[+] REA Recon started for $Slug :: $TargetPath" -ForegroundColor Cyan
Write-Host "[+] Provider: $Provider" -ForegroundColor Gray

# 1. Static overview (always runs, no deep provider needed)
Write-Host "[1/5] Static overview..." -ForegroundColor Yellow
npx -y rea-agents@latest analyze "$TargetPath" --format json --provider $Provider `
    | Out-File "$reconDir\${baseName}_overview.json" -Encoding utf8

# 2. String search for secrets/sensitive patterns
Write-Host "[2/5] Searching strings for secrets..." -ForegroundColor Yellow
npx -y rea-agents@latest search "$TargetPath" "api_key|secret|password|token|jwt|private_key|aws_access_key|AKIA|BEGIN.*PRIVATE" --format json `
    | Out-File "$reconDir\${baseName}_secrets.json" -Encoding utf8

# 3. Trace critical features (auth, payment, admin, etc.)
Write-Host "[3/5] Tracing critical features..." -ForegroundColor Yellow
npx -y rea-agents@latest trace "$TargetPath" "auth|login|payment|admin|bypass|deeplink|export" --format json `
    | Out-File "$reconDir\${baseName}_traces.json" -Encoding utf8

# 4. Inventory (procedures, strings, names, segments)
Write-Host "[4/5] Full inventory..." -ForegroundColor Yellow
npx -y rea-agents@latest list-procedures "$TargetPath" --format json --provider $Provider `
    | Out-File "$reconDir\${baseName}_procedures.json" -Encoding utf8
npx -y rea-agents@latest list-strings "$TargetPath" --format json --provider $Provider `
    | Out-File "$reconDir\${baseName}_strings.json" -Encoding utf8
npx -y rea-agents@latest list-names "$TargetPath" --format json --provider $Provider `
    | Out-File "$reconDir\${baseName}_names.json" -Encoding utf8

# 5. Export evidence bundle (immutable, for reports)
Write-Host "[5/5] Exporting evidence bundle..." -ForegroundColor Yellow
npx -y rea-agents@latest export-evidence "$reconDir\${baseName}_overview.json" "$evidenceDir\${baseName}_evidence.json" --format json

Write-Host "[+] Done. Outputs in $reconDir and $evidenceDir" -ForegroundColor Green
Write-Host "    Overview:    $reconDir\${baseName}_overview.json" -ForegroundColor Gray
Write-Host "    Secrets:     $reconDir\${baseName}_secrets.json" -ForegroundColor Gray
Write-Host "    Traces:      $reconDir\${baseName}_traces.json" -ForegroundColor Gray
Write-Host "    Evidence:    $evidenceDir\${baseName}_evidence.json" -ForegroundColor Gray