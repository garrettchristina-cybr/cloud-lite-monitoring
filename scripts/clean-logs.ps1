<#
.SYNOPSIS
  Clean/truncate demo logs and optionally wipe Loki/Promtail storage.

.DESCRIPTION
  - Stops promtail & php-apache (to release file locks on Windows)
  - Truncates Apache logs INSIDE the php-apache container paths
  - Truncates app_events.log on the host
  - Optionally wipes docker volumes (loki_data + promtail positions)
  - Restarts services (promtail only by default, or the whole stack)

.USAGE
  Basic (truncate logs only):
    powershell -ExecutionPolicy Bypass -File .\scripts\clean-logs.ps1

  Hard wipe (truncate + delete Loki/Promtail volumes + rebuild):
    powershell -ExecutionPolicy Bypass -File .\scripts\clean-logs.ps1 -WipeVolumes -RestartAll

  Truncate and restart full stack:
    powershell -ExecutionPolicy Bypass -File .\scripts\clean-logs.ps1 -RestartAll
#>

param(
  [switch]$WipeVolumes,   # remove loki_data & promtail positions (DESTRUCTIVE)
  [switch]$RestartAll     # docker compose up -d --build (else start promtail only)
)

$ErrorActionPreference = 'Stop'

function Safe {
  param([string]$Cmd)
  try { Invoke-Expression $Cmd | Out-Null } catch { Write-Warning "Command failed: $Cmd`n$($_.Exception.Message)" }
}

# Project root & paths
$root = Get-Location
$appLog    = Join-Path $root "apache-php\src\logs\app_events.log"
$accessLog = Join-Path $root "apache-php\apache-logs\access.log"
$errorLog  = Join-Path $root "apache-php\apache-logs\error.log"

Write-Host "Project root: $root" -ForegroundColor Cyan

# 1) Stop services that lock files
Write-Host "`nStopping promtail + php-apache..." -ForegroundColor Yellow
Safe "docker compose stop promtail php-apache"

# 2) Ensure files/directories exist
foreach ($p in @($appLog, $accessLog, $errorLog)) {
  $dir = Split-Path $p -Parent
  if (-not (Test-Path $dir)) { New-Item -ItemType Directory -Path $dir -Force | Out-Null }
  if (-not (Test-Path $p))   { New-Item -ItemType File -Path $p -Force | Out-Null }
}

# 3) Truncate Apache logs INSIDE the container paths to avoid Windows locks
Write-Host "Truncating Apache logs inside php-apache container..." -ForegroundColor Yellow
# Start php-apache briefly to run the truncation inside, then stop again
Safe "docker compose start php-apache"
Safe "docker compose exec php-apache sh -lc ':> /var/log/apache2/access.log; :> /var/log/apache2/error.log'"
Safe "docker compose stop php-apache"

# 4) Truncate app log on the host (no container lock now)
Write-Host "Truncating app_events.log on host..." -ForegroundColor Yellow
Set-Content -Path $appLog -Value '' -Force

# 5) Optional: Wipe Loki + Promtail volumes (DESTRUCTIVE)
if ($WipeVolumes) {
  Write-Host "`nWiping Loki/Promtail volumes (DESTRUCTIVE)..." -ForegroundColor Red
  Safe "docker compose down"

  # Loki data
  Safe "docker volume rm loki_data"

  # Promtail positions (try common names)
  foreach ($v in @('cloud-lite-monitoring_promtail_positions','promtail_positions')) {
    Safe "docker volume rm $v"
  }
}

# 6) Restart services
if ($RestartAll) {
  Write-Host "`nRebuilding + starting full stack..." -ForegroundColor Green
  Safe "docker compose up -d --build"
} else {
  Write-Host "`nStarting php-apache + promtail..." -ForegroundColor Green
  Safe "docker compose start php-apache promtail"
}

# 7) Quick verify hints
Write-Host "`nDone. Quick checks:" -ForegroundColor Green
Write-Host "  Get-Content `"$appLog`" -Tail 3"
Write-Host "  docker compose exec php-apache sh -lc 'wc -c /var/log/apache2/access.log /var/log/apache2/error.log'"
Write-Host "  docker compose logs promtail --tail 50"