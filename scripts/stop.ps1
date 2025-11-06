<#
Stop script:
 - shuts down the docker compose stack
 - optionally removes Loki + promtail volumes so no old data lingers
#>

param()

Write-Host "Stopping Docker stack and wiping demo data..." -ForegroundColor Cyan

# Use clean-logs to perform a safe down + wipe of volumes.
powershell -ExecutionPolicy Bypass -File ".\scripts\clean-logs.ps1" -WipeVolumes

Write-Host "`nAll done. Stack stopped and demo data wiped." -ForegroundColor Green
docker compose ps