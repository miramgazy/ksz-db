@echo off
chcp 65001 >nul
title KSZ Companion Helper (Локальный агент инженера)

echo =================================================================
echo        KSZ-DB Companion Helper (Клиентский агент v2.0)
echo =================================================================
echo.

REM Проверка наличия Python в системе
set PYTHON_CMD=
where python >nul 2>nul
if %errorlevel% equ 0 (
    set PYTHON_CMD=python
) else (
    where py >nul 2>nul
    if %errorlevel% equ 0 (
        set PYTHON_CMD=py -3
    )
)

if "%PYTHON_CMD%"=="" (
    echo [ОШИБКА] Python не обнаружен в системе!
    echo.
    echo Пожалуйста, установите Python версии 3.10 или выше с сайта https://www.python.org/
    echo При установке обязательно отметьте галочку:
    echo   [X] "Add python.exe to PATH"
    echo.
    pause
    exit /b 1
)

cd /d "%~dp0"

echo [ИНФО] Запуск агента через %PYTHON_CMD%...
echo.

%PYTHON_CMD% ksz_helper.py

if %errorlevel% neq 0 (
    echo.
    echo =================================================================
    echo [ВНИМАНИЕ] Агент завершил работу с кодом ошибки %errorlevel%.
    echo =================================================================
    pause
)
