[CmdletBinding()]
param(
    [string]$PythonLauncher = "py",
    [switch]$SkipDependencyInstall,
    [switch]$SkipInstaller
)

$ErrorActionPreference = "Stop"
$appRoot = Split-Path -Parent $PSCommandPath
$repoRoot = (Resolve-Path (Join-Path $appRoot "..\..")).Path
$venvPath = Join-Path $appRoot ".venv"
$venvPython = Join-Path $venvPath "Scripts\python.exe"
$requirements = Join-Path $appRoot "requirements-windows.txt"

if (-not (Test-Path -LiteralPath $venvPython)) {
    & $PythonLauncher -3.12 -m venv $venvPath
    if ($LASTEXITCODE -ne 0) {
        throw "CPython 3.12 is required to create the build environment."
    }
}

if (-not $SkipDependencyInstall) {
    & $venvPython -m pip install --disable-pip-version-check --requirement $requirements
    if ($LASTEXITCODE -ne 0) {
        throw "Could not install the pinned Windows build dependencies."
    }
}

$distPath = Join-Path $repoRoot "dist"
$workPath = Join-Path $repoRoot "build\auto-bovina"
$specPath = Join-Path $workPath "spec"
$dataPath = Join-Path $appRoot "data"
$sourcePath = Join-Path $appRoot "src"
$entryPoint = Join-Path $appRoot "main.py"

& $venvPython -m PyInstaller `
    --noconfirm `
    --clean `
    --onedir `
    --console `
    --name "autoBovina" `
    --distpath $distPath `
    --workpath $workPath `
    --specpath $specPath `
    --paths $sourcePath `
    --collect-all xlwings `
    --collect-all pyautogui `
    --collect-all pydirectinput `
    --collect-all pyperclip `
    --collect-all pywinauto `
    $entryPoint

if ($LASTEXITCODE -ne 0) {
    throw "PyInstaller did not produce autoBovina.exe."
}

$exePath = Join-Path $distPath "autoBovina\autoBovina.exe"
$distributionDataPath = Join-Path (Split-Path -Parent $exePath) "data"
New-Item -ItemType Directory -Force -Path $distributionDataPath | Out-Null
Copy-Item -Path (Join-Path $dataPath "*") -Destination $distributionDataPath -Recurse -Force
Write-Output "Distribution complete: $exePath"

if ($SkipInstaller) {
    exit 0
}

$versionLine = Select-String -LiteralPath (Join-Path $appRoot "pyproject.toml") -Pattern '^version\s*=\s*"([^"]+)"' | Select-Object -First 1
if ($null -eq $versionLine -or $versionLine.Line -notmatch '"([^"]+)"') {
    throw "Could not read the application version from pyproject.toml."
}
$appVersion = $Matches[1]
$isccCandidates = @(
    (Get-Command ISCC.exe -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Source -ErrorAction SilentlyContinue),
    "C:\Program Files (x86)\Inno Setup 6\ISCC.exe",
    "C:\Program Files\Inno Setup 6\ISCC.exe"
) | Where-Object { $_ -and (Test-Path -LiteralPath $_) }
$iscc = $isccCandidates | Select-Object -First 1
if (-not $iscc) {
    throw "Inno Setup 6 was not found. Re-run with -SkipInstaller to build only dist, or install Inno Setup 6."
}

$installerScript = Join-Path $appRoot "installer\autoBovina.iss"
& $iscc "/DSourceDist=$(Join-Path $distPath 'autoBovina')" "/DMyAppVersion=$appVersion" $installerScript
if ($LASTEXITCODE -ne 0) {
    throw "Inno Setup did not produce the installer."
}

Write-Output "Installer complete: $(Join-Path $repoRoot "release\autoBovina-setup-$appVersion.exe")"
