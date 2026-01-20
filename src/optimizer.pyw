import sys
import os
import subprocess
import shutil
import ctypes
import random
import tempfile
import traceback
import time
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

# --- CONFIGURATION & LOGGING ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(BASE_DIR, "resources", "python"))
sys.path.append(BASE_DIR)

CONFIG_FILE = os.path.join(BASE_DIR, "log_config.txt")
LOG_DIR = BASE_DIR

# Timeouts in seconds
PAGE_TIMEOUT = 60
MERGE_TIMEOUT = 300
WORD_TIMEOUT = 120

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
        try:
            temp_log = os.path.join(tempfile.gettempdir(), 'pdf_optimizer_fallback.log')
            with open(temp_log, "a", encoding="utf-8") as f:
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

def add_long_path_prefix(path):
    if sys.platform == 'win32' and not path.startswith('\\?\\?'):
        return f"\\\\?\\{os.path.abspath(path)}"
    return path

def check_disk_space(required_mb=500, path="."):
    if sys.platform == 'win32':
        try:
            free_bytes = ctypes.c_ulonglong(0)
            ctypes.windll.kernel32.GetDiskFreeSpaceExW(ctypes.c_wchar_p(path), None, None, ctypes.byref(free_bytes))
            free_mb = free_bytes.value / (1024 * 1024)
            return free_mb >= required_mb
        except: return True # Fail open if check fails
    return True

def log_memory_stats():    try:
        class MEMORYSTATUSEX(ctypes.Structure):
            _fields_ = [
                ("dwLength", ctypes.c_ulong),
                ("dwMemoryLoad", ctypes.c_ulong),
                ("ullTotalPhys", ctypes.c_ulonglong),
                ("ullAvailPhys", ctypes.c_ulonglong),
                ("ullTotalPageFile", ctypes.c_ulonglong),
                ("ullAvailPageFile", ctypes.c_ulonglong),
                ("ullTotalVirtual", ctypes.c_ulonglong),
                ("ullAvailVirtual", ctypes.c_ulonglong),
                ("ullAvailExtendedVirtual", ctypes.c_ulonglong),
            ]
        stat = MEMORYSTATUSEX()
        stat.dwLength = ctypes.sizeof(MEMORYSTATUSEX)
        ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(stat))
        
        total_mb = stat.ullTotalPhys / (1024 * 1024)
        avail_mb = stat.ullAvailPhys / (1024 * 1024)
        used_mb = total_mb - avail_mb
        percent = stat.dwMemoryLoad
        
        # ASCII Graphics
        bar_len = 20
        filled = int((percent / 100) * bar_len)
        bar = "█" * filled + "░" * (bar_len - filled)
        
        log(f"RAM: [{bar}] {percent}% | Used: {used_mb:.0f}MB / Total: {total_mb:.0f}MB | Free: {avail_mb:.0f}MB")
        return avail_mb
    except:
        log("RAM: [Unknown] (Check failed)")
        return 4096

# --- Matched Global Scanner Profiles 2024-2025 ---
SCANNER_PROFILES = [
    {"Brand": "Fujitsu", "Producer": "Fujitsu ScanSnap iX1600", "Creator": "ScanSnap Manager"},
    {"Brand": "Ricoh", "Producer": "Ricoh IM C4500", "Creator": "Ricoh Scan Router"},
    {"Brand": "Konica Minolta", "Producer": "Konica Minolta bizhub C250i", "Creator": "bizhub Scan Service"},
    {"Brand": "HP", "Producer": "HP LaserJet Enterprise MFP M776z", "Creator": "HP Scan Extended"},
    {"Brand": "Canon", "Producer": "Canon iR-ADV DX C5840i", "Creator": "imageRUNNER ADVANCE"},
    {"Brand": "Xerox", "Producer": "Xerox AltaLink C8130", "Creator": "Xerox AltaLink Service"},
    {"Brand": "Epson", "Producer": "Epson WorkForce DS-30000", "Creator": "Epson Document Capture"},
    {"Brand": "Kyocera", "Producer": "Kyocera ECOSYS M3645dn", "Creator": "Kyocera Quick Scan"},
    {"Brand": "Brother", "Producer": "Brother ADS-4700W", "Creator": "Brother ControlCenter4"},
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
        result = subprocess.run(cmd, capture_output=True, text=True, creationflags=creation_flags, timeout=30)
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            if lines: return int(lines[0])
    except: pass
    return 1

def process_single_page(page_idx, file_path, read_dpi, quality, im_limits, magick_exe, tmpdir, metadata_args):
    page_out = os.path.join(tmpdir, f"page_{{page_idx:04d}}.pdf")
    cmd = [magick_exe] + im_limits + [
           "-density", read_dpi, f"{file_path}[{{page_idx}}]", 
           "-alpha", "remove", "-alpha", "off", 
           "-filter", "Lanczos", "-distort", "Resize", "95%", 
           "-unsharp", "0x0.5",
           "-sampling-factor", "4:2:0", 
           "-compress", "jpeg", 
           "-quality", quality] + metadata_args + [page_out]
    
    creation_flags = 0x08000000 if sys.platform == 'win32' else 0
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, creationflags=creation_flags, timeout=PAGE_TIMEOUT)
        return page_out if res.returncode == 0 and os.path.exists(page_out) else None
    except subprocess.TimeoutExpired:
        log(f"Timeout processing page {page_idx}")
        return None
    except Exception as e:
        log(f"Error processing page {page_idx}: {e}")
        return None

def optimize_pdf(file_path, dpi):
    log(f"--- SESSION START v4.4.0 (Industrial): {file_path} ---")
    try:
        file_path = os.path.abspath(file_path)
        if not os.path.exists(file_path): return "Error: File missing."
        input_size = os.path.getsize(file_path)

        # 1. Disk Space Check
        if not check_disk_space(required_mb=max(500, (input_size * 3) / (1024*1024)), path=os.path.dirname(file_path)):
             return "Error: Low disk space."

    except Exception as e:
        log_error(e)
        return f"Error reading input: {e}"

    original_file_path = file_path
    temp_pdf_from_word = None

    # Word Conversion with Timeout
    ext = os.path.splitext(file_path)[1].lower()
    if ext in ['.doc', '.docx']:
        converter_script = os.path.join(BASE_DIR, "src", "docx2pdf.vbs")
        temp_pdf_from_word = os.path.join(os.path.dirname(file_path), f"~temp_{{os.path.basename(file_path)}}.pdf")
        try:
            conv_cmd = ["cscript", "//NoLogo", converter_script, file_path, temp_pdf_from_word]
            creation_flags = 0x08000000 if sys.platform == 'win32' else 0
            subprocess.run(conv_cmd, capture_output=True, creationflags=creation_flags, timeout=WORD_TIMEOUT)
            if os.path.exists(temp_pdf_from_word): file_path = temp_pdf_from_word
            else: return "Error: Word conversion failed."
        except subprocess.TimeoutExpired:
             return "Error: Word conversion timeout."
        except Exception as e:
            log_error(e)
            return f"Error converting Word: {e}"

    gs_exe = find_ghostscript()
    magick_exe = find_magick()
    if not gs_exe or not magick_exe: return "Error: External tools missing."

    page_count = get_page_count(magick_exe, file_path)
    final_output_path = f"{os.path.splitext(original_file_path)[0]}_{{dpi}}dpi.pdf"
    
    # 2. Adaptive Resource Management
    # avail_mem = get_available_memory_mb() # Deprecated
    avail_mem = log_memory_stats()
    
    if avail_mem < 2048:
        max_workers = 1
        im_ram = "256MiB"
        im_map = "512MiB"
        log("Mode: LOW MEMORY (Sequential)")
    elif avail_mem < 4096:
        max_workers = min(2, os.cpu_count() or 2)
        im_ram = "384MiB"
        im_map = "768MiB"
        log("Mode: BALANCED")
    else:
        max_workers = os.cpu_count() or 4
        im_ram = "512MiB"
        im_map = "1GiB"
        log(f"Mode: PERFORMANCE ({max_workers} threads)")

    im_limits = ["-limit", "memory", im_ram, "-limit", "map", im_map, "-limit", "area", "256MiB"]
    quality = "40" if str(dpi) == "30" else "70"
    read_dpi = "150" if str(dpi) == "30" else str(dpi)
    
    profile = random.choice(SCANNER_PROFILES)
    metadata_args = get_matched_metadata(profile)

    success = False
    temp_output = f"{final_output_path}.tmp"

    try:
        if page_count > 1:
            with tempfile.TemporaryDirectory() as tmpdir:
                processed_pages_map = {}
                with ThreadPoolExecutor(max_workers=max_workers) as executor:
                    futures = {executor.submit(process_single_page, i, add_long_path_prefix(file_path), read_dpi, quality, im_limits, magick_exe, tmpdir, metadata_args): i for i in range(page_count)}
                    for future in as_completed(futures):
                        idx = futures[future]
                        res_path = future.result()
                        if res_path: processed_pages_map[idx] = res_path
                        else: return f"Error on page {idx}"

                sorted_pages = [processed_pages_map[i] for i in range(page_count)]
                merge_cmd = [gs_exe, "-dNOPAUSE", "-sDEVICE=pdfwrite", f"-sOUTPUTFILE={temp_output}", "-dBATCH"] + sorted_pages
                res_merge = subprocess.run(merge_cmd, capture_output=True, text=True, creationflags=0x08000000, timeout=MERGE_TIMEOUT)
                if res_merge.returncode == 0: success = True
        else:
            cmd = [magick_exe] + im_limits + ["-density", read_dpi, add_long_path_prefix(file_path), "-alpha", "remove", "-alpha", "off", "-filter", "Lanczos", "-distort", "Resize", "95%", "-unsharp", "0x0.5", "-sampling-factor", "4:2:0", "-compress", "jpeg", "-quality", quality] + metadata_args + [temp_output]
            res = subprocess.run(cmd, capture_output=True, creationflags=0x08000000, timeout=PAGE_TIMEOUT)
            if res.returncode == 0: success = True

        # 3. Atomic Write
        if success and os.path.exists(temp_output):
             if os.path.exists(final_output_path):
                 try: os.remove(final_output_path)
                 except: pass # Will fail if file is locked, but rename might still fail
             os.rename(temp_output, final_output_path)
             
             output_size = os.path.getsize(final_output_path)
             diff = input_size - output_size
             pct = (diff / input_size) * 100 if input_size > 0 else 0
             log(f"SUCCESS: {format_size(output_size)} (-{pct:.1f}%)")
             return f"Done! Reduced by {pct:.0f}% ({format_size(output_size)})"
        
        return "Optimization failed (No output)."

    except Exception as e:
        log_error(e)
        return f"Error: {str(e)}"
    finally:
        # 4. Aggressive Cleanup
        for f in [temp_pdf_from_word, temp_output]:
            if f and os.path.exists(f):
                try: os.remove(f)
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
