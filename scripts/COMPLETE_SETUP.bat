@echo off
echo ===============================================
echo   IB Data Manager - Complete Setup
echo ===============================================
echo.

echo This script will:
echo 1. Create a virtual environment
echo 2. Install all required packages
echo 3. Create desktop shortcuts
echo 4. Run the application
echo.

pause

echo.
echo Step 1: Creating virtual environment...
python -m venv venv

echo.
echo Step 2: Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo Step 3: Installing dependencies...
python -m pip install --upgrade pip
python -m pip install pandas numpy ib_insync

echo.
echo Step 4: Creating desktop shortcuts...
cscript //nologo create_shortcut_enhanced.vbs

echo.
echo ===============================================
echo   Setup Complete!
echo ===============================================
echo.
echo The application is now ready to use.
echo Desktop shortcuts have been created.
echo.
echo Would you like to start the application now? (Y/N)
set /p start_now=

if /i "%start_now%"=="Y" (
    echo.
    echo Starting IB Data Manager...
    python main.py
)

deactivate
pause
