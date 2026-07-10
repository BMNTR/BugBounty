param(
    [Parameter(Mandatory=$true)]
    [string]$Message,
    
    [Parameter(Mandatory=$false)]
    [string]$Severity = "Info"
)

$webhookFile = "C:\BugBounty\discord_webhook.txt"

if (-not (Test-Path $webhookFile)) {
    Write-Output "[-] Webhook file not found at $webhookFile. Notifications disabled."
    exit 0
}

$webhookUrl = (Get-Content $webhookFile).Trim()

if (-not $webhookUrl -or $webhookUrl -notmatch "^https://discord\.com/api/webhooks/") {
    Write-Output "[-] Invalid or empty Discord webhook URL."
    exit 0
}

# Set color based on severity
$color = 3447003 # Default blue for Info
if ($Severity -eq "Critical") { $color = 15158332 } # Red
elseif ($Severity -eq "High") { $color = 15105570 } # Orange
elseif ($Severity -eq "Medium") { $color = 16776960 } # Yellow
elseif ($Severity -eq "Low") { $color = 3066993 } # Green

$payload = @{
    embeds = @(
        @{
            title = "[$Severity] Bug Bounty Alert"
            description = $Message
            color = $color
            timestamp = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
        }
    )
} | ConvertTo-Json -Depth 10

try {
    Invoke-RestMethod -Uri $webhookUrl -Method Post -Body $payload -ContentType "application/json" -ErrorAction Stop | Out-Null
    Write-Output "[+] Notification sent via Discord."
} catch {
    Write-Output "[-] Failed to send Discord notification: $_"
}
