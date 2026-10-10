[Setup]
AppId=SimplePDFreader.thundom
AppName=Simple PDF reader
AppVersion=0.3.0
AppPublisher=thundom
DefaultDirName={localappdata}\Programs\Simple PDF reader
DefaultGroupName=Simple PDF reader
PrivilegesRequired=lowest
OutputDir=dist
OutputBaseFilename=Simple-PDF-reader-Setup
Compression=lzma2
SolidCompression=yes
ChangesAssociations=yes
LicenseFile=LICENSE
UninstallDisplayIcon={app}\Simple PDF reader.exe

[Files]
Source: "dist\Simple PDF reader\*"; DestDir: "{app}"; Excludes: "portable.flag"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "README.md"; DestDir: "{app}"
Source: "CLOUD_SETUP.md"; DestDir: "{app}"
Source: "LICENSE"; DestDir: "{app}"
Source: "THIRD_PARTY_NOTICES.md"; DestDir: "{app}"

[Icons]
Name: "{group}\Simple PDF reader"; Filename: "{app}\Simple PDF reader.exe"

[Registry]
Root: HKCU; Subkey: "Software\Classes\SimplePDFreader.Document"; ValueType: string; ValueData: "PDF Document"; Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\Classes\SimplePDFreader.Document\shell\open\command"; ValueType: string; ValueData: """{app}\Simple PDF reader.exe"" ""%1"""
Root: HKCU; Subkey: "Software\Classes\.pdf\OpenWithProgids"; ValueName: "SimplePDFreader.Document"; ValueType: none; Flags: uninsdeletevalue
Root: HKCU; Subkey: "Software\Simple PDF reader\Capabilities"; ValueName: "ApplicationName"; ValueType: string; ValueData: "Simple PDF reader"; Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\Simple PDF reader\Capabilities"; ValueName: "ApplicationDescription"; ValueType: string; ValueData: "Free PDF reader and editor"
Root: HKCU; Subkey: "Software\Simple PDF reader\Capabilities\FileAssociations"; ValueName: ".pdf"; ValueType: string; ValueData: "SimplePDFreader.Document"
Root: HKCU; Subkey: "Software\RegisteredApplications"; ValueName: "Simple PDF reader"; ValueType: string; ValueData: "Software\Simple PDF reader\Capabilities"; Flags: uninsdeletevalue
