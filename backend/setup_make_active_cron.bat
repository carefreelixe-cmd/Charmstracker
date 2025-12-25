@echo off
REM Windows Task Scheduler setup for make_all_active.py
REM Run this script as Administrator to create a scheduled task

echo ================================================
echo Setting up Make All Charms Active Scheduled Task
echo ================================================
echo.
echo This will create a Windows scheduled task to run
echo make_all_active.py every 6 hours
echo.

set SCRIPT_DIR=%~dp0
set PYTHON_PATH=python
set SCRIPT_PATH=%SCRIPT_DIR%make_all_active.py
set TASK_NAME=CharmsTracker_MakeAllActive
set WORK_DIR=%SCRIPT_DIR%

REM Use system Python or check common locations
where python >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Python not found in PATH!
    echo Please install Python or add it to PATH
    pause
    exit /b 1
)

echo.
echo Task Details:
echo   Name: %TASK_NAME%
echo   Script: %SCRIPT_PATH%
echo   Python: %PYTHON_PATH%
echo   Schedule: Every 6 hours
echo.

REM Delete existing task if it exists
schtasks /Query /TN "%TASK_NAME%" >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo Found existing task. Deleting...
    schtasks /Delete /TN "%TASK_NAME%" /F
)

REM Create new scheduled task with working directory
echo Creating scheduled task...
schtasks /Create /TN "%TASK_NAME%" /TR "cmd /c cd /d \"%WORK_DIR%\" && python \"%SCRIPT_PATH%\"" /SC HOURLY /MO 6 /ST 00:00 /F

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ================================================
    echo SUCCESS! Scheduled task created.
    echo ================================================
    echo.
    echo The task will run every 6 hours starting at midnight.
    echo.
    echo To view the task:
    echo   schtasks /Query /TN "%TASK_NAME%" /V
    echo.
    echo To run manually:
    echo   schtasks /Run /TN "%TASK_NAME%"
    echo.
    echo To delete the task:
    echo   schtasks /Delete /TN "%TASK_NAME%" /F
    echo.
) else (
    echo.
    echo ERROR: Failed to create scheduled task!
    echo Make sure you run this script as Administrator.
    echo.
)

pause
