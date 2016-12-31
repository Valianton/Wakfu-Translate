rmdir /S/Q tmpTranslate
powershell -Command "New-Item -ItemType directory -Path  $pwd\tmpTranslate\theme\fonts"
powershell -Command "New-Item -ItemType directory -Path  $pwd\tmpTranslate\i18n"
powershell -Command "New-Item -ItemType directory -Path  $pwd\tmpTranslate\chatonly\theme\fonts"
powershell -Command "Invoke-WebRequest https://github.com/Valianton/Wakfu-Translate/archive/master.zip -OutFile $pwd\tmpTranslate\master.zip"
powershell -Command "Expand-Archive -Path $pwd\tmpTranslate\master.zip -DestinationPath $pwd\tmpTranslate"
rem rus ChatOnly update
cd tmpTranslate
copy Wakfu-Translate-master\Translated\Fonts\wci-bold-9.fnt chatonly\theme\fonts
copy Wakfu-Translate-master\Translated\Fonts\wci-bold-9_0.dds chatonly\theme\fonts
rem rus Fonts update
copy Wakfu-Translate-master\Translated\Fonts theme\fonts
rem rus Text update
copy Wakfu-Translate-master\Translated\Texts i18n
cd ..
pause