@echo off
setlocal
title PDF Optimizer - Download Dependencies

echo [Downloading Dependencies for Build]
echo Target folder: resources\

if not exist "resources" mkdir "resources"

:: --- 1. Python 3.12.8 ---
set "URL_PY=https://www.python.org/ftp/python/3.12.8/python-3.12.8-amd64.exe"
set "OUT_PY=resources\python-installer.exe"
if not exist "%OUT_PY%" (
    echo [1/3] Downloading Python 3.12.8...
    curl -L -o "%OUT_PY%" "%URL_PY%"
) else (
    echo [1/3] Python installer OK.
)

:: --- 2. Ghostscript 10.02.1 ---
set "URL_GS=https://github.com/ArtifexSoftware/ghostpdl-downloads/releases/download/gs10021/gs10021w64.exe"
set "OUT_GS=resources\gs-installer.exe"
if not exist "%OUT_GS%" (
    echo [2/3] Downloading Ghostscript 10.02.1...
    curl -L -o "%OUT_GS%" "%URL_GS%"
) else (
    echo [2/3] Ghostscript installer OK.
)

:: --- 3. ImageMagick 7.1.1 ---
:: Note: Official archive links are unstable. Ideally, mirror this file.
set "URL_IM=https://imagemagick.org/archive/binaries/ImageMagick-7.1.1-29-Q16-HDRI-x64-dll.exe"
set "OUT_IM=resources\ImageMagick-Installer.exe"
if not exist "%OUT_IM%" (
    echo [3/3] Downloading ImageMagick 7.1.1...
    curl -L -o "%OUT_IM%" "%URL_IM%"
) else (
    echo [3/3] ImageMagick installer OK.
)

echo.
echo ----------------------------------------------------
echo Success! All dependencies are ready.
echo You can now run: makensis installer.nsi
echo ----------------------------------------------------
pause
