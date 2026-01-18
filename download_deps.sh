#!/bin/bash

echo "[Downloading Dependencies for Build]"
echo "Target folder: resources/"

mkdir -p resources

# 1. Python
URL_PY="https://www.python.org/ftp/python/3.12.8/python-3.12.8-amd64.exe"
OUT_PY="resources/python-installer.exe"
if [ ! -f "$OUT_PY" ]; then
    echo "[1/3] Downloading Python 3.12.8..."
    curl -L -o "$OUT_PY" "$URL_PY"
else
    echo "[1/3] Python installer OK."
fi

# 2. Ghostscript
URL_GS="https://github.com/ArtifexSoftware/ghostpdl-downloads/releases/download/gs10021/gs10021w64.exe"
OUT_GS="resources/gs-installer.exe"
if [ ! -f "$OUT_GS" ]; then
    echo "[2/3] Downloading Ghostscript 10.02.1..."
    curl -L -o "$OUT_GS" "$URL_GS"
else
    echo "[2/3] Ghostscript installer OK."
fi

# 3. ImageMagick
URL_IM="https://imagemagick.org/archive/binaries/ImageMagick-7.1.1-29-Q16-HDRI-x64-dll.exe"
OUT_IM="resources/ImageMagick-Installer.exe"
if [ ! -f "$OUT_IM" ]; then
    echo "[3/3] Downloading ImageMagick 7.1.1..."
    curl -L -o "$OUT_IM" "$URL_IM"
else
    echo "[3/3] ImageMagick installer OK."
fi

echo ""
echo "Success! All dependencies are ready."
chmod +x "$OUT_PY" "$OUT_GS" "$OUT_IM" 2>/dev/null
