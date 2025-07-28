@echo off
echo ===============================================
echo   Fixing Missing Dependencies
echo ===============================================
echo.

echo Installing missing Python packages...
echo.

python -m pip install pandas numpy ib_insync

echo.
echo Dependencies installed successfully!
echo.
echo You can now run the application using:
echo 1. Double-click run_app.bat
echo 2. Or use the desktop shortcut
echo.

pause
