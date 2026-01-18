# 🚀 PDF Optimizer Suite v3.6

> **The Ghost in the Shell.**  
> *Professional compression & privacy tool integrated directly into Windows Explorer.*

![Version](https://img.shields.io/github/v/release/domadomlab/pdf-optimizer-win?style=for-the-badge&color=blueviolet)
![Platform](https://img.shields.io/badge/Windows-11%20%2F%2010-0078D6?style=for-the-badge&logo=windows)
![Privacy](https://img.shields.io/badge/Privacy-100%25-success?style=for-the-badge&logo=torproject)
![Downloads](https://img.shields.io/github/downloads/domadomlab/pdf-optimizer-win/total?style=for-the-badge&color=orange)

---

## 🕶️ What is this?

This is not just a PDF compressor. It is a **stealth utility** for your workflow.
**PDF Optimizer Suite** adds powerful, server-grade processing tools to your Right-Click Menu. It runs offline, silently, and leaves no trace.

## 🔥 Killer Features (v3.6)

### 🥷 Camouflage Mode (New!)
**Plausible Deniability Engine.**
When you optimize a file, the software strips all original metadata (software traces, timestamps) and injects **fake digital fingerprints** of real physical scanners.
*   Your PDF will look like it was scanned on an **HP LaserJet**, **Xerox WorkCentre**, or **Canon iR-ADV**.
*   Even the internal PDF structure is rewritten to mimic hardware encoding.

### 🔇 Silent Batch Processing
**Efficiency Redefined.**
Select 1 file or 100 files. Right-click. Done.
*   No annoying popup windows.
*   System Tray notifications keep you informed without stealing focus.
*   Multi-threaded processing handles bulk tasks in seconds.

### ⚡ Native Integration
*   **Power Registration:** Uses advanced PowerShell injection to ensure the menu works on ANY Windows locale (perfect Cyrillic support).
*   **Seamless Updates:** Updates the Windows Shell instantly—no restart required.

---

## 🇷🇺 Русское описание

**PDF Optimizer Suite** — это профессиональный инструмент для тех, кто ценит время и приватность. Мы перенесли серверные технологии сжатия прямо в контекстное меню Windows.

### Почему это круто?

1.  **Режим "Хамелеон" (v3.6):** Программа не просто сжимает файл, она "пересобирает" его, подменяя метаданные. Ваш PDF будет выглядеть так, будто его только что отсканировали на офисном МФУ (HP, Canon, Xerox). Никаких следов Word или PDF редакторов.
2.  **Тихий режим:** Выделите 50 файлов, нажмите "Оптимизировать" и продолжайте работать. Уведомления появятся в трее, не прерывая ваш рабочий процесс.
3.  **Умная установка:** Инсталлятор сам найдет или скачает Python и настроит все зависимости.

### 📥 [Download Latest Installer / Скачать](https://github.com/domadomlab/pdf-optimizer-win/releases/latest)

---

## 🏗️ Build from Source / Сборка

If you want to build the installer yourself (requires NSIS):

1.  Clone repository:
    ```bash
    git clone https://github.com/domadomlab/pdf-optimizer-win.git
    cd pdf-optimizer-win
    ```
2.  **Download dependencies** (Python, Ghostscript, ImageMagick):
    *   **Windows:** Run `download_deps.bat`
    *   **Linux/WSL:** Run `bash download_deps.sh`
3.  Compile with NSIS:
    *   **Windows:** Right-click `installer.nsi` -> *Compile NSIS Script*
    *   **Linux:** `makensis installer.nsi`

---

## 🛠️ Profiles / Режимы

| Profile | DPI | Use Case |
| :--- | :--- | :--- |
| **Eco** | 75 | **Maximum Compression.** For archives and quick previews. |
| **Email** | 150 | **Balanced.** Perfect for email attachments. Crystal clear text. |
| **Print** | 200 | **Office Standard.** Great for printing and official documents. |
| **High** | 300 | **Professional.** Pre-press quality. Retains fine details. |

---
*Developed by DomCorp (c) 2026. Open Source. MIT License.*
