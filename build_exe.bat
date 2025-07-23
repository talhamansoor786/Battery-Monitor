@echo off
echo ========================================
echo    Battery Monitor Build Script
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python from python.org
    pause
    exit /b 1
)

echo Installing required packages...
pip install psutil pystray pillow pyinstaller

REM Check if battery_monitor.py exists
if not exist "battery_monitor.py" (
    echo ERROR: battery_monitor.py not found in current directory
    echo Please make sure the Python script is in the same folder as this batch file
    pause
    exit /b 1
)

echo.
echo Building executable...
pyinstaller --onefile --noconsole --name "BatteryMonitor" battery_monitor.py

REM Check if build was successful
if exist "dist\BatteryMonitor.exe" (
    echo.
    echo ========================================
    echo       BUILD SUCCESSFUL!
    echo ========================================
    echo.
    echo Executable created: dist\BatteryMonitor.exe
    echo.
    
    REM Create Battery Alarm directory in dist
    if not exist "dist\Battery Alarm" mkdir "dist\Battery Alarm"
    
    REM Copy sound file if it exists
    if exist "Battery Alarm\siren-alert.wav" (
        copy "Battery Alarm\siren-alert.wav" "dist\Battery Alarm\"
        echo Sound file copied to dist\Battery Alarm\
    ) else (
        echo WARNING: Sound file not found at "Battery Alarm\siren-alert.wav"
        echo You can add it later or configure a different path in settings
    )
    
    echo.
    echo To run: Double-click dist\BatteryMonitor.exe
    echo The app will run in the system tray (notification area)
    echo.
    
) else (
    echo.
    echo BUILD FAILED!
    echo Check the error messages above
    echo.
)

REM Clean up build files
if exist "build" rmdir /s /q "build"
if exist "BatteryMonitor.spec" del "BatteryMonitor.spec"

echo.
pause