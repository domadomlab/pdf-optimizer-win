!include "MUI2.nsh"
!include "FileFunc.nsh"
!include "LogicLib.nsh"

;--------------------------------
;General

  Name "PDF Optimizer Suite"
  OutFile "PDF_Optimizer_Suite_v4.1.1_Installer.exe"
  InstallDir "$PROGRAMFILES64\DomCorp\PDFOptimizer"
  InstallDirRegKey HKCU "Software\DomCorp\PDFOptimizer" ""
  RequestExecutionLevel admin
  ShowInstDetails show
  
  ; Disable compression
  SetCompress off

;--------------------------------
;Interface Configuration

  !define MUI_ABORTWARNING
  !define MUI_ICON "${NSISDIR}\Contrib\Graphics\Icons\modern-install.ico"
  !define MUI_UNICON "${NSISDIR}\Contrib\Graphics\Icons\modern-uninstall.ico"
  
  ; Language Selection Dialog Settings
  !define MUI_LANGDLL_ALLLANGUAGES

;--------------------------------
;Pages

  !insertmacro MUI_PAGE_WELCOME
  !insertmacro MUI_PAGE_LICENSE "LICENSE"
  !insertmacro MUI_PAGE_COMPONENTS
  !insertmacro MUI_PAGE_DIRECTORY
  !insertmacro MUI_PAGE_INSTFILES
  !insertmacro MUI_PAGE_FINISH

  !insertmacro MUI_UNPAGE_WELCOME
  !insertmacro MUI_UNPAGE_CONFIRM
  !insertmacro MUI_UNPAGE_INSTFILES
  !insertmacro MUI_UNPAGE_FINISH

;--------------------------------
;Languages

  !insertmacro MUI_LANGUAGE "English"
  !insertmacro MUI_LANGUAGE "Russian"

;--------------------------------
;Installer Sections

Section "Core Files (Required)" SecCore
  SectionIn RO
  SetOutPath "$INSTDIR"
  
  ; Копируем конкретные файлы и папки проекта
  File "LICENSE"
  File "README.md"
  File "CHANGELOG.md"
  File "Setup_Full.bat"
  File "PROJECT_DESCRIPTION.md"
  File "THIRD_PARTY_NOTICES.md"
  
  ; Копируем папки рекурсивно
  File /r "src"
  File /r "resources"
  File /r "install"
  ; Если есть папка docs, раскомментируйте:
  ; File /r "docs"

  ; Записываем путь установки в реестр (чтобы будущие инсталлеры его нашли)
  WriteRegStr HKCU "Software\DomCorp\PDFOptimizer" "" "$INSTDIR"
  WriteRegStr HKLM "Software\DomCorp\PDFOptimizer" "" "$INSTDIR"

  ; Сохраняем путь к папке с инсталлером (откуда он запущен) в конфиг для логов
  FileOpen $0 "$INSTDIR\log_config.txt" w
  FileWrite $0 "$EXEDIR"
  FileClose $0

  WriteUninstaller "$INSTDIR\uninstall.exe"
SectionEnd

Section "Configuration & Dependencies" SecSetup
  SetOutPath "$INSTDIR"
  DetailPrint "Running Full Setup (Python, ImageMagick, Context Menu)..."
  
  ; Определяем код языка для передачи в батник
  StrCpy $R1 "EN" ; Default to English
  ${If} $LANGUAGE == 1049
    StrCpy $R1 "RU"
  ${EndIf}
  
  ; Передаем $EXEDIR как аргумент для логирования и $R1 как язык (RU/EN)
  ; Используем nsExec::ExecToLog чтобы видеть вывод консоли прямо в окне установки
  nsExec::ExecToLog '"$INSTDIR\Setup_Full.bat" "$EXEDIR" "$R1"'
SectionEnd

;--------------------------------
;Descriptions

  LangString DESC_SecCore ${LANG_RUSSIAN} "Основные файлы программы, лицензии и скрипты."
  LangString DESC_SecSetup ${LANG_RUSSIAN} "Автоматическая настройка: проверка/установка Python 3.12, ImageMagick и регистрация в контекстном меню."
  LangString DESC_SecCore ${LANG_ENGLISH} "Core program files, licenses, and scripts."
  LangString DESC_SecSetup ${LANG_ENGLISH} "Auto-setup: Checks/Installs Python 3.12, ImageMagick, and registers context menu."

  !insertmacro MUI_FUNCTION_DESCRIPTION_BEGIN
    !insertmacro MUI_DESCRIPTION_TEXT ${SecCore} $(DESC_SecCore)
    !insertmacro MUI_DESCRIPTION_TEXT ${SecSetup} $(DESC_SecSetup)
  !insertmacro MUI_FUNCTION_DESCRIPTION_END

;--------------------------------
;Functions

Function .onInit
  ; Show Language Selection Dialog
  !insertmacro MUI_LANGDLL_DISPLAY

  ; Check for previous installation
  ReadRegStr $R0 HKCU "Software\DomCorp\PDFOptimizer" ""
  StrCmp $R0 "" check_hklm
  Goto found

  check_hklm:
  ReadRegStr $R0 HKLM "Software\DomCorp\PDFOptimizer" ""
  StrCmp $R0 "" done

  found:
  IfFileExists "$R0\uninstall.exe" 0 done
  
  ; Notify user (optional, but polite)
  MessageBox MB_OK|MB_ICONINFORMATION "Previous version detected. It will be uninstalled before proceeding."
  
  ; Run uninstaller silently
  ; _?=$R0 forces the uninstaller to run from the installed dir but wait correctly
  ExecWait '"$R0\uninstall.exe" /S _?=$R0'
  
  ; Cleanup leftover uninstaller if needed
  Delete "$R0\uninstall.exe"
  RMDir "$R0"

  done:
FunctionEnd

;--------------------------------
;Uninstaller Section

Section "Uninstall"
  ; Запуск глубокой очистки зависимостей
  ExecWait '"$INSTDIR\install\uninstall.bat"'

  ; Чистим все возможные пути регистрации
  DeleteRegKey HKCR "SystemFileAssociations\.pdf\shell\PDFOptimizer75"
  DeleteRegKey HKCR "SystemFileAssociations\.pdf\shell\PDFOptimizer150"
  DeleteRegKey HKCR "SystemFileAssociations\.pdf\shell\PDFOptimizer200"
  DeleteRegKey HKCR "SystemFileAssociations\.pdf\shell\PDFOptimizer300"

  DeleteRegKey HKCU "Software\Classes\.pdf\shell\PDFOptimizer75"
  DeleteRegKey HKCU "Software\Classes\.pdf\shell\PDFOptimizer150"
  DeleteRegKey HKCU "Software\Classes\.pdf\shell\PDFOptimizer200"
  DeleteRegKey HKCU "Software\Classes\.pdf\shell\PDFOptimizer300"

  DeleteRegKey HKCU "Software\Classes\SystemFileAssociations\.pdf\shell\PDFOptimizer75"
  DeleteRegKey HKCU "Software\Classes\SystemFileAssociations\.pdf\shell\PDFOptimizer150"
  DeleteRegKey HKCU "Software\Classes\SystemFileAssociations\.pdf\shell\PDFOptimizer200"
  DeleteRegKey HKCU "Software\Classes\SystemFileAssociations\.pdf\shell\PDFOptimizer300"

  DeleteRegKey HKCU "Software\Classes\*\shell\PDFOptimizer75"
  DeleteRegKey HKCU "Software\Classes\*\shell\PDFOptimizer150"
  DeleteRegKey HKCU "Software\Classes\*\shell\PDFOptimizer200"
  DeleteRegKey HKCU "Software\Classes\*\shell\PDFOptimizer300"

  DeleteRegKey HKCU "Software\DomCorp\PDFOptimizer"

  Delete "$SMPROGRAMS\DomCorp PDF Optimizer\Uninstall.lnk"
  Delete "$SMPROGRAMS\DomCorp PDF Optimizer\Manual.lnk"
  Delete "$SMPROGRAMS\DomCorp PDF Optimizer\Licenses.lnk"
  RMDir "$SMPROGRAMS\DomCorp PDF Optimizer"
  Delete "$DESKTOP\PDF Optimizer Manual.lnk"

  RMDir /r "$INSTDIR"
SectionEnd
