@echo off
setlocal enabledelayedexpansion

set "LOG_FILE=%~1"
set "PROJECT_ROOT=%~dp0.."

echo --- REGISTRY SHORT-PATH START v3.1.6 --- >> "!LOG_FILE!"

pushd "%PROJECT_ROOT%"
set "PROJECT_ROOT=%CD%"
popd
set "RAW_SCRIPT=%PROJECT_ROOT%\src\optimizer.py"

:: --- FIND PYTHON ---
set "PY_EXE="
for /f "delims=" %%i in ('where pythonw.exe 2^>nul') do set "PY_EXE=%%i"
if not defined PY_EXE (
    for /f "delims=" %%i in ('where python.exe 2^>nul') do set "PY_EXE=%%i"
)

if not defined PY_EXE (
    echo [FAIL] Python NOT found! >> "!LOG_FILE!"
    exit /b 1
)

:: --- CONVERT TO SHORT PATHS (8.3) ---
for %%I in ("!PY_EXE!") do set "S_PY=%%~sI"
for %%I in ("!RAW_SCRIPT!") do set "S_SCRIPT=%%~sI"

echo [OK] Short Python: !S_PY! >> "!LOG_FILE!"
echo [OK] Short Script: !S_SCRIPT! >> "!LOG_FILE!"

:: --- GENERATE REG FILE ---
set "REG_FILE=%TEMP%\pdf_opt_short.reg"
(
echo Windows Registry Editor Version 5.00
echo.

:: Регистрируем во всех возможных местах
for %%H in (HKEY_LOCAL_MACHINE HKEY_CURRENT_USER) do (
    for %%P in (Software\Classes\SystemFileAssociations\.pdf\shell Software\Classes\.pdf\shell Software\Classes\*\shell) do (
        echo [%%H\%%P\PDFOptimizer150]
        echo @="Optimize PDF (150 DPI)"
        echo "Icon"="shell32.dll,166"
        if "%%P"=="Software\Classes\*\shell" echo "AppliesTo"=".pdf"
        echo [%%H\%%P\PDFOptimizer150\command]
        echo @="!S_PY! !S_SCRIPT! 150 \"%%1\""
        echo.
        echo [%%H\%%P\PDFOptimizer200]
        echo @="Optimize PDF (200 DPI)"
        echo "Icon"="shell32.dll,166"
        if "%%P"=="Software\Classes\*\shell" echo "AppliesTo"=".pdf"
        echo [%%H\%%P\PDFOptimizer200\command]
        echo @="!S_PY! !S_SCRIPT! 200 \"%%1\""
        echo.
        echo [%%H\%%P\PDFOptimizer300]
        echo @="Optimize PDF (300 DPI)"
        echo "Icon"="shell32.dll,166"
        if "%%P"=="Software\Classes\*\shell" echo "AppliesTo"=".pdf"
        echo [%%H\%%P\PDFOptimizer300\command]
        echo @="!S_PY! !S_SCRIPT! 300 \"%%1\""
        echo.
    )
)
) > "!REG_FILE!"

reg import "!REG_FILE!" >nul 2>&1
if !errorlevel! equ 0 (
    echo [OK] Short-path registry imported. >> "!LOG_FILE!"
) else (
    echo [FAIL] Registry import failed code !errorlevel! >> "!LOG_FILE!"
)
del "!REG_FILE!" /q