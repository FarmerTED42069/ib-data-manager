@echo off
echo ===============================================
echo   IB Data Manager - Desktop Shortcut Creator
echo ===============================================
echo.

echo This will create desktop shortcuts for:
echo 1. IB Data Manager (Python)
echo 2. IB Data Manager (Batch)
echo.

pause

echo.
echo Creating shortcuts...
echo.

:: Run the enhanced VBS script
cscript //nologo create_shortcut_enhanced.vbs

echo.
echo ===============================================
echo   Shortcuts created successfully!
echo ===============================================
echo.
echo You can now start IB Data Manager from your desktop.
echo.
echo If you have any issues, make sure:
echo 1. Python is installed and in your PATH
echo 2. Required packages are installed (run setup.py)
echo 3. IB Gateway is running with API enabled
echo.

pause
