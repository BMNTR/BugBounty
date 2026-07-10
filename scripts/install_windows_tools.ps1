$ErrorActionPreference = "Continue"

Write-Output "=== Bug Bounty Windows Tools Installer (Non-Admin) ==="
Write-Output "Started: $(Get-Date)`n"

# Verify Scoop is installed, if not, install it locally
if (-not (Get-Command scoop -ErrorAction SilentlyContinue)) {
    Write-Output "[*] Scoop is not installed. Installing Scoop..."
    Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
    Invoke-RestMethod -Uri https://get.scoop.sh | Invoke-Expression
    
    # Reload environment block for current session
    $env:Path = [Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [Environment]::GetEnvironmentVariable("Path", "User")
}

Write-Output "[*] Adding required Scoop buckets..."
scoop bucket add extras
scoop bucket add java
scoop bucket add versions

$packages = @(
    "sysinternals",
    "x64dbg",
    "ghidra",
    "dnspy"
)

Write-Output "`n[*] Installing Windows Reverse Engineering tools via Scoop..."
foreach ($pkg in $packages) {
    Write-Output "  Installing $pkg..."
    scoop install $pkg
    if ($LASTEXITCODE -eq 0 -or $?) {
        Write-Output "  [+] OK: $pkg installed successfully."
    } else {
        Write-Output "  [-] FAIL: Failed to install $pkg."
    }
}

Write-Output "`n[*] Updating tools directory PATH if needed..."
Write-Output "Completed: $(Get-Date)"
