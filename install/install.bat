@echo off
setlocal enabledelayedexpansion

set "LOG_FILE=%~1"
set "PROJECT_ROOT=%~dp0.."

echo --- PORTABLE SETUP START v4.3.0 --- >> "!LOG_FILE!"

pushd "%PROJECT_ROOT%"
set "PROJECT_ROOT=%CD%"
popd
set "RAW_SCRIPT=%PROJECT_ROOT%\src\optimizer.pyw"

:: --- 1. SET EMBEDDED PYTHON ---
set "PY_EXE=%PROJECT_ROOT%\resources\python\python.exe"
set "REGISTER_SCRIPT=%PROJECT_ROOT%\install\register.py"
set "LAUNCHER_VBS=%PROJECT_ROOT%\src\launcher.vbs"
set "LANG_CODE=%~2"

echo [DEBUG] Target Python Path: !PY_EXE! >> "!LOG_FILE!"

if not exist "!PY_EXE!" (
    echo [CRITICAL] Embedded Python NOT found at !PY_EXE! >> "!LOG_FILE!"
    exit /b 1
)

:: --- 2. CLEANUP LEGACY (Simple Reg Delete) ---
echo Cleaning legacy keys... >> "!LOG_FILE!"
for %%R in (HKCU HKLM) do (
    reg delete "%%R\Software\Classes\.pdf\shell\PDFOptimizer75" /f >nul 2>&1
    reg delete "%%R\Software\Classes\.pdf\shell\PDFOptimizer150" /f >nul 2>&1
    reg delete "%%R\Software\Classes\.pdf\shell\PDFOptimizer200" /f >nul 2>&1
    reg delete "%%R\Software\Classes\.pdf\shell\PDFOptimizer300" /f >nul 2>&1
    reg delete "%%R\Software\Classes\SystemFileAssociations\.pdf\shell\PDFOptimizer75" /f >nul 2>&1
    reg delete "%%R\Software\Classes\SystemFileAssociations\.pdf\shell\PDFOptimizer150" /f >nul 2>&1
    reg delete "%%R\Software\Classes\SystemFileAssociations\.pdf\shell\PDFOptimizer200" /f >nul 2>&1
    reg delete "%%R\Software\Classes\SystemFileAssociations\.pdf\shell\PDFOptimizer300" /f >nul 2>&1
)

:: --- 3. PYTHON REGISTRATION ---
echo Executing Python registration... >> "!LOG_FILE!"

"!PY_EXE!" "!REGISTER_SCRIPT!" "!PY_EXE!" "!RAW_SCRIPT!" "!LAUNCHER_VBS!" "!LANG_CODE!" >> "!LOG_FILE!" 2>&1

:: --- 4. FORCE REFRESH ---
echo Refreshing Windows Shell... >> "!LOG_FILE!"
ie4uinit.exe -show >nul 2>&1

echo [OK] Portable setup (Python) complete. >> "!LOG_FILE!"
