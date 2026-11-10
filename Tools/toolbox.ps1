param([ValidateSet('Menu','Configure','New','BuildAssets','BuildCode','Validate','Test16','Test17','Package','Docs','ImportGLB')][string]$Action='Menu')
$ErrorActionPreference='Stop'
$root=Split-Path $PSScriptRoot -Parent
$config=Join-Path $root 'ToolPaths.local.json'
if($Action -eq 'Menu'){
 Write-Host "RMVF Creator Toolbox"
 Write-Host "1 Configure paths   2 New mod   3 Build sample assets   4 Build framework DLLs"
 Write-Host "5 Validate          6 Test 1.6  7 Test 1.7             8 Package"
 Write-Host "9 Open guide       10 Import GLB rest pose"
 $items=@('Configure','New','BuildAssets','BuildCode','Validate','Test16','Test17','Package','Docs','ImportGLB')
 $choice=0;if(-not [int]::TryParse((Read-Host 'Choose 1..10'),[ref]$choice) -or $choice -lt 1 -or $choice -gt 10){throw 'Unknown choice'}
 $Action=$items[$choice-1]
}
if($Action -eq 'Configure'){
 $cfg=[ordered]@{
  Game16Root=(Read-Host 'RimWorld 1.6 directory (optional if not testing/building 1.6)')
  Game17Root=(Read-Host 'RimWorld 1.7 directory (optional if not testing/building 1.7)')
  CompilerPath=(Read-Host 'Existing Roslyn csc.exe (only needed to rebuild C#)')
  PythonPath=(Read-Host 'Existing Python 3.10+ executable (or python)')
 }
 $cfg|ConvertTo-Json|Set-Content -LiteralPath $config -Encoding UTF8
 Write-Host 'Saved locally; excluded from repository and release packages.';return
}
if($Action -eq 'Docs'){Start-Process (Join-Path $root 'README.md');return}
if(-not(Test-Path -LiteralPath $config)){throw 'Run Configure first. Tools never install/download dependencies.'}
$cfg=Get-Content -LiteralPath $config -Raw -Encoding UTF8|ConvertFrom-Json
$python=$cfg.PythonPath;if(-not $python){$python='python'}
$env:PYTHONIOENCODING='utf-8'
switch($Action){
 'New' { $dest=Read-Host 'New mod directory';$id=Read-Host 'Unique package ID (example author.machine)';$name=Read-Host 'Mod display name'; & $python "$PSScriptRoot/new_project.py" $dest --id $id --name $name }
 'BuildAssets' { & $python "$PSScriptRoot/build_assets.py" }
 'BuildCode' { & "$root/Mod/Source/Build.ps1" }
 'Validate' { & $python "$PSScriptRoot/validate.py";if($LASTEXITCODE -ne 0){throw 'Validation failed'};& $python -m unittest discover -s "$root/Verification" -p 'test_*.py' }
 'Test16' { & "$PSScriptRoot/Start-Examples.ps1" -Version 1.6 -AutoTest -Launch }
 'Test17' { & "$PSScriptRoot/Start-Examples.ps1" -Version 1.7 -AutoTest -Launch }
 'Package' { & $python "$PSScriptRoot/package.py" }
 'ImportGLB' { $src=Read-Host 'GLB file';$dest=Read-Host 'New output JSON file'; & $python "$PSScriptRoot/import_glb.py" $src $dest }
}
if($LASTEXITCODE -and $LASTEXITCODE -ne 0){throw "Tool failed ($LASTEXITCODE)"}

