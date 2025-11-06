@echo off
REM Usage:
REM   run bat demo-all
REM   run bat brute
REM   run bat 5xx
REM   run bat clean
REM   run bat start
REM   run bat stop

setlocal
cd /d "%~dp0.."   REM move from scripts folder to project root

if /I "%1"=="demo-all" (
  powershell -ExecutionPolicy Bypass -File ".\scripts\demo-all.ps1"
  goto :EOF
)

if /I "%1"=="brute" (
  powershell -ExecutionPolicy Bypass -File ".\scripts\demo-bruteforce.ps1" %2 %3 %4
  goto :EOF
)

if /I "%1"=="5xx" (
  powershell -ExecutionPolicy Bypass -File ".\scripts\demo-5xx.ps1" %2 %3 %4
  goto :EOF
)

if /I "%1"=="clean" (
  if /I "%2"=="wipe" (
    powershell -ExecutionPolicy Bypass -File ".\scripts\clean-logs.ps1" -WipeVolumes -RestartAll
  ) else if /I "%2"=="restart" (
    powershell -ExecutionPolicy Bypass -File ".\scripts\clean-logs.ps1" -RestartAll
  ) else (
    powershell -ExecutionPolicy Bypass -File ".\scripts\clean-logs.ps1"
  )
  goto :EOF
)

if /I "%1"=="start" (
  powershell -ExecutionPolicy Bypass -File ".\scripts\start.ps1"
  goto :EOF
)

if /I "%1"=="stop" (
  powershell -ExecutionPolicy Bypass -File ".\scripts\stop.ps1"
  goto :EOF
)

echo Unknown command. Use one of: demo-all | brute | 5xx | clean [wipe|restart] | start | stop
endlocal