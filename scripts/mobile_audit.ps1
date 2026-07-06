param(
    [Parameter(Mandatory=$true)]
    [string]$ApkPath,
    [switch]$Decompile,
    [switch]$Analyze,
    [switch]$Frida
)

$ErrorActionPreference = "Continue"
$toolsDir = "C:\BugBounty\tools"
$reportsDir = "C:\BugBounty\reports"
$env:Path = [Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [Environment]::GetEnvironmentVariable("Path", "User") + ";$toolsDir;$env:USERPROFILE\go\bin;$env:USERPROFILE\.cargo\bin"
$reportFile = "$reportsDir\mobile_audit_$(Get-Date -Format 'yyyyMMdd_HHmmss').md"

if (-not (Test-Path $ApkPath)) { Write-Error "APK not found: $ApkPath"; exit 1 }

$results = @("# Mobile Audit Report`n`nTarget: $ApkPath`nDate: $(Get-Date)`n")
$workingDir = "$env:TEMP\mobile_audit_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
New-Item -ItemType Directory -Path $workingDir -Force | Out-Null

if ($Decompile -and (Test-Path "$toolsDir\apktool.bat")) {
    Write-Output "[*] Decompiling with APKTool..."
    & "$toolsDir\apktool.bat" d $ApkPath -o "$workingDir\apktool_out" -f 2>$null
    $results += "`n## APKTool Decompile`n`nOutput: $workingDir\apktool_out`n"
}

if ($Decompile -and (Test-Path "$toolsDir\jadx\bin\jadx.bat")) {
    Write-Output "[*] Decompiling with JADX..."
    & "$toolsDir\jadx\bin\jadx.bat" -d "$workingDir\jadx_out" $ApkPath 2>$null
    $results += "`n## JADX Decompile`n`nOutput: $workingDir\jadx_out`n"
}

if ($Analyze) {
    Write-Output "[*] Analyzing APK..."
    # Check for interesting strings
    if (Get-Command rg -ErrorAction SilentlyContinue) {
        $findings = & rg -i -n "(api[-_]?key|apikey|secret|password|token|aws_key|firebase|https?://|\.sqlite|\.db)" "$workingDir\jadx_out" 2>$null
        if ($findings) {
            $results += "`n## Interesting Findings`n`n" + '```' + "`n"
            $results += ($findings -join "`n") + "`n" + '```' + "`n"
        }
    }
}

if ($Frida -and (Get-Command frida -ErrorAction SilentlyContinue)) {
    Write-Output "[*] Checking Frida setup..."
    $fridaVer = & frida --version 2>$null
    $results += "`n## Frida`n`nVersion: $fridaVer`n"
    $results += "Usage: frida -U -f com.target.app -l script.js`n"
}

$results -join "" | Set-Content -Path $reportFile
Write-Output "[*] Audit complete. Report: $reportFile"
Write-Output "[*] Working directory: $workingDir"
