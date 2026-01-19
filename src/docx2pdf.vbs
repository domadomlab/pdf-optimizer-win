Option Explicit
On Error Resume Next

Dim Word, Doc, FileSystem
Dim InputFile, OutputFile

If WScript.Arguments.Count < 2 Then WScript.Quit 1

InputFile = WScript.Arguments(0)
OutputFile = WScript.Arguments(1)

Set FileSystem = CreateObject("Scripting.FileSystemObject")
Set Word = CreateObject("Word.Application")

If Err.Number <> 0 Then
    ' Word not installed or accessible
    WScript.Quit 2
End If

' Robust suppression of prompts
Word.Visible = False
Word.DisplayAlerts = 0 ' wdAlertsNone
Word.Options.SaveNormalPrompt = False
Word.Options.SavePropertiesPrompt = False

Set Doc = Word.Documents.Open(InputFile, False, True) ' ReadOnly=True

If Err.Number <> 0 Then
    Word.NormalTemplate.Saved = True
    Word.Quit 0 ' wdDoNotSaveChanges
    WScript.Quit 3
End If

' 17 = wdFormatPDF
Doc.SaveAs2 OutputFile, 17

Doc.Close 0 ' wdDoNotSaveChanges

' Ensure Word thinks the global template is clean before quitting
Word.NormalTemplate.Saved = True
Word.Quit 0 ' wdDoNotSaveChanges

If FileSystem.FileExists(OutputFile) Then
    WScript.Quit 0
Else
    WScript.Quit 4
End If