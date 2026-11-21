@echo off
setlocal EnableDelayedExpansion
cd /d "%~dp0"

call :FindPython
if defined PY_CMD goto :RunManager

echo =======================================================================
echo  [AETHERVAULT STUDIO] Python 3.10+ was not found on this PC.
echo =======================================================================
set /p "INST_ANS=Download and install Python 3.11 automatically now? (Y/N): "
if /I not "%INST_ANS%"=="Y" (
    echo [ABORTED] Please install Python 3.11+ from https://www.python.org/downloads/
    pause
    exit /b 1
)

where winget >nul 2>&1
if %errorlevel%==0 (
    echo [STEP 1/2] Installing Python 3.11 via Windows Package Manager (winget)...
    winget install -e --id Python.Python.3.11 --scope user --accept-package-agreements --accept-source-agreements --disable-interactivity
    call :FindPython
    if defined PY_CMD goto :RunManager
)

echo [STEP 1/2] Downloading Official Python 3.11.9 Installer from python.org...
if not exist "%~dp0stock_vault" mkdir "%~dp0stock_vault"
set "PY_INST=%~dp0stock_vault\python-3.11.9-amd64.exe"
powershell -NoProfile -ExecutionPolicy Bypass -Command "[Net.ServicePointManager]::SecurityProtocol=[Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe' -OutFile '%PY_INST%'"
if exist "%PY_INST%" (
    echo [STEP 2/2] Running Python 3.11.9 passive installer...
    start /wait "" "%PY_INST%" /passive InstallAllUsers=0 PrependPath=1 Include_test=0
    call :FindPython
    if defined PY_CMD goto :RunManager
)

echo [ERROR] Could not verify Python installation automatically. Please restart terminal or install Python 3.11+.
pause
exit /b 1

:RunManager
%PY_CMD% "%~dp0manager.py" %*
if errorlevel 1 pause
endlocal
exit /b 0

:FindPython
set "PY_CMD="
if exist "%~dp0.venv\Scripts\python.exe" (
    set "PY_CMD="%~dp0.venv\Scripts\python.exe""
    exit /b 0
)
if exist "%LocalAppData%\Programs\Python\Python311\python.exe" (
    set "PY_CMD="%LocalAppData%\Programs\Python\Python311\python.exe""
    exit /b 0
)
if exist "%LocalAppData%\Programs\Python\Python312\python.exe" (
    set "PY_CMD="%LocalAppData%\Programs\Python\Python312\python.exe""
    exit /b 0
)
where py >nul 2>&1
if %errorlevel%==0 (
    py -3 -c "import sys" >nul 2>&1
    if %errorlevel%==0 (
        set "PY_CMD=py -3"
        exit /b 0
    )
)
where python >nul 2>&1
if %errorlevel%==0 (
    python -c "import sys" >nul 2>&1
    if %errorlevel%==0 (
        set "PY_CMD=python"
        exit /b 0
    )
)
exit /b 1
