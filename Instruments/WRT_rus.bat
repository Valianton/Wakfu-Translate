powershell -Command "Remove-Item $pwd\tmpTranslate -Force -Recurse -ErrorAction SilentlyContinue"
powershell -Command "New-Item -ItemType directory -Path  $pwd\tmpTranslate\theme\fonts"
powershell -Command "New-Item -ItemType directory -Path  $pwd\tmpTranslate\i18n"
powershell -Command "New-Item -ItemType directory -Path  $pwd\tmpTranslate\chatonly\theme\fonts"
powershell -Command "Invoke-WebRequest https://github.com/Valianton/Wakfu-Translate/archive/master.zip -OutFile $pwd\tmpTranslate\master.zip"
powershell -Command "Expand-Archive -Path $pwd\tmpTranslate\master.zip -DestinationPath $pwd\tmpTranslate"
rem rus ChatOnly update
powershell -Command "Copy-Item $pwd\tmpTranslate\Wakfu-Translate-master\Translated\Fonts\wci-bold-9.fnt -destination $pwd\tmpTranslate\chatonly\theme\fonts"
powershell -Command "Copy-Item $pwd\tmpTranslate\Wakfu-Translate-master\Translated\Fonts\wci-bold-9_0.dds -destination $pwd\tmpTranslate\chatonly\theme\fonts"
rem rus Fonts update
powershell -Command "Copy-Item $pwd\tmpTranslate\Wakfu-Translate-master\Translated\fonts -destination $pwd\tmpTranslate\theme -recurse"
powershell -Command "Copy-Item $pwd\tmpTranslate\Wakfu-Translate-master\Translated\texts\texts_en.properties -destination $pwd\tmpTranslate\i18n"
cd tmpTranslate
Wakfu-Translate-master\Instruments\zip.exe -r ..\contents\gui_jar\gui.jar theme
cd i18n
..\Wakfu-Translate-master\Instruments\zip.exe -r ..\..\contents\i18n\i18n_en.jar texts_en.properties
cd ..
cd ..
pause