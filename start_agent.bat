@echo off
title Bridge MCP Agent
echo ==========================================
echo      Bridge MCP - Starting Agent...
echo ==========================================

:: Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [Error] Python is not installed or not in PATH.
    echo Please install Python from https://python.org
    pause
    exit /b
)

:: Install/Check Dependencies
echo [Setup] Checking dependencies...
python -m pip install -r requirements-local.txt >nul 2>&1
if %errorlevel% neq 0 (
    echo [Warning] Failed to install dependencies. Trying to proceed anyway...
) else (
    echo [Setup] Dependencies OK.
)

:: Run Agent (Tray App if available, else console)
if exist tray_app.py (
    echo [Info] Launching System Tray Application...
    python tray_app.py
) else (
    echo [Info] Launching Console Agent...
    python local_agent.py
)

if %errorlevel% neq 0 (
    echo.
    echo [Error] Agent exited with error code %errorlevel%
    pause
)
