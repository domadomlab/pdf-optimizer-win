import sys
import os
import subprocess
import shutil
import ctypes
import random
import tempfile
import traceback
from datetime import datetime

# --- CONFIGURATION & LOGGING ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Add embedded python paths to sys.path
sys.path.append(os.path.join(BASE_DIR, "resources", "python"))
sys.path.append(BASE_DIR)

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
    except:
        # Fallback to temp directory if primary log is unwritable
        try:
            temp_log = os.path.join(tempfile.gettempdir(), 'pdf_optimizer_fallback.log')
            with open(temp_log, "a", encoding="utf-8") as f:
                f.write(f"[{timestamp}] {message}\n")
        except: pass

def log_error(e):
    log(f"CRITICAL ERROR: {str(e)}")
    log(traceback.format_exc())

# --- HELPER FUNCTIONS ---
def format_size(size_bytes):
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0: return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} TB"

# --- Fake Scanners Database ---
FAKE_SCANNERS = [
    {"Producer": "HP LaserJet MFP M426fdw", "Creator": "HP Scan", "Author": "Scanner"},
    {"Producer": "HP Color LaserJet Pro MFP M283fdw", "Creator": "HP Smart", "Author": "Administrator"},
    {"Producer": "Canon iR-ADV C5535", "Creator": "Canon PDF Platform", "Author": ""},
    {"Producer": "Canon MF Scan Utility", "Creator": "Canon MF643Cdw", "Author": "User"},
    {"Producer": "Xerox WorkCentre 7845", "Creator": "Xerox WorkCentre", "Author": "Xerox"},
    {"Producer": "Xerox VersaLink C405", "Creator": "Xerox MFP", "Author": "Scan"},
    {"Producer": "Kyocera ECOSYS M2540dn", "Creator": "KM-4050 Scanner", "Author": "Scanner"},
    {"Producer": "Brother MFC-L2710DW", "Creator": "Brother iPrint&Scan", "Author": ""},
    {"Producer": "Epson Scan 2", "Creator": "EPSON Scan", "Author": ""},
]

def get_fake_metadata_args():
    try:
        profile = random.choice(FAKE_SCANNERS)
        args = []
        if profile["Producer"]: args.extend(["-define", f"pdf:Producer={profile['Producer']}"])
        if profile["Creator"]: args.extend(["-define", f"pdf:Creator={profile['Creator']}"])
        author = profile["Author"] if profile["Author"] else " "
        args.extend(["-define", f"pdf:Author={author}"])
        titles = ["Scanned Document", "Scan", "Doc", "Document", "Scan_2026", "CCF_0001"]
        args.extend(["-define", f"pdf:Title={random.choice(titles)}"])
        return args
    except: return []

def find_ghostscript():
    gs = shutil.which("gswin64c") or shutil.which("gswin32c")
    if gs: return gs
    pf = os.environ.get("ProgramFiles", "C:\\Program Files")
    gs_base = os.path.join(pf, "gs")
    if os.path.exists(gs_base):
        for folder in reversed(os.listdir(gs_base)):
            for sub in ["bin", "lib"]:
                for exe in ["gswin64c.exe", "gswin32c.exe"]:
                    target = os.path.join(gs_base, folder, sub, exe)
                    if os.path.exists(target): return target
    return None

def find_magick():
    magick = shutil.which("magick")
    if magick: return magick
    pf = os.environ.get("ProgramFiles", "C:\\Program Files")
    if os.path.exists(pf):
        for folder in os.listdir(pf):
            if "imagemagick" in folder.lower():
                target = os.path.join(pf, folder, "magick.exe")
                if os.path.exists(target): return target
    return None

def get_page_count(magick_exe, file_path):
    try:
        cmd = [magick_exe, "identify", "-format", "%n\n", file_path]
        creation_flags = 0x08000000 if sys.platform == 'win32' else 0
        result = subprocess.run(cmd, capture_output=True, text=True, creationflags=creation_flags)
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            if lines: return int(lines[0])
    except: pass
    return 1

def optimize_pdf(file_path, dpi):
    log(f"--- SESSION START v4.0.6 (Universal Trellis): {file_path} ---")
    
    try:
        if not os.path.exists(file_path):
            log(f"ERROR: File not found: {file_path}")
            return "Error: File missing."
        input_size = os.path.getsize(file_path)
    except Exception as e:
        log_error(e)
        return f"Error reading input: {e}"

    original_file_path = file_path
    temp_pdf_from_word = None

    # --- WORD CONVERSION ---
    ext = os.path.splitext(file_path)[1].lower()
    if ext in ['.doc', '.docx']:
        log("Converting Word document...")
        converter_script = os.path.join(BASE_DIR, "src", "docx2pdf.vbs")
        temp_pdf_from_word = os.path.join(os.path.dirname(file_path), f"~temp_{os.path.basename(file_path)}.pdf")
        try:
            conv_cmd = ["cscript", "//NoLogo", converter_script, file_path, temp_pdf_from_word]
            creation_flags = 0x08000000 if sys.platform == 'win32' else 0
            subprocess.run(conv_cmd, capture_output=True, creationflags=creation_flags)
            if os.path.exists(temp_pdf_from_word):
                file_path = temp_pdf_from_word
            else:
                log("Word conversion failed.")
                return "Error: MS Word conversion failed."
        except Exception as e:
            log_error(e)
            return f"Error converting Word: {e}"

    # --- TOOLS CHECK ---
    gs_exe = find_ghostscript()
    if gs_exe:
        os.environ["MAGICK_GHOSTSCRIPT_EXE"] = gs_exe
        os.environ["PATH"] += os.pathsep + os.path.dirname(gs_exe)
    else:
        log("ERROR: Ghostscript not found.")
        return "Error: Ghostscript not found."

    magick_exe = find_magick()
    if not magick_exe:
        log("ERROR: ImageMagick not found.")
        return "Error: ImageMagick not found."

    # --- PREPARE ---
    page_count = get_page_count(magick_exe, file_path)
    output_path = f"{os.path.splitext(original_file_path)[0]}_{dpi}dpi.pdf"
    
    # Resource limits for IM
    im_limits = ["-limit", "memory", "2GiB", "-limit", "map", "4GiB", "-limit", "area", "1GiB"]
    
    quality = "70"
    read_dpi = str(dpi)
    if str(dpi) == "30":
        quality = "40"
        read_dpi = "150"

    creation_flags = 0x08000000 if sys.platform == 'win32' else 0
    success = False

    try:
        if page_count > 1:
            log(f"Heavy Duty Mode: {page_count} pages.")
            with tempfile.TemporaryDirectory() as tmpdir:
                processed_pages = []
                for i in range(page_count):
                    page_out = os.path.join(tmpdir, f"page_{i:04d}.pdf")
                    # Scientific Pipeline
                    cmd = [magick_exe] + im_limits + [
                           "-density", read_dpi, f"{file_path}[{i}]", 
                           "-alpha", "remove", "-alpha", "off", 
                           "-filter", "Lanczos", "-distort", "Resize", "95%", 
                           "-unsharp", "0x0.5",
                           "-sampling-factor", "4:2:0", 
                           "-compress", "jpeg", 
                           "-quality", quality] + get_fake_metadata_args() + [page_out]
                    
                    res = subprocess.run(cmd, capture_output=True, creationflags=creation_flags)
                    if res.returncode == 0 and os.path.exists(page_out):
                        processed_pages.append(page_out)
                    else:
                        log(f"Page {i} failed: {res.stderr}")
                        return f"Error on page {i}"

                # Merge back
                log("Merging pages...")
                merge_cmd = [gs_exe, "-dNOPAUSE", "-sDEVICE=pdfwrite", f"-sOUTPUTFILE={output_path}", "-dBATCH"] + processed_pages
                res_merge = subprocess.run(merge_cmd, capture_output=True, creationflags=creation_flags)
                if res_merge.returncode == 0: success = True
        else:
            log("Single page mode.")
            cmd = [magick_exe] + im_limits + [
                   "-density", read_dpi, file_path, 
                   "-alpha", "remove", "-alpha", "off", 
                   "-filter", "Lanczos", "-distort", "Resize", "95%", 
                   "-unsharp", "0x0.5",
                   "-sampling-factor", "4:2:0", 
                   "-compress", "jpeg", 
                   "-quality", quality] + get_fake_metadata_args() + [output_path]
            
            res = subprocess.run(cmd, capture_output=True, creationflags=creation_flags)
            if res.returncode == 0: success = True

        if success and os.path.exists(output_path):
            output_size = os.path.getsize(output_path)
            diff = input_size - output_size
            pct = (diff / input_size) * 100 if input_size > 0 else 0
            log(f"SUCCESS: {format_size(output_size)}")
            return f"Done! Reduced by {pct:.0f}% ({format_size(output_size)})"
        else:
            log("FAILED: Success flag false or output missing.")
            return "Optimization failed."

    except Exception as e:
        log_error(e)
        return str(e)
    finally:
        if temp_pdf_from_word and os.path.exists(temp_pdf_from_word):
            try: os.remove(temp_pdf_from_word)
            except: pass

def show_notification(title, message):
    safe_msg = message.replace('"', "'" ).replace("\n", " ")
    safe_title = title.replace('"', "'" )
    ps_script = f"Add-Type -AssemblyName System.Windows.Forms; $n = New-Object System.Windows.Forms.NotifyIcon; $n.Icon = [System.Drawing.SystemIcons]::Information; $n.Visible = $True; $n.BalloonTipTitle = '{safe_title}'; $n.BalloonTipText = '{safe_msg}'; $n.ShowBalloonTip(3000); Start-Sleep -Seconds 4; $n.Dispose()"
    if sys.platform == 'win32':
        try:
            subprocess.Popen(["powershell", "-Command", ps_script], creationflags=0x08000000)
        except: pass

def main():
    if len(sys.argv) < 3: return
    try:
        res = optimize_pdf(sys.argv[2], sys.argv[1])
        show_notification("PDF Optimizer Suite", res)
    except Exception as e:
        log_error(e)

if __name__ == "__main__":
    main()
