# Changelog - PDF Optimizer Suite

## [3.9.0] - 2026-01-19
### Added
- **Extreme Mode (Min Size)**: Integrated a new scientific compression strategy based on **Trellis-Quantization Mimic**. It uses Lanczos filtering and adaptive 95% resizing to achieve up to 83% file size reduction while maintaining high text legibility.
- **Scientific Engine Update**: Optimized ImageMagick pipeline for all presets based on DSP (Digital Signal Processing) benchmarks.

## [3.8.4] - 2026-01-19
### Fixed
- **Word Template Lock**: Fixed an issue where MS Word would prompt about `Normal.dot` being in use or modified. Added explicit suppression of template save prompts in `docx2pdf.vbs`.

## [3.8.3] - 2026-01-19
### Fixed
- **Critical Syntax Error**: Fixed a typo (extra parenthesis) in the optimization script that prevented the application from running in v3.8.2.

## [3.8.2] - 2026-01-19
### Fixed
- **Temp File Leak**: Rewrote the optimization logic to use a `try...finally` block. This guarantees that temporary PDF files generated during Word conversion are deleted in 100% of cases (success, error, or crash).

## [3.8.1] - 2026-01-19
### Fixed
- **Naming Logic**: Fixed a bug where converted Word documents resulted in filenames like `~temp_Name.doc_75dpi.pdf`. Now the output filename is correctly derived from the original document name: `Name_75dpi.pdf`.
- **Temp Cleanup**: Improved temporary file cleanup logic to ensure intermediate PDF files are always removed, even if optimization fails.

## [3.8.0] - 2026-01-19
### Added
- **Word to PDF Conversion**: Added support for `.docx` and `.doc` files. The application now uses an installed Microsoft Word instance (via VBScript automation) to silently convert documents to PDF before optimizing them. This ensures 100% layout fidelity.
- **Extended Context Menu**: The "PDF: ..." context menu options now appear for Word documents as well.

## [3.7.2] - 2026-01-19
### Fixed
- **Registration Engine**: Replaced VBScript/PowerShell registration logic with a **Native Python Script** (`register.py`). Since the application now includes its own Python runtime, this ensures 100% reliable registry modification with full Unicode support and no dependency on Windows Script Host or PowerShell policies.

## [3.7.1] - 2026-01-19
### Fixed
- **Corporate Compatibility**: Replaced PowerShell registration script with **VBScript**. This bypasses "Execution Policy" restrictions and AppLocker blocks common in corporate environments, ensuring the context menu is successfully created.
- **Path Handling**: Improved path escaping in the generated VBScript to handle spaces and special characters robustly.

## [3.7.0] - 2026-01-19
### Added
- **Portable Architecture**: Switched to **Embedded Python 3.12**. The application now carries its own isolated Python environment, eliminating the need for system-wide installation. This resolves compatibility issues on Corporate/LTSC Windows versions with strict security policies (GPO, AppLocker).
- **Setup Reliability**: Removed all dependency on system PATH or Registry for Python detection.
### Changed
- **Installer Size**: Increased by ~10 MB due to embedded Python runtime.

## [3.6.5] - 2026-01-19
### Fixed
- **Python Detection**: Improved `Setup_Full.bat` to perform a double-check for Python. It now verifies the direct existence of `pythonw.exe` in standard directories if the `python` command is missing from PATH, preventing false negatives during installation.

## [3.6.4] - 2026-01-19
### Fixed
- **Zero-Window Policy**: Completely switched the execution engine to **VBScript** (`launcher.vbs`).
    - The registry now calls `wscript.exe` (Windows Script Host), which natively supports running commands without ANY console window.
    - This bypasses `py.exe` and `cmd.exe` window flashes entirely.
    - Python and ImageMagick are invoked as hidden subprocesses from within the VBS wrapper.

## [3.6.3] - 2026-01-19
### Fixed
- **Compression Size**: Reverted from JPEG 2000 back to standard **JPEG** engine. The JP2 implementation caused file size inflation on certain document types.
- **Console Windows**: Implemented `CREATE_NO_WINDOW` flag and `stdin` redirection for all subprocesses. This definitively solves the issue of flashing console windows during operation.
### Changed
- **Optimization Strategy**: Now using **JPEG Quality 70** + **Chroma Subsampling 4:2:0**. This combination provides the most reliable file size reduction (~15-20% better than standard settings) while maintaining text legibility.
- **Logging**: Added detailed file size statistics (Input vs Output) to the log file and user notification.

## [3.6.2] - 2026-01-19
### Changed
- **Compression Engine**: Switched from standard JPEG to **JPEG 2000 (.jp2)**. This modern algorithm provides 30-50% better compression at the same visual quality.
- **Quality Tuning**: Adjusted default quality setting from 80 to **75**. Combined with JPEG 2000, this offers superior file size reduction without visible artifacts.
- **Chroma Subsampling**: Enabled **4:2:0 subsampling**. This optimizes color data storage, significantly reducing file size for scanned documents while keeping text sharp.
- **Privacy**: Retained strict metadata stripping and "Camouflage Mode" from v3.6.1.

## [3.6.1] - 2026-01-19
### Added
- **Camouflage Mode**: Added fake metadata injection. Optimized files now masquerade as scans from popular office hardware (HP, Canon, Xerox) to ensure privacy and plausible deniability.
- **Silent Mode**: Replaced intrusive popup windows with non-blocking Windows System Tray notifications (via PowerShell).
- **Power Registration**: Implemented Base64-encoded PowerShell commands for registry injection, solving all character encoding issues with Cyrillic paths.
- **Seamless Updates**: Added `SHChangeNotify` call to instantly refresh Windows Explorer context menu after installation.

## [3.6.0] - 2026-01-18
### Added
- **Camouflage Foundation**: Initial implementation of metadata randomization logic.
- **Silent Notifications**: Beta version of PowerShell-based notification system.

## [3.5.0] - 2026-01-17
### Added
- **Multilingual Support**: The installer now prompts the user to select a language (English/Russian) at startup.
- **Dynamic Context Menu**: The context menu labels now adapt to the selected installation language (e.g., "PDF: Email" vs "PDF: Почта").

## [3.4.4] - 2026-01-17
### Changed
- **Repo Structure**: Moved `installer.nsi` inside the repository for better version control.
- **Build Process**: Updated installer script to copy files relative to the project root, ensuring a cleaner build without accidental inclusion of `.git` or parent directory artifacts.

## [3.4.3] - 2026-01-17
### Fixed
- **Uninstaller Update**: Added removal logic for the new "75 DPI" registry keys. The uninstaller now correctly cleans up all four menu entries (75, 150, 200, 300) from all registry locations.

## [3.4.2] - 2026-01-17
### Changed
- **Distribution Cleanup**: Added an explicit exclusion rule to prevent installer executables (if present in source) from being copied into the `src` folder of the installation directory. They are only needed in `resources`.

## [3.4.1] - 2026-01-17
### Changed
- **Menu Labels**: Switched to short English labels for a more professional and compact context menu:
    - PDF: Eco (75 dpi)
    - PDF: Email (150 dpi)
    - PDF: Print (200 dpi)
    - PDF: High (300 dpi)

## [3.4.0] - 2026-01-17
### Added
- **New Menu Preset**: Added "Minimum" (75 DPI) option for extreme file size reduction.
- **Localized Menu Names**: Replaced technical English names with user-friendly Russian labels:
    - PDF: Минимум (75 dpi)
    - PDF: Для почты (150 dpi)
    - PDF: Для печати (200 dpi)
    - PDF: Качественно (300 dpi)

## [3.3.5] - 2026-01-17
### Fixed
- **Python Detection Final**: Re-implemented the direct disk path check for Python. The installer now looks for `pythonw.exe` in `Program Files`, `AppData`, and other standard locations if the registry query fails. This ensures successful context menu registration even if the registry is lagging or inaccessible.

## [3.3.4] - 2026-01-17
### Added
- **Global Context Menu Test**: Registered context menu for ALL files (`*`) in addition to PDF files. This is a diagnostic measure to determine if the `.pdf` extension is being exclusively locked by another application.
- **UI Refresh**: Re-enabled Explorer restart to force registry changes to take effect immediately.

## [3.3.3] - 2026-01-17
### Added
- **Python Self-Healing**: Added `/repair` flag to the Python installation step. If Python is already present but broken (e.g., missing registry keys), the installer will now attempt to repair the existing installation to restore functionality.

## [3.3.2] - 2026-01-17
### Critical Fix
- **Installer Logic**: Fixed a syntax error in `Setup_Full.bat` (missing `EnableDelayedExpansion`) that caused the Python installer path to be misread as a literal string `!INSTALLER!`. This prevented Python from installing on clean systems.

## [3.3.1] - 2026-01-17
### Fixed
- **Python Installation Debug**: Added detailed logging to the Python installation step (`Setup_Full.bat`). Now logs whether the installer file was found, the result of the version check, and confirmation of installer execution.

## [3.3.0] - 2026-01-17
### Added
- **Triple Registry Injection**: The installer now registers the context menu in three separate registry locations simultaneously:
    1. `HKLM\...\SystemFileAssociations` (Global)
    2. `HKCU\...\SystemFileAssociations` (User)
    3. `HKCU\Software\Classes\.pdf` (Direct Extension Override)
    This "nuclear" approach ensures the menu appears on almost any Windows configuration, bypassing issues with SystemFileAssociations logic.

## [3.2.9] - 2026-01-17
### Changed
- **Debug Logging**: Greatly expanded logging during installation (Setup_Full.bat and install.bat) to diagnose Python detection issues. Logs now include registry query results and file path checks.

## [3.2.8] - 2026-01-17
### Fixed
- **Python Detection**: Implemented robust Python discovery via Windows Registry (HKLM/HKCU). This fixes the issue where context menu registration failed because Python couldn't be located.
### Changed
- **Packaging**: Disabled installer compression to ensure maximum speed and compatibility during installation.

## [3.2.7] - 2026-01-17
### Fixed
- **Context Menu Missing**: Restored "Dual Registration" logic. Context menu entries are now written to both `HKLM` (System-wide) and `HKCU` (Current User) registries to guarantee visibility even if system policies restrict one or the other.

## [3.2.6] - 2026-01-17
### Changed
- **Optimization**: Switched to LZMA Solid compression. This significantly reduces the installer size and improves start-up time by reducing disk I/O.

## [3.2.5] - 2026-01-17
### Changed
- **UX Improvement**: Installation details (file copying list) are now shown by default during the installation process.

## [3.2.4] - 2026-01-17
### Changed
- **Cleaner Distribution**: Excluded development files (.git, .gitignore, logs) from the installer package to reduce size and clutter.

## [3.2.3] - 2026-01-17
### Fixed
- **Installer Stability**: Replaced console execution with integrated logging window (`nsExec`) to prevent UI freezes.
- **Cleanup**: Removed aggressive Explorer restart and timeouts from the setup script.

## [3.2.2] - 2026-01-17
### Added
- **Auto-Uninstall**: Installer now automatically detects and removes previous versions before installation to ensure a clean update.
- **Registry Tracking**: Installation path is now saved to HKCU and HKLM to facilitate auto-detection.
- **Localization**: Full Russian language support for the installer interface.

## [3.1.6] - 2026-01-17
### Added
- Ultimate registry integration: menu is now registered in 6 locations (HKLM and HKCU) simultaneously.
- Short-path (8.3) format for all paths in registry to avoid space/quote issues.

## [3.1.0] - [3.1.5]
### Fixed
- UTF-8 encoding issues in Setup_Full.bat.
- Ghostscript silent installation using `/S` flag and Temp folder execution.
- Windowless execution using `pythonw.exe`.
- Dual registration logic (HKLM + HKCU).

## [3.0.0] - Anniversary Release
### Added
- Professional console UI for installer.
- Deep Uninstall: uninstaller now automatically removes Python, ImageMagick, and Ghostscript.
- Full documentation update.

## [2.9.0] - [2.9.8]
### Added
- Automatic Ghostscript integration (download and install).
- Intelligent logging system: logs are now saved in the same folder as the installer.
- Exit code tracking for dependency installers.

## [2.1.0] - [2.8.0]
### Evolution
- Migrated from simple `reg add` to `.reg` files, then to PowerShell, then back to `.reg` for maximum reliability.
- Introduced VBScript and Batch wrappers to handle Windows shell limitations.
- Implemented system-wide (HKLM) support.
