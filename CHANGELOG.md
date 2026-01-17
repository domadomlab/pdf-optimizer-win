# Changelog - PDF Optimizer Suite

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
