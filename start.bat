@echo off
setlocal
echo ===================================================
echo 🚀 Launching RetailFlow Platform
echo ===================================================

:: Try to activate conda 'ml' env if available, otherwise fallback gracefully
call conda activate ml 2>nul

python start_retailflow.py
if errorlevel 1 (
    echo.
    echo If python is not in PATH, please ensure Python 3.10+ is installed.
)
pause
