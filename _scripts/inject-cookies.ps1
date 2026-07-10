param(
    [string]$CookiesFile = "C:\BugBounty\cookies.txt",
    [string]$TargetUrl = "https://hackerone.com/hackers"
)

# Parse Netscape cookies
$allCookies = @()
Get-Content $CookiesFile | ForEach-Object {
    if ($_ -match "^#|^$") { return }
    $parts = $_ -split "`t"
    if ($parts.Length -ge 7) {
        $domain = $parts[0] -replace "^#HttpOnly_", ""
        $path = $parts[2]
        $secure = $parts[3] -eq "TRUE"
        $name = $parts[5]
        $value = $parts[6]
        $isHttpOnly = $_ -match "^#HttpOnly_"
        $allCookies += @{
            name = $name; value = $value; domain = $domain
            path = $path; secure = $secure; httpOnly = $isHttpOnly
            sameSite = "None"
        }
    }
}

Write-Host "Parsed $($allCookies.Count) cookies"

# Get tab WebSocket URL
$tabs = Invoke-RestMethod -Uri "http://localhost:9222/json"
$targetTab = $tabs | Where-Object { $_.url -like "*hackerone*" -or $_.url -like "*hacker.one*" } | Select-Object -First 1
if (-not $targetTab) { $targetTab = $tabs[-1] }
$wsUrl = $targetTab.webSocketDebuggerUrl

Write-Host "Using tab: $($targetTab.title)"

# WebSocket helper
function Send-CdpCommand {
    param($WsUrl, $CommandJson)
    $ws = New-Object System.Net.WebSockets.ClientWebSocket
    $ct = New-Object System.Threading.CancellationToken
    $ws.ConnectAsync([System.Uri]$WsUrl, $ct).Wait()

    $bytes = [System.Text.Encoding]::UTF8.GetBytes($CommandJson)
    $seg = New-Object System.ArraySegment[byte] -ArgumentList @(,$bytes)
    $ws.SendAsync($seg, [System.Net.WebSockets.WebSocketMessageType]::Text, $true, $ct).Wait()

    # Read response
    $buf = New-Object byte[] 4096
    $result = $ws.ReceiveAsync((New-Object System.ArraySegment[byte] -ArgumentList @(,$buf)), $ct).Wait()
    $resp = [System.Text.Encoding]::UTF8.GetString($buf, 0, $buf.Length)
    $ws.Dispose()
    return $resp
}

# 1. Enable network layer
Send-CdpCommand $wsUrl (@{id=1; method="Network.enable"} | ConvertTo-Json -Compress)
Start-Sleep -Milliseconds 200

# 2. Set cookies
$setCookies = @{
    id = 2
    method = "Network.setCookies"
    params = @{ cookies = $allCookies }
} | ConvertTo-Json -Depth 10 -Compress
Send-CdpCommand $wsUrl $setCookies
Start-Sleep -Milliseconds 300
Write-Host "Cookies injected"

# 3. Navigate
$navigate = @{
    id = 3
    method = "Page.navigate"
    params = @{ url = $TargetUrl }
} | ConvertTo-Json -Compress
Send-CdpCommand $wsUrl $navigate
Write-Host "Navigated to $TargetUrl"
