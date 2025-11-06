<#
Start script:
 - wipes previous demo data (removes loki_data and promtail positions)
 - starts the stack fresh (docker compose up -d --build)
 - waits for app & grafana to respond
#>

param()

function Wait-ForUrl {
  param([string]$Url,[int]$Tries=30,[int]$Delay=2)
  for ($i=1; $i -le $Tries; $i++) {
    try {
      $resp = Invoke-WebRequest -Uri $Url -UseBasicParsing -TimeoutSec 3
      if ($resp.StatusCode -ge 200 -and $resp.StatusCode -lt 500) {
        Write-Host "OK: $Url" -ForegroundColor Green
        return $true
      }
    } catch {
      Write-Host "." -NoNewline
    }
    Start-Sleep -Seconds $Delay
  }
  Write-Host "`nTimed out waiting for $Url" -ForegroundColor Yellow
  return $false
}

Write-Host "Cleaning previous demo data (Loki + Promtail positions)..." -ForegroundColor Cyan
# use the clean-logs script to do the wipe (it will docker compose down and remove volumes)
powershell -ExecutionPolicy Bypass -File ".\scripts\clean-logs.ps1" -WipeVolumes

Write-Host "`nStarting Docker stack (fresh)..." -ForegroundColor Cyan
docker compose up -d --build

Write-Host "Waiting for App (http://localhost:8080)..." -NoNewline
Wait-ForUrl "http://localhost:8080" | Out-Null

Write-Host "Waiting for Grafana (http://localhost:3000)..." -NoNewline
Wait-ForUrl "http://localhost:3000" | Out-Null

Write-Host "`nStack is up." -ForegroundColor Green
docker compose ps