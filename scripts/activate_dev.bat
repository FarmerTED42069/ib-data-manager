@echo off
echo ===============================================
echo   Activating Development Environment
echo ===============================================
echo.

if not exist "venv\" (
    echo Virtual environment not found. Creating it now...
    python -m venv venv
    call venv\Scripts\activate.bat
    echo Installing dependencies...
    python -m pip install --upgrade pip
    python -m pip install -r requirements.txt
) else (
    call venv\Scripts\activate.bat
)

echo.
echo Development environment activated!
echo.
echo You can now:
echo 1. Run: python main.py
echo 2. Test: python test_connection.py  
echo 3. Install additional packages: pip install package_name
echo 4. Deactivate when done: deactivate
echo.

cmd /k
