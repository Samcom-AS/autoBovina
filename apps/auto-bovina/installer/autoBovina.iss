; Inno Setup installer for the reconstructed autoBovina application.
; Build through ..\build.ps1 so SourceDist and MyAppVersion are supplied.

#ifndef SourceDist
  #define SourceDist "..\..\..\dist\autoBovina"
#endif

#ifndef MyAppVersion
  #define MyAppVersion "0.3.0"
#endif

#define MyAppName "autoBovina"
#define MyAppPublisher "Samcom"
#define MyAppExeName "autoBovina.exe"

[Setup]
AppId={{CC995B07-BC1E-4D84-8E2B-194C5D3A3F53}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={localappdata}\Samcom\autoBovina
DefaultGroupName=Samcom\autoBovina
DisableProgramGroupPage=yes
OutputDir=..\..\..\release
OutputBaseFilename=autoBovina-setup-{#MyAppVersion}
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest
UninstallDisplayName={#MyAppName}
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible

[Files]
; The executable and libraries are replaced on each upgrade. The two local
; configuration files are preserved after first install.
Source: "{#SourceDist}\*"; DestDir: "{app}"; Excludes: "data\settings.txt,data\rasa.txt"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "{#SourceDist}\data\settings.txt"; DestDir: "{app}\data"; Flags: onlyifdoesntexist
Source: "{#SourceDist}\data\rasa.txt"; DestDir: "{app}\data"; Flags: onlyifdoesntexist

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Creează o scurtătură pe Desktop"; GroupDescription: "Scurtături suplimentare:"; Flags: unchecked
