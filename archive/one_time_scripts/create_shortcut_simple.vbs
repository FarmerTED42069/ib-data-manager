Set oWS = WScript.CreateObject("WScript.Shell")
Set oFSO = CreateObject("Scripting.FileSystemObject")

' Get the desktop path
sDesktop = oWS.SpecialFolders("Desktop")

' Get the current script directory
sScriptDir = oFSO.GetParentFolderName(WScript.ScriptFullName)

' Create shortcut on desktop
sLinkFile = sDesktop & "\IB Data Manager.lnk"
Set oLink = oWS.CreateShortcut(sLinkFile)

oLink.TargetPath = "D:\\projects\\trading-bots\\ib_data_manager\\scripts\\run_app.bat"
oLink.WorkingDirectory = "D:\\projects\\trading-bots\\ib_data_manager\\scripts"
oLink.Description = "Interactive Brokers Data Manager"
oLink.IconLocation = "%SystemRoot%\System32\cmd.exe"

oLink.Save

MsgBox "Desktop shortcut created successfully!" & vbCrLf & vbCrLf & "You can now double-click 'IB Data Manager' on your desktop to start the application.", vbInformation, "Shortcut Created"
