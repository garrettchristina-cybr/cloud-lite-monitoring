param(
  [int]$Count = 8,
  [int]$DelayMs = 300
)

Write-Host "Generating $Count HTTP 500 errors..." -ForegroundColor Cyan
1..$Count | ForEach-Object {
  Invoke-WebRequest -Uri http://localhost:8080/error.php -UseBasicParsing | Out-Null
  Start-Sleep -Milliseconds $DelayMs
}
Write-Host "Done. Check the 5xx panel & Discord." -ForegroundColor Green