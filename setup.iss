[Setup]
AppName=MyApp
AppVersion=1.0.0
DefaultDirName={pf}\MyApp
OutputDir=.
DisableDirPage=no
Compression=lzma
SolidCompression=yes

[Files]
; Копируем весь собранный дистрибутив
Source: "dist_full\*"; DestDir: "{app}"; Flags: recursesubdirs ignoreversion

[Icons]
Name: "{group}\MyApp"; Filename: "{app}\main.exe"
Name: "{commondesktop}\MyApp"; Filename: "{app}\main.exe"; Tasks: desktopicon

[Tasks] 
Name: "desktopicon"; Description: "Создать ярлык на рабочем столе"; GroupDescription: "Ярлыки:";

[Run]
Filename: "{app}\main.exe"; Description: "Запустить MyApp"; Flags: nowait postinstall skipifsilent
    
