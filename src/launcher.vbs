Set objShell = CreateObject("WScript.Shell")
Set objFSO = CreateObject("Scripting.FileSystemObject")

' Determine Installation Root (parent of src folder)
SrcFolder = objFSO.GetParentFolderName(WScript.ScriptFullName)
InstRoot = objFSO.GetParentFolderName(SrcFolder)

' Default log directory is the Installation Root
LogDir = InstRoot

' Try to read custom log path from log_config.txt
ConfigPath = objFSO.BuildPath(InstRoot, "log_config.txt")
If objFSO.FileExists(ConfigPath) Then
    On Error Resume Next
    Set objFile = objFSO.OpenTextFile(ConfigPath, 1)
    SavedPath = Trim(objFile.ReadLine)
    objFile.Close
    If objFSO.FolderExists(SavedPath) Then
        LogDir = SavedPath
    End If
    On Error GoTo 0
End If

LogFile = objFSO.BuildPath(LogDir, "pdf_launcher_debug.log")

Sub WriteLog(msg)
    On Error Resume Next
    Set f = objFSO.OpenTextFile(LogFile, 8, True)
    f.WriteLine "[" & Now & "] " & msg
    f.Close
End Sub

WriteLog "--- Launcher Started v4.0.5 ---"
WriteLog "Arg Count: " & WScript.Arguments.Count

If WScript.Arguments.Count < 4 Then
    WriteLog "ERROR: Not enough arguments."
    WScript.Quit
End If

PythonExe = WScript.Arguments(0)
ScriptPath = WScript.Arguments(1)
DPI = WScript.Arguments(2)
PDF = WScript.Arguments(3)

' Construct Command with double quotes for all paths
Cmd = """" & PythonExe & """ """ & ScriptPath & """ " & DPI & " """ & PDF & """"

WriteLog "Exec: " & Cmd

' Run hidden (0) and do not wait (False)
On Error Resume Next
objShell.Run Cmd, 0, False

If Err.Number <> 0 Then
    WriteLog "EXECUTION ERROR: " & Err.Description & " (Code: " & Err.Number & ")"
Else
    WriteLog "Process spawned successfully."
End If