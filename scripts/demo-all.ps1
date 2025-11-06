param(
  [string]$Ip = "8.8.8.8"
)

Write-Host "Ensuring stack is up..." -ForegroundColor Cyan
docker compose ps | Out-Null
if ($LASTEXITCODE -ne 0) { docker compose up -d --build }

Start-Sleep -Seconds 5

& "$PSScriptRoot\demo-bruteforce.ps1" -Ip $Ip -Count 12 -DelayMs 1000
Start-Sleep -Seconds 5
& "$PSScriptRoot\demo-5xx.ps1" -Count 8 -DelayMs 300

Write-Host "Traffic generated. Alerts may take ~1 minute to evaluate." -ForegroundColor Green

# AI summary
python ai/ai_summarize.py