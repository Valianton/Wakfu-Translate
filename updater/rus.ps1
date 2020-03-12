$i18n = "texts_en.properties"
$fonts = "fonts"
$theme = "theme"
$pathToExpand = "$pwd\tmpTranslate"
$pathToTheme = "$pathToExpand\$theme"
$pathToFonts = "$pathToTheme\$fonts"
$updateFontPath = "$pathToExpand\Wakfu-Translate-master\Translated\fonts\*"
$updateLangPath = "$pathToExpand\Wakfu-Translate-master\Translated\texts\texts_en.properties"

# create carcas
Remove-Item $pathToExpand -Force -Recurse -ErrorAction SilentlyContinue
New-Item -ItemType directory -Path  $pathToFonts

# upload resource
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
Invoke-WebRequest https://github.com/Valianton/Wakfu-Translate/archive/master.zip -OutFile $pathToExpand\master.zip
Expand-Archive -Path $pathToExpand\master.zip -DestinationPath $pathToExpand

# prepare resource
Copy-Item $updateFontPath -destination $pathToFonts -Recurse
Copy-Item $updateLangPath -destination $pathToExpand

# update resource
$zip = "$pwd\zip.exe"
$sourceFont = "$pwd\contents\gui_jar\gui.jar"
$sourceLang = "$pwd\contents\i18n\i18n_en.jar"
Set-Location -Path $pathToExpand
Invoke-Expression "$zip -r $sourceFont $theme"
Invoke-Expression "$zip -r $sourceLang $i18n"