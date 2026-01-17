# Changelog - PDF Optimizer Suite

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
