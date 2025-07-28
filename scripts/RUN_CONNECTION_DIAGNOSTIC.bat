@echo off
echo Running IB Gateway Connection Diagnostic...
echo.

if exist "venv\" (
    call venv\Scripts\activate.bat
    python -m pip install psutil
)

python connection_diagnostic.py

pause
