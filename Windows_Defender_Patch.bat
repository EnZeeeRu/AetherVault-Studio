@echo off
setlocal EnableDelayedExpansion
title AetherVault Studio v4.0 - Windows Defender Patch and Unstick Utility

cd /d "%~dp0"
set "ROOT_DIR=%~dp0"
if "%ROOT_DIR:~-1%"=="\" set "ROOT_DIR=%ROOT_DIR:~0,-1%"

echo =======================================================================
echo   AETHERVAULT STUDIO v4.0 - WINDOWS DEFENDER PATCH AND UNSTICK TOOL
echo   Fixes MsMpEng.exe GGUF Scan Freezes, SQLite Locks, and Stuck Port 8000
echo =======================================================================
echo.

:: Check for Administrator privileges; if not Admin, self-elevate via UAC
net session >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [INFO] Requesting Administrator privileges ^(UAC Prompt^) to register
    echo        Windows Defender exclusions for your AetherVault folder...
    powershell.exe -NoProfile -ExecutionPolicy Bypass -Command "Start-Process -FilePath '%~f0' -WorkingDirectory '%ROOT_DIR%' -Verb RunAs"
    exit /b 0
)

echo [STEP 1/5] Stopping any stuck or zombie Python / Port 8000 processes...
powershell.exe -NoProfile -ExecutionPolicy Bypass -Command ^
    "$procs = Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess -Unique; " ^
    "foreach ($p in $procs) { if ($p -gt 0) { Stop-Process -Id $p -Force -ErrorAction SilentlyContinue; Write-Host (' -> Freed port 8000 (PID ' + $p + ')') -ForegroundColor Yellow } }; " ^
    "Get-Process python -ErrorAction SilentlyContinue | Where-Object { $_.Path -like '*AetherVault*' -or $_.Path -like '*.venv*' } | Stop-Process -Force -ErrorAction SilentlyContinue"
echo  [OK] Port 8000 and local Python workers cleared.
echo.

echo [STEP 2/5] Clearing any stale SQLite database lock / journal files...
if exist "%ROOT_DIR%\memory_core.db-journal" del /f /q "%ROOT_DIR%\memory_core.db-journal" >nul 2>&1
if exist "%ROOT_DIR%\memory_core.db-wal" del /f /q "%ROOT_DIR%\memory_core.db-wal" >nul 2>&1
if exist "%ROOT_DIR%\memory_core.db-shm" del /f /q "%ROOT_DIR%\memory_core.db-shm" >nul 2>&1
echo  [OK] SQLite lock files cleared.
echo.

echo [STEP 3/5] Registering Windows Defender Exclusions (Stops MsMpEng.exe Freezes)...
powershell.exe -NoProfile -ExecutionPolicy Bypass -Command ^
    "$root = '%ROOT_DIR%'; " ^
    "$paths = @($root, (Join-Path $root 'models'), (Join-Path $root '.venv'), (Join-Path $root 'hf_cache'), (Join-Path $root 'pip_cache'), (Join-Path $root '.temp_cache')); " ^
    "foreach ($p in $paths) { " ^
    "  try { Add-MpPreference -ExclusionPath $p -ErrorAction Stop; Write-Host (' -> Excluded Folder : ' + $p) -ForegroundColor Green } " ^
    "  catch { Write-Host (' -> [Note] Could not exclude ' + $p + ': ' + $_.Exception.Message) -ForegroundColor Yellow } " ^
    "}; " ^
    "try { Add-MpPreference -ExclusionExtension @('gguf', 'onnx', 'bin', 'part', 'db', 'wal', 'shm') -ErrorAction Stop; Write-Host ' -> Excluded Extensions: .gguf, .onnx, .bin, .part, .db, .wal, .shm' -ForegroundColor Green } catch {}; " ^
    "$venvPy = Join-Path $root '.venv\Scripts\python.exe'; " ^
    "try { Add-MpPreference -ExclusionProcess $venvPy -ErrorAction Stop; Write-Host (' -> Excluded Process   : ' + $venvPy) -ForegroundColor Green } catch {}"
echo.

echo [STEP 4/5] Checking CPU Core Count and Legacy APU Safe Mode Flag...
if not exist "%ROOT_DIR%\.venv" mkdir "%ROOT_DIR%\.venv"
if %NUMBER_OF_PROCESSORS% LEQ 2 (
    echo cpu> "%ROOT_DIR%\.venv\engine_mode.flag"
    echo  [OK] Detected %NUMBER_OF_PROCESSORS%-thread CPU ^(e.g. AMD A9-9420^). Locked engine_mode.flag to SAFE CPU MODE
    echo       so legacy Radeon R5/R7 Vulkan drivers never hang during GGUF load!
) else (
    echo  [OK] Detected %NUMBER_OF_PROCESSORS%-thread CPU.
    set /p "FORCE_CPU=Lock engine to Safe CPU Mode anyway for maximum stability? (Y/N, default=N): "
    if /i "!FORCE_CPU!"=="Y" (
        echo cpu> "%ROOT_DIR%\.venv\engine_mode.flag"
        echo  [OK] Locked engine_mode.flag to SAFE CPU MODE.
    )
)
echo.

echo [STEP 5/5] Cleaning temporary session cache (.temp_cache)...
if exist "%ROOT_DIR%\.temp_cache" (
    rmdir /s /q "%ROOT_DIR%\.temp_cache" >nul 2>&1
)
mkdir "%ROOT_DIR%\.temp_cache" >nul 2>&1
echo  [OK] Local .temp_cache reset cleanly.
echo.
echo =======================================================================
echo  [PATCH COMPLETE] SQLite locks cleared and Windows Defender exclusions
echo  registered! You can now run Launch.bat normally.
echo =======================================================================
pause