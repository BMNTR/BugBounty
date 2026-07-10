param(
    [Parameter(Mandatory=$true)]
    [string]$Domain,
    [string]$OutputDir,
    [string]$InScopeFile,
    [string]$OutOfScopeFile,
    [switch]$Quick,
    [switch]$Nuclei,
    [switch]$Screenshots
)

$ErrorActionPreference = "Continue"
$reconDir = if ($OutputDir) { $OutputDir } else { "C:\BugBounty\recon\$Domain" }
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

# Deduplicate and initial domain filter
$allSubs = $allSubs | Select-Object -Unique | Where-Object { $_ -match "\.$Domain$|^$Domain$" } | Sort-Object

# Scope Filtering
if ($InScopeFile -and (Test-Path $InScopeFile)) {
    $inScopeRegexes = Get-Content $InScopeFile | Where-Object { $_ -match '\S' }
    if ($inScopeRegexes.Count -gt 0) {
        Write-Output "  [-] Enforcing IN-SCOPE rules..."
        $allSubs = $allSubs | Where-Object {
            $sub = $_
            $match = $false
            foreach ($regex in $inScopeRegexes) { if ($sub -match $regex) { $match = $true; break } }
            $match
        }
    }
}

if ($OutOfScopeFile -and (Test-Path $OutOfScopeFile)) {
    $outScopeRegexes = Get-Content $OutOfScopeFile | Where-Object { $_ -match '\S' }
    if ($outScopeRegexes.Count -gt 0) {
        Write-Output "  [-] Enforcing OUT-OF-SCOPE rules..."
        $allSubs = $allSubs | Where-Object {
            $sub = $_
            $match = $false
            foreach ($regex in $outScopeRegexes) { if ($sub -match $regex) { $match = $true; break } }
            -not $match
        }
    }
}

$allSubs | Set-Content -Path $subsFile
$subCount = if (Test-Path $subsFile) { (Get-Content $subsFile | Measure-Object -Line).Lines } else { 0 }
Write-Output "  [+] Found $subCount unique in-scope subdomains"

# Phase 2: Alive check and Port Scanning
Write-Output "`n[+] Phase 2: Checking alive hosts and open ports"
$aliveFile = "$reconDir\alive.txt"
$naabuOut = "$reconDir\naabu_ports.txt"

if ((Get-Command naabu -ErrorAction SilentlyContinue) -and (Test-Path $subsFile)) {
    Write-Output "  [-] Running naabu for fast port scanning..."
    & naabu -l $subsFile -p - -silent -o $naabuOut 2>$null
    if (Test-Path $naabuOut) {
        $portCount = (Get-Content $naabuOut | Measure-Object -Line).Lines
        Write-Output "  [+] Found $portCount open ports"
        $httpxInput = $naabuOut
    } else {
        $httpxInput = $subsFile
    }
} else {
    $httpxInput = $subsFile
}

if ((Get-Command httpx -ErrorAction SilentlyContinue) -and (Test-Path $httpxInput)) {
    Write-Output "  [-] Running httpx on targets..."
    & httpx -l $httpxInput -silent -o $aliveFile -threads 50 2>$null
    $aliveCount = (Get-Content $aliveFile | Measure-Object -Line).Lines
    Write-Output "  [+] $aliveCount alive HTTP servers"
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

# Phase 4: Content discovery & Secret Hunting
if ($Quick -eq $false) {
    Write-Output "`n[+] Phase 4: Content discovery & Secret Hunting"
    $wordlist = "C:\BugBounty\wordlists\common.txt"
    $ffufOut = "$reconDir\ffuf_results.json"
    
    if ((Get-Command ffuf -ErrorAction SilentlyContinue) -and (Test-Path $wordlist) -and (Test-Path $aliveFile)) {
        Write-Output "  [-] Running ffuf with common.txt..."
        if ((Get-Item $aliveFile).length -gt 0) {
            foreach ($host in (Get-Content $aliveFile)) {
                $hostUrl = $host.TrimEnd('/')
                & ffuf -w $wordlist -u "$hostUrl/FUZZ" -mc 200,204,301,302,307,401,403,500 -t 50 -silent >> "$reconDir\ffuf.log" 2>$null
            }
        }
    }
    
    # Check parameters and run dalfox (DISABLED due to CPU hangs)
    # Write-Output "  [-] Skipping dalfox to save CPU and prevent hangs..."

    # Extract JS URLs and run SecretFinder
    $jsUrls = "$reconDir\js_urls.txt"
    $secretOut = "$reconDir\secrets.txt"
    if (Test-Path $urlsFile) {
        Get-Content $urlsFile | Where-Object { $_ -match '\.js$' } | Set-Content -Path $jsUrls
        $jsCount = if (Test-Path $jsUrls) { (Get-Content $jsUrls | Measure-Object -Line).Lines } else { 0 }
        
        if ($jsCount -gt 0 -and (Get-Command SecretFinder -ErrorAction SilentlyContinue)) {
            Write-Output "  [-] Running SecretFinder on $jsCount JavaScript files..."
            & SecretFinder -i $jsUrls -o cli > $secretOut 2>$null
        }
    }

    # dalfox for XSS on parametrized URLs
    $paramUrls = "$reconDir\param_urls.txt"
    $dalfoxOut = "$reconDir\dalfox_xss.txt"
    if ((Test-Path $urlsFile) -and (Get-Command dalfox -ErrorAction SilentlyContinue)) {
        Get-Content $urlsFile | Where-Object { $_ -match '\?' -and $_ -match '=' } | Set-Content -Path $paramUrls
        $paramCount = if (Test-Path $paramUrls) { (Get-Content $paramUrls | Measure-Object -Line).Lines } else { 0 }
        
        if ($paramCount -gt 0) {
            Write-Output "  [-] Running dalfox on $paramCount parametrized URLs..."
            & dalfox file $paramUrls -b "https://your-oast-server.com" -o $dalfoxOut --silence 2>$null
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
        
        # Check for Critical/High findings and notify
        if (Test-Path $nucleiOut) {
            $critCount = @(Get-Content $nucleiOut | Where-Object { $_ -match '\[critical\]' }).Count
            $highCount = @(Get-Content $nucleiOut | Where-Object { $_ -match '\[high\]' }).Count
            
            if ($critCount -gt 0) {
                & "C:\BugBounty\scripts\notify.ps1" -Message "Nuclei found $critCount CRITICAL vulnerabilities on $Domain! Check $nucleiOut" -Severity "Critical"
            }
            if ($highCount -gt 0) {
                & "C:\BugBounty\scripts\notify.ps1" -Message "Nuclei found $highCount HIGH vulnerabilities on $Domain. Check $nucleiOut" -Severity "High"
            }
        }
    }
}

# Phase 6: Smart Evidence Capture (Screenshots & DOM)
if ($Screenshots -and (Test-Path $aliveFile)) {
    Write-Output "`n[+] Phase 6: Smart Evidence Capture"
    $evidenceDir = "$reconDir\evidence"
    New-Item -ItemType Directory -Path $evidenceDir -Force | Out-Null
    
    Write-Output "  [-] Running capture-evidence.js on all alive hosts..."
    $aliveHosts = Get-Content $aliveFile
    foreach ($h in $aliveHosts) {
        Write-Output "      -> Capturing $h"
        & node "C:\BugBounty\scripts\capture-evidence.js" $h $evidenceDir 2>&1 | Out-Null
    }
    Write-Output "  [+] Evidence saved to $evidenceDir"
}

Write-Output "`n[*] Recon complete at $(Get-Date)"
Write-Output "[*] Results in: $reconDir"

# Summary
Write-Output "`n=== RECON SUMMARY ==="
Write-Output "Subdomains: $subCount"
Write-Output "Alive hosts: $aliveCount"
Write-Output "URLs: $urlCount"
if ($Nuclei) { Write-Output "Nuclei findings: $(if (Test-Path $nucleiOut) { (Get-Content $nucleiOut | Measure-Object -Line).Lines } else { 'N/A' })" }
