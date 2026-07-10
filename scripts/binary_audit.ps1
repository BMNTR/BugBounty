param(
    [Parameter(Mandatory=$true)]
    [string]$TargetExe,
    [string]$OutputDir
)

$ErrorActionPreference = "Continue"

# Ensure Scoop shims are in PATH
$env:Path = "$env:USERPROFILE\scoop\shims;" + $env:Path

if (-not (Test-Path $TargetExe)) {
    Write-Error "Target file does not exist: $TargetExe"
    exit 1
}

$targetName = [System.IO.Path]::GetFileNameWithoutExtension($TargetExe)
$reconDir = if ($OutputDir) { $OutputDir } else { "C:\BugBounty\recon\$targetName" }

New-Item -ItemType Directory -Path $reconDir -Force | Out-Null
Set-Location $reconDir

Write-Output "[*] Starting binary triage on $TargetExe at $(Get-Date)"
Write-Output "[*] Output directory: $reconDir"

# 1. Hashes
Write-Output "`n[+] Phase 1: Generating Hashes"
$hashFile = "$reconDir\hashes.txt"
"Hashes for $TargetExe" | Out-File -FilePath $hashFile
"----------------------------------------" | Out-File -FilePath $hashFile -Append
Get-FileHash -Algorithm MD5 -Path $TargetExe | Select-Object Algorithm, Hash | Out-File -FilePath $hashFile -Append
Get-FileHash -Algorithm SHA1 -Path $TargetExe | Select-Object Algorithm, Hash | Out-File -FilePath $hashFile -Append
Get-FileHash -Algorithm SHA256 -Path $TargetExe | Select-Object Algorithm, Hash | Out-File -FilePath $hashFile -Append
Write-Output "    Saved to hashes.txt"

# 2. Strings Extraction
Write-Output "`n[+] Phase 2: Extracting Strings"
if (Get-Command strings -ErrorAction SilentlyContinue) {
    strings $TargetExe > "$reconDir\strings.txt"
    Write-Output "    Saved to strings.txt"
} else {
    Write-Output "    [-] strings.exe not found in PATH. Skipping."
}

# 3. Security Flags & Extended Info (Sigcheck)
Write-Output "`n[+] Phase 3: Analyzing Security Flags (Sigcheck)"
if (Get-Command sigcheck -ErrorAction SilentlyContinue) {
    # -a: extended info, -h: hashes, -nobanner: hide banner
    sigcheck -a -h -nobanner $TargetExe > "$reconDir\sigcheck.txt"
    Write-Output "    Saved to sigcheck.txt"
} else {
    Write-Output "    [-] sigcheck.exe not found in PATH. Skipping."
}

Write-Output "`n[*] Triage complete at $(Get-Date)"
Write-Output "[*] Summary generated in $reconDir"
