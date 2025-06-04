; Inno Setup Script for Fava PQC Installer
; This script would be compiled by Inno Setup (iscc.exe)

#define MyAppName "Fava PQC"
#define MyAppVersion "1.2.0" ; Placeholder - should match Fava's version
#define MyAppPublisher "Fava PQC Contributors"
#define MyAppURL "https://github.com/beancount/fava" ; Adjust if there's a specific PQC fork URL
#define MyAppExeName "fava_pqc_installer.exe" ; This is the PyInstaller output, not the final installer name
#define MyPyInstallerOutput "fava_pqc_dist" ; The folder created by PyInstaller in dist/

[Setup]
; NOTE: The value of AppId uniquely identifies this application.
; Do not use a random GUID - generate one from Inno Setup IDE if needed.
AppId={{F92D1SO4-F123-45A6-BCDE-F123456789AB}} ; Placeholder GUID
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\{#MyAppName}
;DefaultDirName={userappdata}\Programs\{#MyAppName} ; Alternative for non-admin install
DisableProgramGroupPage=yes
OutputBaseFilename=fava_pqc_windows_installer_v{#MyAppVersion} ; Final installer .exe name
Compression=lzma
SolidCompression=yes
WizardStyle=modern
;PrivilegesRequired=none ; or lowest if installing to userappdata
UninstallDisplayIcon={app}\{#MyAppExeName}
;SetupIconFile=c:\code\ChrisFava\src\fava\static\favicon.ico ; Icon for the installer itself

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "dist\{#MyPyInstallerOutput}\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\{#MyPyInstallerOutput}\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
; Note: The above line copies all contents from the PyInstaller output directory.
; Ensure that dist\{#MyPyInstallerOutput} contains everything Fava needs to run.
; This includes the main exe, all DLLs, data files, etc.

[Icons]
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent