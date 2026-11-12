@echo off
setlocal
cd /d "%~dp0"

where py >nul 2>nul
if %errorlevel%==0 (
  py -3 -c "import sys; raise SystemExit(0 if sys.version_info ^>= (3, 10) else 1)"
  if errorlevel 1 goto version_error
  py -3 run_workbench.py
) else (
  where python >nul 2>nul
  if errorlevel 1 (
    echo Python 3 was not found. Install Python 3.10 or newer first.
    pause
    exit /b 1
  )
  python -c "import sys; raise SystemExit(0 if sys.version_info ^>= (3, 10) else 1)"
  if errorlevel 1 goto version_error
  python run_workbench.py
)

set "WORKBENCH_STATUS=%errorlevel%"
if not "%WORKBENCH_STATUS%"=="0" pause
exit /b %WORKBENCH_STATUS%

:version_error
echo Python 3.10 or newer is required. Install a newer Python version, then start again.
pause
exit /b 1
