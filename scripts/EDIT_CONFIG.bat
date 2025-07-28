@echo off
echo Opening Configuration Editor...
echo.

if exist "venv\" (
    call venv\Scripts\activate.bat
)

python config_editor.py

pause
