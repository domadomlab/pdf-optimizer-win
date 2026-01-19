# PDF Optimizer Suite 🚀

[![Release](https://img.shields.io/github/v/release/domadomlab/pdf-optimizer-win?style=for-the-badge&color=blue)](https://github.com/domadomlab/pdf-optimizer-win/releases/latest)
[![Platform](https://img.shields.io/badge/Platform-Windows%2010%2F11%2FLTSC-win?style=for-the-badge)](https://www.microsoft.com/windows)
[![License](https://img.shields.io/github/license/domadomlab/pdf-optimizer-win?style=for-the-badge)](LICENSE)

**The ultimate right-click tool for reducing PDF size, ensuring privacy, and converting documents.**
**Идеальный инструмент контекстного меню для сжатия PDF, защиты приватности и конвертации документов.**

---

## ✨ Features / Возможности

### 📉 Smart Compression / Умное Сжатие
Drastically reduce file size (up to 90%) while maintaining print-ready quality.
*   **75 DPI (Eco):** For archives and drafts.
*   **150 DPI (Email):** Perfect balance for sharing.
*   **200 DPI (Print):** High quality for documents.
*   **300 DPI (High):** Maximum fidelity.

### 🔄 Word Integration / Поддержка Word
Convert `.doc` and `.docx` directly to optimized PDF via the context menu. Requires MS Word installed.
*Конвертация `.doc` и `.docx` в PDF прямо из меню (требуется установленный Word).*

### 🕵️ Camouflage & Privacy / Маскировка
*   **Metadata Stripping:** Removes all Author, Creator, and GPS tags.
*   **Camouflage Mode:** Injects fake metadata to make the PDF look like a scan from a physical device (HP, Canon, Xerox).
*   *Очистка метаданных и маскировка под сканер.*

### 🛡️ Corporate Ready / Для Корпораций
*   **Portable Core:** Embedded Python engine. No admin rights required for runtime.
*   **Silent Operation:** No console windows, only system tray notifications.
*   **LTSC Compatible:** Works on restricted systems (bypasses PowerShell blocks).

---

## 🚀 Installation / Установка

1.  Download the latest [Release](https://github.com/domadomlab/pdf-optimizer-win/releases).
2.  Run `PDF_Optimizer_Suite_vX.X.X_Installer.exe`.
3.  Right-click any PDF or Word file to see the magic.

---

## 🛠 Tech Stack / Технологии

*   **Core:** Python 3.12 (Embedded)
*   **Imaging:** ImageMagick 7 + Ghostscript
*   **UI:** Native Windows Context Menu (Registry)
*   **Automation:** VBScript + Win32 COM

---

*(c) 2026 DomCorp. Licensed under MIT.*