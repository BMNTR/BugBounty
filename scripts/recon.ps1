param(
    [Parameter(Mandatory=$true)]
    [string]$Domain,
    [switch]$Quick,
    [switch]$Nuclei,
    [switch]$Screenshots
)

$ErrorActionPreference = "Continue"
$reconDir = "C:\BugBounty\recon\$Domain"
$toolsDir = "C:\BugBounty\tools"
$wordlistsDir = "C:\BugBounty\wordlists"
$env:Path = "$toolsDir;$env:USERPROFILE\go\bin;$env:USERPROFILE\.cargo\bin;" + [Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [Environment]::GetEnvironmentVariable("Path", "User")

New-Item -ItemType Directory -Path $reconDir -Force | Out-Null
Set-Location $reconDir

Write-Output "[*] Starting recon on $Domain at $(Get-Date)"
Write-Output "[*] Output directory: $reconDir"

# Phase 1: Subdomain enumeration
Write-Output "`n[+] Phase 1: Subdomain enumeration"

$subsFile = "$reconDir\subdomains.txt"
$allSubs = @()

if (Get-Command subfinder -ErrorAction SilentlyContinue) {
    Write-Output "  [-] Running subfinder..."
    $out = & subfinder -d $Domain -silent 2>$null
    $allSubs += $out
}

if (Get-Command assetfinder -ErrorAction SilentlyContinue) {
    Write-Output "  [-] Running assetfinder..."
    $out = & assetfinder --subs-only $Domain 2>$null
    $allSubs += $out
}

if (Get-Command amass -ErrorAction SilentlyContinue) {
    Write-Output "  [-] Running amass (passive)..."
    if ($Quick) { $amassArgs = "-passive -d $Domain -silent" }
    else { $amassArgs = "-passive -d $Domain -o $reconDir\amass_output.txt -silent" }
    $out = & amass enum $amassArgs 2>$null
    $allSubs += $out
}

# Deduplicate and save
$allSubs | Select-Object -Unique | Where-Object { $_ -match "\.$Domain$" } | Sort-Object | Set-Content -Path $subsFile
$subCount = (Get-Content $subsFile | Measure-Object -Line).Lines
Write-Output "  [+] Found $subCount unique subdomains"

# Phase 2: Alive check
Write-Output "`n[+] Phase 2: Checking alive hosts"
$aliveFile = "$reconDir\alive.txt"
if ((Get-Command httpx -ErrorAction SilentlyContinue) -and (Test-Path $subsFile)) {
    & httpx -l $subsFile -silent -o $aliveFile -threads 50 2>$null
    $aliveCount = (Get-Content $aliveFile | Measure-Object -Line).Lines
    Write-Output "  [+] $aliveCount alive hosts"
}

# Phase 3: URL discovery
Write-Output "`n[+] Phase 3: URL discovery"
$urlsFile = "$reconDir\urls.txt"
$allUrls = @()

if (Get-Command gau -ErrorAction SilentlyContinue) {
    Write-Output "  [-] Running gau..."
    $out = & gau --subs $Domain 2>$null
    $allUrls += $out
}

if (Get-Command waybackurls -ErrorAction SilentlyContinue) {
    Write-Output "  [-] Running waybackurls..."
    $out = & waybackurls $Domain 2>$null
    $allUrls += $out
}

if ($Quick -eq $false -and (Get-Command katana -ErrorAction SilentlyContinue) -and (Test-Path $aliveFile)) {
    Write-Output "  [-] Running katana..."
    if ($Screenshots) { $katanaArgs = "-list $aliveFile -silent -jc -kf -aff" }
    else { $katanaArgs = "-list $aliveFile -silent" }
    $out = & katana $katanaArgs 2>$null
    $allUrls += $out
}

$allUrls | Select-Object -Unique | Sort-Object | Set-Content -Path $urlsFile
$urlCount = (Get-Content $urlsFile | Measure-Object -Line).Lines
Write-Output "  [+] Found $urlCount unique URLs"

# Phase 4: Content discovery (if not quick)
if ($Quick -eq $false) {
    Write-Output "`n[+] Phase 4: Content discovery"
    if (Get-Command ffuf -ErrorAction SilentlyContinue) {
        $wordlist = "$wordlistsDir\SecLists\Discovery\Web-Content\common.txt"
        if (Test-Path $wordlist) {
            $ffufOut = "$reconDir\ffuf_common.txt"
            Write-Output "  [-] Running ffuf with common.txt..."
            & ffuf -u "https://FUZZ.$Domain/" -w $wordlist -t 50 -o $ffufOut -of csv -ac -silent 2>$null
        }
    }
}

# Phase 5: Nuclei scan (optional)
if ($Nuclei) {
    Write-Output "`n[+] Phase 5: Nuclei scanning"
    if (Get-Command nuclei -ErrorAction SilentlyContinue -and (Test-Path $aliveFile)) {
        $nucleiOut = "$reconDir\nuclei_results.txt"
        & nuclei -l $aliveFile -t ~/nuclei-templates/ -severity low,medium,high,critical -o $nucleiOut -silent 2>$null
        Write-Output "  [+] Nuclei scan complete"
    }
}

Write-Output "`n[*] Recon complete at $(Get-Date)"
Write-Output "[*] Results in: $reconDir"

# Summary
Write-Output "`n=== RECON SUMMARY ==="
Write-Output "Subdomains: $subCount"
Write-Output "Alive hosts: $aliveCount"
Write-Output "URLs: $urlCount"
if ($Nuclei) { Write-Output "Nuclei findings: $(if (Test-Path $nucleiOut) { (Get-Content $nucleiOut | Measure-Object -Line).Lines } else { 'N/A' })" }
