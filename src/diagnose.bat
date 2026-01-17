@echo off
setlocal
set "DIAG_LOG=%~dp0..\logs\diagnostics.log"
if not exist "%~dp0..\logs" mkdir "%~dp0..\logs"

echo --- DIAGNOSTICS START --- > "%DIAG_LOG%"
echo Date: %DATE% %TIME% >> "%DIAG_LOG%"
echo OS: >> "%DIAG_LOG%"
ver >> "%DIAG_LOG%"

echo. >> "%DIAG_LOG%"
echo --- REGISTRY CHECK --- >> "%DIAG_LOG%"
echo [SystemFileAssociations] >> "%DIAG_LOG%"
reg query "HKCU\Software\Classes\SystemFileAssociations\.pdf\shell\PDFOptimizer200\command" /ve >> "%DIAG_LOG%" 2>&1

echo. >> "%DIAG_LOG%"
echo --- FILE CHECK --- >> "%DIAG_LOG%"
echo Launcher exists: >> "%DIAG_LOG%"
if exist "%~dp0launcher.vbs" (echo YES) else (echo NO) >> "%DIAG_LOG%"
echo Python in PATH: >> "%DIAG_LOG%"
python --version >> "%DIAG_LOG%" 2>&1

echo. >> "%DIAG_LOG%"
echo --- PYTHON REGISTRY --- >> "%DIAG_LOG%"
reg query "HKLM\SOFTWARE\Python\PythonCore\3.12\InstallPath" /ve >> "%DIAG_LOG%" 2>&1

echo Diagnostics complete. Log saved to logs\diagnostics.log
