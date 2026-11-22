@echo off
chcp 65001 >nul
title KSZ Companion Helper (Локальный агент инженера)

echo =================================================================
echo        KSZ-DB Companion Helper (Клиентский агент v2.0)
echo =================================================================
echo.

set "PYTHON_CMD="

REM 1. Проверяем рабочий python в переменной PATH (проверяем реальный запуск)
python -c "import sys" >nul 2>&1
if %errorlevel% equ 0 (
    set "PYTHON_CMD=python"
    goto :found_python
)

REM 2. Проверяем официальный Python Launcher (py.exe)
py -3 -c "import sys" >nul 2>&1
if %errorlevel% equ 0 (
    set "PYTHON_CMD=py -3"
    goto :found_python
)

REM 3. Поиск Python в стандартных системных каталогах установки
for %%P in (
    "C:\Program Files\Python313\python.exe"
    "C:\Program Files\Python312\python.exe"
    "C:\Program Files\Python311\python.exe"
    "C:\Program Files\Python310\python.exe"
    "C:\Python313\python.exe"
    "C:\Python312\python.exe"
    "C:\Python311\python.exe"
    "C:\Python310\python.exe"
    "%LOCALAPPDATA%\Programs\Python\Python313\python.exe"
    "%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
    "%LOCALAPPDATA%\Programs\Python\Python311\python.exe"
    "%LOCALAPPDATA%\Programs\Python\Python310\python.exe"
) do (
    if exist %%P (
        %%P -c "import sys" >nul 2>&1
        if %errorlevel% equ 0 (
            set "PYTHON_CMD=%%P"
            goto :found_python
        )
    )
)

:not_found
echo =================================================================
echo [ОШИБКА 9009] Интерпретатор Python не найден на этом компьютере!
echo =================================================================
echo.
echo Для работы агента на Windows Server 2019 необходим Python 3.10+:
echo.
echo Способ 1: Быстрая автоматическая установка через PowerShell (от Администратора):
echo   Invoke-WebRequest -Uri https://www.python.org/ftp/python/3.12.7/python-3.12.7-amd64.exe -OutFile python_setup.exe
echo   .\python_setup.exe /quiet InstallAllUsers=1 PrependPath=1
echo.
echo Способ 2: Скачать установщик вручную:
echo   https://www.python.org/downloads/
echo   При установке обязательно отметьте галочку:
echo     [X] "Add python.exe to PATH"
echo.
pause
exit /b 1

:found_python
cd /d "%~dp0"

echo [ИНФО] Найден интерпретатор: %PYTHON_CMD%
%PYTHON_CMD% -V
echo.
echo [ИНФО] Запуск агента ksz_helper.py...
echo.

%PYTHON_CMD% ksz_helper.py

if %errorlevel% neq 0 (
    echo.
    echo =================================================================
    echo [ВНИМАНИЕ] Агент завершил работу с кодом ошибки %errorlevel%.
    echo =================================================================
    pause
)
