@echo off
setlocal enabledelayedexpansion

set "LOG_FILE=%~1"
set "PROJECT_ROOT=%~dp0.."

echo --- TOTAL REGISTRY CLEAN ^& RESET START v3.6.0 --- >> "!LOG_FILE!"

pushd "%PROJECT_ROOT%"
set "PROJECT_ROOT=%CD%"
popd
set "RAW_SCRIPT=%PROJECT_ROOT%\src\optimizer.py"

:: --- 1. FIND PYTHON ---
echo [DEBUG] Finding Python... >> "!LOG_FILE!"
set "PY_EXE="

:: 1.1 Check common versions in registry (HKLM and HKCU)
for %%V in (3.12 3.11 3.10 3.13 3.9) do (
    if not defined PY_EXE (
        echo [DEBUG] Checking Python %%V registry keys... >> "!LOG_FILE!"
        for %%R in (HKLM HKCU) do (
            echo   [DEBUG] Querying %%R\SOFTWARE\Python\PythonCore\%%V\InstallPath >> "!LOG_FILE!"
            for /f "tokens=2*" %%a in ('reg query "%%R\SOFTWARE\Python\PythonCore\%%V\InstallPath" /ve 2^>nul') do (
                echo     [DEBUG] Found raw value: %%b >> "!LOG_FILE!"
                set "DP=%%b"
                if "!DP:~-1!" neq \" set "DP=!DP!\" 
                if exist "!DP!pythonw.exe" (
                    set "PY_EXE=!DP!pythonw.exe"
                    echo     [SUCCESS] Found pythonw.exe at !DP!pythonw.exe >> "!LOG_FILE!"
                )
            )
        )
    )
)

:: 1.2 Check common disk paths directly (if registry failed)
if not defined PY_EXE (
    echo [DEBUG] Registry failed. Checking common disk paths... >> "!LOG_FILE!"
    set "COMMON_PATHS="
    set "COMMON_PATHS=!COMMON_PATHS! %LOCALAPPDATA%\Programs\Python\Python312\pythonw.exe"
    set "COMMON_PATHS=!COMMON_PATHS! %LOCALAPPDATA%\Programs\Python\Python313\pythonw.exe"
    set "COMMON_PATHS=!COMMON_PATHS! %LOCALAPPDATA%\Programs\Python\Python311\pythonw.exe"
    set "COMMON_PATHS=!COMMON_PATHS! C:\Python312\pythonw.exe"
    set "COMMON_PATHS=!COMMON_PATHS! C:\Program Files\Python312\pythonw.exe"
    set "COMMON_PATHS=!COMMON_PATHS! C:\Program Files\Python313\pythonw.exe"
    
    for %%P in (!COMMON_PATHS!) do (
        if exist "%%P" (
            set "PY_EXE=%%P"
            echo [SUCCESS] Found direct path: %%P >> "!LOG_FILE!"
        )
    )
)

:: 1.3 Try Python Launcher (py.exe)
if not defined PY_EXE (
    where py.exe >nul 2>&1
    if !errorlevel! equ 0 (
        set "PY_EXE=py.exe" 
        echo [SUCCESS] Found Python Launcher py.exe >> "!LOG_FILE!"
    )
)

:: 1.4 Fallback to WHERE command
if not defined PY_EXE (
    echo [DEBUG] Trying where pythonw.exe... >> "!LOG_FILE!"
    for /f "delims=" %%i in ('where pythonw.exe 2^>nul') do (
        set "PY_EXE=%%i"
        echo [DEBUG] where found: %%i >> "!LOG_FILE!"
    )
)

:: 1.5 Final check
if not defined PY_EXE (
    echo [FAIL] Python NOT found! >> "!LOG_FILE!"
    exit /b 1
)
echo [OK] Using Python: !PY_EXE! >> "!LOG_FILE!"

:: --- 2. THE NUKE (Delete all possible legacy paths) ---
echo Cleaning all legacy registry paths... >> "!LOG_FILE!"
set "PATHS_TO_NUKE="
set "PATHS_TO_NUKE=!PATHS_TO_NUKE! HKCR\SystemFileAssociations\.pdf\shell"
set "PATHS_TO_NUKE=!PATHS_TO_NUKE! HKCU\Software\Classes\.pdf\shell"
set "PATHS_TO_NUKE=!PATHS_TO_NUKE! HKCU\Software\Classes\SystemFileAssociations\.pdf\shell"
set "PATHS_TO_NUKE=!PATHS_TO_NUKE! HKCU\Software\Classes\*\shell"
set "PATHS_TO_NUKE=!PATHS_TO_NUKE! HKLM\SOFTWARE\Classes\SystemFileAssociations\.pdf\shell"
set "PATHS_TO_NUKE=!PATHS_TO_NUKE! HKLM\SOFTWARE\Classes\.pdf\shell"
set "PATHS_TO_NUKE=!PATHS_TO_NUKE! HKLM\SOFTWARE\Classes\*\shell"

for %%K in (%PATHS_TO_NUKE%) do (
    reg delete "%%K\PDFOptimizer75" /f >nul 2>&1
    reg delete "%%K\PDFOptimizer150" /f >nul 2>&1
    reg delete "%%K\PDFOptimizer200" /f >nul 2>&1
    reg delete "%%K\PDFOptimizer300" /f >nul 2>&1
)

:: --- 3. POWER REGISTRATION (Reliable Unicode via Base64) ---
echo Generating PowerShell registration script... >> "!LOG_FILE!"

set "PS_SCRIPT=%TEMP%\register_menu.ps1"
if exist "!PS_SCRIPT!" del "!PS_SCRIPT!"

set "LANG_CODE=%~2"

echo $PyExe = '!PY_EXE!' >> "!PS_SCRIPT!"
echo $ScriptPath = '!RAW_SCRIPT!' >> "!PS_SCRIPT!"
echo $Lang = '!LANG_CODE!' >> "!PS_SCRIPT!"
echo function Get-StrFromB64 { param($s); [System.Text.Encoding]::UTF8.GetString([System.Convert]::FromBase64String($s)) } >> "!PS_SCRIPT!"
echo if ($Lang -eq 'RU') { >> "!PS_SCRIPT!"
echo     $Names = @{ '75'=(Get-StrFromB64 'UERGOiDQrdC60L4gKDc1IGRwaSk='); '150'=(Get-StrFromB64 'UERGOiDQn9C+0YfRgtCwICgxNTAgZHBpKQ=='); '200'=(Get-StrFromB64 'UERGOiDQn9C10YfQsNGC0YwgKDIwMCBkcGkp'); '300'=(Get-StrFromB64 'UERGOiDQmtCw0YfQtdGB0YLQstC+ICgzMDAgZHBpKQ==') } >> "!PS_SCRIPT!"
echo } else { >> "!PS_SCRIPT!"
echo     $Names = @{ '75'='PDF: Eco (75 dpi)'; '150'='PDF: Email (150 dpi)'; '200'='PDF: Print (200 dpi)'; '300'='PDF: High (300 dpi)' } >> "!PS_SCRIPT!"
echo } >> "!PS_SCRIPT!"
echo $Roots = @('HKLM:\SOFTWARE\Classes\SystemFileAssociations\.pdf\shell', 'HKCU:\Software\Classes\SystemFileAssociations\.pdf\shell', 'HKCU:\Software\Classes\.pdf\shell', 'HKCU:\Software\Classes\*\shell') >> "!PS_SCRIPT!"
echo foreach ($Root in $Roots) { >> "!PS_SCRIPT!"
echo     if (!(Test-Path $Root)) { New-Item -Path $Root -Force ^| Out-Null } >> "!PS_SCRIPT!"
echo     foreach ($Dpi in @('75','150','200','300')) { >> "!PS_SCRIPT!"
echo         $KeyPath = "$Root\PDFOptimizer$Dpi" >> "!PS_SCRIPT!"
echo         New-Item -Path $KeyPath -Force -Value $Names[$Dpi] ^| Out-Null >> "!PS_SCRIPT!"
echo         Set-ItemProperty -Path $KeyPath -Name 'Icon' -Value 'shell32.dll,166' >> "!PS_SCRIPT!"
echo         $CmdPath = "$KeyPath\command" >> "!PS_SCRIPT!"
echo         $CmdVal = "`"$PyExe`" `"$ScriptPath`" $Dpi `"%%1`"" >> "!PS_SCRIPT!"
echo         New-Item -Path $CmdPath -Force -Value $CmdVal ^| Out-Null >> "!PS_SCRIPT!"
echo     } >> "!PS_SCRIPT!"
echo } >> "!PS_SCRIPT!"

echo try { >> "!PS_SCRIPT!"
echo     if (-not ([System.Management.Automation.PSTypeName]'Win32.Shell32').Type) { >> "!PS_SCRIPT!"
echo         Add-Type -MemberDefinition '[DllImport("shell32.dll")] public static extern void SHChangeNotify(long wEventId, uint uFlags, IntPtr dwItem1, IntPtr dwItem2);' -Name "Shell32" -Namespace Win32 >> "!PS_SCRIPT!"
echo     } >> "!PS_SCRIPT!"
echo     [Win32.Shell32]::SHChangeNotify(0x08000000, 0, [IntPtr]::Zero, [IntPtr]::Zero) >> "!PS_SCRIPT!"
echo } catch { } >> "!PS_SCRIPT!"

echo Executing PowerShell registration... >> "!LOG_FILE!"
powershell -ExecutionPolicy Bypass -File "!PS_SCRIPT!" >> "!LOG_FILE!" 2>&1
if exist "!PS_SCRIPT!" del "!PS_SCRIPT!"

:: --- 4. FORCE REFRESH ---
echo Refreshing Windows Shell... >> "!LOG_FILE!"
ie4uinit.exe -show >nul 2>&1

echo [OK] All systems reset and registered. >> "!LOG_FILE!"