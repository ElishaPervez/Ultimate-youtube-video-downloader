@echo off
echo Starting YouTube Video Downloader...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not found in PATH.
    echo Please install Python 3.7 or higher from https://python.org
    pause
    exit /b 1
)

REM Check if yt-dlp is installed
python -c "import yt_dlp" >nul 2>&1
if errorlevel 1 (
    echo yt-dlp is not installed. Installing dependencies...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo Error: Failed to install dependencies.
        echo Please check your internet connection and try again.
        pause
        exit /b 1
    )
)

REM Run the application
echo Launching YouTube Video Downloader...
python run.py

REM Keep console open if there's an error
if errorlevel 1 (
    echo.
    echo Application exited with an error.
    pause
)