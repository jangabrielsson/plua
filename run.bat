@echo off
REM EPLua runner script for Windows

echo 🚀 EPLua - Native UI System
echo ============================

REM Set PYTHONPATH to include src directory
set "PYTHONPATH=%~dp0src;%PYTHONPATH%"

REM Check if .venv exists and activate it
if exist ".venv\Scripts\activate.bat" (
    call .venv\Scripts\activate.bat
    echo ℹ️ Activated .venv virtual environment
) else (
    echo ℹ️ .venv not found, using system Python
)

REM Run with Python module syntax, passing all arguments
python -m eplua.cli %*
