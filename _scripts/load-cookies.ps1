param(
    [string]$CookiesFile = "C:\BugBounty\cookies.txt",
    [string]$Url = "https://hackerone.com"
)

# Parse Netscape cookie file
$allCookies = @()
Get-Content $CookiesFile | ForEach-Object {
    if ($_ -match "^#|^$") { return }
    $parts = $_ -split "`t"
    if ($parts.Length -ge 7) {
        $domain = $parts[0] -replace "^#HttpOnly_", ""
        $flag = $parts[1]    # TRUE/FALSE - include subdomains
        $path = $parts[2]
        $secure = $parts[3] -eq "TRUE"
        $expiry = [long]$parts[4]
        $name = $parts[5]
        $value = $parts[6]
        $isHttpOnly = $_ -match "^#HttpOnly_"

        $cookie = @{
            name = $name
            value = $value
            domain = $domain
            path = $path
            secure = $secure
            httpOnly = $isHttpOnly
            sameSite = "None"
        }
        $allCookies += $cookie
    }
}

Write-Host "Parsed $($allCookies.Count) cookies"

# Kill existing Chrome
Get-Process chrome -ErrorAction SilentlyContinue | Stop-Process -Force
Start-Sleep -Seconds 2

# Start Chrome with remote debugging
$chromePath = "C:\Program Files\Google\Chrome\Application\chrome.exe"
if (-not (Test-Path $chromePath)) {
    $chromePath = "${env:ProgramFiles}\Google\Chrome\Application\chrome.exe"
}
if (-not (Test-Path $chromePath)) {
    $chromePath = "${env:LocalAppData}\Google\Chrome\Application\chrome.exe"
}

$userDataDir = "$env:TEMP\chrome-h1-$(Get-Random)"
Start-Process $chromePath -ArgumentList "--remote-debugging-port=9222", "--user-data-dir=`"$userDataDir`"", "--no-first-run", "about:blank"
Start-Sleep -Seconds 3

# Get WebSocket URL
try {
    $tabs = Invoke-RestMethod -Uri "http://localhost:9222/json" -ErrorAction Stop
    $wsUrl = $tabs[0].webSocketDebuggerUrl
    Write-Host "Connected to Chrome DevTools: $wsUrl"
} catch {
    Write-Error "Failed to connect to Chrome DevTools: $_"
    exit 1
}

# Send CDP command via WebSocket to set cookies
$ws = New-Object System.Net.WebSockets.ClientWebSocket
$ct = New-Object System.Threading.CancellationToken
$ws.ConnectAsync([System.Uri]$wsUrl, $ct).Wait()
Write-Host "WebSocket connected"

$sendCommand = @{
    id = 1
    method = "Network.setCookies"
    params = @{
        cookies = $allCookies
    }
} | ConvertTo-Json -Depth 10 -Compress

$bytes = [System.Text.Encoding]::UTF8.GetBytes($sendCommand)
$segment = New-Object System.ArraySegment[byte] -ArgumentList @(,$bytes)
$ws.SendAsync($segment, [System.Net.WebSockets.WebSocketMessageType]::Text, $true, $ct).Wait()
Write-Host "Cookies sent via CDP"
Start-Sleep -Milliseconds 500

# Navigate to the target URL
$navigateCommand = @{
    id = 2
    method = "Page.navigate"
    params = @{
        url = $Url
    }
} | ConvertTo-Json -Depth 10 -Compress

$bytes2 = [System.Text.Encoding]::UTF8.GetBytes($navigateCommand)
$segment2 = New-Object System.ArraySegment[byte] -ArgumentList @(,$bytes2)
$ws.SendAsync($segment2, [System.Net.WebSockets.WebSocketMessageType]::Text, $true, $ct).Wait()
Write-Host "Navigated to $Url"

$ws.Dispose()
