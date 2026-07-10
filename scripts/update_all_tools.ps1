$ErrorActionPreference = "Continue"
$toolsDir = "C:\BugBounty\tools"
$env:Path = [Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [Environment]::GetEnvironmentVariable("Path", "User") + ";$toolsDir;$env:USERPROFILE\go\bin;$env:USERPROFILE\.cargo\bin;$env:USERPROFILE\AppData\Roaming\npm;$env:USERPROFILE\AppData\Local\Programs\Python\Python311\Scripts"

$log = @()
Write-Output "=== Bug Bounty Tool Updater ==="
Write-Output "Started: $(Get-Date)`n"

# Update Go tools
Write-Output "[*] Updating Go tools..."
$goTools = @(
    "github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest",
    "github.com/tomnomnom/assetfinder@latest",
    "github.com/owasp-amass/amass/v4/...@master",
    "github.com/projectdiscovery/httpx/cmd/httpx@latest",
    "github.com/projectdiscovery/dnsx/cmd/dnsx@latest",
    "github.com/projectdiscovery/katana/cmd/katana@latest",
    "github.com/lc/gau/v2/cmd/gau@latest",
    "github.com/tomnomnom/waybackurls@latest",
    "github.com/hakluke/hakrawler@latest",
    "github.com/ffuf/ffuf/v2@latest",
    "github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest",
    "github.com/projectdiscovery/interactsh/cmd/interactsh-client@latest",
    "github.com/mikefarah/yq/v4@latest"
)
foreach ($tool in $goTools) {
    $name = $tool.Split('/')[-1].Split('@')[0]
    Write-Output "  Updating $name..."
    $result = go install $tool 2>&1
    if ($LASTEXITCODE -eq 0) { $log += "OK: $name updated" }
    else { $log += "FAIL: $name - $result" }
}

# Update Python tools
Write-Output "`n[*] Updating Python tools..."
pip install --upgrade bandit pip-audit semgrep frida-tools objection --quiet 2>&1 | Out-Null
$log += "OK: Python tools updated"

# Update npm tools
Write-Output "`n[*] Updating npm tools..."
npm update -g playwright retire 2>&1 | Out-Null
$log += "OK: npm tools updated"

# Update nuclei templates
Write-Output "`n[*] Updating nuclei templates..."
if (Get-Command nuclei -ErrorAction SilentlyContinue) {
    nuclei -update-templates 2>&1 | Out-Null
    $log += "OK: nuclei templates updated"
}

# Update Rust tools
Write-Output "`n[*] Updating Rust tools..."
$cargoTools = @("cargo-audit", "cargo-deny", "cargo-geiger")
foreach ($tool in $cargoTools) {
    $result = cargo install $tool 2>&1
    if ($LASTEXITCODE -eq 0) { $log += "OK: $tool updated" }
    else { $log += "SKIP: $tool (compile error - use prebuilt)" }
}

# Update wordlists
Write-Output "`n[*] Updating wordlists..."
$wlDir = "C:\BugBounty\wordlists"
if (Test-Path "$wlDir\SecLists\.git") { Set-Location "$wlDir\SecLists"; git pull 2>&1 | Out-Null; $log += "OK: SecLists updated" }
if (Test-Path "$wlDir\PayloadsAllTheThings\.git") { Set-Location "$wlDir\PayloadsAllTheThings"; git pull 2>&1 | Out-Null; $log += "OK: PayloadsAllTheThings updated" }

Write-Output "`n=== UPDATE LOG ==="
$log | ForEach-Object { Write-Output $_ }
Write-Output "`nCompleted: $(Get-Date)"
