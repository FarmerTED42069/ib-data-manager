@echo off
echo Running IB Data Manager Troubleshooting...
echo.

if exist "venv\" (
    call venv\Scripts\activate.bat
)

python troubleshoot.py

echo.
pause
