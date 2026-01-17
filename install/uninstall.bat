@echo off
setlocal enabledelayedexpansion
title PDF Optimizer Suite - Silent Uninstall

:: Отключаем окна безопасности
set SEE_MASK_NOZONECHECKS=1

:: 1. CLEAN REGISTRY
set "PATHS=HKLM\SOFTWARE\Classes\SystemFileAssociations\.pdf\shell HKLM\SOFTWARE\Classes\.pdf\shell HKLM\SOFTWARE\Classes\*\shell"
for %%P in (%PATHS%) do (
    reg delete "%%P\PDFOptimizer150" /f >nul 2>&1
    reg delete "%%P\PDFOptimizer200" /f >nul 2>&1
    reg delete "%%P\PDFOptimizer300" /f >nul 2>&1
)

:: 2. SILENT UNINSTALL DEPENDENCIES

:: Ghostscript
for /f "tokens=2*" %%a in ('reg query "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall" /s /f "Ghostscript" 2^>nul ^| findstr "UninstallString"') do (
    set "UNINST=%%b"
    if defined UNINST (
        :: Добавляем /S для тихой деинсталляции Ghostscript
        start /wait "" !UNINST! /S
    )
)

:: ImageMagick
for /f "tokens=2*" %%a in ('reg query "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall" /s /f "ImageMagick" 2^>nul ^| findstr "UninstallString"') do (
    set "UNINST=%%b"
    if defined UNINST (
        start /wait "" !UNINST! /VERYSILENT
    )
)

:: Python 3.12
if exist "%~dp0..\resources\python-installer.exe" (
    start /wait "" "%~dp0..\resources\python-installer.exe" /uninstall /quiet
)

timeout /t 2 >nul