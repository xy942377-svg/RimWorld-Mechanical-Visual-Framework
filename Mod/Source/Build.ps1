param(
 [ValidateSet('1.6','1.7')][string[]]$Versions=@('1.6','1.7'),
 [string]$CompilerPath, [string]$Game16Root, [string]$Game17Root, [string]$ConfigPath
)
$ErrorActionPreference='Stop'
$mod=Split-Path $PSScriptRoot -Parent
$kit=Split-Path $mod -Parent
if(-not $ConfigPath){$ConfigPath=Join-Path $kit 'ToolPaths.local.json'}
if(Test-Path -LiteralPath $ConfigPath){
 $cfg=Get-Content -LiteralPath $ConfigPath -Encoding UTF8 -Raw | ConvertFrom-Json
 if(-not $CompilerPath){$CompilerPath=$cfg.CompilerPath}
 if(-not $Game16Root){$Game16Root=$cfg.Game16Root}
 if(-not $Game17Root){$Game17Root=$cfg.Game17Root}
}
if(-not $CompilerPath -or -not(Test-Path -LiteralPath $CompilerPath -PathType Leaf)){throw 'Set -CompilerPath or ToolPaths.local.json to an existing Roslyn csc.exe.'}
$sources=@(Get-ChildItem -LiteralPath $PSScriptRoot -Filter '*.cs' | Sort-Object Name)
$targets=@()
# The tested 1.6 uses Unity Managed references; tested 1.7 exposes compatibility assemblies at game root.
# Recheck the actual target after game updates. Never mix these sets.
foreach($v in $Versions){
 $game=if($v -eq '1.6'){$Game16Root}else{$Game17Root}
 if(-not $game){throw "Game root missing for $v"}
 $refsRoot=if($v -eq '1.6'){Join-Path $game 'RimWorldWin64_Data/Managed'}else{$game}
 if($v -eq '1.6'){
  $refs=@('mscorlib','System','System.Core','System.Xml','netstandard','Assembly-CSharp','UnityEngine.CoreModule','UnityEngine.IMGUIModule','UnityEngine.TextRenderingModule') | ForEach-Object {Join-Path $refsRoot "$_.dll"}
 }else{
  $refs=@(Get-ChildItem -LiteralPath $refsRoot -Filter 'System*.dll' | Where-Object Name -NotLike '*Native*' | ForEach-Object FullName)
  $refs+=@('netstandard','mscorlib','Assembly-CSharp','UnityStubs','Waylith','Waylith.UnityCompat') | ForEach-Object {Join-Path $refsRoot "$_.dll"}
 }
 foreach($ref in $refs){if(-not(Test-Path -LiteralPath $ref -PathType Leaf)){throw "Missing $v reference: $ref"}}
 $dest=Join-Path $mod "$v/Assemblies";New-Item -ItemType Directory -Path $dest -Force | Out-Null
 $compilerArgs=@('/nologo','/noconfig','/nostdlib+','/target:library','/optimize+','/unsafe+','/deterministic+','/warnaserror+','/langversion:12',"/define:RW$($v.Replace('.',''))","/out:$dest/MechanicalVisualFramework.dll","/pathmap:$mod=/_/MechanicalVisualFramework")
 $compilerArgs+=@($refs|ForEach-Object{"/reference:$_"});$compilerArgs+=$sources.FullName
 & $CompilerPath $compilerArgs
 if($LASTEXITCODE -ne 0){throw "Compilation failed: $v"}
 $targets+=[pscustomobject]@{Version=$v;AssemblySHA256=(Get-FileHash -LiteralPath "$dest/MechanicalVisualFramework.dll").Hash;GameSHA256=(Get-FileHash -LiteralPath "$refsRoot/Assembly-CSharp.dll").Hash}
 Write-Output "Built $v"
}
# Manifest covers only the versions built in this invocation. Build BOTH for a dual-version release.
[pscustomobject]@{
 Build='0.1.0-candidate1'
 Sources=@($sources|ForEach-Object{[pscustomobject]@{Name=$_.Name;SHA256=(Get-FileHash -LiteralPath $_.FullName).Hash}})

 Targets=$targets
}|ConvertTo-Json -Depth 5|Set-Content -LiteralPath "$mod/BuildManifest.json" -Encoding UTF8

