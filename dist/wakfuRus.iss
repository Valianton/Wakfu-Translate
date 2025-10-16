[Setup]
; Настройки установщика
AppName=Wakfu Русификатор
AppVerName=Wakfu Русификатор 1.88.1
DefaultDirName={commonpf}\Wakfu Русификатор
DefaultGroupName=Wakfu Русификатор
UninstallDisplayIcon={app}\Wakfu Русификатор.exe
Compression=lzma
AppendDefaultDirName=no
AppPublisher=Wakfu Русификатор
AppPublisherURL=https://vk.com/wakfu_translate
OutputBaseFilename=wakfu_rus
VersionInfoVersion=1.88.1

[Files]
; Копирование файлов
Source: "texts_en.properties"; DestDir: "{app}\contents\i18n";
Source: "theme\fonts\*"; DestDir: "{app}\contents\gui_jar\theme\fonts";
Source: "zip.exe"; DestDir: "{app}\contents\i18n";
Source: "zip.exe"; DestDir: "{app}\contents\gui_jar";


[Run]
; Создание архива i18n_en.jar
Filename: "{app}\contents\i18n\zip.exe"; Parameters: "-r ""i18n_en.jar"" ""texts_en.properties"""; Flags: runminimized shellexec
; Обоновление шрифтов
Filename: "{app}\contents\gui_jar\zip.exe"; Parameters: "-r ""gui.jar"" ""theme"""; Flags: runminimized shellexec