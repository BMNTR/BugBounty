param([string]$Url = "https://yeswehack.com")

$bbDir = "C:\BugBounty"
$cookieFile = "$bbDir\cookies.txt"

Write-Output "=== Cookie Setup for Private Programs ==="
Write-Output ""

if (Test-Path $cookieFile) {
    $lines = Get-Content $cookieFile | Where-Object { $_ -notmatch '^#' -and $_.Trim() -ne '' }
    Write-Output "  cookies.txt found with $($lines.Count) cookie(s)"
    
    # Test cookies
    $cookies = @()
    foreach ($line in $lines) {
        $parts = $line -split '\t'
        if ($parts.Count -ge 7) { $cookies += "$($parts[5])=$($parts[6])" }
    }
    Write-Output "  Testing against $Url ..."
    try {
        $r = Invoke-WebRequest -Uri $Url -Headers @{ Cookie = ($cookies -join '; ') } -UseBasicParsing -TimeoutSec 10 -ErrorAction Stop
        Write-Output "  HTTP $($r.StatusCode) ($($r.Content.Length) bytes)"
        if ($r.Content.Length -gt 5000) {
            Write-Output "  [OK] Cookies work! Private program pages should be accessible."
        } else {
            Write-Output "  [WARN] Page is small ($($r.Content.Length) bytes). Cookies might be expired or invalid."
        }
    } catch {
        Write-Output "  [FAIL] Cookies not working: $_"
    }
} else {
    Write-Output "  cookies.txt not found."
}

Write-Output ""
Write-Output "=== How to set up cookies ==="
Write-Output ""
Write-Output "1. Open browser and log into YesWeHack"
Write-Output "2. Install a cookie exporter extension:"
Write-Output "   - Chrome: 'Get cookies.txt LOCALLY' or 'EditThisCookie'"
Write-Output "   - Firefox: 'cookies.txt' or 'Cookie Quick Manager'"
Write-Output "3. Export cookies for yeswehack.com in Netscape format"
Write-Output "4. Save/replace the file: $cookieFile"
Write-Output ""
Write-Output "Alternative - Manual:"
Write-Output "1. Open DevTools (F12) -> Network tab"
Write-Output "2. Find any request to yeswehack.com"
Write-Output "3. Copy the 'Cookie' request header value"
Write-Output "4. Create $cookieFile with content:"
Write-Output "   # Netscape HTTP Cookie File"
Write-Output "   .yeswehack.com TRUE / TRUE 0 session <paste-value>"
