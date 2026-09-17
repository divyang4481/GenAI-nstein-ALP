@echo off
setlocal
echo ===================================================
echo Launching RetailFlow with Docker and AWS Profile
echo ===================================================

python start_docker.py
if errorlevel 1 (
    echo.
    echo Make sure Docker Desktop is running and Python is installed.
)
pause
