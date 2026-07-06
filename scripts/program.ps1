param(
    [Parameter(Mandatory = $true, Position = 0)]
    [string]$Url,
    [string]$ProgramName,
    [switch]$Force
)

$ErrorActionPreference = "Continue"
$bbDir = "C:\BugBounty"
$toolsDir = "$bbDir\tools"
$goBin = "$env:USERPROFILE\go\bin"
$cargoBin = "$env:USERPROFILE\.cargo\bin"
$env:Path = "$toolsDir;$goBin;$cargoBin;" + [Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [Environment]::GetEnvironmentVariable("Path", "User")

function Write-Step { param([string]$s) Write-Output "`n>>> $s" }
function Write-Skip { param([string]$s) Write-Output "  ~ $s (tool not available)" }

function Resolve-Name {
    param([string]$u)
    $u = $u -replace 'https?://' -replace 'hackerone\.com/?' -replace 'yeswehack\.com/?' -replace 'bugcrowd\.com/?' -replace 'intigriti\.com/?' -replace '/programs/' -replace '/bug-bounty/' -replace '/', '-' -replace '[^\w-]', '' -replace '^-+|-+$', ''
    if (-not $u) { $u = "target-$(Get-Date -Format 'yyyyMMdd-HHmmss')" }
    return $u
}

# --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  
# PHASE 0: SETUP
# --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  
Write-Step "PHASE 0: Setup"

$platform = "unknown"
if ($Url -match 'hackerone\.com') { $platform = "hackerone" }
elseif ($Url -match 'yeswehack\.com') { $platform = "yeswehack" }
elseif ($Url -match 'bugcrowd\.com') { $platform = "bugcrowd" }
elseif ($Url -match 'intigriti\.com') { $platform = "intigriti" }

$slug = if ($ProgramName) { $ProgramName -replace '[^\w-]', '' } else { Resolve-Name $Url }
if (-not $slug) { $slug = "target-$(Get-Date -Format 'yyyyMMdd-HHmmss')" }

$progDir = "$bbDir\programs\$slug"
$reconDir = "$progDir\recon"
$evidenceDir = "$progDir\evidence"
$reportsDir = "$progDir\reports"

$subDirs = @("policy", "source", "downloads", "evidence", "reports", "attachments", "notes", "recon")
foreach ($d in $subDirs) { New-Item -ItemType Directory -Path "$progDir\$d" -Force -ErrorAction SilentlyContinue | Out-Null }

Write-Output "  Program:     $slug"
Write-Output "  Workspace:   $progDir"
Write-Output "  Platform:    $platform"

# Program policy --  -   save URL for reference
@"
# Program: $slug

- URL: $Url
- Platform: $platform
- Created: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')

Review the program policy at $Url for:
- In-scope assets
- Out-of-scope findings
- Account/KYC requirements
- Allowed testing methods
- Bounty range
"@ | Set-Content -Path "$progDir\policy\README.md" -Encoding utf8

# --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  
# PHASE 1: FETCH & CLASSIFY
# --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  
Write-Step "PHASE 1: Fetching program page & classifying"

$body = ""
$domains = @()
$classification = @{
    web    = $false
    api    = $false
    mobile = $false
    source = $false
    cloud  = $false
    crypto = $false
    rust   = $false
}
$foundApk = $null
$foundRepo = $null

# Check for cookies
$cookieHeader = $null
$cookieFile = "$bbDir\cookies.txt"
if (Test-Path $cookieFile) {
    $cookieLines = Get-Content $cookieFile | Where-Object { $_ -notmatch '^#' -and $_.Trim() -ne '' }
    if ($cookieLines.Count -gt 0) {
        $cookies = @()
        foreach ($line in $cookieLines) {
            $parts = $line -split '\t'
            if ($parts.Count -ge 7) { $cookies += "$($parts[5])=$($parts[6])" }
        }
        if ($cookies.Count -gt 0) { $cookieHeader = @{ Cookie = $cookies -join '; ' } }
    }
}

try {
    $params = @{ Uri = $Url; UseBasicParsing = $true; TimeoutSec = 30; MaximumRedirection = 5; ErrorAction = 'Stop' }
    if ($cookieHeader) { $params.Headers = $cookieHeader }
    $resp = Invoke-WebRequest @params
    $body = $resp.Content
    Write-Output "  HTTP $($resp.StatusCode) ($($body.Length) bytes)"
    if ($cookieHeader) { Write-Output "  Authenticated via cookies.txt" }
} catch {
    Write-Output "  Fetch failed: $($_.Exception.Message)"
}

# Extract domains
if ($body) {
    $matches = [System.Text.RegularExpressions.Regex]::Matches($body, '(?:https?://)?(?:[\w-]+\.)+[\w-]{2,}(?:/[\w\-./?%&=]*)?')
    $skip = @('google','facebook','twitter','github','linkedin','youtube','hackerone','yeswehack','bugcrowd','intigriti','cloudflare','gravatar','googleapis','gstatic','jquery','bootstrap','githubusercontent','cdn.')
    foreach ($m in $matches) {
        $d = $m.Value.Trim().Trim('/') -replace '^https?://', ''
        if ($d -match '\.(png|jpg|jpeg|gif|css|js|svg|ico|woff|woff2|ttf|eot|pdf)$') { continue }
        $d = $d -replace '/.*$', ''
        $skipIt = $false
        foreach ($s in $skip) { if ($d -match [regex]::Escape($s)) { $skipIt = $true; break } }
        if ($skipIt) { continue }
        if ($d -match '^[a-zA-Z0-9][-a-zA-Z0-9]*(\.[-a-zA-Z0-9]+)+$' -and $d -notmatch '\.(html|aspx?|php)$') {
            $tld = $d -replace '^.*\.', ''
            if ($tld.Length -ge 2 -and $tld -match '^[a-zA-Z]+$') { $domains += $d }
        }
    }

    # H1 structured scope
    $m2 = [System.Text.RegularExpressions.Regex]::Matches($body, '"asset_identifier"\s*:\s*"([^"]+)"')
    foreach ($m in $m2) {
        $a = $m.Groups[1].Value -replace '^\*\.', '' -replace '^https?://', '' -replace '/.*$', ''
        if ($a -match '^[a-zA-Z0-9][-a-zA-Z0-9]*(\.[-a-zA-Z0-9]+)+$') { $domains += $a }
    }

    # Use program name as hint
    $slugMatch = [System.Text.RegularExpressions.Regex]::Match($Url, '/([^/]+?)$')
    if ($slugMatch.Success) {
        $hint = $slugMatch.Groups[1].Value -replace '[^\w.-]', ''
        if ($hint -match '\.(com|org|net|io|app|dev)$') { $domains += $hint }
        else { $domains += "$hint.com" }
    }
}

$domains = $domains | Select-Object -Unique
if ($domains.Count -eq 0) { $domains += "$slug.com", "$slug.io", "$slug.app" }
Write-Output "  Extracted $($domains.Count) unique domains"

# --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  
# PHASE 1b: CLASSIFICATION
# --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  
Write-Step "PHASE 1b: Target classification"

$targetDomains = $domains | Where-Object { $_ -notmatch '^https?://' -and $_ -notmatch '/$' }

if ($body) {
    $bodyLower = $body.ToLower()

    # API detection
    if ($bodyLower -match 'api|graphql|rest|swagger|openapi|endpoint|oauth|jwt') {
        $classification.api = $true
        Write-Output "  [api] API patterns detected"
    }
    if ($bodyLower -match '/api/|graphql|swagger\.json|openapi\.json|/v[0-9]+/') {
        $classification.api = $true
    }

    # Mobile detection
    if ($bodyLower -match 'android|apk|\.apk|play\.google|mobile app|ios|ipa|app store') {
        $classification.mobile = $true
        Write-Output "  [mobile] Mobile app patterns detected"
        # Extract APK URL
        $apkMatch = [System.Text.RegularExpressions.Regex]::Match($body, '(https?://[^"''\s]+\.apk)')
        if ($apkMatch.Success) { $foundApk = $apkMatch.Groups[1].Value; Write-Output "    APK URL: $foundApk" }
    }

    # Source code detection
    if ($bodyLower -match 'source|repository|github|gitlab|bitbucket|open.source|code review|audit') {
        $classification.source = $true
        Write-Output "  [source] Source code patterns detected"
        $repoMatch = [System.Text.RegularExpressions.Regex]::Match($body, '(https?://(github|gitlab|bitbucket)\.com/[^"''\s]+)')
        if ($repoMatch.Success) { $foundRepo = $repoMatch.Groups[1].Value; Write-Output "    Repo URL: $foundRepo" }
    }

    # Cloud detection
    if ($bodyLower -match 's3|bucket|cloud|aws|gcp|azure|storage|cloudflare|cdn|terraform|kubernetes') {
        $classification.cloud = $true
        Write-Output "  [cloud] Cloud infrastructure patterns detected"
    }

    # Crypto detection
    if ($bodyLower -match 'crypto|cryptographic|tls|certificate|jwt|oauth|signing|encryption|pki') {
        $classification.crypto = $true
        Write-Output "  [crypto] Cryptography patterns detected"
    }

    # Rust detection
    if ($bodyLower -match 'rust|cargo|unsafe|rustlang|rust-lang') {
        $classification.rust = $true
        Write-Output "  [rust] Rust patterns detected"
    }
}

# Default: treat as web target
$classification.web = $true
Write-Output "  [web] Default classification (all targets)"

# Save classification
$classification | ConvertTo-Json | Set-Content -Path "$progDir\classification.json" -Encoding utf8

# --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  
# PHASE 2: SUBDOMAIN ENUMERATION
# --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  
Write-Step "PHASE 2: Subdomain enumeration ($($targetDomains.Count) targets)"

$allSubdomains = @()
$reconLog = @()
$sourcesSummary = @{}

foreach ($domain in $targetDomains) {
    $domain = $domain.Trim().TrimEnd('.')
    if ($domain -notmatch '\.') { continue }
    Write-Output "  Target: $domain"

    # subfinder
    Write-Output "    subfinder..."
    $outFile = "$reconDir\subfinder-$domain.txt"
    try {
        $out = & "$toolsDir\subfinder.exe" -d $domain -silent -o $outFile 2>&1
        if ($LASTEXITCODE -eq 0 -and (Test-Path $outFile)) {
            $cnt = (Get-Content $outFile | Measure-Object -Line).Lines
            Write-Output "      -> $cnt subdomains"
            $allSubdomains += Get-Content $outFile
            $sourcesSummary["subfinder"] = $cnt
        } else { Write-Output "      -> 0 or failed" }
    } catch { Write-Output "      -> failed" }

    # assetfinder
    Write-Output "    assetfinder..."
    $outFile = "$reconDir\assetfinder-$domain.txt"
    try {
        $out = & "$toolsDir\assetfinder.exe" --subs-only $domain 2>$null
        if ($out) {
            $out | Set-Content -Path $outFile
            $cnt = ($out | Measure-Object -Line).Lines
            Write-Output "      -> $cnt subdomains"
            $allSubdomains += $out
            $sourcesSummary["assetfinder"] = $cnt
        } else { Write-Output "      -> 0" }
    } catch { Write-Output "      -> failed" }

    # amass (passive, 120s timeout)
    Write-Output "    amass (passive)..."
    $outFile = "$reconDir\amass-$domain.txt"
    try {
        $job = Start-Job -ScriptBlock { param($d,$o) & "C:\BugBounty\tools\amass.exe" enum -passive -d $d -silent -o $o 2>&1 } -ArgumentList $domain, $outFile
        if ($job -and (Wait-Job $job -Timeout 120 -ErrorAction SilentlyContinue)) { Receive-Job $job -ErrorAction SilentlyContinue | Out-Null }
        else { if ($job) { Stop-Job $job -ErrorAction SilentlyContinue; Remove-Job $job -Force -ErrorAction SilentlyContinue } }
        Remove-Job $job -Force -ErrorAction SilentlyContinue
        if (Test-Path $outFile) {
            $cnt = (Get-Content $outFile | Measure-Object -Line).Lines
            Write-Output "      -> $cnt subdomains"
            $allSubdomains += Get-Content $outFile
            $sourcesSummary["amass"] = $cnt
        } else { Write-Output "      -> 0 or timeout" }
    } catch { Write-Output "      -> failed" }

    # gau (URL-based subdomain extraction, 90s timeout)
    Write-Output "    gau..."
    $outFile = "$reconDir\gau-$domain.txt"
    try {
        $job = Start-Job -ScriptBlock { param($d,$o) & "C:\BugBounty\tools\gau.exe" --subs $d 2>$null | Set-Content -Path $o } -ArgumentList $domain, $outFile
        if ($job -and (Wait-Job $job -Timeout 90 -ErrorAction SilentlyContinue)) { Receive-Job $job -ErrorAction SilentlyContinue | Out-Null }
        else { if ($job) { Stop-Job $job -ErrorAction SilentlyContinue; Remove-Job $job -Force -ErrorAction SilentlyContinue } }
        Remove-Job $job -Force -ErrorAction SilentlyContinue
        if (Test-Path $outFile) {
            $urlDomains = (Get-Content $outFile | ForEach-Object { if ($_ -match 'https?://([^/]+)') { $Matches[1] } }) | Select-Object -Unique
            $cnt = ($urlDomains | Measure-Object).Count
            Write-Output "      -> $cnt subdomains in URLs"
            $allSubdomains += $urlDomains
            $sourcesSummary["gau"] = $cnt
        } else { Write-Output "      -> 0" }
    } catch { Write-Output "      -> failed" }

    # waybackurls
    Write-Output "    waybackurls..."
    $outFile = "$reconDir\waybackurls-$domain.txt"
    try {
        $job = Start-Job -ScriptBlock { param($d,$o) & "C:\BugBounty\tools\waybackurls.exe" $d 2>$null | Set-Content -Path $o } -ArgumentList $domain, $outFile
        if ($job -and (Wait-Job $job -Timeout 90 -ErrorAction SilentlyContinue)) { Receive-Job $job -ErrorAction SilentlyContinue | Out-Null }
        else { if ($job) { Stop-Job $job -ErrorAction SilentlyContinue; Remove-Job $job -Force -ErrorAction SilentlyContinue } }
        Remove-Job $job -Force -ErrorAction SilentlyContinue
        if (Test-Path $outFile) {
            $urlDomains = (Get-Content $outFile | ForEach-Object { if ($_ -match 'https?://([^/]+)') { $Matches[1] } }) | Select-Object -Unique
            $cnt = ($urlDomains | Measure-Object).Count
            Write-Output "      -> $cnt subdomains in URLs"
            $allSubdomains += $urlDomains
            $sourcesSummary["waybackurls"] = $cnt
        } else { Write-Output "      -> 0" }
    } catch { Write-Output "      -> failed" }
}

# --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  
# PHASE 3: MERGE & FILTER
# --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  
Write-Step "PHASE 3: Merge & deduplicate"

$allSubdomains = $allSubdomains | Where-Object { $_ -and $_.Trim() -ne '' } | ForEach-Object { $_.Trim().ToLower() } | Select-Object -Unique | Sort-Object
$allSubdomains = $allSubdomains | Where-Object { $_ -match '^[a-zA-Z0-9][-a-zA-Z0-9]*(\.[a-zA-Z0-9][-a-zA-Z0-9]*)+$' }

$mergedFile = "$reconDir\all-subdomains.txt"
$allSubdomains | Set-Content -Path $mergedFile
Write-Output "  $($allSubdomains.Count) unique subdomains"

# --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  
# PHASE 4: DNS RESOLUTION
# --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  
Write-Step "PHASE 4: DNS resolution"

$resolvedFile = "$reconDir\resolved.txt"
$resolved = @()
try {
    if ($allSubdomains.Count -gt 0) {
        $out = & "$toolsDir\dnsx.exe" -l $mergedFile -silent -o $resolvedFile -a -resp 2>$null
        $resolved = if (Test-Path $resolvedFile) { Get-Content $resolvedFile } else { @() }
        Write-Output "  $($resolved.Count) resolved hosts"
    } else { Write-Output "  No subdomains to resolve" }
} catch { Write-Output "  Failed: $($_.Exception.Message)" }

# --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  
# PHASE 5: HTTP PROBING
# --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  
Write-Step "PHASE 5: HTTP probing"

$aliveFile = "$reconDir\alive.txt"
$alive = @()
try {
    $probeTargets = if ($resolved.Count -gt 0) { $resolved } else { $allSubdomains }
    if ($probeTargets.Count -gt 0) {
        $subOnly = $probeTargets | ForEach-Object { ($_ -split '\s+')[0] } | Select-Object -Unique | Where-Object { $_ -match '\.' }
        if ($subOnly.Count -gt 0) {
            $subOnly | Set-Content -Path "$reconDir\_probe_targets.txt"
            $out = & "$toolsDir\httpx.exe" -l "$reconDir\_probe_targets.txt" -silent -o $aliveFile -threads 50 -timeout 5 2>$null
            $alive = if (Test-Path $aliveFile) { Get-Content $aliveFile } else { @() }
            Write-Output "  $($alive.Count) alive hosts"
        } else { Write-Output "  No valid targets" }
    } else { Write-Output "  No targets to probe" }
} catch { Write-Output "  Failed: $($_.Exception.Message)" }

# --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  
# PHASE 6: URL COLLECTION
# --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  
Write-Step "PHASE 6: URL crawling"

$urlsFile = "$reconDir\urls.txt"
$allUrls = @()

if ($alive.Count -gt 0) {
    try {
        Write-Output "  katana..."
        $job = Start-Job -ScriptBlock { param($f,$o) & "C:\BugBounty\tools\katana.exe" -list $f -silent -o $o -jc -kf -d 2 -c 25 2>$null } -ArgumentList $aliveFile, "$reconDir\katana-urls.txt"
        if ($job -and (Wait-Job $job -Timeout 120 -ErrorAction SilentlyContinue)) { Receive-Job $job -ErrorAction SilentlyContinue | Out-Null }
        else { if ($job) { Stop-Job $job -ErrorAction SilentlyContinue; Remove-Job $job -Force -ErrorAction SilentlyContinue } }
        Remove-Job $job -Force -ErrorAction SilentlyContinue
        if (Test-Path "$reconDir\katana-urls.txt") { $allUrls += Get-Content "$reconDir\katana-urls.txt" }
    } catch { Write-Output "    katana failed" }

    try {
        Write-Output "  hakrawler..."
        $job = Start-Job -ScriptBlock { param($f,$o) Get-Content $f | & "C:\BugBounty\tools\hakrawler.exe" -depth 2 -subs -u 2>$null | Set-Content -Path $o } -ArgumentList $aliveFile, "$reconDir\hakrawler-urls.txt"
        if ($job -and (Wait-Job $job -Timeout 120 -ErrorAction SilentlyContinue)) { Receive-Job $job -ErrorAction SilentlyContinue | Out-Null }
        else { if ($job) { Stop-Job $job -ErrorAction SilentlyContinue; Remove-Job $job -Force -ErrorAction SilentlyContinue } }
        Remove-Job $job -Force -ErrorAction SilentlyContinue
        if (Test-Path "$reconDir\hakrawler-urls.txt") { $allUrls += Get-Content "$reconDir\hakrawler-urls.txt" }
    } catch { Write-Output "    hakrawler failed" }
}

$allUrls = $allUrls | Where-Object { $_ -and $_.Trim() -ne '' } | Select-Object -Unique | Sort-Object
$allUrls | Set-Content -Path $urlsFile
Write-Output "  $($allUrls.Count) unique URLs"

# --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  
# PHASE 7: CLASSIFICATION-SPECIFIC SCANS
# --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  

# 7a: API scan
if ($classification.api) {
    Write-Step "PHASE 7a: API-specific scanning"
    
    # Look for API endpoints in URLs
    $apiEndpoints = $allUrls | Where-Object { $_ -match '/api/|/v[0-9]/|/graphql|swagger|openapi' }
    if ($apiEndpoints.Count -gt 0) {
        $apiEndpoints | Set-Content -Path "$reconDir\api-endpoints.txt"
        Write-Output "  Found $($apiEndpoints.Count) API-related URLs"
    } else { Write-Output "  No API endpoints found in URLs" }

    # Probe common API paths on alive hosts
    $apiProbeFile = "$reconDir\api-probe.txt"
    $apiPaths = @("/api", "/api/v1", "/api/v2", "/graphql", "/swagger.json", "/openapi.json", "/.well-known/openid-configuration")
    $apiAlive = @()
    foreach ($h in $alive) {
        $base = $h.Trim()
        foreach ($p in $apiPaths) {
            try {
                $uri = "$base$p"
                $r = Invoke-WebRequest -Uri $uri -UseBasicParsing -TimeoutSec 5 -Method Head -ErrorAction SilentlyContinue
                if ($r.StatusCode -lt 500) { $apiAlive += "$uri (HTTP $($r.StatusCode))" }
            } catch {}
        }
    }
    if ($apiAlive.Count -gt 0) {
        $apiAlive | Set-Content -Path $apiProbeFile
        Write-Output "  Found $($apiAlive.Count) live API endpoints"
    } else { Write-Output "  No live API endpoints detected" }
}

# 7b: Cloud scan
if ($classification.cloud) {
    Write-Step "PHASE 7b: Cloud infrastructure scanning"
    $cloudFile = "$reconDir\cloud-checks.txt"
    $cloudResults = @()

    # Check common bucket names
    $bucketNames = $targetDomains | ForEach-Object { $_.Split('.')[0] }
    $bucketNames += $slug
    $bucketSuffixes = @("assets", "uploads", "static", "media", "backup", "config", "data", "files", "public", "dev", "prod", "staging")
    foreach ($b in $bucketNames) {
        foreach ($s in $bucketSuffixes) {
            $name = "$b-$s"
            # AWS S3
            try {
                $r = Invoke-WebRequest -Uri "https://$name.s3.amazonaws.com" -UseBasicParsing -TimeoutSec 5 -Method Head -ErrorAction SilentlyContinue
                if ($r.StatusCode -ne 404) { $cloudResults += "S3 bucket accessible: $name.s3.amazonaws.com (HTTP $($r.StatusCode))" }
            } catch {}
            # GCP
            try {
                $r = Invoke-WebRequest -Uri "https://storage.googleapis.com/$name" -UseBasicParsing -TimeoutSec 5 -Method Head -ErrorAction SilentlyContinue
                if ($r.StatusCode -ne 404) { $cloudResults += "GCP bucket accessible: storage.googleapis.com/$name (HTTP $($r.StatusCode))" }
            } catch {}
        }
    }

    # Subdomain takeover check (CNAME to unclaimed cloud service)
    foreach ($s in $allSubdomains | Select-Object -First 20) {
        try {
            $cname = Resolve-DnsName $s -Type CNAME -ErrorAction SilentlyContinue
            if ($cname) {
                $target = $cname.NameHost
                if ($target -match 's3\.amazonaws\.com|cloudfront\.net|azureedge\.net|azurewebsites\.net|storage\.googleapis\.com|herokuapp\.com|squarespace\.com|unbounce\.com|surge\.sh|github\.io|bitbucket\.io|worksites\.net|pantheonsite\.io|domains\.googledomains\.com') {
                    $cloudResults += "Possible takeover: $s -> $target"
                }
            }
        } catch {}
    }

    if ($cloudResults.Count -gt 0) {
        $cloudResults | Set-Content -Path $cloudFile
        Write-Output "  Found $($cloudResults.Count) cloud issues"
    } else { Write-Output "  No cloud issues detected" }
}

# 7c: Crypto scan
if ($classification.crypto) {
    Write-Step "PHASE 7c: Crypto/TLS scanning"
    $cryptoFile = "$reconDir\crypto-checks.txt"
    $cryptoResults = @()

    if (Get-Command nmap -ErrorAction SilentlyContinue) {
        foreach ($h in $alive | Select-Object -First 10) {
            $hostname = $h.Trim() -replace '^https?://', '' -replace '/.*$', ''
            try {
                $nmapOut = & nmap --script ssl-enum-ciphers -p 443 $hostname 2>$null
                if ($nmapOut -match 'weak|DES|RC4|MD5|SHA1|export|3DES') {
                    $cryptoResults += "${hostname}: weak ciphers detected"
                }
                if ($nmapOut -match 'TLSv1\.0|TLSv1\.1|SSLv') {
                    $cryptoResults += "${hostname}: outdated TLS version"
                }
                $cryptoResults += "${hostname}: TLS scan completed"
            } catch {}
        }
    } else { Write-Skip "nmap" }

    # Check for JWT in URLs
    $jwtEndpoints = $allUrls | Where-Object { $_ -match 'token|jwt|auth|oauth|bearer' }
    if ($jwtEndpoints.Count -gt 0) {
        $cryptoResults += "JWT/auth endpoints found: $($jwtEndpoints.Count) URLs"
    }

    if ($cryptoResults.Count -gt 0) {
        $cryptoResults | Set-Content -Path $cryptoFile
        Write-Output "  Found $($cryptoResults.Count) crypto-relevant findings"
    } else { Write-Output "  No crypto findings" }
}

# 7d: Mobile
if ($classification.mobile -and $foundApk) {
    Write-Step "PHASE 7d: Mobile APK download"
    try {
        $apkFile = "$progDir\downloads\$(Split-Path $foundApk -Leaf)"
        Invoke-WebRequest -Uri $foundApk -UseBasicParsing -TimeoutSec 120 -OutFile $apkFile -ErrorAction Stop
        Write-Output "  Downloaded: $apkFile"
        $hash = (Get-FileHash $apkFile -Algorithm SHA256).Hash
        Write-Output "  SHA256: $hash"

        if (Test-Path "$toolsDir\apktool.bat") {
            Write-Output "  Decompiling with apktool..."
            & "$toolsDir\apktool.bat" d $apkFile -o "$progDir\source\apktool_out" -f 2>$null
            Write-Output "    done"
        }
    } catch { Write-Output "  Failed: $($_.Exception.Message)" }
}

# 7e: Source code
if ($classification.source -and $foundRepo) {
    Write-Step "PHASE 7e: Source code download"
    try {
        $sourceDir = "$progDir\source\repo"
        if (Get-Command git -ErrorAction SilentlyContinue) {
            & git clone --depth 1 $foundRepo $sourceDir 2>&1 | Out-Null
            if (Test-Path $sourceDir) {
                Write-Output "  Cloned: $foundRepo"
                # Rust check
                if (Test-Path "$sourceDir\Cargo.toml") {
                    $classification.rust = $true
                    Write-Output "  [rust] Cargo.toml found --  -   Rust project"
                    @{rust=$true} | ConvertTo-Json | Set-Content -Path "$progDir\classification.json" -Encoding utf8
                }
            }
        } else { Write-Output "  git not available" }
    } catch { Write-Output "  Failed: $($_.Exception.Message)" }
}

# --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  
# PHASE 8: VULNERABILITY SCANNING (nuclei)
# --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  
Write-Step "PHASE 8: Vulnerability scanning (nuclei)"

$nucleiTemplates = "$env:USERPROFILE\nuclei-templates"
if (-not (Test-Path $nucleiTemplates)) {
    $nucleiTemplates = "$bbDir\wordlists\nuclei-templates"
}

$nucleiResultsFile = "$evidenceDir\nuclei-results.txt"
$nucleiJsonFile = "$evidenceDir\nuclei-results.json"

if ($alive.Count -gt 0) {
    try {
        Write-Output "  Scanning $($alive.Count) hosts"
        $job = Start-Job -ScriptBlock {
            param($f,$o,$jf,$tpl)
            & "C:\BugBounty\tools\nuclei.exe" -l $f -severity low,medium,high,critical -o $o -json-export $jf -silent 2>&1
        } -ArgumentList $aliveFile, $nucleiResultsFile, $nucleiJsonFile, $nucleiTemplates
        if ($job -and (Wait-Job $job -Timeout 600 -ErrorAction SilentlyContinue)) { Receive-Job $job -ErrorAction SilentlyContinue | Out-Null }
        else { if ($job) { Stop-Job $job -ErrorAction SilentlyContinue; Remove-Job $job -Force -ErrorAction SilentlyContinue } }
        Remove-Job $job -Force -ErrorAction SilentlyContinue

        $nucleiCount = if (Test-Path $nucleiResultsFile) { (Get-Content $nucleiResultsFile | Measure-Object -Line).Lines } else { 0 }
        Write-Output "  Found $nucleiCount findings"
    } catch { Write-Output "  Failed: $($_.Exception.Message)" }
} else { Write-Output "  No alive hosts to scan" }

# --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  
# PHASE 9: REPORT GENERATION
# --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  
Write-Step "PHASE 9: Generating reports"

# Parse nuclei results
$findingsTable = ""
$nucleiSummary = ""
$severityCounts = @{}
$nucleiCount = 0

if (Test-Path $nucleiResultsFile) {
    $nucleiResults = Get-Content $nucleiResultsFile
    $nucleiCount = ($nucleiResults | Measure-Object -Line).Lines
    if ($nucleiCount -gt 0) {
        $ft = @()
        $idx = 1
        foreach ($line in $nucleiResults) {
            $parsed = $null
            try { $parsed = $line | ConvertFrom-Json -ErrorAction SilentlyContinue } catch {}
            if ($parsed) {
                $sev = if ($parsed.info.severity) { $parsed.info.severity } else { "unknown" }
                $name = if ($parsed.info.name) { $parsed.info.name } else { "unknown" }
                $host = if ($parsed.host) { $parsed.host } else { "unknown" }
                $ft += '| {0} | {1} | {2} | {3} | open |' -f $idx, $name, $sev, $host
                if (-not $severityCounts.ContainsKey($sev)) { $severityCounts[$sev] = 0 }
                $severityCounts[$sev]++
                $idx++
            }
        }
        $findingsTable = $ft -join $([Environment]::NewLine)
        $nl = [Environment]::NewLine
        $nucleiSummary = "### Nuclei Findings by Severity$($nl)$($nl)"
        foreach ($s in @("critical","high","medium","low","info")) {
            if ($severityCounts.ContainsKey($s)) { $nucleiSummary += "- **$s**: $($severityCounts[$s])`n" }
        }
    }
}

$subdomainCount = $allSubdomains.Count
$assetCount = $alive.Count
$urlCount = $allUrls.Count

# Classifications detected
$classList = @()
if ($classification.web) { $classList += "web" }
if ($classification.api) { $classList += "api" }
if ($classification.mobile) { $classList += "mobile" }
if ($classification.source) { $classList += "source" }
if ($classification.cloud) { $classList += "cloud" }
if ($classification.crypto) { $classList += "crypto" }
if ($classification.rust) { $classList += "rust" }

# --  -  --  -   attack_surface.md --  -  --  -  
$assetRows = @()
if ($alive.Count -gt 0) {
    foreach ($h in $alive) {
        $h = $h.Trim() -replace '^https?://', '' -replace '/.*$', ''
        $assetRows += '| {0} | web | alive | |' -f $h
    }
} elseif ($allSubdomains.Count -gt 0) {
    $assetRows = $allSubdomains | Select-Object -First 50 | ForEach-Object { '| {0} | subdomain | discovered | |' -f $_ }
}
$assetTable = if ($assetRows.Count -gt 0) { $assetRows -join [Environment]::NewLine } else { '| {0} | - | - | |' -f '_(none)_' }

$sourcesText = $sourcesSummary.Keys | ForEach-Object { "- ${_}: $($sourcesSummary[$_]) entries" } | Sort-Object -Unique
$sourcesText = $sourcesText -join "`n"

$skillsPipeline = @()
$skillsPipeline += "Load these skills based on classification:"
$skillsPipeline += ""
$skillsPipeline += "1. Load bbp-program-triage - validate target and policy"
$skillsPipeline += "2. Load bbp-web-recon --  -   web recon (default)" + $(if ($classification.api) { ", bbp-api-audit --  -   API testing" } else { "" }) + $(if ($classification.mobile) { ", bbp-android-apk-audit --  -   APK audit" } else { "" }) + $(if ($classification.source) { ", bbp-source-code-audit --  -   code review" } else { "" }) + $(if ($classification.cloud) { ", bbp-cloud-security-audit --  -   cloud infra" } else { "" }) + $(if ($classification.crypto) { ", bbp-crypto-audit --  -   crypto review" } else { "" }) + $(if ($classification.rust) { ", bbp-rust-security-review --  -   Rust audit" } else { "" })
$skillsPipeline += "3. Load bbp-evidence-workbench --  -   organize findings"
$skillsPipeline += "4. Load bbp-report-writer --  -   final report"
$skillsPipeline += "5. Before deep-dive, load bbp-duplicate-guard"
$skillsPipeline = $skillsPipeline -join "`n"

@"
# Attack Surface: $slug

**Generated:** $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')
**Platform:** $platform
**URL:** $Url
**Classification:** $($classList -join ', ')

---

## Recon Summary

| Metric | Count |
|--------|-------|
| Targets analyzed | $($targetDomains.Count) |
| Unique subdomains | $subdomainCount |
| Alive hosts | $assetCount |
| URLs discovered | $urlCount |
| Nuclei findings | $nucleiCount |

## Asset Inventory

| Asset | Type | Status | Notes |
|-------|------|--------|-------|
$assetTable

## Findings

$($findingsTable -replace '(?m)^', '')
$($nucleiSummary -replace '(?m)^', '')

## Reconnaissance Sources

$sourcesText

## Skills Pipeline

$skillsPipeline
"@ | Set-Content -Path "$progDir\attack_surface.md" -Encoding utf8
Write-Output "  attack_surface.md updated"

# --  -  --  -   findings.md --  -  --  -  
@"
# Findings: $slug

**Program:** $slug
**Platform:** $platform
**Classification:** $($classList -join ', ')
**Generated:** $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')

---

## Summary

- Subdomains: $subdomainCount
- Alive hosts: $assetCount
- URLs crawled: $urlCount
- Nuclei findings: $nucleiCount

## Nuclei Findings

| # | Finding | Severity | Host | Status |
|---|---------|----------|------|--------|
$(if ($findingsTable) { $findingsTable } else { "| - | No vulnerabilities detected | - | - | reviewed |" })

$(if ($nucleiSummary) { $nucleiSummary } else { "" })
## Classification-Specific Artifacts

$(if ($classification.api -and (Test-Path "$reconDir\api-endpoints.txt")) { "- API endpoints: $reconDir\api-endpoints.txt`n- API probe results: $reconDir\api-probe.txt`n" } else { "" })
$(if ($classification.cloud -and (Test-Path "$reconDir\cloud-checks.txt")) { "- Cloud checks: $reconDir\cloud-checks.txt`n" } else { "" })
$(if ($classification.crypto -and (Test-Path "$reconDir\crypto-checks.txt")) { "- Crypto/TLS checks: $reconDir\crypto-checks.txt`n" } else { "" })
$(if ($classification.mobile) { "- APK: $progDir\downloads\`n- Source: $progDir\source\apktool_out`n" } else { "" })
$(if ($classification.source -and $foundRepo) { "- Repo: $foundRepo`n- Source: $progDir\source\repo`n" } else { "" })

## Next Steps

See attack_surface.md for the skills pipeline.
"@ | Set-Content -Path "$progDir\findings.md" -Encoding utf8
Write-Output "  findings.md updated"

# --  -  --  -   final_report.md --  -  --  -  
$findingsTableClean = if ($findingsTable) { $findingsTable } else { "No vulnerabilities were identified during automated scanning." }

@"
# Final Report: $slug

**Program:** $slug
**Platform:** $platform
**Classification:** $($classList -join ', ')
**Generated:** $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')

---

## Summary of Work

Automated reconnaissance and classification-driven scanning was performed against $subdomainCount discovered subdomains across $($targetDomains.Count) root domains.

**Target classified as:** $($classList -join ', ')

**Reconnaissance completed:**
- Subdomain enumeration via subfinder, assetfinder, amass
- URL collection via gau, waybackurls, katana, hakrawler
- DNS resolution via dnsx
- HTTP probing via httpx
- Web crawling via katana, hakrawler
- Vulnerability scanning via nuclei

$(if ($classification.api) { @"
**API-specific:**
- API endpoint discovery from URL corpus
- Live API path probing (common endpoints)
- See bbp-api-audit skill for manual API testing

"@ } else { "" })
$(if ($classification.cloud) { @"
**Cloud-specific:**
- S3/GCP bucket enumeration
- DNS CNAME takeover checks
- See bbp-cloud-security-audit skill for deeper review

"@ } else { "" })
$(if ($classification.crypto) { @"
**Crypto-specific:**
- TLS cipher scan via nmap
- JWT/auth endpoint discovery
- See bbp-crypto-audit skill for implementation review

"@ } else { "" })
$(if ($classification.mobile) { @"
**Mobile-specific:**
- APK downloaded and decompiled with apktool
- See bbp-android-apk-audit skill for manifest analysis

"@ } else { "" })
$(if ($classification.source) { @"
**Source-specific:**
- Repository cloned for local analysis
- See bbp-source-code-audit skill for static review

"@ } else { "" })
## Findings Summary

$nucleisummary

## Asset Inventory

- Alive hosts identified: $assetCount
- Unique URLs discovered: $urlCount

## Findings Detail

| # | Finding | Severity | Host | Status |
|---|---------|----------|------|--------|
$findingsTableClean

## Risk Rating

$(if ($nucleiCount -gt 0) {
    if ($severityCounts.ContainsKey("critical")) { "**CRITICAL**: Critical findings detected." }
    elseif ($severityCounts.ContainsKey("high")) { "**HIGH**: High-severity findings detected." }
    elseif ($severityCounts.ContainsKey("medium")) { "**MEDIUM**: Medium-severity findings." }
    elseif ($severityCounts.ContainsKey("low")) { "**LOW**: Low-severity findings." }
    else { "**INFO**: No actionable findings." }
} else { "**NONE**: No vulnerabilities identified through automated scanning." })

## Raw Outputs

- Subdomains: `$mergedFile`
- Alive hosts: `$aliveFile`
- URLs: `$urlsFile`
- Nuclei results: `$nucleiResultsFile`

## Recommendations

$(if ($nucleiCount -gt 0) {
@"
1. Review and validate each nuclei finding for false positives (load bbp-duplicate-guard first).
2. Manually test critical- and high-severity findings to confirm exploitability.
3. Run targeted manual tests based on classification:
"@ +
$(if ($classification.api) { "   - API: bbp-api-audit (IDOR, BOLA, mass assignment, rate limiting)`n" } else { "" }) +
$(if ($classification.cloud) { "   - Cloud: bbp-cloud-security-audit (bucket policies, metadata SSRF)`n" } else { "" }) +
$(if ($classification.crypto) { "   - Crypto: bbp-crypto-audit (algorithm, key mgmt, TLS)`n" } else { "" }) +
$(if ($classification.mobile) { "   - Mobile: bbp-android-apk-audit (exported components, WebViews)`n" } else { "" }) +
$(if ($classification.source) { "   - Source: bbp-source-code-audit (rg patterns, semgrep)`n" } else { "" }) +
$(if ($classification.rust) { "   - Rust: bbp-rust-security-review (unsafe, cargo audit)`n" } else { "" }) + @"
4. Organize evidence with bbp-evidence-workbench.
5. Generate final report with bbp-report-writer.
"@ } else {
@"
1. No vulnerabilities were automatically detected.
2. Load classification-specific skills for manual testing.
3. Review the application manually for logic flaws.
"@ })
"@ | Set-Content -Path "$progDir\final_report.md" -Encoding utf8
Write-Output "  final_report.md updated"

# --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  
# STATE: generate state.json for autonomous loop
# --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  
$state = @{
    program     = $slug
    slug        = $slug
    created     = (Get-Date -Format "yyyy-MM-ddTHH:mm:ss")
    updated     = (Get-Date -Format "yyyy-MM-ddTHH:mm:ss")
    phase       = "recon_done"
    domains     = $targetDomains
    subdomains  = @{ total = $subdomainCount; scanned = $true; file = $mergedFile }
    alive       = @{ total = $assetCount; scanned = $true; file = $aliveFile }
    urls        = @{ total = $urlCount; scanned = $true; file = $urlsFile }
    scans       = @(
        @{ tool = "program.ps1"; date = (Get-Date -Format "yyyy-MM-ddTHH:mm:ss"); status = "completed"; targets = $targetDomains.Count; subdomains = $subdomainCount; alive = $assetCount; urls = $urlCount; nuclei = $nucleiCount }
    )
    queue       = @()
    errors      = @()
}

# Populate queue based on findings
if ($nucleiCount -gt 0) {
    # Prioritize: validate critical/high findings first
    $criticals = @()
    $highs = @()
    foreach ($sev in @("critical", "high")) {
        if ($severityCounts.ContainsKey($sev) -and $severityCounts[$sev] -gt 0) {
            $state.queue += "validate-nuclei-$sev"
        }
    }
}

# API endpoints --  -   schedule sqlmap
if ($classification.api -and (Test-Path "$reconDir\api-endpoints.txt")) {
    $state.queue += "sqlmap-api-endpoints"
}

# Crypto --  -   schedule nmap TLS + JWT check
if ($classification.crypto) {
    $state.queue += "nmap-tls-scan"
}

# Cloud --  -   schedule bucket check
if ($classification.cloud) {
    $state.queue += "cloud-bucket-deep"
}

# Always: content discovery on new hosts if queue is empty
$state.queue += "ffuf-content-discovery"

$state | ConvertTo-Json -Depth 5 | Set-Content -Path "$progDir\state.json" -Encoding utf8
Write-Output "  state.json generated ($($state.queue.Count) queued actions)"

# --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  
# SUMMARY
# --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  --  -  
Write-Output ""
Write-Output "=============================================="
Write-Output "  /program ORCHESTRATOR --  -   COMPLETE"
Write-Output "=============================================="
Write-Output ""
Write-Output "  Program:       $slug"
Write-Output "  URL:           $Url"
Write-Output "  Platform:      $platform"
Write-Output "  Classification: $($classList -join ', ')"
Write-Output "  Workspace:     $progDir"
Write-Output ""
Write-Output "  Recon Results:"
Write-Output "    Target domains:     $($targetDomains.Count)"
Write-Output "    Unique subdomains:  $subdomainCount"
Write-Output "    Alive hosts:        $assetCount"
Write-Output "    URLs discovered:    $urlCount"
Write-Output "    Nuclei findings:    $nucleiCount"
Write-Output ""
Write-Output "  Classification Artifacts:"
if ($classification.api) { Write-Output "    API endpoints:  $(if (Test-Path "$reconDir\api-endpoints.txt") { (Get-Content "$reconDir\api-endpoints.txt" | Measure-Object -Line).Lines } else { 0 })" }
if ($classification.cloud) { Write-Output "    Cloud checks:   $(if (Test-Path "$reconDir\cloud-checks.txt") { (Get-Content "$reconDir\cloud-checks.txt" | Measure-Object -Line).Lines } else { 0 })" }
if ($classification.crypto) { Write-Output "    Crypto checks:  $(if (Test-Path "$reconDir\crypto-checks.txt") { (Get-Content "$reconDir\crypto-checks.txt" | Measure-Object -Line).Lines } else { 0 })" }
if ($classification.mobile) { Write-Output "    APK downloaded: $(if (Test-Path "$progDir\downloads\*.apk") { 'yes' } else { 'no' })" }
if ($classification.source) { Write-Output "    Repo cloned:    $(if (Test-Path "$progDir\source\repo") { 'yes' } else { 'no' })" }
Write-Output ""
Write-Output "  Reports:"
Write-Output "    attack_surface.md"
Write-Output "    findings.md"
Write-Output "    final_report.md"
Write-Output ""
Write-Output "  Skills Pipeline:"
Write-Output "    1. bbp-program-triage"
Write-Output "    2. $(if ($classification.api) { 'bbp-api-audit' } elseif ($classification.mobile) { 'bbp-android-apk-audit' } elseif ($classification.source) { 'bbp-source-code-audit' } else { 'bbp-web-recon' })"
if ($classification.cloud) { Write-Output "       bbp-cloud-security-audit" }
if ($classification.crypto) { Write-Output "       bbp-crypto-audit" }
if ($classification.rust) { Write-Output "       bbp-rust-security-review" }
Write-Output "    3. bbp-evidence-workbench"
Write-Output "    4. bbp-duplicate-guard"
Write-Output "    5. bbp-report-writer"
Write-Output ""
Write-Output "=============================================="
