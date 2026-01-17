Set objShell = CreateObject("WScript.Shell")
Set objFSO = CreateObject("Scripting.FileSystemObject")

' Setup Logging
BaseDir = objFSO.GetParentFolderName(objFSO.GetParentFolderName(WScript.ScriptFullName))
LogDir = objFSO.BuildPath(BaseDir, "logs")
If Not objFSO.FolderExists(LogDir) Then objFSO.CreateFolder(LogDir)
LogFile = objFSO.BuildPath(LogDir, "launcher_debug.log")

Sub WriteLog(msg)
    On Error Resume Next
    Set f = objFSO.OpenTextFile(LogFile, 8, True)
    f.WriteLine "[" & Now & "] " & msg
    f.Close
End Sub

WriteLog "--- Launcher Started ---"
WriteLog "Args count: " & WScript.Arguments.Count

If WScript.Arguments.Count < 2 Then
    WriteLog "ERROR: Not enough arguments"
    WScript.Quit
End If

DPI = WScript.Arguments(0)
PDF = WScript.Arguments(1)
ScriptPath = objFSO.BuildPath(objFSO.GetParentFolderName(WScript.ScriptFullName), "optimizer.py")

WriteLog "DPI: " & DPI
WriteLog "PDF: " & PDF
WriteLog "Script: " & ScriptPath

' Find Python
Function GetPythonPath()
    On Error Resume Next
    Dim path
    path = objShell.RegRead("HKLM\SOFTWARE\Python\PythonCore\3.12\InstallPath\")
    If path = "" Then path = objShell.RegRead("HKCU\SOFTWARE\Python\PythonCore\3.12\InstallPath\")
    If path = "" Then path = objShell.RegRead("HKLM\SOFTWARE\WOW6432Node\Python\PythonCore\3.12\InstallPath\")
    
    If path <> "" Then
        If Right(path, 1) <> "\" Then path = path & "\"
        GetPythonPath = path & "pythonw.exe"
    Else
        GetPythonPath = "pythonw.exe"
    End If
End Function

PythonEXE = GetPythonPath()
WriteLog "Target Python: " & PythonEXE

Cmd = """" & PythonEXE & """ """ & ScriptPath & """ " & DPI & " """ & PDF & """"
WriteLog "Executing: " & Cmd

On Error Resume Next
objShell.Run Cmd, 0, False
If Err.Number <> 0 Then
    WriteLog "EXECUTION FAILED: " & Err.Description
    MsgBox "Failed to start optimizer: " & Err.Description, 16, "PDF Optimizer Launcher"
Else
    WriteLog "Execution sent to shell."
End If