param(
    [Parameter(Mandatory=$true)]
    [string]$Path,
    [switch]$Gitleaks,
    [switch]$Trufflehog,
    [switch]$All = $true
)

$ErrorActionPreference = "Continue"
$toolsDir = "C:\BugBounty\tools"
$reportsDir = "C:\BugBounty\reports"
$env:Path = [Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [Environment]::GetEnvironmentVariable("Path", "User") + ";$toolsDir;$env:USERPROFILE\go\bin;$env:USERPROFILE\.cargo\bin"
$reportFile = "$reportsDir\secrets_scan_$(Get-Date -Format 'yyyyMMdd_HHmmss').md"

if (-not (Test-Path $Path)) { Write-Error "Path not found: $Path"; exit 1 }

$results = @("# Secrets Scan Report`n`nTarget: $Path`nDate: $(Get-Date)`n")

if ($All -or $Gitleaks) {
    Write-Output "[*] Running Gitleaks..."
    if (Get-Command gitleaks -ErrorAction SilentlyContinue) {
        $gitleaksOut = & gitleaks detect --source $Path --report-path "$reportsDir\gitleaks_report.json" --no-git 2>&1
        $results += "`n## Gitleaks Results`n`n`n```"
        $results += "`n$($gitleaksOut -join "`n")`n```"
        $results += "`n"
        if (Test-Path "$reportsDir\gitleaks_report.json") {
            $results += "Full report: $reportsDir\gitleaks_report.json`n"
        }
    }
}

if ($All -or $Trufflehog) {
    Write-Output "[*] Running TruffleHog..."
    if (Get-Command trufflehog -ErrorAction SilentlyContinue) {
        $truffleOut = & trufflehog filesystem --directory $Path --json 2>$null
        if ($truffleOut) {
            $results += "`n## TruffleHog Results`n`n"
            $truffleOut | ConvertFrom-Json -ErrorAction SilentlyContinue | ForEach-Object {
                $results += "- Source: $($_.SourceMetadata.Data.Filesystem.file)`n  Reason: $($_.DetectorName)`n  Date: $($_.Date)`n`n"
            }
        }
    }
}

$results -join "" | Set-Content -Path $reportFile
Write-Output "[*] Scan complete. Report: $reportFile"
