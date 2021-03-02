[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
function Get-IniFile {  
    param(  
        [parameter(Mandatory = $true)] [string] $filePath  
    )  
    
    $anonymous = "NoSection"
  
    $ini = @{}  
    switch -regex -file $filePath  
    {  
        "^\[(.+)\]$" # Section  
        {  
            $section = $matches[1]  
            $ini[$section] = @{}  
            $CommentCount = 0  
        }  

        "^(;.*)$" # Comment  
        {  
            if (!($section))  
            {  
                $section = $anonymous  
                $ini[$section] = @{}  
            }  
            $value = $matches[1]  
            $CommentCount = $CommentCount + 1  
            $name = "Comment" + $CommentCount  
            $ini[$section][$name] = $value  
        }   

        "(.+?)\s*=\s*(.*)" # Key  
        {  
            if (!($section))  
            {  
                $section = $anonymous  
                $ini[$section] = @{}  
            }  
            $name,$value = $matches[1..2]  
            $ini[$section][$name] = $value  
        }  
    }  
    return $ini  
}

Function Get-GameFolder() {
	return (Get-ItemProperty -Path $HKCU_SOFTWARE_ANKAMA\$wakfuKey).GameFolder
}

Function Get-Version() {
	return (Get-ItemProperty -Path $HKCU_SOFTWARE_ANKAMA\$wakfuKey).version
}

Function Create-RegKey($name, $value) {
	New-ItemProperty -Path $HKCU_SOFTWARE_ANKAMA\$wakfuKey -Name $name -Value $value -PropertyType "String"
}

Function Update-RegKey($name, $value) {
	Set-ItemProperty -Path $HKCU_SOFTWARE_ANKAMA\$wakfuKey -Name $name -Value $value
}

Function Check-ValidPath($path) {
	$v = ".release.infos.json"
	return [System.IO.File]::Exists("$path\$v")
}

Function Get-Folder($initialDirectory) {
    [void] [System.Reflection.Assembly]::LoadWithPartialName('System.Windows.Forms')
    $FolderBrowserDialog = New-Object System.Windows.Forms.FolderBrowserDialog
    $FolderBrowserDialog.RootFolder = 'MyComputer'
    if ($initialDirectory) { $FolderBrowserDialog.SelectedPath = $initialDirectory }

	if($FolderBrowserDialog.ShowDialog() -eq "OK")
    {
        $folder += $FolderBrowserDialog.SelectedPath
    }
    return $folder
}
Function CreateDistrib() {
	New-Item –Path $HKCU_SOFTWARE_ANKAMA –Name $wakfuKey
	(Create-RegKey 'GameFolder' '')
	(Create-RegKey 'version' 0)
	Write-Output "Создан новый дистрибутив для русификатора"
}

#app
$appWidth = 500
$appHeight = 200

#init settings
Invoke-WebRequest https://github.com/Valianton/Wakfu-Translate/raw/master/data/info.ini -OutFile $pwd\info.ini
$iniFile = Get-IniFile "$pwd\info.ini"
$NewVersion = $iniFile.info.version
Remove-Item $pwd\info.ini -Force -Recurse -ErrorAction SilentlyContinue
$ankamaKey = "AnkamaRus"
$wakfuKey = "WakfuRussifier"
$HKCU_SOFTWARE = "HKCU:\SOFTWARE"
$HKCU_SOFTWARE_ANKAMA = "$HKCU_SOFTWARE\$ankamaKey"

if (!(Get-Item -Path $HKCU_SOFTWARE_ANKAMA -ErrorAction SilentlyContinue)) {
	New-Item –Path $HKCU_SOFTWARE –Name $ankamaKey
	(CreateDistrib)
	$version = "0"
} else {
	$WakfuRegObject = (Get-ChildItem $HKCU_SOFTWARE_ANKAMA -Include $wakfuKey -Recurse)
	if (!$WakfuRegObject) {
		(CreateDistrib)
	} else {
		$version = (Get-Version)
		Write-Output "Текущая версия русификатора: $version"
	}
}

#GUI
Add-Type -assembly System.Windows.Forms
#Label
$FormLabel = New-Object System.Windows.Forms.Label
$FormLabel.Location = New-Object System.Drawing.Point(20,10)
$FormLabel.Text = "Путь до игры"
$FormLabel.AutoSize = $true

$InfoLabel = New-Object System.Windows.Forms.Label
$InfoLabel.Location = New-Object System.Drawing.Point(20,100)
$InfoLabel.ForeColor = [System.Drawing.ColorTranslator]::FromHtml("#00A2E8")
$InfoLabel.AutoSize = $true

$FolderText = New-Object system.Windows.Forms.TextBox
$FolderText.multiline = $false
$FolderText.width = 435
$FolderText.location = New-Object System.Drawing.Point(25,40)
$FolderText.Add_TextChanged({
	if ((Check-ValidPath $FolderText.text)) {
		$InstallButton.enabled = $true
		(Update-RegKey 'GameFolder' $FolderText.text)
	} else {
		$InstallButton.enabled = $false
	}
})

# FolderButton
$FolderButton = New-Object System.Windows.Forms.Button
$FolderButton.Location = New-Object System.Drawing.Size(360,10)
$FolderButton.Size = New-Object System.Drawing.Size(100,20)
$FolderButton.Text = "Выбрать папку"

# Install Button
$installButtonWidth = 200
$InstallButton_positionX = $appWidth / 2 - $installButtonWidth / 2
$InstallButton = New-Object System.Windows.Forms.Button
$InstallButton.Location = New-Object System.Drawing.Size($InstallButton_positionX, 70)
$InstallButton.Size = New-Object System.Drawing.Size($installButtonWidth,20)
$InstallButton.enabled = $false
$InstallButton.Add_Click({
	$targetPath = $FolderText.text
	$modPath = "$targetPath\mods"
	# update carcas
	Remove-Item $modPath -Force -Recurse -ErrorAction SilentlyContinue
	New-Item -ItemType directory -Path  $modPath

	# alias - curl
	Invoke-WebRequest https://github.com/Valianton/Wakfu-Translate/raw/master/Instruments/zip.exe -OutFile $modPath\zip.exe
	Invoke-WebRequest https://github.com/Valianton/Wakfu-Translate/raw/master/data/data.zip -OutFile $modPath\data.zip
	Expand-Archive -LiteralPath $modPath\data.zip -DestinationPath $modPath

	# update russifier
	$zip = "$targetPath\mods\zip.exe"
	Set-Location -Path $modPath
	$sourceLang = "$targetPath\contents\i18n\i18n_en.jar"
	Invoke-Expression "$zip $sourceLang texts_en.properties"
	$sourceFont = "$targetPath\contents\gui_jar\gui.jar"
	Invoke-Expression "$zip -r $sourceFont theme"
	(Update-RegKey 'version' $NewVersion)
	$window_form.Text = "ВАКФУ Русификатор v$NewVersion"
	$InfoLabel.Text = "Русификатор успешно установлен"
})


$FolderButton.Add_Click({
	$defaultFolder = (Get-GameFolder)

	if (!$defaultFolder) {
		$defaultFolder = 'C:\Users'
	}

	($selectedFolder = Get-Folder $defaultFolder)
	$FolderText.text = $selectedFolder
	if ($selectedFolder) {
		if (!(Check-ValidPath $selectedFolder)) {
			if ($FolderText.text) {
				if ((Check-ValidPath $FolderText.text)) {
					$InstallButton.enabled = $true
				}
			}
		} else {
			Write-Warning $selectedFolder
			(Update-RegKey 'GameFolder' $selectedFolder)
			$FolderText.text = $selectedFolder
		}
	}
})


$window_form = New-Object System.Windows.Forms.Form
$formTitle = "ВАКФУ Русификатор"
$installText = "Установить Русификатор"

if ($version) {
	if ($NewVersion -gt $version) {
		$formTitle = "ВАКФУ Русификатор v$version (доступна версия $NewVersion)"
		$installText = "Обновить Русификатор"
		$InfoLabel.Text = "В наличии имеется новая версия русификатора"
	} else {
		$formTitle = "ВАКФУ Русификатор v$version"
		$installText = "Переустановить Русификатор"
		$InfoLabel.Text = "Русификатор обновлен до последней версии, но его можно переустановить"
	}
}

$InstallButton.Text = $installText

$window_form.Text = $formTitle
$window_form.Width = $appWidth
$window_form.Height = $appHeight
$window_form.AutoSize = 1

$window_form.Controls.Add($FormLabel)
$window_form.Controls.Add($FolderButton)
$window_form.Controls.Add($InstallButton)
$window_form.Controls.Add($FolderText)
$window_form.Controls.Add($InfoLabel)
$FolderText.text = (Get-GameFolder)

$window_form.ShowDialog()
