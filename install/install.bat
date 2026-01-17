@echo off
setlocal

:: Get the root directory of the project (parent of 'install')
pushd "%~dp0.."
set "PROJECT_ROOT=%CD%"
popd

set "SCRIPT_PATH=%PROJECT_ROOT%\src\optimizer.py"

echo ========================================================
echo       PDF Optimizer Context Menu Installer
echo ========================================================
echo.
echo Project Location: %PROJECT_ROOT%
echo Script Path:      %SCRIPT_PATH%
echo.

:: Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not found in PATH!
    echo Please install Python and check "Add Python to PATH".
    pause
    exit /b 1
)

:: Check if Script exists
if not exist "%SCRIPT_PATH%" (
    echo [ERROR] optimizer.py not found at:
    echo %SCRIPT_PATH%
    pause
    exit /b 1
)

:: Check for ImageMagick (Warning only)
magick -version >nul 2>&1
if %errorlevel% neq 0 (
    echo [WARNING] 'magick' command not found in PATH!
    echo The optimizer will fail until ImageMagick is installed and added to PATH.
    echo.
)

echo Adding Registry Keys...
echo Note: This requires Administrator privileges.
echo.

:: 150 DPI
reg add "HKCR\SystemFileAssociations\.pdf\shell\PDFOptimizer150" /ve /d "Optimize PDF (150 DPI)" /f
reg add "HKCR\SystemFileAssociations\.pdf\shell\PDFOptimizer150\command" /ve /d "python \"%SCRIPT_PATH%\" 150 \"%%1\"" /f

:: 200 DPI
reg add "HKCR\SystemFileAssociations\.pdf\shell\PDFOptimizer200" /ve /d "Optimize PDF (200 DPI)" /f
reg add "HKCR\SystemFileAssociations\.pdf\shell\PDFOptimizer200\command" /ve /d "python \"%SCRIPT_PATH%\" 200 \"%%1\"" /f

:: 300 DPI
reg add "HKCR\SystemFileAssociations\.pdf\shell\PDFOptimizer300" /ve /d "Optimize PDF (300 DPI)" /f
reg add "HKCR\SystemFileAssociations\.pdf\shell\PDFOptimizer300\command" /ve /d "python \"%SCRIPT_PATH%\" 300 \"%%1\"" /f

echo.
if %errorlevel% equ 0 (
    echo [SUCCESS] Context menu entries added!
    echo Right-click a PDF file to see "Optimize PDF..." options.
) else (
    echo [ERROR] Failed to add registry keys. 
    echo Please run this script as Administrator.
)

pause
