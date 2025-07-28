@echo off
echo ===============================================
echo   Creating Virtual Environment for IB Data Manager
echo ===============================================
echo.

echo Creating virtual environment...
python -m venv venv

echo.
echo Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo Installing required packages...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

echo.
echo ===============================================
echo   Virtual Environment Setup Complete!
echo ===============================================
echo.
echo Virtual environment created successfully!
echo.
echo To use the application:
echo 1. The virtual environment will be activated automatically when you run the app
echo 2. All dependencies are now installed in the virtual environment
echo.
pause
