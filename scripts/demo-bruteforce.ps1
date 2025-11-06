param(
  [string]$Ip = "8.8.8.8",
  [int]$Count = 12,
  [int]$DelayMs = 1000
)

Write-Host "Generating $Count failed logins from $Ip..." -ForegroundColor Cyan
1..$Count | ForEach-Object {
  curl.exe -X POST http://localhost:8080/login.php `
    -H "X-Forwarded-For: $Ip" `
    -H "Content-Type: application/x-www-form-urlencoded" `
    --data "username=admin&password=wrong" | Out-Null
  Start-Sleep -Milliseconds $DelayMs
}
Write-Host "Done. Check Grafana & Discord in ~1 minute." -ForegroundColor Green