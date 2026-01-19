@echo off
setlocal enabledelayedexpansion

:: %1 is DPI, %2 is File Path
set "DPI=%~1"
set "PDF_FILE=%~2"

:: Find Python
set "PY_EXE="
for %%V in (3.12 3.11 3.10 3.9) do (
    if not defined PY_EXE (
        for %%R in (HKLM HKCU) do (
            for /f "tokens=2*" %%a in ('reg query "%%R\SOFTWARE\Python\PythonCore\%%V\InstallPath" /ve 2^>nul') do (
                set "DP=%%b"
                if "!DP:~-1!" neq \" set "DP=!DP!\"
                if exist "!DP!pythonw.exe" set "PY_EXE=!DP!pythonw.exe"
            )
        )
    )
)

if not defined PY_EXE (
    where pythonw.exe >nul 2>&1
    if %errorlevel% equ 0 set "PY_EXE=pythonw.exe"
)

if not defined PY_EXE (
    msg * "Error: Python 3.12 not found. Please reinstall PDF Optimizer."
    exit /b 1
)

:: Run the script
start "" "!PY_EXE!" "%~dp0optimizer.pyw" !DPI! "!PDF_FILE!"

