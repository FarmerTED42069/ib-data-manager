@echo off
echo 🚀 Launching IB Data Manager - Unified Dashboard...
echo ✨ Streamlined interface with no more GUI fragmentation!
echo.

cd /d "%~dp0"
python launch_unified_dashboard.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ❌ Failed to launch dashboard
    echo Make sure Python is installed and in your PATH
    pause
)
