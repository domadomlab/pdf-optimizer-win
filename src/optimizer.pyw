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

def format_size(size_bytes):
    """Converts bytes to human readable string."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} TB"

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
    log(f"--- SESSION START v3.9.2: {file_path} ---")
    
    # Analyze Input File
    try:
        input_size = os.path.getsize(file_path)
        log(f"INPUT FILE: Size {format_size(input_size)}")
    except Exception as e:
        log(f"Input Error: {e}")
        return f"Error reading input: {e}"

    original_file_path = file_path # Keep original path for naming output

    # --- WORD CONVERSION START ---
    ext = os.path.splitext(file_path)[1].lower()
    is_word_doc = ext in ['.doc', '.docx']
    temp_pdf = None

    if is_word_doc:
        log("Detected Word document. Converting to PDF...")
        converter_script = os.path.join(BASE_DIR, "src", "docx2pdf.vbs")
        temp_pdf = os.path.join(os.path.dirname(file_path), f"~temp_{os.path.basename(file_path)}.pdf")
        
        try:
            # Run VBScript to convert using MS Word
            # cscript //Nologo script.vbs input output
            conv_cmd = ["cscript", "//NoLogo", converter_script, file_path, temp_pdf]
            
            # Use CREATE_NO_WINDOW
            creation_flags = 0x08000000 if sys.platform == 'win32' else 0
            
            conv_res = subprocess.run(conv_cmd, capture_output=True, creationflags=creation_flags)
            
            if conv_res.returncode != 0 or not os.path.exists(temp_pdf):
                log(f"Word Conversion Failed. Code: {conv_res.returncode}")
                return "Error: MS Word conversion failed."
            
            # Swap file_path to point to the new temp PDF for optimization
            file_path = temp_pdf
            log(f"Conversion successful. Temp PDF: {file_path}")
            
        except Exception as e:
            log(f"Conversion Exception: {e}")
            return f"Error converting Word: {e}"
    # --- WORD CONVERSION END ---

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

    # Use original path for naming, stripping original extension (.doc/.pdf)
    output_path = f"{os.path.splitext(original_file_path)[0]}_{dpi}dpi.pdf"
    
    # 1. Base command
    if str(dpi) == "30":
        # Extreme Mode (Method 5: Trellis-Quantization Mimic)
        cmd = [magick_exe, "-limit", "memory", "1GiB", "-limit", "map", "2GiB", "-density", "150", "-units", "PixelsPerInch", file_path, 
               "-alpha", "remove", "-alpha", "off", 
               "-filter", "Lanczos", "-distort", "Resize", "95%", 
               "-unsharp", "0x0.5",
               "-sampling-factor", "4:2:0", 
               "-compress", "jpeg", 
               "-quality", "40"]
    elif str(dpi) == "150":
        # Scientific Email Mode (Trellis Mimic + Quality 70)
        cmd = [magick_exe, "-limit", "memory", "1GiB", "-limit", "map", "2GiB", "-density", "150", "-units", "PixelsPerInch", file_path, 
               "-alpha", "remove", "-alpha", "off", 
               "-filter", "Lanczos", "-distort", "Resize", "95%", 
               "-unsharp", "0x0.5",
               "-sampling-factor", "4:2:0", 
               "-compress", "jpeg", 
               "-quality", "70"]
    else:
        # Standard Modes (Eco, Print, High)
        cmd = [magick_exe, "-limit", "memory", "1GiB", "-limit", "map", "2GiB", "-density", str(dpi), "-units", "PixelsPerInch", file_path, 
               "-alpha", "remove", "-alpha", "off", 
               "-sampling-factor", "4:2:0", 
               "-compress", "jpeg", 
               "-quality", "70"]
           
    # 2. Strip ALL existing metadata (Privacy First)
    cmd.extend(["+profile", "*"])
    
    # 3. Inject FAKE metadata (Camouflage)
    cmd.extend(get_fake_metadata_args())
    
    # 4. Output
    cmd.append(output_path)

    try:
        log(f"Running: {' '.join(cmd)}")
        
        # Use CREATE_NO_WINDOW for robust window suppression on Windows
        # and redirect stdin to DEVNULL to prevent hanging/errors in background
        creation_flags = 0
        if sys.platform == 'win32':
            creation_flags = 0x08000000  # CREATE_NO_WINDOW
            
        result = subprocess.run(
            cmd, 
            capture_output=True, 
            text=True, 
            creationflags=creation_flags,
            stdin=subprocess.DEVNULL
        )
        
        if result.returncode == 0:
            if os.path.exists(output_path):
                output_size = os.path.getsize(output_path)
                
                # Statistics
                diff = input_size - output_size
                percent = (diff / input_size) * 100 if input_size > 0 else 0
                
                log(f"OUTPUT FILE: Size {format_size(output_size)}")
                log(f"STATS: Reduced by {format_size(diff)} ({percent:.1f}%)")
                log("SUCCESS")
                
                return f"Done! Reduced by {percent:.0f}% ({format_size(output_size)})"
            else:
                log("Error: Output file not created despite 0 exit code.")
                return "Error: Output file missing."
        else:
            log(f"MAGICK ERROR: {result.stderr}")
            return f"Error: {result.stderr}"
            
    except Exception as e:
        log(f"EXCEPTION: {str(e)}")
        return str(e)
    finally:
        # CLEANUP: Ensure temporary PDF is deleted regardless of success/error
        if temp_pdf and os.path.exists(temp_pdf):
            try: 
                os.remove(temp_pdf)
                log(f"Cleanup: Removed temporary file {temp_pdf}")
            except Exception as e: 
                log(f"Cleanup Error: {e}")

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
            # Use CREATE_NO_WINDOW for PowerShell too
            subprocess.Popen(
                ["powershell", "-Command", ps_script],
                creationflags=0x08000000
            )
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