; Build with Inno Setup 6.5 or newer. Private Google configuration is opt-in.
#ifndef SourceDir
  #define SourceDir "dist\Simple PDF reader"
#endif
#ifndef OutputFolder
  #define OutputFolder "dist"
#endif
#ifndef OutputName
  #define OutputName "Simple-PDF-reader-Setup"
#endif

[Setup]
AppId=SimplePDFreader.thundom
AppName=Simple PDF reader
AppVersion=0.4.0
AppPublisher=thundom
DefaultDirName={localappdata}\Programs\Simple PDF reader
DefaultGroupName=Simple PDF reader
PrivilegesRequired=lowest
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
WizardStyle=modern
DisableWelcomePage=no
DisableDirPage=no
DisableProgramGroupPage=no
DisableReadyPage=no
DisableFinishedPage=no
AlwaysShowDirOnReadyPage=yes
ShowLanguageDialog=yes
LanguageDetectionMethod=none
AllowNoIcons=yes
CloseApplications=yes
RestartApplications=no
AppPublisherURL=https://github.com/thundom/Simple-PDF-reader
AppSupportURL=https://github.com/thundom/Simple-PDF-reader/issues
OutputDir={#OutputFolder}
OutputBaseFilename={#OutputName}
Compression=lzma2
SolidCompression=yes
ChangesAssociations=yes
InfoBeforeFile=LICENSE
UninstallDisplayIcon={app}\Simple PDF reader.exe

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"
Name: "chinesesimp"; MessagesFile: "installer-languages\ChineseSimplified.isl"
Name: "japanese"; MessagesFile: "compiler:Languages\Japanese.isl"

[CustomMessages]
english.DesktopShortcut=Create a desktop shortcut
chinesesimp.DesktopShortcut=创建桌面快捷方式
japanese.DesktopShortcut=デスクトップにショートカットを作成
english.LaunchReader=Launch Simple PDF reader
chinesesimp.LaunchReader=启动 Simple PDF reader
japanese.LaunchReader=Simple PDF reader を起動

[Tasks]
Name: "desktopicon"; Description: "{cm:DesktopShortcut}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "{#SourceDir}\*"; DestDir: "{app}"; Excludes: "portable.flag,Data\*,oauth-clients.json"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "README.md"; DestDir: "{app}"
Source: "CLOUD_SETUP.md"; DestDir: "{app}"
Source: "LICENSE"; DestDir: "{app}"
Source: "THIRD_PARTY_NOTICES.md"; DestDir: "{app}"

#ifdef IncludeGoogle
Source: "oauth-clients.json"; DestDir: "{app}"; Flags: ignoreversion
#endif

[Icons]
Name: "{group}\Simple PDF reader"; Filename: "{app}\Simple PDF reader.exe"

Name: "{autodesktop}\Simple PDF reader"; Filename: "{app}\Simple PDF reader.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\Simple PDF reader.exe"; WorkingDir: "{app}"; Description: "{cm:LaunchReader}"; Flags: postinstall nowait skipifsilent

[Registry]
Root: HKCU; Subkey: "Software\Classes\SimplePDFreader.Document"; ValueType: string; ValueData: "PDF Document"; Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\Classes\SimplePDFreader.Document\shell\open\command"; ValueType: string; ValueData: """{app}\Simple PDF reader.exe"" ""%1"""
Root: HKCU; Subkey: "Software\Classes\.pdf\OpenWithProgids"; ValueName: "SimplePDFreader.Document"; ValueType: none; Flags: uninsdeletevalue
Root: HKCU; Subkey: "Software\Simple PDF reader\Capabilities"; ValueName: "ApplicationName"; ValueType: string; ValueData: "Simple PDF reader"; Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\Simple PDF reader\Capabilities"; ValueName: "ApplicationDescription"; ValueType: string; ValueData: "Free PDF reader and editor"
Root: HKCU; Subkey: "Software\Simple PDF reader\Capabilities\FileAssociations"; ValueName: ".pdf"; ValueType: string; ValueData: "SimplePDFreader.Document"
Root: HKCU; Subkey: "Software\RegisteredApplications"; ValueName: "Simple PDF reader"; ValueType: string; ValueData: "Software\Simple PDF reader\Capabilities"; Flags: uninsdeletevalue
