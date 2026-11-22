# Сборка автономного KSZ-Agent.exe через PowerShell
$ErrorActionPreference = "Stop"

Write-Host "=================================================" -ForegroundColor Cyan
Write-Host "  Сборка автономного KSZ-Agent.exe (PowerShell)"   -ForegroundColor Cyan
Write-Host "=================================================" -ForegroundColor Cyan
Write-Host ""

Set-Location $PSScriptRoot

# Поиск рабочего Python
$pyCmd = $null
$candidates = @("python", "py -3")

foreach ($c in $candidates) {
    try {
        $test = Start-Process -FilePath ($c.Split(' ')[0]) -ArgumentList "-c `"import sys`"" -NoNewWindow -Wait -PassThru
        if ($test.ExitCode -eq 0) {
            $pyCmd = $c
            break
        }
    } catch {}
}

if (-not $pyCmd) {
    # Поиск по стандартным путям
    $paths = @(
        "C:\Program Files\Python313\python.exe",
        "C:\Program Files\Python312\python.exe",
        "C:\Program Files\Python311\python.exe",
        "C:\Program Files\Python310\python.exe",
        "C:\Python312\python.exe",
        "C:\Python311\python.exe",
        "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe",
        "$env:LOCALAPPDATA\Programs\Python\Python311\python.exe"
    )
    foreach ($p in $paths) {
        if (Test-Path $p) {
            $pyCmd = "`"$p`""
            break
        }
    }
}

if (-not $pyCmd) {
    Write-Host "[ОШИБКА] Python 3.10+ не найден на компьютере!" -ForegroundColor Red
    Write-Host "Для автоматической тихой установки запустите:" -ForegroundColor Yellow
    Write-Host "Invoke-WebRequest -Uri https://www.python.org/ftp/python/3.12.7/python-3.12.7-amd64.exe -OutFile python_setup.exe; .\python_setup.exe /quiet InstallAllUsers=1 PrependPath=1"
    Exit 1
}

Write-Host "[1/3] Установка библиотек pyinstaller, pystray, pillow..." -ForegroundColor Yellow
Invoke-Expression "$pyCmd -m pip install --upgrade pip"
Invoke-Expression "$pyCmd -m pip install --upgrade pyinstaller pystray pillow"

Write-Host "`n[2/3] Компиляция KSZ-Agent.exe..." -ForegroundColor Yellow
Invoke-Expression "$pyCmd -m PyInstaller --noconfirm --clean --onefile --noconsole --name `"KSZ-Agent`" ksz_helper_gui.py"

if (Test-Path "dist\KSZ-Agent.exe") {
    Copy-Item -Path "dist\KSZ-Agent.exe" -Destination "KSZ-Agent.exe" -Force
    Write-Host "`n=================================================" -ForegroundColor Green
    Write-Host " [УСПЕХ] Файл собран: $PSScriptRoot\KSZ-Agent.exe" -ForegroundColor Green
    Write-Host "=================================================" -ForegroundColor Green
}
