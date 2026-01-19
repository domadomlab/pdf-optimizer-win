import sys
import os
import subprocess
import shutil
import ctypes
import random
import tempfile
import traceback
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

# --- CONFIGURATION & LOGGING ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
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
    except: pass

def log_error(e):
    log(f"CRITICAL ERROR: {str(e)}")
    log(traceback.format_exc())

def format_size(size_bytes):
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0: return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} TB"

# --- Matched Scanner Profiles (Logic Integrity) ---
SCANNER_PROFILES = [
    {"Brand": "HP", "Producer": "HP LaserJet MFP M426fdw", "Creator": "HP Scan"},
    {"Brand": "HP", "Producer": "HP Color LaserJet Pro MFP M283fdw", "Creator": "HP Smart"},
    {"Brand": "Canon", "Producer": "Canon iR-ADV C5535", "Creator": "Canon PDF Platform"},
    {"Brand": "Canon", "Producer": "Canon MF Scan Utility", "Creator": "Canon MF643Cdw"},
    {"Brand": "Xerox", "Producer": "Xerox WorkCentre 7845", "Creator": "Xerox WorkCentre"},
    {"Brand": "Xerox", "Producer": "Xerox VersaLink C405", "Creator": "Xerox MFP"},
    {"Brand": "Kyocera", "Producer": "Kyocera ECOSYS M2540dn", "Creator": "KM-4050 Scanner"},
    {"Brand": "Brother", "Producer": "Brother MFC-L2710DW", "Creator": "Brother iPrint&Scan"},
    {"Brand": "Epson", "Producer": "Epson Scan 2", "Creator": "EPSON Scan"},
]

def get_matched_metadata(profile):
    args = []
    args.extend(["-define", f"pdf:Producer={profile['Producer']}"])
    args.extend(["-define", f"pdf:Creator={profile['Creator']}"])
    
    titles = ["Scanned Document", "Scan", "Doc", "Document", "Scan_2026", "CCF_0001"]
    args.extend(["-define", f"pdf:Title={random.choice(titles)}"])
    args.extend(["-define", "pdf:Author=Scanner"])
    return args

def find_ghostscript():
    gs = shutil.which("gswin64c") or shutil.which("gswin32c")
    if gs: return gs
    pf = os.environ.get("ProgramFiles", "C:\\ Program Files")
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
    pf = os.environ.get("ProgramFiles", "C:\\ Program Files")
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

def process_single_page(page_idx, file_path, read_dpi, quality, im_limits, magick_exe, tmpdir, metadata_args):
    page_out = os.path.join(tmpdir, f"page_{page_idx:04d}.pdf")
    cmd = [magick_exe] + im_limits + [
           "-density", read_dpi, f"{file_path}[{page_idx}]", 
           "-alpha", "remove", "-alpha", "off", 
           "-filter", "Lanczos", "-distort", "Resize", "95%", 
           "-unsharp", "0x0.5",
           "-sampling-factor", "4:2:0", 
           "-compress", "jpeg", 
           "-quality", quality] + metadata_args + [page_out]
    
    creation_flags = 0x08000000 if sys.platform == 'win32' else 0
    res = subprocess.run(cmd, capture_output=True, text=True, creationflags=creation_flags)
    return page_out if res.returncode == 0 and os.path.exists(page_out) else None

def optimize_pdf(file_path, dpi):
    log(f"--- SESSION START v4.2.1 (Logic Fix): {file_path} ---")
    try:
        if not os.path.exists(file_path): return "Error: File missing."
        input_size = os.path.getsize(file_path)
    except Exception as e:
        log_error(e)
        return f"Error reading input: {e}"

    original_file_path = file_path
    temp_pdf_from_word = None

    ext = os.path.splitext(file_path)[1].lower()
    if ext in ['.doc', '.docx']:
        converter_script = os.path.join(BASE_DIR, "src", "docx2pdf.vbs")
        temp_pdf_from_word = os.path.join(os.path.dirname(file_path), f"~temp_{os.path.basename(file_path)}.pdf")
        try:
            conv_cmd = ["cscript", "//NoLogo", converter_script, file_path, temp_pdf_from_word]
            creation_flags = 0x08000000 if sys.platform == 'win32' else 0
            subprocess.run(conv_cmd, capture_output=True, creationflags=creation_flags)
            if os.path.exists(temp_pdf_from_word): file_path = temp_pdf_from_word
            else: return "Error: Word conversion failed."
        except Exception as e:
            log_error(e)
            return f"Error converting Word: {e}"

    gs_exe = find_ghostscript()
    magick_exe = find_magick()
    if not gs_exe or not magick_exe: return "Error: External tools missing."

    page_count = get_page_count(magick_exe, file_path)
    output_path = f"{os.path.splitext(original_file_path)[0]}_{dpi}dpi.pdf"
    
    im_limits = ["-limit", "memory", "512MiB", "-limit", "map", "1GiB", "-limit", "area", "256MiB"]
    quality = "40" if str(dpi) == "30" else "70"
    read_dpi = "150" if str(dpi) == "30" else str(dpi)
    
    # Selection of matched profile
    profile = random.choice(SCANNER_PROFILES)
    log(f"Applying Matched Profile: {profile['Brand']} ({profile['Producer']})")
    metadata_args = get_matched_metadata(profile)

    success = False
    try:
        if page_count > 1:
            max_workers = os.cpu_count() or 4
            with tempfile.TemporaryDirectory() as tmpdir:
                processed_pages_map = {}
                with ThreadPoolExecutor(max_workers=max_workers) as executor:
                    futures = {executor.submit(process_single_page, i, file_path, read_dpi, quality, im_limits, magick_exe, tmpdir, metadata_args): i for i in range(page_count)}
                    for future in as_completed(futures):
                        idx = futures[future]
                        res_path = future.result()
                        if res_path: processed_pages_map[idx] = res_path
                        else: return f"Error on page {idx}"

                sorted_pages = [processed_pages_map[i] for i in range(page_count)]
                merge_cmd = [gs_exe, "-dNOPAUSE", "-sDEVICE=pdfwrite", f"-sOUTPUTFILE={output_path}", "-dBATCH"] + sorted_pages
                res_merge = subprocess.run(merge_cmd, capture_output=True, text=True, creationflags=0x08000000)
                if res_merge.returncode == 0: success = True
        else:
            cmd = [magick_exe] + im_limits + ["-density", read_dpi, file_path, "-alpha", "remove", "-alpha", "off", "-filter", "Lanczos", "-distort", "Resize", "95%", "-unsharp", "0x0.5", "-sampling-factor", "4:2:0", "-compress", "jpeg", "-quality", quality] + metadata_args + [output_path]
            res = subprocess.run(cmd, capture_output=True, creationflags=0x08000000)
            if res.returncode == 0: success = True

        if success and os.path.exists(output_path):
            output_size = os.path.getsize(output_path)
            pct = ((input_size - output_size) / input_size) * 100 if input_size > 0 else 0
            return f"Done! Reduced by {pct:.0f}% ({format_size(output_size)})")
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
        try: subprocess.Popen(["powershell", "-Command", ps_script], creationflags=0x08000000)
        except: pass

def main():
    if len(sys.argv) < 3: return
    try:
        res = optimize_pdf(sys.argv[2], sys.argv[1])
        show_notification("PDF Optimizer Suite", res)
    except Exception as e: log_error(e)

if __name__ == "__main__":
    main()
