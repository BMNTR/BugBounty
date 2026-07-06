param(
    [Parameter(Mandatory=$true)]
    [string]$Path,
    [switch]$Syft,
    [switch]$Grype,
    [switch]$OSV,
    [switch]$Trivy
)

$ErrorActionPreference = "Continue"
$toolsDir = "C:\BugBounty\tools"
$reportsDir = "C:\BugBounty\reports"
$env:Path = [Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [Environment]::GetEnvironmentVariable("Path", "User") + ";$toolsDir;$env:USERPROFILE\go\bin;$env:USERPROFILE\.cargo\bin"
$reportFile = "$reportsDir\dependency_audit_$(Get-Date -Format 'yyyyMMdd_HHmmss').md"

if (-not (Test-Path $Path)) { Write-Error "Path not found: $Path"; exit 1 }

$results = @("# Dependency Audit Report`n`nTarget: $Path`nDate: $(Get-Date)`n")

if ($Syft -and (Get-Command syft -ErrorAction SilentlyContinue)) {
    Write-Output "[*] Running Syft (SBOM generation)..."
    $sbomFile = "$reportsDir\sbom_$(Get-Date -Format 'yyyyMMdd_HHmmss').json"
    & syft $Path -o json > $sbomFile 2>$null
    if ($LASTEXITCODE -eq 0) { $results += "`n## Syft SBOM`n`nSBOM saved to: $sbomFile`n" }
}

if ($Grype -and (Get-Command grype -ErrorAction SilentlyContinue)) {
    Write-Output "[*] Running Grype (vulnerability scan)..."
    $grypeOut = & grype $Path 2>$null
    if ($grypeOut) {
        $results += "`n## Grype Vulnerabilities`n`n`n```"
        $results += "`n$($grypeOut -join "`n")`n```"
        $results += "`n"
    }
}

if ($OSV -and (Get-Command osv-scanner -ErrorAction SilentlyContinue)) {
    Write-Output "[*] Running OSV-Scanner..."
    $osvOut = & osv-scanner scan $Path 2>$null
    if ($osvOut) {
        $results += "`n## OSV-Scanner Results`n`n`n```"
        $results += "`n$($osvOut -join "`n")`n```"
        $results += "`n"
    }
}

if ($Trivy -and (Get-Command trivy -ErrorAction SilentlyContinue)) {
    Write-Output "[*] Running Trivy..."
    $trivyOut = & trivy fs --format table $Path 2>$null
    if ($trivyOut) {
        $results += "`n## Trivy Results`n`n`n```"
        $results += "`n$($trivyOut -join "`n")`n```"
        $results += "`n"
    }
}

$results -join "" | Set-Content -Path $reportFile
Write-Output "[*] Audit complete. Report: $reportFile"
