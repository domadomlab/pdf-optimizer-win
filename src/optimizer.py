import sys
import os
import subprocess
import shutil
import ctypes
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_FILE = os.path.join(BASE_DIR, "log_config.txt")
LOG_DIR = BASE_DIR

if os.path.exists(CONFIG_FILE):
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8", errors="ignore") as f:
            saved_path = f.read().strip()
            if os.path.isdir(saved_path): LOG_DIR = saved_path
    except: pass

LOG_FILE = os.path.join(LOG_DIR, 'pdf_optimizer_debug.log')

def log(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] {message}\n")
    except: pass

def find_ghostscript():
    # 1. Проверка в PATH
    gs = shutil.which("gswin64c") or shutil.which("gswin32c")
    if gs: return gs

    # 2. Поиск по стандартным путям (агрессивный)
    pf = os.environ.get("ProgramFiles", "C:\\Program Files")
    gs_base = os.path.join(pf, "gs")
    if os.path.exists(gs_base):
        for folder in reversed(os.listdir(gs_base)): # Ищем последнюю версию
            for sub in ["bin", "lib"]:
                for exe in ["gswin64c.exe", "gswin32c.exe"]:
                    target = os.path.join(gs_base, folder, sub, exe)
                    if os.path.exists(target): return target
    return None

def find_magick():
    magick = shutil.which("magick")
    if magick: return magick
    
    pf = os.environ.get("ProgramFiles", "C:\\Program Files")
    for folder in os.listdir(pf):
        if "imagemagick" in folder.lower():
            target = os.path.join(pf, folder, "magick.exe")
            if os.path.exists(target): return target
    return None

def optimize_pdf(file_path, dpi):
    log(f"--- SESSION START v3.1.8: {file_path} ---")
    
    gs_exe = find_ghostscript()
    if gs_exe:
        log(f"Ghostscript located: {gs_exe}")
        # Принудительно задаем переменную для ImageMagick
        os.environ["MAGICK_GHOSTSCRIPT_EXE"] = gs_exe
        os.environ["PATH"] += os.pathsep + os.path.dirname(gs_exe)
    else:
        log("CRITICAL: Ghostscript not found!")
        return "Error: Ghostscript not found. Please reinstall."

    magick_exe = find_magick()
    if not magick_exe:
        log("CRITICAL: ImageMagick not found!")
        return "Error: ImageMagick not found."

    output_path = f"{os.path.splitext(file_path)[0]}_{dpi}dpi.pdf"
    cmd = [magick_exe, "-density", str(dpi), "-units", "PixelsPerInch", file_path, 
           "-alpha", "remove", "-alpha", "off", "-compress", "jpeg", "-quality", "80", "+profile", "*", output_path]

    try:
        log(f"Running: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            log("SUCCESS")
            return "Optimization Successful!"
        else:
            log(f"MAGICK ERROR: {result.stderr}")
            return f"Error: {result.stderr}"
    except Exception as e:
        log(f"EXCEPTION: {str(e)}")
        return str(e)

def main():
    if len(sys.argv) < 3: return
    res = optimize_pdf(sys.argv[2], sys.argv[1])
    ctypes.windll.user32.MessageBoxW(0, res, "PDF Optimizer Suite", 64)

if __name__ == "__main__":
    main()