@echo off
chcp 65001 >nul
title Сборка KSZ-Agent.exe (Автономный агент для Windows)

echo =================================================================
echo        Сборка автономного KSZ-Agent.exe (GUI + Трей)
echo =================================================================
echo.

set "PYTHON_CMD="

REM 1. Проверяем python в PATH
python -c "import sys" >nul 2>&1
if %errorlevel% equ 0 (
    set "PYTHON_CMD=python"
    goto :found_py
)

REM 2. Проверяем launcher py
py -3 -c "import sys" >nul 2>&1
if %errorlevel% equ 0 (
    set "PYTHON_CMD=py -3"
    goto :found_py
)

REM 3. Поиск в стандартных каталогах
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
            goto :found_py
        )
    )
)

:not_found
echo =================================================================
echo [ОШИБКА] Для сборки .exe необходим Python 3.10+
echo =================================================================
echo Выполните в PowerShell от Администратора быструю установку:
echo   Invoke-WebRequest -Uri https://www.python.org/ftp/python/3.12.7/python-3.12.7-amd64.exe -OutFile python_setup.exe; .\python_setup.exe /quiet InstallAllUsers=1 PrependPath=1
echo.
pause
exit /b 1

:found_py
cd /d "%~dp0"

echo [ИНФО] Используется Python: %PYTHON_CMD%
%PYTHON_CMD% -V
echo.

echo [1/3] Установка необходимых пакетов (pyinstaller, pystray, pillow)...
%PYTHON_CMD% -m pip install --upgrade pip
%PYTHON_CMD% -m pip install --upgrade pyinstaller pystray pillow

echo.
echo [2/3] Компиляция KSZ-Agent.exe (один файл, без черного окна консоли)...
%PYTHON_CMD% -m PyInstaller --noconfirm --clean --onefile --noconsole --name "KSZ-Agent" ksz_helper_gui.py

if %errorlevel% neq 0 (
    echo.
    echo =================================================================
    echo [ОШИБКА] Сборка завершилась с ошибкой!
    echo =================================================================
    pause
    exit /b %errorlevel%
)

echo.
echo [3/3] Копирование готового файла в текущую папку...
if exist "dist\KSZ-Agent.exe" (
    copy /Y "dist\KSZ-Agent.exe" "KSZ-Agent.exe" >nul
)

echo.
echo =================================================================
echo [УСПЕХ] Файл KSZ-Agent.exe успешно собран!
echo Расположение: %~dp0KSZ-Agent.exe
echo.
echo Особенности собранного файла:
echo  1. Полностью автономен — работает БЕЗ установленного Python!
echo  2. Работает в системном трее рядом с часами.
echo  3. При нажатии кнопки закрытия [X] или "Свернуть" уходит в трей.
echo  4. Поддерживает автозапуск вместе с Windows.
echo =================================================================
echo.
pause
