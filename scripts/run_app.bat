@echo off
echo Starting IB Data Manager...

:: Check if virtual environment exists
if not exist "venv\" (
    echo Virtual environment not found. Creating it now...
    call create_venv.bat
)

:: Activate virtual environment
call venv\Scripts\activate.bat

:: Run the application
python D:\projects\trading-bots\ib_data_manager\ib_data_manager\main.py

:: Deactivate virtual environment when done
deactivate

echo Application exited. (Launched from D:\projects\trading-bots\ib_data_manager) & pause
