import sys
import os
import subprocess
import shutil
import ctypes
from datetime import datetime

# Папка, где лежит скрипт
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_FILE = os.path.join(BASE_DIR, "log_config.txt")

# По умолчанию логи в ту же папку, где скрипт
LOG_DIR = BASE_DIR

# Пытаемся прочитать путь к инсталлеру (место для логов)
if os.path.exists(CONFIG_FILE):
    try:
        # NSIS пишет в системной кодировке (обычно cp1251 или utf-8)
        with open(CONFIG_FILE, "r", encoding="utf-8", errors="ignore") as f:
            saved_path = f.read().strip()
            if os.path.isdir(saved_path):
                LOG_DIR = saved_path
    except:
        LOG_DIR = os.environ.get('TEMP', BASE_DIR)

LOG_FILE = os.path.join(LOG_DIR, 'pdf_optimizer_debug.log')

def log(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    msg = f"[{timestamp}] {message}\n"
    try:
        # Пробуем записать. Если не удается (нет прав), пишем в Temp
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(msg)
    except:
        try:
            temp_log = os.path.join(os.environ.get('TEMP', 'C:\\Temp'), 'pdf_optimizer_backup.log')
            with open(temp_log, "a", encoding="utf-8") as f:
                f.write(f"Fallback Log (Original failed): {msg}")
        except: pass

def find_tool(tool_name, registry_path=None):
    path = shutil.which(tool_name)
    if path: return path
    if registry_path:
        try:
            import winreg
            for root in [winreg.HKEY_LOCAL_MACHINE, winreg.HKEY_CURRENT_USER]:
                try:
                    key = winreg.OpenKey(root, registry_path)
                    val, _ = winreg.QueryValueEx(key, "BinPath")
                    full_path = os.path.join(val, f"{tool_name}.exe")
                    if os.path.exists(full_path): return full_path
                except: continue
        except: pass
    return None

def optimize_pdf(file_path, dpi):
    log(f"--- SESSION START v3.0.3: {file_path} ---")
    
    gs_exe = find_tool("gswin64c") or find_tool("gswin32c")
    if gs_exe:
        os.environ["PATH"] += os.pathsep + os.path.dirname(gs_exe)
        log(f"GS found: {gs_exe}")

    magick_exe = find_tool("magick", r"Software\ImageMagick\Current")
    if not magick_exe:
        log("ERROR: ImageMagick not found.")
        return "ImageMagick not found."

    output_path = f"{os.path.splitext(file_path)[0]}_{dpi}dpi.pdf"
    cmd = [magick_exe, "-density", str(dpi), "-units", "PixelsPerInch", file_path, 
           "-alpha", "remove", "-alpha", "off", "-compress", "jpeg", "-quality", "80", "+profile", "*", output_path]

    try:
        log(f"CMD: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            log("SUCCESS")
            return "Optimization Successful!"
        else:
            log(f"FAILED: {result.stderr}")
            return f"Error: {result.stderr}"
    except Exception as e:
        log(f"CRITICAL: {str(e)}")
        return str(e)

def main():
    if len(sys.argv) < 3: return
    res = optimize_pdf(sys.argv[2], sys.argv[1])
    ctypes.windll.user32.MessageBoxW(0, res, "PDF Optimizer Suite", 64)

if __name__ == "__main__":
    main()
