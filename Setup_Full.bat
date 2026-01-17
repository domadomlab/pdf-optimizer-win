@echo off
setlocal
title PDF Optimizer Suite - Full Setup

echo ========================================================
echo        PDF Optimizer Suite for Windows 11
echo           Full Installation Wrapper
echo ========================================================
echo.

:: 1. Check for Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo [WARNING] Python is NOT found in PATH.
    echo Launching bundled installer...
    echo.
    echo *** IMPORTANT INSTRUCTION ***
    echo You MUST check the box "Add Python.exe to PATH" at the bottom of the installer window!
    echo.
    pause
    
    if exist "%~dp0resources\python-installer.exe" (
        "%~dp0resources\python-installer.exe"
        
        echo.
        echo Please wait for installation to finish...
        pause
    ) else (
        echo [ERROR] Bundled installer not found in 'resources' folder!
        echo Please install Python manually.
        pause
    )
) else (
    echo [OK] Python is found.
)

:: 2. Check for ImageMagick
magick -version >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo [WARNING] ImageMagick is NOT found in PATH.
    echo Launching bundled installer...
    echo.
    echo *** IMPORTANT INSTRUCTIONS ***
    echo 1. In the installer, check "Install legacy utilities (e.g. convert)"
    echo 2. Check "Add application directory to your system path"
    echo 3. Complete the installation.
    echo.
    pause
    
    if exist "%~dp0resources\ImageMagick-Installer.exe" (
        "%~dp0resources\ImageMagick-Installer.exe"
        
        :: Re-check after install (might require restart, but let's try)
        echo.
        echo Please wait for installation to finish...
        pause
    ) else (
        echo [ERROR] Bundled installer not found in 'resources' folder!
        echo Please install ImageMagick manually.
        pause
    )
) else (
    echo [OK] ImageMagick is found.
)

:: 3. Run the Registration Script
echo.
echo Launching Context Menu Registration...
call "%~dp0install\install.bat"

echo.
echo ========================================================
echo        Setup Complete!
echo ========================================================
pause
