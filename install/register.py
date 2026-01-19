import sys
import os
import winreg
import ctypes

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def register_key(hive, key_path, value_name, value_data, value_type=winreg.REG_SZ):
    try:
        # Create or open the key
        key = winreg.CreateKeyEx(hive, key_path, 0, winreg.KEY_SET_VALUE | winreg.KEY_WRITE)
        winreg.SetValueEx(key, value_name, 0, value_type, value_data)
        winreg.CloseKey(key)
        # print(f"[OK] Registered: {key_path} -> {value_name}={value_data}")
        return True
    except Exception as e:
        print(f"[ERROR] Failed to register {key_path}: {e}")
        return False

def main():
    if len(sys.argv) < 5:
        print("Usage: register.py <python_exe> <script_path> <launcher_vbs> <lang_code>")
        return

    python_exe = sys.argv[1]
    script_path = sys.argv[2]
    launcher_vbs = sys.argv[3]
    lang_code = sys.argv[4].upper()

    print(f"--- Python Registry Setup ---")
    print(f"Python: {python_exe}")
    print(f"Script: {script_path}")
    print(f"Lang: {lang_code}")

    # Menu Names
    if lang_code == 'RU':
        menu_names = {
            '30': 'PDF: Экстрим (Min Size)',
            '75': 'PDF: Эко (75 dpi)',
            '150': 'PDF: Почта (150 dpi)',
            '200': 'PDF: Печать (200 dpi)',
            '300': 'PDF: Качество (300 dpi)'
        }
    else:
        menu_names = {
            '30': 'PDF: Extreme (Min Size)',
            '75': 'PDF: Eco (75 dpi)',
            '150': 'PDF: Email (150 dpi)',
            '200': 'PDF: Print (200 dpi)',
            '300': 'PDF: High (300 dpi)'
        }

    # Registry Roots to target
    # We try both HKLM (System) and HKCU (User)
    roots = [
        (winreg.HKEY_CURRENT_USER, r"Software\Classes\SystemFileAssociations\.pdf\shell"),
        (winreg.HKEY_CURRENT_USER, r"Software\Classes\.pdf\shell"),
        (winreg.HKEY_CURRENT_USER, r"Software\Classes\SystemFileAssociations\.docx\shell"),
        (winreg.HKEY_CURRENT_USER, r"Software\Classes\.docx\shell"),
        (winreg.HKEY_CURRENT_USER, r"Software\Classes\SystemFileAssociations\.doc\shell"),
        (winreg.HKEY_CURRENT_USER, r"Software\Classes\.doc\shell"),
        (winreg.HKEY_CURRENT_USER, r"Software\Classes\*\shell"),
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Classes\SystemFileAssociations\.pdf\shell"),
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Classes\SystemFileAssociations\.docx\shell"),
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Classes\SystemFileAssociations\.doc\shell")
    ]

    success_count = 0

    for root_hive, root_path in roots:
        try:
            # Try to create the root path first
            try:
                winreg.CreateKey(root_hive, root_path)
            except OSError:
                # Permission denied or similar, skip this root
                continue

            for dpi, name in menu_names.items():
                key_base = f"{root_path}\\PDFOptimizer{dpi}"
                
                # 1. Menu Name
                if register_key(root_hive, key_base, "", name):
                    success_count += 1
                
                # 2. Icon
                register_key(root_hive, key_base, "Icon", "shell32.dll,166")
                
                # 3. Command
                # wscript.exe "launcher" "python" "script" dpi "%1"
                cmd_val = f'wscript.exe "{launcher_vbs}" "{python_exe}" "{script_path}" {dpi} "%1"'
                register_key(root_hive, f"{key_base}\\command", "", cmd_val)

        except Exception as e:
            print(f"Skipping root {root_path}: {e}")

    print(f"Registry keys set: {success_count} (groups)")

    # Notify Shell
    try:
        ctypes.windll.shell32.SHChangeNotify(0x08000000, 0, 0, 0) # SHCNE_ASSOCCHANGED
        print("Shell Notified.")
    except:
        pass

if __name__ == "__main__":
    main()
