@echo off
cd /d "%~dp0"
echo Starting IB Data Manager (Async GUI)...
python -m ib_data_manager.gui.main_async
pause
