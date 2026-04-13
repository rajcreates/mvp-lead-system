@echo off
REM ─────────────────────────────────────────────────────────────
REM  Schedule MVP Lead Monitor to run every 2 hours on Windows
REM  Run this ONCE as Administrator
REM ─────────────────────────────────────────────────────────────

set SCRIPT_DIR=%~dp0
set PYTHON_PATH=python

REM Create scheduled task — runs every 2 hours
schtasks /create /tn "MVP Lead Monitor" ^
  /tr "\"%PYTHON_PATH%\" \"%SCRIPT_DIR%monitor.py\"" ^
  /sc hourly /mo 2 ^
  /st 08:00 ^
  /ru "%USERNAME%" ^
  /f

echo.
echo ✓ Scheduled task created: "MVP Lead Monitor"
echo   Runs every 2 hours starting at 8:00 AM
echo   Leads saved to: %SCRIPT_DIR%leads.csv
echo   Notifications sent to your Telegram bot
echo.
echo To remove:  schtasks /delete /tn "MVP Lead Monitor" /f
echo To run now: python "%SCRIPT_DIR%monitor.py"
pause
