@echo off
REM Composite Indicator Builder Launcher
REM Author: Dr. Merwan Roudane

echo ====================================
echo Composite Indicator Builder
echo by Dr. Merwan Roudane
echo ====================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher
    pause
    exit /b 1
)

REM Check if package is installed
python -c "import indicator" >nul 2>&1
if errorlevel 1 (
    echo Package not found. Installing...
    pip install -e .
    if errorlevel 1 (
        echo Installation failed!
        pause
        exit /b 1
    )
)

REM Launch the application
echo Launching application...
echo.
python -m indicator.gui

pause
