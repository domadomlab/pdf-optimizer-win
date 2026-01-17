@echo off
setlocal enabledelayedexpansion
title PDF Optimizer Suite v3.1.4 - Setup & Diagnostics

set SEE_MASK_NOZONECHECKS=1
color 07

set "RAW_LOG_DIR=%~1"
if "!RAW_LOG_DIR!"=="" set "RAW_LOG_DIR=%TEMP%"
set "LOG_FILE=!RAW_LOG_DIR!\pdf_optimizer_debug.log"

echo --- SETUP LOG v3.1.4 START --- >> "!LOG_FILE!"
echo Date: %DATE% %TIME% >> "!LOG_FILE!"

echo [1/4] Python Check...
python --version 2>nul | findstr "3.12" >nul
if %errorlevel% neq 0 (
    if exist "%~dp0resources\python-installer.exe" (
        echo      Installing Python...
        start /wait "" "%~dp0resources\python-installer.exe" /quiet InstallAllUsers=1 PrependPath=1
        echo [INFO] Python Install Exit Code: !errorlevel! >> "!LOG_FILE!"
    )
)

echo [2/4] Ghostscript Check...
echo [DEBUG] Checking Ghostscript before install... >> "!LOG_FILE!"

set "GS_FOUND=NO"
gswin64c -version >nul 2>&1 && set "GS_FOUND=YES (PATH)"
if "!GS_FOUND!"=="NO" (
    reg query "HKLM\SOFTWARE\GPL Ghostscript" /ve >nul 2>&1 && set "GS_FOUND=YES (REG-GPL)"
)
if "!GS_FOUND!"=="NO" (
    reg query "HKLM\SOFTWARE\Artifex\Ghostscript" /ve >nul 2>&1 && set "GS_FOUND=YES (REG-ARTIFEX)"
)

echo [INFO] GS Status before install: !GS_FOUND! >> "!LOG_FILE!"

if "!GS_FOUND!"=="NO" (
    if exist "%~dp0resources\gs-installer.exe" (
        echo      Installing Ghostscript...
        copy /y "%~dp0resources\gs-installer.exe" "%TEMP%\gs_setup.exe" >nul
        echo [DEBUG] Running: %TEMP%\gs_setup.exe /S >> "!LOG_FILE!"
        start /wait "" "%TEMP%\gs_setup.exe" /S
        set "GS_EXIT=!errorlevel!"
        echo [INFO] GS Install Exit Code: !GS_EXIT! >> "!LOG_FILE!"
        del "%TEMP%\gs_setup.exe" /q
        
        :: Проверка после установки
        set "GS_POST=FAIL"
        if exist "C:\Program Files\gs" set "GS_POST=OK (Files exist)"
        gswin64c -version >nul 2>&1 && set "GS_POST=OK (PATH works)"
        echo [INFO] GS Status after install: !GS_POST! >> "!LOG_FILE!"
        
        if "!GS_POST!"=="FAIL" (
            echo [WARN] Ghostscript failed to install automatically. >> "!LOG_FILE!"
            echo      ^> Warning: GS not detected after install.
        )
    ) else (
        echo [ERROR] GS installer NOT FOUND in resources! >> "!LOG_FILE!"
    )
) else (
    echo      Detected: !GS_FOUND!
)

echo [3/4] ImageMagick Check...
magick -version >nul 2>&1
if %errorlevel% neq 0 (
    if exist "%~dp0resources\ImageMagick-Installer.exe" (
        echo      Installing ImageMagick...
        start /wait "" "%~dp0resources\ImageMagick-Installer.exe" /VERYSILENT /TASKS="legacy_support,add_path"
        echo [INFO] ImageMagick Install Exit Code: !errorlevel! >> "!LOG_FILE!"
    )
)

echo [4/4] Registry Integration...
call "%~dp0install\install.bat" "!LOG_FILE!"

echo Finalizing...
taskkill /f /im explorer.exe >nul 2>&1
start explorer.exe

echo --- SETUP LOG v3.1.4 END --- >> "!LOG_FILE!"
echo Setup Finished.
timeout /t 3