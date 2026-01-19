Set objShell = CreateObject("WScript.Shell")
Set objFSO = CreateObject("Scripting.FileSystemObject")

' Setup Logging (Optional, can be disabled for speed)
LogFile = objFSO.BuildPath(objFSO.GetParentFolderName(WScript.ScriptFullName), "launcher_debug.log")

Sub WriteLog(msg)
    On Error Resume Next
    ' Set f = objFSO.OpenTextFile(LogFile, 8, True)
    ' f.WriteLine "[" & Now & "] " & msg
    ' f.Close
End Sub

If WScript.Arguments.Count < 4 Then
    WScript.Quit
End If

PythonExe = WScript.Arguments(0)
ScriptPath = WScript.Arguments(1)
DPI = WScript.Arguments(2)
PDF = WScript.Arguments(3)

' Construct Command
' Quote paths to handle spaces correctly
Cmd = """" & PythonExe & """ """ & ScriptPath & """ " & DPI & " """ & PDF & """"

WriteLog "Exec: " & Cmd

' Run hidden (0) and do not wait (False)
objShell.Run Cmd, 0, False