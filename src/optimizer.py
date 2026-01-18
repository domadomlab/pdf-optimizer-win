import sys
import os
import subprocess
import shutil
import ctypes
import random
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

# --- Fake Scanners Database ---
FAKE_SCANNERS = [
    # HP
    {"Producer": "HP LaserJet MFP M426fdw", "Creator": "HP Scan", "Author": "Scanner"},
    {"Producer": "HP Color LaserJet Pro MFP M283fdw", "Creator": "HP Smart", "Author": "Administrator"},
    # Canon
    {"Producer": "Canon iR-ADV C5535", "Creator": "Canon PDF Platform", "Author": ""},
    {"Producer": "Canon MF Scan Utility", "Creator": "Canon MF643Cdw", "Author": "User"},
    # Xerox
    {"Producer": "Xerox WorkCentre 7845", "Creator": "Xerox WorkCentre", "Author": "Xerox"},
    {"Producer": "Xerox VersaLink C405", "Creator": "Xerox MFP", "Author": "Scan"},
    # Kyocera
    {"Producer": "Kyocera ECOSYS M2540dn", "Creator": "KM-4050 Scanner", "Author": "Scanner"},
    # Brother
    {"Producer": "Brother MFC-L2710DW", "Creator": "Brother iPrint&Scan", "Author": ""},
    # Epson
    {"Producer": "Epson Scan 2", "Creator": "EPSON Scan", "Author": ""},
]

def log(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] {message}\n")
    except: pass

def get_fake_metadata_args():
    """Generates random metadata to impersonate a physical scanner."""
    try:
        profile = random.choice(FAKE_SCANNERS)
        args = []
        
        # Using -define pdf:Property=Value is more reliable for PDF output in ImageMagick
        if profile["Producer"]: args.extend(["-define", f"pdf:Producer={profile['Producer']}"])
        if profile["Creator"]: args.extend(["-define", f"pdf:Creator={profile['Creator']}"])
        
        # Author is often empty or generic
        author = profile["Author"] if profile["Author"] else " "
        args.extend(["-define", f"pdf:Author={author}"])
        
        # Title is usually generic for scans
        titles = ["Scanned Document", "Scan", "Doc", "Document", "Scan_2026", "CCF_0001"]
        args.extend(["-define", f"pdf:Title={random.choice(titles)}"])
        
        log(f"Applying Fake Profile: {profile['Producer']}")
        return args
    except Exception as e:
        log(f"Metadata Error: {e}")
        return []

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
    log(f"--- SESSION START v3.6.0: {file_path} ---")
    
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
    
    # 1. Base command
    cmd = [magick_exe, "-density", str(dpi), "-units", "PixelsPerInch", file_path, 
           "-alpha", "remove", "-alpha", "off", "-compress", "jpeg", "-quality", "80"]
           
    # 2. Strip ALL existing metadata (Privacy First)
    cmd.extend(["+profile", "*"])
    
    # 3. Inject FAKE metadata (Camouflage)
    cmd.extend(get_fake_metadata_args())
    
    # 4. Output
    cmd.append(output_path)

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

def show_notification(title, message):
    # Escape quotes for PowerShell
    safe_msg = message.replace('"', "'" ).replace("\n", " ")
    safe_title = title.replace('"', "'" )
    
    ps_script = f"""
    Add-Type -AssemblyName System.Windows.Forms
    $notify = New-Object System.Windows.Forms.NotifyIcon
    $notify.Icon = [System.Drawing.SystemIcons]::Information
    $notify.Visible = $True
    $notify.BalloonTipTitle = '{safe_title}'
    $notify.BalloonTipText = '{safe_msg}'
    $notify.ShowBalloonTip(3000)
    Start-Sleep -Seconds 4
    $notify.Dispose()
    """
    try:
        if sys.platform == 'win32':
            si = subprocess.STARTUPINFO()
            si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            subprocess.Popen(["powershell", "-Command", ps_script], startupinfo=si)
        else:
            # Fallback for Linux testing or other OS
            print(f"NOTIFICATION [{title}]: {message}")
    except Exception as e:
        log(f"Notification Error: {e}")

def main():
    if len(sys.argv) < 3: return
    res = optimize_pdf(sys.argv[2], sys.argv[1])
    # Убираем блокирующее окно, используем тихое уведомление
    show_notification("PDF Optimizer Suite", res)

if __name__ == "__main__":
    main()
