param([ValidateSet('1.6','1.7')][string]$Version='1.7',[string]$ConfigPath,[switch]$AutoTest,[switch]$Launch,
 [ValidateSet('Framework')][string]$ProbeKind='Framework',[switch]$Visible)
$ErrorActionPreference='Stop'
if($PSBoundParameters.ContainsKey('ProbeKind') -and -not $AutoTest){throw '-ProbeKind requires -AutoTest.'}
$kit=Split-Path $PSScriptRoot -Parent
if(-not $ConfigPath){$ConfigPath=Join-Path $kit 'ToolPaths.local.json'}
if(-not(Test-Path -LiteralPath $ConfigPath)){throw 'Create ToolPaths.local.json from ToolPaths.example.json first.'}
$cfg=Get-Content -LiteralPath $ConfigPath -Encoding UTF8 -Raw|ConvertFrom-Json
$game=if($Version -eq '1.6'){$cfg.Game16Root}else{$cfg.Game17Root}
$exe=if($Version -eq '1.6'){'RimWorldWin64.exe'}else{'RimWorld.exe'}
if(-not $game -or -not(Test-Path -LiteralPath "$game/$exe")){throw "The configured RimWorld $Version directory does not contain $exe. Check Game16Root or Game17Root in the configuration."}
$runtime="$kit/Work/Runtime/$Version";$mod="$kit/Mod"
if((Get-PSDrive -Name ([IO.Path]::GetPathRoot($kit).Substring(0,1))).Free -lt 10GB){throw 'The project drive needs at least 10 GiB of free space to prepare a test run.'}
$owned=0
if(Test-Path -LiteralPath "$kit/Work/Runs"){$owned=(Get-ChildItem -LiteralPath "$kit/Work/Runs" -Recurse -File|Measure-Object Length -Sum).Sum}
if($owned -gt 192MB){throw 'Reserve 64 MiB for a run within the 256 MiB Work output budget; review finished runs first.'}
if(Get-Process RimWorld,RimWorldWin64 -ErrorAction SilentlyContinue){throw 'A RimWorld process is already running. Finish it before starting an isolated test.'}
if([IO.Path]::GetPathRoot($runtime) -ne [IO.Path]::GetPathRoot([IO.Path]::GetFullPath($game))){throw 'The project and game must be on the same drive for hard links. Alternatively, install Mod and Examples/Mechanisms manually as described in the quick start.'}
New-Item -ItemType Directory -Path "$runtime/Mods" -Force|Out-Null
foreach($f in Get-ChildItem -LiteralPath $game -File|Where-Object {$_.Extension -in '.dll','.exe','.json','.zip' -or $_.Name -in 'Version.txt','steam_appid.txt'}){
 $target=[IO.Path]::GetFullPath("$runtime/$($f.Name)")
 if(-not $target.StartsWith([IO.Path]::GetFullPath($runtime)+'\',[StringComparison]::OrdinalIgnoreCase)){throw 'Target escaped runtime'}
 if(Test-Path -LiteralPath $target){
  if((Get-FileHash -LiteralPath $target).Hash -eq (Get-FileHash -LiteralPath $f.FullName).Hash){continue}
  # Unlink first; overwriting a hard link would overwrite the original game file.
  Remove-Item -LiteralPath $target -Force
 }
 New-Item -ItemType HardLink -Path $target -Target $f.FullName|Out-Null
}
function Ensure-Junction([string]$path,[string]$target){
 if(Test-Path -LiteralPath $path){
  $item=Get-Item -LiteralPath $path
  if(-not($item.Attributes -band [IO.FileAttributes]::ReparsePoint) -or [IO.Path]::GetFullPath(@($item.Target)[0]) -ne [IO.Path]::GetFullPath($target)){throw "Unexpected link/directory: $path"}
 }else{New-Item -ItemType Junction -Path $path -Target $target|Out-Null}
}
foreach($d in $(if($Version -eq '1.6'){@('Data','MonoBleedingEdge','RimWorldWin64_Data')}else{@('Data','Rendering')})){Ensure-Junction "$runtime/$d" "$game/$d"}
Ensure-Junction "$runtime/Mods/RMVF" $mod
Ensure-Junction "$runtime/Mods/RMVFExamples" "$kit/Examples/Mechanisms"
$mods=@('ludeon.rimworld','greyoviin.mechanicalvisualframework','greyoviin.rmvf.examples')
if($AutoTest){
 if(-not $cfg.CompilerPath -or -not(Test-Path -LiteralPath $cfg.CompilerPath)){throw 'AutoTest needs existing Roslyn csc.exe.'}
 $probe="$kit/Work/Probe/$Version";New-Item -ItemType Directory -Path "$probe/About","$probe/Assemblies" -Force|Out-Null
 if($Version -eq '1.6'){
  $refs=@('mscorlib','System','System.Core','System.Xml','netstandard','Assembly-CSharp','UnityEngine.CoreModule','UnityEngine.IMGUIModule')|ForEach-Object{"$game/RimWorldWin64_Data/Managed/$_.dll"}
 }else{
  $refs=@(Get-ChildItem -LiteralPath $game -Filter 'System*.dll'|Where-Object Name -NotLike '*Native*'|ForEach-Object FullName)
  $refs+=@('netstandard','mscorlib','Assembly-CSharp','UnityStubs','Waylith','Waylith.UnityCompat')|ForEach-Object{"$game/$_.dll"}
 }
 $refs+="$mod/$Version/Assemblies/MechanicalVisualFramework.dll"
 $argsCompile=@('/nologo','/noconfig','/nostdlib+','/target:library','/optimize+','/langversion:12',"/out:$probe/Assemblies/FrameworkProbe.dll")
 # FrameworkProbe runs automated checks in the isolated test profile.
 $argsCompile+=@($refs|ForEach-Object{"/reference:$_"});$argsCompile+="$kit/Verification/FrameworkProbe.cs"
 & $cfg.CompilerPath $argsCompile
 if($LASTEXITCODE -ne 0){throw 'Probe build failed'}
 '<ModMetaData><name>RMVF verification</name><author>Grey·Oviin/OpenAI Assisted</author><packageId>local.rmvf.audit</packageId><supportedVersions><li>1.6</li><li>1.7</li></supportedVersions></ModMetaData>'|Set-Content -LiteralPath "$probe/About/About.xml" -Encoding UTF8
 Ensure-Junction "$runtime/Mods/FrameworkProbe" $probe
 $mods=$mods+@('local.rmvf.audit')
}
$runs="$kit/Work/Runs"
if(Test-Path -LiteralPath $runs){if(@(Get-ChildItem -LiteralPath $runs -Directory|Where-Object Name -Like "$Version-*").Count -ge 2){throw 'Two test profiles already exist for this version in Work/Runs. Save the results you need, then remove a completed test profile before starting another.'}}
$id=$Version+'-'+(Get-Date -Format 'yyyyMMdd-HHmmss');$profile="$runs/$id"
New-Item -ItemType Directory -Path "$profile/Config" -Force|Out-Null
('<ModsConfigData><version>'+$Version+'</version><activeMods>'+(($mods|ForEach-Object{"<li>$_</li>"})-join '')+'</activeMods></ModsConfigData>')|Set-Content -LiteralPath "$profile/Config/ModsConfig.xml" -Encoding UTF8
'<PrefsData><langFolderName>ChineseSimplified (简体中文)</langFolderName><screenWidth>1280</screenWidth><screenHeight>800</screenHeight><fullscreen>false</fullscreen><runInBackground>true</runInBackground><pauseOnLoad>true</pauseOnLoad></PrefsData>'|Set-Content -LiteralPath "$profile/Config/Prefs.xml" -Encoding UTF8
$launchArgs='-quicktest -screen-fullscreen 0 -savedatafolder="'+$profile+'"'
if($Version -eq '1.7'){$launchArgs+=' -NoFileLog -texCacheCompression=zstd'}else{$launchArgs+=' -logFile "'+$profile+'/Player.log"'}
[pscustomobject]@{Version=$Version;GameVersion=(Get-Content -LiteralPath "$game/Version.txt" -First 1);Profile=$profile;AutoTest=[bool]$AutoTest;ProbeKind=$(if($AutoTest){$ProbeKind}else{'None'});Visible=[bool]($Visible -or -not $AutoTest);DllSHA256=(Get-FileHash -LiteralPath "$mod/$Version/Assemblies/MechanicalVisualFramework.dll").Hash}|ConvertTo-Json|Set-Content -LiteralPath "$profile/run.json" -Encoding UTF8
Write-Output "Prepared: $profile"
if($Launch){
 $style=if($AutoTest -and -not $Visible){'Hidden'}else{'Normal'}
 $p=Start-Process -FilePath "$runtime/$exe" -WorkingDirectory $runtime -ArgumentList $launchArgs -WindowStyle $style -RedirectStandardOutput "$profile/stdout.txt" -RedirectStandardError "$profile/stderr.txt" -PassThru
 Write-Output "Started PID=$($p.Id). Automated tests close the game when finished. Test output is saved in $profile."
}else{Write-Output 'The test profile is ready. To launch a new run, repeat the command with -Launch; this creates a new profile.'}



