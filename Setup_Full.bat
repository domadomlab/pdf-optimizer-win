@echo off
setlocal enabledelayedexpansion
title PDF Optimizer Suite v3.6.0 - Setup

:: Возврат к стабильным настройкам
color 07
set "LOG_DIR=%~1"
if "%LOG_DIR%"=="" set "LOG_DIR=%TEMP%"
set "LOG_FILE=%LOG_DIR%\pdf_optimizer_debug.log"

echo Starting Installation v3.6.0...
echo --- SETUP LOG v3.6.0 START --- >> "%LOG_FILE%"

:: 1. Python
echo [1/4] Checking Python status...
echo [DEBUG] Checking for existing Python 3.12... >> "%LOG_FILE%"

:: Попытка определить версию
python --version 2>> "%LOG_FILE%" | findstr "3.12" >nul
set "PY_CHECK=%errorlevel%"
echo [DEBUG] Python 3.12 check errorlevel: %PY_CHECK% >> "%LOG_FILE%"

if %PY_CHECK% neq 0 (
    echo [DEBUG] Python 3.12 NOT found or version mismatch. Proceeding to install/repair. >> "%LOG_FILE%"
    
    set "INSTALLER=%~dp0resources\python-installer.exe"
    if exist "!INSTALLER!" (
        echo [DEBUG] Found installer at: !INSTALLER! >> "%LOG_FILE%"
        echo [INFO] Installing/Repairing Python 3.12... >> "%LOG_FILE%"
        
        :: Сначала пробуем обычную установку/обновление. 
        :: Если он уже есть, он может обновиться или потребовать Repair.
        :: Добавляем /repair флаг в качестве альтернативы, если обычный запуск не помог, 
        :: но проще всего использовать штатный инсталлер, он сам умеет в Repair если запущен повторно.
        start /wait "" "!INSTALLER!" /quiet /repair InstallAllUsers=1 PrependPath=1
        
        echo [DEBUG] Python Installer/Repair finished. >> "%LOG_FILE%"
    ) else (
        echo [ERROR] Python installer NOT found at: !INSTALLER! >> "%LOG_FILE%"
    )
) else (
    echo [INFO] Python 3.12 is already installed. >> "%LOG_FILE%"
)

:: 2. Ghostscript (Прямая установка как в v3.0.9)
echo [2/4] Ghostscript...
gswin64c -version >nul 2>&1
if %errorlevel% neq 0 (
    if exist "%~dp0resources\gs-installer.exe" (
        start /wait "" "%~dp0resources\gs-installer.exe" /S
    )
)

:: 3. ImageMagick
echo [3/4] ImageMagick...
magick -version >nul 2>&1
if %errorlevel% neq 0 (
    if exist "%~dp0resources\ImageMagick-Installer.exe" (
        start /wait "" "%~dp0resources\ImageMagick-Installer.exe" /VERYSILENT /TASKS="legacy_support,add_path"
    )
)

:: 4. Registry
echo [4/4] Registry...
:: Pass the language argument (%2) to install.bat
call "%~dp0install\install.bat" "%LOG_FILE%" "%~2"

echo Finalizing...
echo --- SETUP LOG v3.6.0 END --- >> "%LOG_FILE%"

:: Force UI Refresh - DISABLED (Handled gently by PS)
:: taskkill /f /im explorer.exe >nul 2>&1
:: start explorer.exe