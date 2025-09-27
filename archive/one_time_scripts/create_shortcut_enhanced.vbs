Set oWS = WScript.CreateObject("WScript.Shell")
Set oFSO = CreateObject("Scripting.FileSystemObject")

' Get the desktop path
sDesktop = oWS.SpecialFolders("Desktop")

' Get the current script directory
sScriptDir = oFSO.GetParentFolderName(WScript.ScriptFullName)

' Create shortcut for Python script
sLinkFile = sDesktop & "\IB Data Manager.lnk"
Set oLink = oWS.CreateShortcut(sLinkFile)

' Check if Python is in PATH
On Error Resume Next
sPythonPath = oWS.Exec("where python").StdOut.ReadLine()
On Error GoTo 0

If sPythonPath <> "" Then
    ' Python found, create Python shortcut
    oLink.TargetPath = sPythonPath
    oLink.Arguments = """" & sScriptDir & "\main.py"""
    oLink.WorkingDirectory = sScriptDir
    oLink.Description = "Interactive Brokers Data Manager"
    
    ' Try to use custom icon if it exists
    sIconPath = sScriptDir & "\ib_data_manager.ico"
    If oFSO.FileExists(sIconPath) Then
        oLink.IconLocation = sIconPath
    Else
        oLink.IconLocation = sPythonPath
    End If
Else
    ' Python not found, create batch file shortcut
    oLink.TargetPath = sScriptDir & "\run_app.bat"
    oLink.WorkingDirectory = sScriptDir
    oLink.Description = "Interactive Brokers Data Manager"
    oLink.IconLocation = "%SystemRoot%\System32\cmd.exe"
End If

oLink.Save

' Create batch file shortcut as backup
sBatchLinkFile = sDesktop & "\IB Data Manager (Batch).lnk"
Set oBatchLink = oWS.CreateShortcut(sBatchLinkFile)

oBatchLink.TargetPath = sScriptDir & "\run_app.bat"
oBatchLink.WorkingDirectory = sScriptDir
oBatchLink.Description = "Interactive Brokers Data Manager (Batch)"
oBatchLink.IconLocation = "%SystemRoot%\System32\cmd.exe"

oBatchLink.Save

MsgBox "Desktop shortcuts created successfully!" & vbCrLf & vbCrLf & _
       "You can now double-click 'IB Data Manager' on your desktop to start the application." & vbCrLf & vbCrLf & _
       "Two shortcuts were created:" & vbCrLf & _
       "1. IB Data Manager - Direct Python execution" & vbCrLf & _
       "2. IB Data Manager (Batch) - Batch file execution", _
       vbInformation, "Shortcuts Created"
