@echo off
setlocal enabledelayedexpansion
title PDF Optimizer Suite v3.9.5 - Portable Setup

color 07
set "LOG_DIR=%~1"
if "%LOG_DIR%"=="" set "LOG_DIR=%TEMP%"
set "LOG_FILE=%LOG_DIR%\pdf_optimizer_debug.log"

echo Starting Portable Installation v3.9.5...
echo --- SETUP LOG v3.9.5 START --- >> "%LOG_FILE%"

:: 1. Python (Embedded - Skipped check)
echo [1/3] Configuring Embedded Python...
echo [INFO] Using Embedded Python (skip system check). >> "%LOG_FILE%"

:: 2. Ghostscript
echo [2/3] Checking Ghostscript...
gswin64c -version >nul 2>&1
if %errorlevel% neq 0 (
    if exist "%~dp0resources\gs-installer.exe" (
        echo [INFO] Installing Ghostscript... >> "%LOG_FILE%"
        start /wait "" "%~dp0resources\gs-installer.exe" /S
    ) else (
        echo [WARN] Ghostscript installer not found. >> "%LOG_FILE%"
    )
) else (
    echo [INFO] Ghostscript already installed. >> "%LOG_FILE%"
)

:: 3. ImageMagick
echo [3/3] Checking ImageMagick...
magick -version >nul 2>&1
if %errorlevel% neq 0 (
    if exist "%~dp0resources\ImageMagick-Installer.exe" (
        echo [INFO] Installing ImageMagick... >> "%LOG_FILE%"
        start /wait "" "%~dp0resources\ImageMagick-Installer.exe" /VERYSILENT /TASKS="legacy_support,add_path"
    ) else (
        echo [WARN] ImageMagick installer not found. >> "%LOG_FILE%"
    )
) else (
    echo [INFO] ImageMagick already installed. >> "%LOG_FILE%"
)

:: 4. Registry Registration
echo [Finalizing] Registering Menu...
:: Pass the language argument (%2) to install.bat
call "%~dp0install\install.bat" "%LOG_FILE%" "%~2"

echo Setup Finished.
echo --- SETUP LOG v3.9.5 END --- >> "%LOG_FILE%"