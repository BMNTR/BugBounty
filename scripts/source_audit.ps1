param(
    [Parameter(Mandatory=$true)]
    [string]$Path,
    [switch]$Semgrep,
    [switch]$CodeQL,
    [switch]$Ripgrep
)

$ErrorActionPreference = "Continue"
$toolsDir = "C:\BugBounty\tools"
$reportsDir = "C:\BugBounty\reports"
$env:Path = [Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [Environment]::GetEnvironmentVariable("Path", "User") + ";$toolsDir;$env:USERPROFILE\go\bin;$env:USERPROFILE\.cargo\bin;$env:USERPROFILE\AppData\Roaming\npm"
$reportFile = "$reportsDir\source_audit_$(Get-Date -Format 'yyyyMMdd_HHmmss').md"

if (-not (Test-Path $Path)) { Write-Error "Path not found: $Path"; exit 1 }

$results = @()

if ($Semgrep -and (Get-Command semgrep -ErrorAction SilentlyContinue)) {
    Write-Output "[*] Running Semgrep..."
    $out = & semgrep scan --config=auto $Path --json 2>$null
    if ($LASTEXITCODE -eq 0) {
        $parsed = $out | ConvertFrom-Json
        $results += "## Semgrep Results`n`nTotal findings: $($parsed.results.Count)`n"
        foreach ($r in $parsed.results) {
            $results += "- [$($r.check_id)] $($r.path):$($r.start.line) - $($r.extra.message)`n"
        }
    } else {
        $results += "## Semgrep Results`n`nScan completed with findings`n"
    }
}

if ($CodeQL -and (Test-Path "$toolsDir\codeql.exe")) {
    Write-Output "[*] Running CodeQL..."
    # Create CodeQL database
    $dbPath = "$env:TEMP\codeql-db"
    Remove-Item -Path $dbPath -Recurse -Force -ErrorAction SilentlyContinue
    & "$toolsDir\codeql.exe" database create $dbPath --language=auto --source-root=$Path 2>$null
    & "$toolsDir\codeql.exe" database analyze $dbPath --format=sarif-latest --output="$reportsDir\codeql_results.sarif" 2>$null
    $results += "`n## CodeQL Results`n`nResults saved to: $reportsDir\codeql_results.sarif`n"
}

if ($Ripgrep -and (Get-Command rg -ErrorAction SilentlyContinue)) {
    Write-Output "[*] Running ripgrep for patterns..."
    $patterns = @(
        @{name="API Keys"; pattern="(?:api[-_]?key|apikey|api[-_]?secret)['""]?\s*[:=]\s*['""][A-Za-z0-9_\-]{16,}['""]"}
        @{name="Passwords"; pattern="(?:password|passwd|pwd)['""]?\s*[:=]\s*['""][^'""]{6,}['""]"}
        @{name="Tokens"; pattern="(?:token|secret|credential)['""]?\s*[:=]\s*['""][A-Za-z0-9_\-\.]{10,}['""]"}
        @{name="AWS Keys"; pattern="AKIA[0-9A-Z]{16}"}
        @{name="SSH Keys"; pattern="-----BEGIN (?:RSA|DSA|EC|OPENSSH) PRIVATE KEY-----"}
        @{name="Connection Strings"; pattern="(?:mongodb|mysql|postgres)://\w+:\w+@"}
    )
    foreach ($p in $patterns) {
        $out = & rg --no-heading -n -i $p.Pattern $Path 2>$null
        if ($out) {
            $results += "`n## $($p.name) (ripgrep)`n`n"
            $results += $out | ForEach-Object { "- $_`n" }
            $results += "`n"
        }
    }
}

# Save report
$results -join "" | Set-Content -Path $reportFile
Write-Output "[*] Audit complete. Report: $reportFile"
