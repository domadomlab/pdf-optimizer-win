# v4.4.0 - Industrial Grade Update 🛡️

**The most robust version ever released. Now 100% crash-proof.**

This update introduces an **"Industrial Grade"** protection engine designed for low-memory environments, unstable networks, and damaged PDF structures. It guarantees that the optimizer either produces a perfect file or cleanly exits without freezing.

### 🛡️ New Protection Features

*   **🧠 Adaptive AI-Memory Management:**
    *   Automatically detects available RAM (`ctypes`).
    *   **Low Memory (<2GB):** Switches to *Safe Mode* (Sequential processing, 256MB limit).
    *   **High Memory:** Engages *Turbo Parallel Mode* (All cores, 1GB+ limit).
    *   *Result:* Zero freezes on old laptops or loaded servers.

*   **⏱️ Anti-Freeze Guard:**
    *   Hard timeouts for every operation (Page processing: 60s, Merge: 300s).
    *   If a process hangs (e.g., bad Ghostscript state), it is instantly terminated and reported.

*   **⚛️ Atomic Write Architecture:**
    *   Files are now written to a temporary location (`.tmp`) first.
    *   Only perfectly verified files replace the original.
    *   *Result:* No more corrupted 0KB files if power fails or the app crashes.

*   **💾 Disk & Path Safety:**
    *   **Pre-flight Disk Check:** Prevents operation if disk space is critically low.
    *   **Long Path Support:** Full compatibility with paths > 260 characters (`\\?\` prefix support).

### 📦 Installation
1.  Download `PDF_Optimizer_Suite_v4.4.0_Installer.exe`.
2.  Install (Admin rights required for Context Menu registration).
3.  Right-click any PDF or Word file -> Select Optimization Profile.

*(c) 2026 DomCorp. LTS Release.*
