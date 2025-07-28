@echo off
echo ===============================================
echo   IB Data Manager - Setup and Run
echo ===============================================
echo.

echo Checking Python installation...
python --version
if errorlevel 1 (
    echo.
    echo ERROR: Python is not installed or not in PATH!
    echo Please install Python from python.org and make sure to check "Add Python to PATH"
    echo.
    pause
    exit
)

echo.
echo Installing required packages...
echo.

python -m pip install --upgrade pip
python -m pip install ib_insync pandas numpy

echo.
echo ===============================================
echo   Starting IB Data Manager
echo ===============================================
echo.

python main.py

pause
