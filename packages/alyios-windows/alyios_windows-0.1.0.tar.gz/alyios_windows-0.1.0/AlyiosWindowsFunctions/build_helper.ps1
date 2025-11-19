# Build script for DialogHelper.exe
# Compiles the C# helper with DPI awareness

$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
$csFile = Join-Path $scriptPath "DialogHelper.cs"
$manifestFile = Join-Path $scriptPath "app.manifest"
$outputExe = Join-Path $scriptPath "DialogHelper.exe"

Write-Host "Building AlyiosDialogHelper..." -ForegroundColor Cyan

# Find csc.exe (C# compiler)
$cscPath = $null
$frameworkPaths = @(
    "C:\Windows\Microsoft.NET\Framework64\v4.0.30319\csc.exe",
    "C:\Windows\Microsoft.NET\Framework\v4.0.30319\csc.exe"
)

foreach ($path in $frameworkPaths) {
    if (Test-Path $path) {
        $cscPath = $path
        break
    }
}

if (-not $cscPath) {
    Write-Host "ERROR: C# compiler (csc.exe) not found!" -ForegroundColor Red
    Write-Host "Please install .NET Framework 4.0 or later" -ForegroundColor Yellow
    exit 1
}

Write-Host "Using compiler: $cscPath" -ForegroundColor Gray

# Compile with manifest
$compileArgs = @(
    "/target:exe",
    "/win32manifest:$manifestFile",
    "/out:$outputExe",
    "/reference:System.Windows.Forms.dll",
    "/reference:System.Drawing.dll",
    "/optimize+",
    "/nologo",
    $csFile
)

Write-Host "Compiling..." -ForegroundColor Gray
& $cscPath $compileArgs

if ($LASTEXITCODE -eq 0) {
    Write-Host "[SUCCESS] Build successful: $outputExe" -ForegroundColor Green
    Write-Host ""
    Write-Host "File size: $((Get-Item $outputExe).Length / 1KB) KB" -ForegroundColor Gray
} else {
    Write-Host "[ERROR] Build failed!" -ForegroundColor Red
    exit 1
}
