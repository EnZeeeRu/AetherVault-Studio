@echo off
setlocal EnableExtensions
title AetherVault Studio - Bootstrapper
cd /d "%~dp0"

set "PY_EXE="
set "PY_ARGS="

if exist "%~dp0.venv\Scripts\python.exe" (
    set "PY_EXE=%~dp0.venv\Scripts\python.exe"
    goto :run_bootstrapper
)

where py >nul 2>&1
if %errorlevel%==0 (
    for %%V in (-3.12 -3.11 -3.10 -3) do (
        py %%V -c "import sys; assert sys.version_info >= (3, 10)" >nul 2>&1
        if not errorlevel 1 (
            set "PY_EXE=py"
            set "PY_ARGS=%%V"
            goto :run_bootstrapper
        )
    )
)

where python >nul 2>&1
if %errorlevel%==0 (
    python -c "import sys; assert sys.version_info >= (3, 10)" >nul 2>&1
    if %errorlevel%==0 (
        set "PY_EXE=python"
        goto :run_bootstrapper
    )
)

echo =======================================================================
echo  [AETHERVAULT STUDIO BOOTSTRAPPER] Python 3.10+ was not found.
echo =======================================================================
where winget >nul 2>&1
if %errorlevel%==0 (
    set /p INSTALL_ANS="Install Python 3.11 automatically via winget? (Y/N): "
    if /I "%INSTALL_ANS%"=="Y" (
        winget install -e --id Python.Python.3.11 --accept-package-agreements --accept-source-agreements
        echo.
        echo Python installed! Close this window and double-click Launch.bat again.
        pause
        exit /b 0
    )
)
echo [HINT] Download Python 3.11+ from https://www.python.org/downloads/ (check "Add Python to PATH").
pause
exit /b 1

:run_bootstrapper
"%PY_EXE%" %PY_ARGS% "%~dp0manager.py" %*
set "EXIT_CODE=%errorlevel%"
if not "%EXIT_CODE%"=="0" (
    echo.
    echo [AETHERVAULT BOOTSTRAPPER] Exited with code %EXIT_CODE%.
    pause
)
exit /b %EXIT_CODE%
