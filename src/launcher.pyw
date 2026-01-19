import sys
import subprocess
import os

# This is a transparent proxy to launch the main optimizer hiddenly
# while ensuring 100% Unicode support for file paths.

def main():
    if len(sys.argv) < 5:
        return

    # args: launcher.pyw <python_exe> <script_path> <dpi> <pdf_path>
    py_exe = sys.argv[1]
    script_path = sys.argv[2]
    dpi = sys.argv[3]
    pdf_path = sys.argv[4]

    # Build command
    cmd = [py_exe, script_path, dpi, pdf_path]

    # Spawn process without window
    try:
        creation_flags = 0x08000000  # CREATE_NO_WINDOW
        subprocess.Popen(cmd, creationflags=creation_flags, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except:
        pass

if __name__ == "__main__":
    main()
