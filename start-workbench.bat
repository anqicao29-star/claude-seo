@echo off
setlocal
cd /d "%~dp0"

where py >nul 2>nul
if %errorlevel%==0 (
  py -3 run_workbench.py
) else (
  where python >nul 2>nul
  if errorlevel 1 (
    echo Python 3 was not found. Install Python 3.10 or newer first.
    pause
    exit /b 1
  )
  python run_workbench.py
)

if errorlevel 1 pause
