import sys
import os
import subprocess
import shutil
import ctypes # For MessageBox
from datetime import datetime

# --- Configuration ---
DEFAULT_DPI = 200
LOG_FILE = os.path.join(os.environ.get('TEMP', 'C:\\Temp'), 'pdf_optimizer.log')

def log(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    formatted_message = f"[{timestamp}] {message}"
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(formatted_message + "\n")
    except Exception:
        pass # Fail silently on logging errors
    print(formatted_message)

def show_message(title, text, style=0):
    # Styles: 0=OK, 1=OK/Cancel, 48=Warning, 64=Info
    try:
        ctypes.windll.user32.MessageBoxW(0, text, title, style)
    except Exception as e:
        log(f"Error showing message box: {e}")

def optimize_pdf(file_path, dpi):
    if not os.path.exists(file_path):
        log(f"File not found: {file_path}")
        return False

    directory = os.path.dirname(file_path)
    filename = os.path.basename(file_path)
    name, ext = os.path.splitext(filename)
    
    output_filename = f"{name}_{dpi}dpi{ext}"
    output_path = os.path.join(directory, output_filename)

    log(f"Processing: {filename} -> {output_filename} @ {dpi} DPI")

    # Check for ImageMagick
    magick_cmd = "magick"
    if not shutil.which(magick_cmd):
        # Try legacy 'convert' if 'magick' is not found, though on Windows 'convert' is often system tool
        # Better to rely on 'magick' being in PATH from modern ImageMagick installers
        log("Error: 'magick' command not found. Please install ImageMagick.")
        show_message("PDF Optimizer Error", "ImageMagick ('magick' command) not found in PATH.\nPlease install ImageMagick for Windows.", 16) # 16 = Critical Error
        return False

    # Construct command
    # convert -density {dpi} -units PixelsPerInch "{input}" -alpha remove -alpha off -compress jpeg -quality 80 +profile "*" "{output}"
    cmd = [
        magick_cmd,
        "-density", str(dpi),
        "-units", "PixelsPerInch",
        file_path,
        "-alpha", "remove",
        "-alpha", "off",
        "-compress", "jpeg",
        "-quality", "80",
        "+profile", "*",
        output_path
    ]

    try:
        # Run subprocess, hiding the console window if possible
        startupinfo = None
        if os.name == 'nt':
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

        result = subprocess.run(cmd, capture_output=True, text=True, startupinfo=startupinfo)

        if result.returncode == 0 and os.path.exists(output_path):
            old_size = os.path.getsize(file_path)
            new_size = os.path.getsize(output_path)
            
            size_diff_mb = (old_size - new_size) / (1024 * 1024)
            result_msg = f"Done!\nOld: {old_size/1024:.1f} KB\nNew: {new_size/1024:.1f} KB"
            
            if new_size > old_size:
                result_msg += "\n\nWarning: File size increased!"
                log(f"Warning: Size increased for {filename}")
            else:
                 log(f"Success: Reduced by {size_diff_mb:.2f} MB")

            return result_msg
        else:
            err_msg = f"Magick Error: {result.stderr}"
            log(err_msg)
            return f"Error optimizing {filename}.\nSee log at {LOG_FILE}"

    except Exception as e:
        log(f"Exception: {e}")
        return f"Critical error: {e}"

def main():
    if len(sys.argv) < 2:
        print("Usage: python optimizer.py [dpi] [file_path]")
        return

    # Parse arguments
    # Expected: script.py [dpi] [file] OR script.py [file] (defaults dpi)
    
    first_arg = sys.argv[1]
    file_path = ""
    dpi = DEFAULT_DPI

    if first_arg.isdigit():
        dpi = int(first_arg)
        if len(sys.argv) > 2:
            file_path = sys.argv[2]
    else:
        file_path = first_arg

    if not file_path:
        print("No file specified.")
        return

    # Run optimization
    result_message = optimize_pdf(file_path, dpi)
    
    if result_message:
        show_message("PDF Optimizer Result", result_message, 64) # 64 = Info

if __name__ == "__main__":
    main()
