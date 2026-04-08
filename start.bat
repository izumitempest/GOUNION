@echo off
:: ──────────────────────────────────────────────
::  GoUnion — Dev Startup Script (Windows)
:: ──────────────────────────────────────────────
title GoUnion Dev Server

set "SCRIPT_DIR=%~dp0"
set "BACKEND_DIR=%SCRIPT_DIR%"
set "FRONTEND_DIR=%SCRIPT_DIR%gounion-remake"
set "VENV_DIR=%SCRIPT_DIR%venv"
set "ENV_FILE=%SCRIPT_DIR%.env"

echo.
echo  @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
echo   GoUnion - Starting Dev Environment
echo  @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
echo.

:: ── Check .env ────────────────────────────────
if not exist "%ENV_FILE%" (
    echo [WARN] .env file not found. Backend may be missing environment variables.
    echo.
)

:: ── Python venv ───────────────────────────────
echo [GoUnion] Setting up Python virtual environment...
if not exist "%VENV_DIR%" (
    python -m venv "%VENV_DIR%"
    echo [  OK  ] Created virtual environment
)

call "%VENV_DIR%\Scripts\activate.bat"

echo [GoUnion] Installing / verifying Python dependencies...
pip install -r "%BACKEND_DIR%requirements.txt" -q
echo [  OK  ] Python dependencies ready

:: ── Backend in new window ─────────────────────
echo [GoUnion] Starting FastAPI backend on http://127.0.0.1:8001 ...
start "GoUnion Backend" cmd /k "cd /d "%BACKEND_DIR%" && call "%VENV_DIR%\Scripts\activate.bat" && uvicorn fastapi_server.main:app --port 8001 --reload"
echo [  OK  ] Backend window opened

:: ── Frontend in new window ────────────────────
echo [GoUnion] Checking Node.js dependencies...
if not exist "%FRONTEND_DIR%\node_modules" (
    echo [GoUnion] node_modules not found - running npm install...
    cd /d "%FRONTEND_DIR%"
    call npm install
    echo [  OK  ] npm install complete
)

echo [GoUnion] Starting Vite frontend on http://localhost:3000 ...
start "GoUnion Frontend" cmd /k "cd /d "%FRONTEND_DIR%" && npm run dev"
echo [  OK  ] Frontend window opened

:: ── Done ──────────────────────────────────────
echo.
echo  @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
echo   GoUnion is running!
echo  @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
echo.
echo   Frontend  ^>  http://localhost:3000
echo   Backend   ^>  http://127.0.0.1:8001
echo   API Docs  ^>  http://127.0.0.1:8001/docs
echo.
echo  @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
echo   Close the backend and frontend windows
echo   to stop the servers.
echo  @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
echo.
pause
