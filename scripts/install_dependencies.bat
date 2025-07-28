@echo off
echo ===============================================
echo   IB Data Manager - Installing Dependencies
echo ===============================================
echo.

echo This will install all required Python packages:
echo - ib_insync (Interactive Brokers API)
echo - pandas (Data manipulation)
echo - numpy (Numerical computing)
echo.

pause

echo.
echo Installing dependencies...
echo.

python -m pip install --upgrade pip
python -m pip install -r requirements.txt

echo.
echo ===============================================
echo   Installation Complete!
echo ===============================================
echo.
echo Dependencies installed. You can now run IB Data Manager.
echo.

pause
