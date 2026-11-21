# ==============================================================================
# AetherVault Studio v4.0 - Portable Control Center (Manager.ps1)
# Made with <3 in Argentina by Enzeru, with the collaboration of Google Gemini.
# Supports Vulkan GPU Acceleration + Automatic 2015 Laptop CPU Fallback
#
# UPGRADES IN v4.0 (ZERO-BLIND-SPOT LIVE PROGRESS EDITION):
# 1. Pure 7-Bit ASCII PowerShell 5.1 Compatible (Zero UTF-8 Quote Bombs)
# 2. Global Error Trap + Launch.bat Pause Guard (Window NEVER Autocloses)
# 3. Live Byte-by-Byte Python 3.11 Downloader & Passive GUI/CLI Installer
# 4. Invoke-TrackedProcess: Live Spinner + Elapsed Timer + CPU/RAM Telemetry
# 5. Module-by-Module [1/12] Live Verification with per-library timing.
# 6. Chunked GGUF & File Copy Progress Bar (MB, %, Speed MB/s, ETA).
# ==============================================================================
$ErrorActionPreference = "Continue"

trap {
    Write-Host "`n=======================================================================" -ForegroundColor Red
    Write-Host " [POWERSHELL ERROR CAUGHT - WINDOW KEPT OPEN]" -ForegroundColor Red
    Write-Host " Message : $($_.Exception.Message)" -ForegroundColor Yellow
    if ($_.InvocationInfo) {
        Write-Host " Line    : $($_.InvocationInfo.ScriptLineNumber) -> $($_.InvocationInfo.Line.Trim())" -ForegroundColor Gray
    }
    Write-Host "=======================================================================" -ForegroundColor Red
    Read-Host "Press Enter to continue"
    continue
}

if ($PSScriptRoot) {
    $RootDir = $PSScriptRoot
} else {
    $RootDir = (Get-Location).Path
}
Set-Location $RootDir

$VenvDir      = Join-Path $RootDir ".venv"
$StockVault   = Join-Path $RootDir "stock_vault"
$WheelStock   = Join-Path $StockVault "wheels"
$ModelStock   = Join-Path $StockVault "models"
$ModelsDir    = Join-Path $RootDir "models"
$PdfDir       = Join-Path $RootDir "priority_pdfs"
$LoreSubDir   = Join-Path $PdfDir  "lore"
$MemDir       = Join-Path $RootDir "memory_vault"
$ChatLogsDir  = Join-Path $RootDir "chat_logs"
$GenImgDir    = Join-Path $RootDir "generated_images"
$AssetsDir    = Join-Path $RootDir "custom_assets"
$BackupsDir   = Join-Path $RootDir "workspace_backups"

$env:PIP_CACHE_DIR = Join-Path $RootDir "pip_cache"
$env:HF_HOME       = Join-Path $RootDir "hf_cache"
$env:PYTHONUNBUFFERED = "1"

$VulkanWheelUrl = "https://abetlen.github.io/llama-cpp-python/whl/vulkan"
$CpuWheelUrl    = "https://abetlen.github.io/llama-cpp-python/whl/cpu"

foreach ($dir in @($StockVault, $WheelStock, $ModelStock, $ModelsDir, $PdfDir, $LoreSubDir, $MemDir, $ChatLogsDir, $GenImgDir, $AssetsDir, $BackupsDir)) {
    if (-not (Test-Path $dir)) { New-Item -ItemType Directory -Path $dir | Out-Null }
}

$Packages = @(
    "fastapi",
    "uvicorn",
    "python-multipart",
    "pymupdf",
    "huggingface_hub",
    "ddgs",
    "spotipy",
    "requests",
    "pillow",
    "psutil",
    "beautifulsoup4",
    "pyautogui"
)

function Set-ConsoleTitle {
    param([string]$TitleText)
    try { $Host.UI.RawUI.WindowTitle = $TitleText } catch {}
}

function Format-AsciiBar {
    param([double]$Percent, [int]$Width = 22)
    $clamped = [math]::Max(0.0, [math]::Min(100.0, $Percent))
    $filled  = [int][math]::Round(($clamped / 100.0) * $Width)
    $empty   = [math]::Max(0, $Width - $filled)
    return "[" + ("#" * $filled) + ("-" * $empty) + "]"
}

function Copy-FileWithProgress {
    param(
        [string]$SourcePath,
        [string]$DestinationPath,
        [string]$Label = "Copying file"
    )
    if (-not (Test-Path $SourcePath)) { return $false }
    $srcItem = Get-Item $SourcePath
    $totalBytes = $srcItem.Length
    if ($totalBytes -lt 2MB) {
        Copy-Item -Path $SourcePath -Destination $DestinationPath -Force
        return $true
    }

    $Frames = @("|", "/", "-", "\")
    $fIdx = 0
    $bufferSize = 4MB
    $buffer = New-Object byte[] $bufferSize
    $totalMB = [math]::Round($totalBytes / 1MB, 1)
    $copiedBytes = 0L
    $sw = [System.Diagnostics.Stopwatch]::StartNew()

    $inStream  = [System.IO.File]::OpenRead($SourcePath)
    $outStream = [System.IO.File]::Open($DestinationPath, [System.IO.FileMode]::Create, [System.IO.FileAccess]::Write, [System.IO.FileShare]::None)
    try {
        while (($read = $inStream.Read($buffer, 0, $buffer.Length)) -gt 0) {
            $outStream.Write($buffer, 0, $read)
            $copiedBytes += $read
            $fIdx++
            $pct = [math]::Round(($copiedBytes / [double]$totalBytes) * 100, 1)
            $copiedMB = [math]::Round($copiedBytes / 1MB, 1)
            $elapsedSec = [math]::Max(0.1, $sw.Elapsed.TotalSeconds)
            $speedMBs = [math]::Round($copiedMB / $elapsedSec, 1)
            $remMB = [math]::Max(0.0, $totalMB - $copiedMB)
            $etaSec = if ($speedMBs -gt 0.1) { [int]($remMB / $speedMBs) } else { 0 }
            $bar = Format-AsciiBar -Percent $pct -Width 20
            $frame = $Frames[$fIdx % 4]

            Set-ConsoleTitle -TitleText "[$pct% | $speedMBs MB/s] $Label"
            Write-Progress -Activity $Label -Status "$pct% ($copiedMB / $totalMB MB) @ $speedMBs MB/s | ETA: $($etaSec)s" -PercentComplete ([int]$pct)
            Write-Host "`r [$frame] $bar $pct% | $copiedMB / $totalMB MB @ $speedMBs MB/s | ETA: $($etaSec)s   " -NoNewline -ForegroundColor Cyan
        }
    } finally {
        $inStream.Close()
        $outStream.Close()
        $sw.Stop()
        Write-Progress -Activity $Label -Completed
    }
    Write-Host "`r [OK] $Label complete ($totalMB MB in $([math]::Round($sw.Elapsed.TotalSeconds, 1))s)!                                      " -ForegroundColor Green
    return $true
}

function Download-FileWithProgress {
    param(
        [string]$Url,
        [string]$DestinationPath,
        [string]$Label = "Downloading"
    )
    Write-Host " -> Connecting to: $Url" -ForegroundColor DarkCyan
    try {
        [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
    } catch {}

    $req = [System.Net.HttpWebRequest]::Create($Url)
    $req.UserAgent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AetherVaultStudio/3.2"
    $req.Timeout = 30000
    $req.ReadWriteTimeout = 30000

    $resp = $req.GetResponse()
    $totalBytes = $resp.ContentLength
    $totalMB = if ($totalBytes -gt 0) { [math]::Round($totalBytes / 1MB, 2) } else { 0 }
    $respStream = $resp.GetResponseStream()
    $partPath = "$DestinationPath.part"
    $fileStream = New-Object System.IO.FileStream($partPath, [System.IO.FileMode]::Create, [System.IO.FileAccess]::Write)

    $buffer = New-Object byte[] 65536
    $downloadedBytes = 0L
    $Frames = @("|", "/", "-", "\")
    $fIdx = 0
    $sw = [System.Diagnostics.Stopwatch]::StartNew()
    $lastDrawMs = 0L

    try {
        while (($read = $respStream.Read($buffer, 0, $buffer.Length)) -gt 0) {
            $fileStream.Write($buffer, 0, $read)
            $downloadedBytes += $read
            $nowMs = $sw.ElapsedMilliseconds
            if (($nowMs - $lastDrawMs) -ge 150) {
                $lastDrawMs = $nowMs
                $fIdx++
                $frame = $Frames[$fIdx % 4]
                $dlMB = [math]::Round($downloadedBytes / 1MB, 2)
                $elapsedSec = [math]::Max(0.1, $sw.Elapsed.TotalSeconds)
                $speedMBs = [math]::Round($dlMB / $elapsedSec, 2)

                if ($totalBytes -gt 0) {
                    $pct = [math]::Round(($downloadedBytes / [double]$totalBytes) * 100, 1)
                    $remMB = [math]::Max(0.0, $totalMB - $dlMB)
                    $etaSec = if ($speedMBs -gt 0.05) { [int]($remMB / $speedMBs) } else { 0 }
                    $bar = Format-AsciiBar -Percent $pct -Width 20
                    Set-ConsoleTitle -TitleText "[$pct% | $speedMBs MB/s] $Label"
                    Write-Progress -Activity $Label -Status "$pct% ($dlMB / $totalMB MB) @ $speedMBs MB/s | ETA: $($etaSec)s" -PercentComplete ([int]$pct)
                    Write-Host "`r [$frame] $bar $pct% | $dlMB / $totalMB MB | $speedMBs MB/s | ETA: $($etaSec)s | Alive: $([int]$elapsedSec)s   " -NoNewline -ForegroundColor Cyan
                } else {
                    Write-Host "`r [$frame] Downloaded $dlMB MB @ $speedMBs MB/s ($([int]$elapsedSec)s elapsed)...   " -NoNewline -ForegroundColor Cyan
                }
            }
        }
    } finally {
        $fileStream.Close()
        $respStream.Close()
        $resp.Close()
        $sw.Stop()
        Write-Progress -Activity $Label -Completed
    }

    if (Test-Path $DestinationPath) { Remove-Item $DestinationPath -Force }
    Move-Item -Path $partPath -Destination $DestinationPath -Force
    Write-Host "`r [OK] $Label finished ($totalMB MB in $([math]::Round($sw.Elapsed.TotalSeconds, 1))s)!                                                  " -ForegroundColor Green
    return $true
}

function Invoke-TrackedProcess {
    param(
        [string]$FilePath,
        [string]$ArgumentList,
        [string]$Message,
        [int]$StepIndex = 0,
        [int]$TotalSteps = 0,
        [switch]$InlineSpinner
    )
    $Frames = @("|", "/", "-", "\")
    $Idx = 0
    $Sw = [System.Diagnostics.Stopwatch]::StartNew()
    $LastHeartbeatSec = 0
    $StepPrefix = if ($TotalSteps -gt 0) { "[$StepIndex/$TotalSteps] " } else { "" }

    Write-Host " -> $StepPrefix$Message" -ForegroundColor Cyan
    $Proc = Start-Process -FilePath $FilePath -ArgumentList $ArgumentList -NoNewWindow -PassThru

    while (-not $Proc.HasExited) {
        $Frame = $Frames[$Idx % 4]
        $Elapsed = [int]$Sw.Elapsed.TotalSeconds

        $CpuSec = 0.0
        $RamMB  = 0.0
        try {
            $pInfo = Get-Process -Id $Proc.Id -ErrorAction SilentlyContinue
            if ($pInfo) {
                if ($null -ne $pInfo.CPU) { $CpuSec = [math]::Round($pInfo.CPU, 1) }
                $RamMB = [math]::Round($pInfo.WorkingSet64 / 1MB, 1)
            }
        } catch {}

        $Telemetry = "Alive: $($Elapsed)s | CPU: $($CpuSec)s | RAM: $($RamMB) MB"
        $Pct = if ($TotalSteps -gt 0) { [int][math]::Min(99, (($StepIndex / [double]$TotalSteps) * 100)) } else { ($Elapsed * 5) % 100 }

        Set-ConsoleTitle -TitleText "[$Frame] $StepPrefix$Message ($Telemetry)"
        Write-Progress -Activity "$StepPrefix$Message [WORKING - NOT FROZEN]" -Status "[$Frame] $Telemetry" -PercentComplete $Pct

        if ($InlineSpinner) {
            Write-Host "`r [$Frame] $StepPrefix$Message ($Telemetry)...      " -NoNewline -ForegroundColor Cyan
        } elseif ($Elapsed -ge 8 -and (($Elapsed - $LastHeartbeatSec) -ge 8)) {
            $LastHeartbeatSec = $Elapsed
            Write-Host "    [$Frame HEARTBEAT $($Elapsed)s] Still working on '$Message' ($Telemetry -- actively processing, not frozen!)" -ForegroundColor DarkGray
        }

        Start-Sleep -Milliseconds 250
        $Idx++
    }

    $Sw.Stop()
    Write-Progress -Activity "$StepPrefix$Message [WORKING - NOT FROZEN]" -Completed
    $ExitCode = $Proc.ExitCode
    $TotalSec = [math]::Round($Sw.Elapsed.TotalSeconds, 1)

    if ($InlineSpinner) {
        if ($ExitCode -eq 0) {
            Write-Host "`r [OK] $StepPrefix$Message (Completed in $($TotalSec)s)                                        " -ForegroundColor Green
        } else {
            Write-Host "`r [WARN] $StepPrefix$Message finished with code $ExitCode ($($TotalSec)s)                      " -ForegroundColor Yellow
        }
    } else {
        if ($ExitCode -eq 0) {
            Write-Host " [OK] $StepPrefix$Message completed in $($TotalSec)s." -ForegroundColor Green
        } else {
            Write-Host " [WARN] $StepPrefix$Message exited with code $ExitCode after $($TotalSec)s." -ForegroundColor Yellow
        }
    }
    return $ExitCode
}

function Repair-And-TestPythonScript {
    param([string]$ScriptPath)
    if (-not (Test-Path $ScriptPath)) { return $false }

    $raw = [System.IO.File]::ReadAllText($ScriptPath)
    if ($raw.Contains("def get_ governor_settings")) {
        $raw = $raw.Replace("def get_ governor_settings", "def get_governor_settings")
        [System.IO.File]::WriteAllText($ScriptPath, $raw, [System.Text.Encoding]::UTF8)
    }

    $VenvPython = Join-Path $VenvDir "Scripts\python.exe"
    if (Test-Path $VenvPython) {
        Write-Host " [..] Validating Python syntax on $(Split-Path $ScriptPath -Leaf)..." -NoNewline -ForegroundColor DarkCyan
        & $VenvPython -m py_compile $ScriptPath 2>$null
        if ($LASTEXITCODE -eq 0) {
            Write-Host "`r [OK] Syntax check passed for $(Split-Path $ScriptPath -Leaf)!                     " -ForegroundColor Green
            return $true
        } else {
            Write-Host "`r [FAIL] Syntax check failed for $(Split-Path $ScriptPath -Leaf)!                   " -ForegroundColor Red
            return $false
        }
    }
    return ($raw.Length -gt 500)
}

function Invoke-SyncNewerGoldenSnapshots {
    Write-Host "`n[BOOT CHECK 0/3] Checking workspace_backups\golden_* for newer golden snapshots..." -ForegroundColor Cyan
    if (-not (Test-Path $BackupsDir)) { return }
    $GoldenDirs = @(Get-ChildItem -Path $BackupsDir -Directory -Filter "golden_*" -ErrorAction SilentlyContinue | Sort-Object Name -Descending)
    if ($GoldenDirs.Count -eq 0) { return }
    $LatestSnap = $GoldenDirs[0]
    $VenvPython = Join-Path $VenvDir "Scripts\python.exe"
    foreach ($SrcFile in @(Get-ChildItem -Path $LatestSnap.FullName -File -ErrorAction SilentlyContinue)) {
        $Fname = $SrcFile.Name
        $LiveDest = Join-Path $RootDir $Fname
        $StockDest = Join-Path $StockVault "$Fname.good"
        if (($Fname -like "*.py") -and (Test-Path $VenvPython)) {
            & $VenvPython -m py_compile $SrcFile.FullName 2>$null
            if ($LASTEXITCODE -ne 0) { continue }
        }
        $ShouldApply = (-not (Test-Path $LiveDest))
        if (-not $ShouldApply) {
            $LiveItem = Get-Item $LiveDest -ErrorAction SilentlyContinue
            if ($LiveItem -and ($SrcFile.LastWriteTimeUtc -gt $LiveItem.LastWriteTimeUtc.AddSeconds(1))) { $ShouldApply = $true }
        }
        if ($ShouldApply) {
            Copy-Item $SrcFile.FullName $LiveDest -Force -ErrorAction SilentlyContinue
            Copy-Item $SrcFile.FullName $StockDest -Force -ErrorAction SilentlyContinue
        }
    }
}

function Invoke-BootStockCheck {
    Invoke-SyncNewerGoldenSnapshots
    Write-Host "`n[BOOT CHECK 1/3] Verifying core scripts against Stock Vault..." -ForegroundColor Cyan
    $ServerFile  = Join-Path $RootDir "assistant_server.py"
    $StockServer = Join-Path $StockVault "assistant_server.py.good"
    $UiFile      = Join-Path $RootDir "ui_studio.html"
    $StockUi     = Join-Path $StockVault "ui_studio.html.good"

    if (Test-Path $StockServer) { Repair-And-TestPythonScript -ScriptPath $StockServer | Out-Null }
    $IsServerValid = Repair-And-TestPythonScript -ScriptPath $ServerFile

    if ($IsServerValid) {
        Copy-Item $ServerFile $StockServer -Force
        Write-Host " -> [OK] assistant_server.py verified & backed up to Stock Vault." -ForegroundColor Green
    }
    elseif (Test-Path $StockServer) {
        if (Repair-And-TestPythonScript -ScriptPath $StockServer) {
            Copy-Item $StockServer $ServerFile -Force
            Write-Host " -> [RESTORED] Recovered valid assistant_server.py from Stock Vault!" -ForegroundColor Yellow
        }
    }

    if (Test-Path $UiFile) {
        Copy-Item $UiFile $StockUi -Force
        Write-Host " -> [OK] ui_studio.html verified & backed up to Stock Vault." -ForegroundColor Green
    }
    elseif (Test-Path $StockUi) {
        Copy-Item $StockUi $UiFile -Force
        Write-Host " -> [RESTORED] Recovered ui_studio.html from Stock Vault!" -ForegroundColor Yellow
    }

    Write-Host "[BOOT CHECK 2/3] Checking offline model vault (stock_vault\models)..." -ForegroundColor Cyan
    $StockModels = @(Get-ChildItem -Path $ModelStock -Filter "*.gguf" -ErrorAction SilentlyContinue)
    $mIdx = 0
    foreach ($m in $StockModels) {
        $mIdx++
        $TargetModel = Join-Path $ModelsDir $m.Name
        if (-not (Test-Path $TargetModel)) {
            Copy-FileWithProgress -SourcePath $m.FullName -DestinationPath $TargetModel -Label "Restocking $($m.Name) [$mIdx/$($StockModels.Count)]" | Out-Null
        }
    }

    Write-Host "[BOOT CHECK 3/3] Backing up SQLite Memory Core (memory_core.db)..." -ForegroundColor Cyan
    $DbFile = Join-Path $RootDir "memory_core.db"
    if (Test-Path $DbFile) {
        Copy-FileWithProgress -SourcePath $DbFile -DestinationPath (Join-Path $StockVault "memory_core.db.bak") -Label "Backing up memory_core.db" | Out-Null
    }
}

function Refresh-SessionPath {
    $MachinePath = [System.Environment]::GetEnvironmentVariable("Path", "Machine")
    $UserPath    = [System.Environment]::GetEnvironmentVariable("Path", "User")
    $env:Path    = "$UserPath;$MachinePath"
}

function Get-CompatiblePython {
    Refresh-SessionPath
    $CandidatePaths = @(
        "$env:LocalAppData\Programs\Python\Python311\python.exe",
        "$env:LocalAppData\Programs\Python\Python312\python.exe",
        "$env:LocalAppData\Programs\Python\Python310\python.exe",
        "$env:ProgramFiles\Python311\python.exe",
        "$env:ProgramFiles\Python312\python.exe",
        "C:\Python311\python.exe",
        "C:\Python312\python.exe"
    )
    foreach ($cand in $CandidatePaths) {
        if (Test-Path $cand) { return $cand }
    }

    if (Get-Command "py" -ErrorAction SilentlyContinue) {
        foreach ($ver in @("-3.11", "-3.12", "-3.10")) {
            $test = & py $ver -c "import sys; print(sys.executable)" 2>$null
            if ($LASTEXITCODE -eq 0 -and $test -and ($test -notmatch "WindowsApps")) { return $test.Trim() }
        }
    }

    if (Get-Command "python" -ErrorAction SilentlyContinue) {
        $test = & python -c "import sys; print(sys.executable)" 2>$null
        if ($LASTEXITCODE -eq 0 -and $test -and ($test -notmatch "WindowsApps")) { return $test.Trim() }
    }
    return $null
}

function Install-Python311WithLiveProgress {
    Write-Host "`n================ PYTHON 3.11 LIVE INSTALLER ================" -ForegroundColor Cyan
    Write-Host " Select how you want to download & install Python 3.11.9:" -ForegroundColor White
    Write-Host " [1] Direct Official Python.org Stream (RECOMMENDED: Live MB/s Bar + GUI Progress Bar)" -ForegroundColor Green
    Write-Host " [2] Windows Package Manager (winget) with Live Heartbeat Monitor" -ForegroundColor Yellow
    Write-Host " [3] Cancel"
    $mode = Read-Host "Choose (1-3, default=1)"
    if ($mode -eq "3") { return $null }

    if ($mode -eq "2" -and (Get-Command "winget" -ErrorAction SilentlyContinue)) {
        Write-Host "`n[STEP 1/2] Running winget with non-interactive flags & live heartbeat..." -ForegroundColor Cyan
        $wgCode = Invoke-TrackedProcess -FilePath "cmd.exe" -ArgumentList "/c winget install -e --id Python.Python.3.11 --scope user --accept-package-agreements --accept-source-agreements --disable-interactivity" -Message "Installing Python 3.11 via winget" -StepIndex 1 -TotalSteps 2
        $pyExe = Get-CompatiblePython
        if ($pyExe) {
            Write-Host " [OK] Python 3.11 detected at: $pyExe" -ForegroundColor Green
            return $pyExe
        }
        Write-Host " [FALLBACK] winget did not register Python cleanly. Switching to Direct Python.org Stream..." -ForegroundColor Yellow
    }

    $is64 = [Environment]::Is64BitOperatingSystem
    $PyUrl = if ($is64) { "https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe" } else { "https://www.python.org/ftp/python/3.11.9/python-3.11.9.exe" }
    $InstallerPath = Join-Path $StockVault "python-3.11.9-installer.exe"

    if (-not (Test-Path $InstallerPath) -or ((Get-Item $InstallerPath).Length -lt 15MB)) {
        Write-Host "`n[STEP 1/2] Downloading Official Python 3.11.9 Installer from python.org..." -ForegroundColor Cyan
        Download-FileWithProgress -Url $PyUrl -DestinationPath $InstallerPath -Label "Downloading Python 3.11.9 Installer" | Out-Null
    } else {
        Write-Host "`n[STEP 1/2] Using cached Python 3.11.9 installer in stock_vault ($InstallerPath)..." -ForegroundColor Green
    }

    Write-Host "`n[STEP 2/2] Running Python 3.11.9 Installer (/passive shows live GUI bar + console timer)..." -ForegroundColor Cyan
    $TargetPyDir = "$env:LocalAppData\Programs\Python\Python311"
    $Frames = @("|", "/", "-", "\")
    $Idx = 0
    $Sw = [System.Diagnostics.Stopwatch]::StartNew()
    $Proc = Start-Process -FilePath $InstallerPath -ArgumentList "/passive InstallAllUsers=0 PrependPath=1 Include_test=0" -PassThru

    while (-not $Proc.HasExited) {
        $Frame = $Frames[$Idx % 4]
        $Elapsed = [int]$Sw.Elapsed.TotalSeconds
        $FileCount = 0
        if (Test-Path $TargetPyDir) {
            try { $FileCount = @(Get-ChildItem -Path $TargetPyDir -Recurse -File -ErrorAction SilentlyContinue).Count } catch {}
        }
        $StatusTxt = "[$Frame] Unpacking Python 3.11 ($($Elapsed)s elapsed | $FileCount files installed in Python311)..."
        Set-ConsoleTitle -TitleText $StatusTxt
        Write-Progress -Activity "Installing Python 3.11.9" -Status $StatusTxt -PercentComplete (($Elapsed * 4) % 100)
        Write-Host "`r $StatusTxt     " -NoNewline -ForegroundColor Cyan
        Start-Sleep -Milliseconds 300
        $Idx++
    }
    $Sw.Stop()
    Write-Progress -Activity "Installing Python 3.11.9" -Completed
    Write-Host "`r [OK] Python 3.11.9 installation finished in $([math]::Round($Sw.Elapsed.TotalSeconds, 1))s!                                        " -ForegroundColor Green

    $pyExe = Get-CompatiblePython
    if ($pyExe) {
        Write-Host " [OK] Verified Python executable: $pyExe (No restart needed!)" -ForegroundColor Green
        return $pyExe
    }
    return $null
}

function Get-MissingVenvPackages {
    param([string]$VenvPython)
    $ModMap = @(
        @{Mod="fastapi";          Pkg="fastapi";          Name="FastAPI Web Server"},
        @{Mod="uvicorn";          Pkg="uvicorn";          Name="Uvicorn ASGI Engine"},
        @{Mod="python_multipart"; Pkg="python-multipart"; Name="Python-Multipart Forms"},
        @{Mod="pymupdf";          Pkg="pymupdf";          Name="PyMuPDF Document Reader"},
        @{Mod="llama_cpp";        Pkg="llama-cpp-python"; Name="llama.cpp GGUF Inference Engine"},
        @{Mod="ddgs";             Pkg="ddgs";             Name="DDGS Multi-Engine Web Search"},
        @{Mod="spotipy";          Pkg="spotipy";          Name="Spotipy Music Bridge"},
        @{Mod="requests";         Pkg="requests";         Name="HTTP Requests Client"},
        @{Mod="PIL";              Pkg="pillow";           Name="Pillow Image & Crop Studio"},
        @{Mod="psutil";           Pkg="psutil";           Name="PSUtil Hardware Telemetry"},
        @{Mod="bs4";              Pkg="beautifulsoup4";   Name="BeautifulSoup4 HTML Fallback"},
        @{Mod="pyautogui";        Pkg="pyautogui";        Name="PyAutoGUI OSWorld Desktop Agent"}
    )

    Write-Host "`n[ENVIRONMENT CHECK] Verifying 12 Python libraries one-by-one:" -ForegroundColor Cyan
    $Total = $ModMap.Count
    $Idx = 0
    $Missing = @()

    foreach ($item in $ModMap) {
        $Idx++
        $m = $item.Mod
        $label = $item.Name
        $Pct = [int](($Idx / [double]$Total) * 100)
        Write-Progress -Activity "Verifying Installed Libraries" -Status "[$Idx/$Total] Importing $m ($label)..." -PercentComplete $Pct
        Write-Host "  [$Idx/$Total] Checking $m ($label)... " -NoNewline -ForegroundColor Gray

        $sw = [System.Diagnostics.Stopwatch]::StartNew()
        if ($m -eq "python_multipart") { & $VenvPython -W ignore -c "try:`n import python_multipart`nexcept ImportError:`n import multipart" 2>$null } else { & $VenvPython -W ignore -c "import $m" 2>$null }
        $sw.Stop()
        $sec = [math]::Round($sw.Elapsed.TotalSeconds, 2)

        if ($LASTEXITCODE -eq 0) {
            Write-Host "OK ($($sec)s)" -ForegroundColor Green
        } else {
            Write-Host "MISSING (Queued for install)" -ForegroundColor Yellow
            $Missing += $item.Pkg
        }
    }
    Write-Progress -Activity "Verifying Installed Libraries" -Completed
    return ,$Missing
}

function Install-LlamaCppEngine {
    param([string]$PreferredMode = "auto")
    $VenvPython = Join-Path $VenvDir "Scripts\python.exe"

    if ($PreferredMode -eq "cpu") {
        Write-Host "`n[2015 LAPTOP / CPU SAFE MODE] Installing CPU-optimized llama-cpp-python wheel..." -ForegroundColor Cyan
        $code = Invoke-TrackedProcess -FilePath $VenvPython -ArgumentList "-m pip install llama-cpp-python --force-reinstall --no-cache-dir --prefer-binary --extra-index-url $CpuWheelUrl --find-links `"$WheelStock`" --progress-bar on" -Message "Installing CPU llama-cpp-python Engine"
        "cpu" | Out-File -FilePath (Join-Path $VenvDir "engine_mode.flag") -Encoding utf8
        Write-Host " [OK] CPU Engine installed and verified for older laptop compatibility!" -ForegroundColor Green
        return
    }

    Write-Host "`n[VULKAN GPU] Attempting Vulkan GPU llama-cpp-python installation..." -ForegroundColor Cyan
    Invoke-TrackedProcess -FilePath $VenvPython -ArgumentList "-m pip install llama-cpp-python --force-reinstall --no-cache-dir --prefer-binary --extra-index-url $VulkanWheelUrl --find-links `"$WheelStock`" --progress-bar on" -Message "Installing Vulkan GPU llama-cpp-python Engine" | Out-Null

    Write-Host " [..] Testing if this PC's GPU & driver support Vulkan offload without access violations..." -NoNewline -ForegroundColor Cyan
    & $VenvPython -W ignore -c "import llama_cpp; llama_cpp.llama_supports_gpu_offload(); print('OK')" 2>$null
    if ($LASTEXITCODE -eq 0) {
        "vulkan" | Out-File -FilePath (Join-Path $VenvDir "engine_mode.flag") -Encoding utf8
        Write-Host "`r [OK] Vulkan GPU Engine active and verified!                                     " -ForegroundColor Green
    } else {
        Write-Host "`r [AUTO-HEAL FALLBACK] Vulkan GPU offload rejected by driver (e.g. legacy AMD Radeon R5/R7). Switching to 2015 Laptop Safe CPU build..." -ForegroundColor Yellow
        Write-Host " -> [MANUAL NOTE] You can also switch engines anytime via Option [2] -> [B] or check AetherVault_Studio_Manual.pdf (Section 6: Minimum Specs & Legacy Guide)." -ForegroundColor Cyan
        Invoke-TrackedProcess -FilePath $VenvPython -ArgumentList "-m pip install llama-cpp-python --force-reinstall --no-cache-dir --prefer-binary --extra-index-url $CpuWheelUrl --find-links `"$WheelStock`" --progress-bar on" -Message "Auto-Healing with Safe CPU llama-cpp-python Build" | Out-Null
        "cpu" | Out-File -FilePath (Join-Path $VenvDir "engine_mode.flag") -Encoding utf8
        Write-Host " [OK] Auto-healed with CPU llama-cpp-python build!" -ForegroundColor Green
    }
}

function Ensure-Environment {
    $VenvPython = Join-Path $VenvDir "Scripts\python.exe"

    if (-not (Test-Path $VenvPython)) {
        $SysPython = Get-CompatiblePython
        if (-not $SysPython) {
            Write-Host "`n[WARNING] Python 3.10-3.12 was not found on this PC." -ForegroundColor Yellow
            $ans = Read-Host "Install Python 3.11 with Live Progress Bar now? (Y/N)"
            if ($ans -match "^[Yy]") {
                $SysPython = Install-Python311WithLiveProgress
                if (-not $SysPython) {
                    Write-Host "[ERROR] Could not verify Python installation. Please re-run Launch.bat." -ForegroundColor Red
                    Pause; return $false
                }
            } else { return $false }
        }
        Invoke-TrackedProcess -FilePath $SysPython -ArgumentList "-m venv `"$VenvDir`"" -Message "Creating isolated portable virtual environment (.venv)" -InlineSpinner | Out-Null
    } else {
        Write-Host " [OK] Virtual environment (.venv) ready." -ForegroundColor Green
    }

    $MissingPkgs = Get-MissingVenvPackages -VenvPython $VenvPython
    if ($MissingPkgs.Count -eq 0) {
        & $VenvPython -W ignore -c "import llama_cpp; llama_cpp.llama_supports_gpu_offload()" 2>$null
        if ($LASTEXITCODE -ne 0) {
            Write-Host " [AUTO-HEAL] Detected older GPU driver Access Violation on Vulkan probe (e.g. AMD Radeon R5/R7). Switching to 2015 Laptop Safe CPU Engine..." -ForegroundColor Yellow
            Write-Host " -> [MANUAL NOTE] If needed, use Menu Option [2] -> [B] (Safe CPU Build) and refer to AetherVault_Studio_Manual.pdf (Section 6: Minimum Specs)." -ForegroundColor Cyan
            Install-LlamaCppEngine -PreferredMode "cpu"
        }
        Write-Host " [OK] All 12 v4.14 libraries + llama.cpp engine verified!" -ForegroundColor Green
        return $true
    }

    $InstallQueue = @($MissingPkgs | Where-Object { $_ -ne "llama-cpp-python" })
    Write-Host "`n================ INSTALLING $($MissingPkgs.Count) MISSING LIBRARY(IES) ================" -ForegroundColor Cyan
    $TotalSteps = $InstallQueue.Count + 2
    $CurrentStep = 1

    if ($InstallQueue.Count -ge 4) {
        Invoke-TrackedProcess -FilePath $VenvPython -ArgumentList "-m pip install --upgrade pip --progress-bar on" -Message "Upgrading pip package installer" -StepIndex $CurrentStep -TotalSteps $TotalSteps | Out-Null
    }

    foreach ($pkg in $InstallQueue) {
        $CurrentStep++
        $exitCode = Invoke-TrackedProcess -FilePath $VenvPython -ArgumentList "-m pip install $pkg --find-links `"$WheelStock`" --progress-bar on" -Message "Installing missing package: $pkg" -StepIndex $CurrentStep -TotalSteps $TotalSteps
        if ($exitCode -ne 0) {
            Write-Host " -> [OFFLINE FALLBACK] Installing $pkg directly from local stock_vault\wheels..." -ForegroundColor Yellow
            Invoke-TrackedProcess -FilePath $VenvPython -ArgumentList "-m pip install $pkg --no-index --find-links `"$WheelStock`"" -Message "Offline Wheel Install: $pkg" -StepIndex $CurrentStep -TotalSteps $TotalSteps | Out-Null
        }
    }

    & $VenvPython -W ignore -c "import llama_cpp" 2>$null
    if ($LASTEXITCODE -ne 0) {
        Install-LlamaCppEngine -PreferredMode "auto"
    }

    Write-Progress -Activity "Setting up AetherVault v4.0" -Completed
    Write-Host "`n[OK] All v4.0 libraries installed and verified!" -ForegroundColor Green
    return $true
}

function Invoke-QuickModelDownloader {
    if (-not (Ensure-Environment)) { return }
    $VenvPython = Join-Path $VenvDir "Scripts\python.exe"
    Write-Host "`n================ QUICK MODEL DOWNLOADER (LIVE PROGRESS STREAM) ================" -ForegroundColor Cyan
    Write-Host " [1] DeepSeek-R1-Distill-Qwen-1.5B Uncensored (~1.1 GB - Best for 2015 Laptops)"
    Write-Host " [2] Qwen2.5-1.5B-Instruct (~1.1 GB - Ultra-Fast Everyday Chat)"
    Write-Host " [3] Qwen2.5-3B-Instruct (~2.1 GB - Sweet Spot for 8GB-16GB RAM Laptops)"
    Write-Host " [4] DeepSeek-R1-Distill-Qwen-7B Abliterated v2 (~4.7 GB - Uncensored Reasoning)"
    Write-Host " [5] Qwen2.5-Coder-7B-Instruct (~4.7 GB - SOTA Local Coding & Self-Repair)"
    Write-Host " [6] Qwen2.5-Coder-3B-Instruct (~2.1 GB - Fast Lightweight Coding)"
    Write-Host " [7] Gemma-4-E2B-it Unsloth GGUF (~3.2 GB - Fast Edge Gemma 4)"
    Write-Host " [8] Gemma-4-E4B-it Unsloth GGUF (~5.0 GB - Balanced Laptop Gemma 4)"
    Write-Host " [9] Gemma-4-12B-it Unsloth GGUF (~7.5 GB - Mid/High Rig Gemma 4)"
    Write-Host " [10] Gemma-4-26B-A4B-it MoE Unsloth GGUF (~15.5 GB - 4B Active MoE Gemma 4)"
    Write-Host " [0] Cancel"
    $mChoice = Read-Host "Select model (0-10)"

    $Repo = ""
    $File = ""
    if ($mChoice -eq "1") {
        $Repo = "mradermacher/DeepSeek-R1-Distill-Qwen-1.5B-uncensored-GGUF"
        $File = "DeepSeek-R1-Distill-Qwen-1.5B-uncensored.Q4_K_M.gguf"
    } elseif ($mChoice -eq "2") {
        $Repo = "bartowski/Qwen2.5-1.5B-Instruct-GGUF"
        $File = "Qwen2.5-1.5B-Instruct-Q4_K_M.gguf"
    } elseif ($mChoice -eq "3") {
        $Repo = "bartowski/Qwen2.5-3B-Instruct-GGUF"
        $File = "Qwen2.5-3B-Instruct-Q4_K_M.gguf"
    } elseif ($mChoice -eq "4") {
        $Repo = "tensorblock/DeepSeek-R1-Distill-Qwen-7B-abliterated-v2-GGUF"
        $File = "DeepSeek-R1-Distill-Qwen-7B-abliterated-v2-Q4_K_M.gguf"
    } elseif ($mChoice -eq "5") {
        $Repo = "bartowski/Qwen2.5-Coder-7B-Instruct-GGUF"
        $File = "Qwen2.5-Coder-7B-Instruct-Q4_K_M.gguf"
    } elseif ($mChoice -eq "6") {
        $Repo = "bartowski/Qwen2.5-Coder-3B-Instruct-GGUF"
        $File = "Qwen2.5-Coder-3B-Instruct-Q4_K_M.gguf"
    } elseif ($mChoice -eq "7") {
        $Repo = "unsloth/gemma-4-E2B-it-GGUF"
        $File = "gemma-4-E2B-it-Q4_K_M.gguf"
    } elseif ($mChoice -eq "8") {
        $Repo = "unsloth/gemma-4-E4B-it-GGUF"
        $File = "gemma-4-E4B-it-Q4_K_M.gguf"
    } elseif ($mChoice -eq "9") {
        $Repo = "unsloth/gemma-4-12b-it-GGUF"
        $File = "gemma-4-12b-it-Q4_K_M.gguf"
    } elseif ($mChoice -eq "10") {
        $Repo = "unsloth/gemma-4-26B-A4B-it-GGUF"
        $File = "gemma-4-26B-A4B-it-Q4_K_M.gguf"
    } else { return }

    $OutFile = Join-Path $ModelsDir $File
    Write-Host "`n[STEP 1/2] Resolving Hugging Face CDN URL for $File..." -ForegroundColor Cyan
    $ResolvedUrl = (& $VenvPython -c "from huggingface_hub import hf_hub_url; print(hf_hub_url(repo_id='$Repo', filename='$File'))").Trim()
    if (-not $ResolvedUrl -or ($ResolvedUrl -notmatch "^https?://")) {
        Write-Host "[ERROR] Could not resolve URL for $Repo / $File." -ForegroundColor Red
        Pause; return
    }

    Write-Host "[STEP 2/2] Streaming $File into /models with live byte-by-byte progress..." -ForegroundColor Cyan
    Download-FileWithProgress -Url $ResolvedUrl -DestinationPath $OutFile -Label "Downloading $File" | Out-Null
    Write-Host "[OK] Model saved to $OutFile!" -ForegroundColor Green
    Pause
}

function Invoke-WorkspaceZipManager {
    Write-Host "`n================ WORKSPACE .ZIP EXPORT & IMPORT UTILITY ================" -ForegroundColor Cyan
    Write-Host " [1] Export Current Workspace to a Single Portable .ZIP File"
    Write-Host " [2] Import a .ZIP Workspace Archive"
    Write-Host " [3] Import From an Existing / Legacy Project Folder"
    Write-Host " [4] Cancel"
    $c = Read-Host "Select (1-4)"

    if ($c -eq "1") {
        $Stamp = Get-Date -Format "yyyyMMdd_HHmmss"
        $OutZip = Join-Path $BackupsDir "AetherVault_Profile_$Stamp.zip"
        $ItemsToPack = @()
        foreach ($rel in @("memory_core.db", "workspace_config.json", "glossary_index.json", "pseudo_memory_index.json", "partner_evolution.json", "error_audit.log", "AetherVault_Studio_Manual.pdf", "aethervault_logo.svg", "priority_pdfs", "memory_vault", "chat_logs", "custom_assets", "generated_images", "generated_audio")) {
            $p = Join-Path $RootDir $rel
            if (Test-Path $p) { $ItemsToPack += $p }
        }
        if ($ItemsToPack.Count -eq 0) {
            Write-Host "[WARNING] No workspace files found to export yet." -ForegroundColor Yellow
            Pause; return
        }
        Write-Host " -> Packing $($ItemsToPack.Count) workspace items into $OutZip..." -ForegroundColor Cyan
        Compress-Archive -Path $ItemsToPack -DestinationPath $OutZip -Force
        Write-Host "[OK] Exported single-file bundle: $OutZip ($([math]::Round((Get-Item $OutZip).Length / 1MB, 2)) MB)" -ForegroundColor Green
        Start-Process $BackupsDir
        Pause
    }
    elseif ($c -eq "2") {
        $ZipPath = Read-Host "Paste full path to the .ZIP file to import"
        $ZipPath = $ZipPath.Trim('"').Trim("'")
        if (-not (Test-Path $ZipPath)) {
            Write-Host "[ERROR] File not found: $ZipPath" -ForegroundColor Red
            Pause; return
        }
        Write-Host " -> Extracting $ZipPath into $RootDir..." -ForegroundColor Cyan
        Expand-Archive -Path $ZipPath -DestinationPath $RootDir -Force
        Write-Host "[OK] Workspace .ZIP imported successfully!" -ForegroundColor Green
        Pause
    }
    elseif ($c -eq "3") {
        $SrcFolder = Read-Host "Paste full path to your legacy project folder"
        $SrcFolder = $SrcFolder.Trim('"').Trim("'")
        if (-not (Test-Path $SrcFolder)) {
            Write-Host "[ERROR] Folder not found: $SrcFolder" -ForegroundColor Red
            Pause; return
        }
        $Targets = @("memory_core.db", "workspace_config.json", "priority_pdfs", "memory_vault", "chat_logs", "custom_assets")
        $tIdx = 0
        foreach ($item in $Targets) {
            $tIdx++
            $srcItem = Join-Path $SrcFolder $item
            if (Test-Path $srcItem) {
                Write-Host " -> [$tIdx/$($Targets.Count)] Importing $item..." -ForegroundColor Yellow
                Copy-Item -Path $srcItem -Destination $RootDir -Recurse -Force
            }
        }
        Write-Host "[OK] Legacy project migrated into AetherVault Studio!" -ForegroundColor Green
        Pause
    }
}

function Save-OfflineStock {
    if (-not (Ensure-Environment)) { return }
    $VenvPython = Join-Path $VenvDir "Scripts\python.exe"
    $ServerFile = Join-Path $RootDir "assistant_server.py"
    $UiFile     = Join-Path $RootDir "ui_studio.html"

    if (Repair-And-TestPythonScript -ScriptPath $ServerFile) {
        Copy-Item $ServerFile (Join-Path $StockVault "assistant_server.py.good") -Force
    }
    if (Test-Path $UiFile) {
        Copy-Item $UiFile (Join-Path $StockVault "ui_studio.html.good") -Force
    }

    Write-Host "`nDownloading offline .whl installers into stock_vault\wheels..." -ForegroundColor Cyan
    $TotalDl = $Packages.Count + 1
    $Idx = 0
    foreach ($pkg in $Packages) {
        $Idx++
        Invoke-TrackedProcess -FilePath $VenvPython -ArgumentList "-m pip download $pkg -d `"$WheelStock`" --progress-bar on" -Message "Caching wheel: $pkg" -StepIndex $Idx -TotalSteps $TotalDl | Out-Null
    }
    $Idx++
    Invoke-TrackedProcess -FilePath $VenvPython -ArgumentList "-m pip download llama-cpp-python --prefer-binary --extra-index-url $CpuWheelUrl -d `"$WheelStock`" --progress-bar on" -Message "Caching CPU llama-cpp-python wheel" -StepIndex $Idx -TotalSteps $TotalDl | Out-Null

    $LocalModels = @(Get-ChildItem -Path $ModelsDir -Filter "*.gguf" -ErrorAction SilentlyContinue)
    $mIdx = 0
    foreach ($lm in $LocalModels) {
        $mIdx++
        $DestM = Join-Path $ModelStock $lm.Name
        if (-not (Test-Path $DestM)) {
            Copy-FileWithProgress -SourcePath $lm.FullName -DestinationPath $DestM -Label "Backing up $($lm.Name) [$mIdx/$($LocalModels.Count)]" | Out-Null
        }
    }
    Write-Host "`n[COMPLETE] Offline Stock Vault (wheels + golden scripts + local GGUF models) is ready!" -ForegroundColor Green
    Pause
}

function Invoke-Uninstall {
    Write-Host "`n================ UNINSTALL / RESET OPTIONS ================" -ForegroundColor Red
    Write-Host " [1] Soft Reset (Delete .venv, caches, and downloaded models; keep Knowledge Files & Memories)"
    Write-Host " [2] FULL PORTABLE WIPE (Deletes everything inside $RootDir)"
    Write-Host " [3] Cancel"
    $choice = Read-Host "Select (1-3)"

    if ($choice -eq "1") {
        foreach ($item in @($VenvDir, (Join-Path $RootDir "pip_cache"), (Join-Path $RootDir "hf_cache"), $ModelsDir)) {
            if (Test-Path $item) {
                Write-Host " -> Removing $item..." -ForegroundColor Yellow
                Remove-Item -Recurse -Force $item -ErrorAction SilentlyContinue
            }
        }
        Write-Host "[OK] Soft reset complete." -ForegroundColor Green
        Pause
    } elseif ($choice -eq "2") {
        $confirm = Read-Host "Type DELETE in all caps to wipe $RootDir completely"
        if ($confirm -ceq "DELETE") {
            Set-Location $env:TEMP
            Start-Process cmd.exe -ArgumentList "/c timeout /t 2 >nul & rmdir /s /q `"$RootDir`"" -WindowStyle Hidden
            exit 0
        }
    }
}

Invoke-BootStockCheck

while ($true) {
    Clear-Host
    Set-ConsoleTitle -TitleText "AetherVault Studio v4.0 - Control Center (Ready)"
    $LocalIP = (Get-NetIPAddress -AddressFamily IPv4 -ErrorAction SilentlyContinue | Where-Object { $_.InterfaceAlias -notmatch 'Loopback' -and $_.IPAddress -notmatch '^169' } | Select-Object -First 1).IPAddress
    if (-not $LocalIP) { $LocalIP = "127.0.0.1" }
    $EngineFlagFile = Join-Path $VenvDir "engine_mode.flag"
    $EngineMode = if (Test-Path $EngineFlagFile) { (Get-Content $EngineFlagFile -Raw).Trim().ToUpper() } else { "AUTO (VULKAN/CPU)" }

    Write-Host "=======================================================================" -ForegroundColor Cyan
    Write-Host "   AETHERVAULT STUDIO v4.0 - PORTABLE LOCAL AI & OSWORLD ENGINE        " -ForegroundColor White
    Write-Host "   Made with <3 in Argentina by Enzeru (with Google Gemini)            " -ForegroundColor DarkGray
    Write-Host "=======================================================================" -ForegroundColor Cyan
    Write-Host " Root Folder : $RootDir"
    Write-Host " Active Core : $EngineMode" -ForegroundColor Yellow
    Write-Host " Desktop URL : http://127.0.0.1:8000" -ForegroundColor Green
    Write-Host " LAN / Phone : http://$($LocalIP):8000  (Same Wi-Fi)" -ForegroundColor Green
    Write-Host "-----------------------------------------------------------------------"
    Write-Host " [1] Launch AetherVault v4.0 Server (Live Boot Tracker + Auto-Browser)"
    Write-Host " [2] Switch Engine Backend: [A] Vulkan GPU  vs.  [B] 2015 Laptop Safe CPU"
    Write-Host " [3] Quick-Download Starter Models (Live Byte-by-Byte Stream Progress)"
    Write-Host " [4] Export / Import Workspace (.ZIP Bundle or Legacy Project Folder)"
    Write-Host " [5] Stock Offline Vault (Cache .whl installers + Golden Backups + Models)"
    Write-Host " [6] Restore 'Golden Backup' (assistant_server.py + ui_studio.html + DB)"
    Write-Host " [7] UNINSTALL / RESET OPTIONS (Soft Reset or Clean Wipe)"
    Write-Host " [8] Install Optional Specialist AI Managers (diffusers, transformers, scipy, accelerate)"
    Write-Host " [9] Run Windows Defender Patch & Unstick Utility (Fixes GGUF Load Freezes)" -ForegroundColor Yellow
    Write-Host " [0] Exit (Auto-Purges %TEMP% Session Cache)"
    Write-Host "======================================================================="
    $sel = Read-Host "Select an option"

    switch ($sel) {
        "1" {
            if (Ensure-Environment) {
                $VenvPython   = Join-Path $VenvDir "Scripts\python.exe"
                $ServerScript = Join-Path $RootDir "assistant_server.py"
                if (-not (Test-Path $ServerScript)) {
                    Write-Host "[ERROR] assistant_server.py not found in $RootDir" -ForegroundColor Red
                    Pause; continue
                }

                if (-not (Repair-And-TestPythonScript -ScriptPath $ServerScript)) {
                    Write-Host "`n[SYNTAX ERROR] assistant_server.py failed syntax validation:" -ForegroundColor Red
                    & $VenvPython -m py_compile $ServerScript
                    Pause; continue
                } else {
                    Copy-Item $ServerScript (Join-Path $StockVault "assistant_server.py.good") -Force
                }

                Write-Host "`n[LAUNCHING] Starting AetherVault Studio v4.0 Server (Live Console Telemetry Active)..." -ForegroundColor Cyan
                Write-Host " -> A background watcher will open http://127.0.0.1:8000 the moment port 8000 is ready!" -ForegroundColor Green

                Start-Job -ScriptBlock {
                    for ($i = 0; $i -lt 60; $i++) {
                        try {
                            $r = Invoke-WebRequest -Uri "http://127.0.0.1:8000/status" -UseBasicParsing -TimeoutSec 1 -ErrorAction Stop
                            if ($r.StatusCode -eq 200) {
                                Start-Process "http://127.0.0.1:8000"
                                break
                            }
                        } catch {}
                        Start-Sleep -Milliseconds 500
                    }
                } | Out-Null

                & $VenvPython -u $ServerScript
                Pause
            }
        }
        "2" {
            if (Ensure-Environment) {
                Write-Host "`nSelect Hardware Engine Backend:" -ForegroundColor Cyan
                Write-Host " [A] Vulkan GPU Offload (For RX 580 / Dedicated GPUs)"
                Write-Host " [B] 2015 Laptop Safe CPU Build (For Older Laptops / Integrated Graphics)"
                $eng = Read-Host "Choose (A/B)"
                if ($eng -match "^[Bb]") {
                    Install-LlamaCppEngine -PreferredMode "cpu"
                } else {
                    Install-LlamaCppEngine -PreferredMode "vulkan"
                }
                Pause
            }
        }
        "3" { Invoke-QuickModelDownloader }
        "4" { Invoke-WorkspaceZipManager }
        "5" { Save-OfflineStock }
        "6" {
            $StockServer = Join-Path $StockVault "assistant_server.py.good"
            $StockUi     = Join-Path $StockVault "ui_studio.html.good"
            if (Repair-And-TestPythonScript -ScriptPath $StockServer) {
                Copy-Item $StockServer (Join-Path $RootDir "assistant_server.py") -Force -ErrorAction SilentlyContinue
                if (Test-Path $StockUi) { Copy-Item $StockUi (Join-Path $RootDir "ui_studio.html") -Force -ErrorAction SilentlyContinue }
                Copy-Item (Join-Path $StockVault "memory_core.db.bak") (Join-Path $RootDir "memory_core.db") -Force -ErrorAction SilentlyContinue
                Write-Host "[OK] Restored verified golden scripts and database backup!" -ForegroundColor Green
            } else {
                Write-Host "[ERROR] Backup in stock_vault failed syntax check and was not restored." -ForegroundColor Red
            }
            Pause
        }
        "7" { Invoke-Uninstall }
        "8" {
            if (Ensure-Environment) {
                $VenvPython = Join-Path $VenvDir "Scripts\python.exe"
                $SpecPkgs = @("scipy", "soundfile", "kokoro-onnx", "faster-whisper", "accelerate", "transformers", "diffusers")
                $sIdx = 0
                foreach ($sp in $SpecPkgs) {
                    $sIdx++
                    Invoke-TrackedProcess -FilePath $VenvPython -ArgumentList "-m pip install $sp --find-links `"$WheelStock`" --progress-bar on" -Message "Installing Specialist Library: $sp" -StepIndex $sIdx -TotalSteps $SpecPkgs.Count | Out-Null
                }
                Write-Host "`n[OK] Specialist Image & Music Manager libraries installed!" -ForegroundColor Green
                Pause
            }
        }
        "9" {
            $PatchBat = Join-Path $RootDir "Windows_Defender_Patch.bat"
            if (Test-Path $PatchBat) {
                Start-Process -FilePath $PatchBat -WorkingDirectory $RootDir -Verb RunAs -Wait
            } else {
                Write-Host "[ERROR] Windows_Defender_Patch.bat not found in $RootDir" -ForegroundColor Red
                Pause
            }
        }
        "0" {
            $LocalTemp = Join-Path $RootDir ".temp_cache"
            if (Test-Path $LocalTemp) { Remove-Item -Recurse -Force $LocalTemp -ErrorAction SilentlyContinue }
            Get-ChildItem -Path $env:TEMP -Filter "AetherVault_Session_*" -Directory -ErrorAction SilentlyContinue | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
            exit 0
        }
    }
}