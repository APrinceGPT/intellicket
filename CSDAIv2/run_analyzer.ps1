# Deep Security Unified Analyzer - PowerShell Launcher
# ====================================================

Write-Host "Deep Security Unified Analyzer - Python Launcher" -ForegroundColor Cyan
Write-Host "====================================================" -ForegroundColor Cyan
Write-Host ""

# Get the directory where this script is located
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

Write-Host "Current directory: $(Get-Location)" -ForegroundColor Yellow
Write-Host ""

# Function to test Python executable
function Test-PythonExecutable {
    param([string]$PythonPath)
    
    try {
        if (Test-Path $PythonPath) {
            $version = & $PythonPath --version 2>&1
            if ($LASTEXITCODE -eq 0) {
                Write-Host "✓ Found Python at: $PythonPath" -ForegroundColor Green
                Write-Host "  Version: $version" -ForegroundColor Gray
                return $true
            }
        }
    }
    catch {
        # Silently continue
    }
    return $false
}

# Function to run the analyzer
function Start-Analyzer {
    param([string]$PythonPath)
    
    Write-Host ""
    Write-Host "Starting UNIFIED_ANALYZER.py..." -ForegroundColor Green
    Write-Host ""
    
    try {
        & $PythonPath "UNIFIED_ANALYZER.py"
    }
    catch {
        Write-Host "Error running the analyzer: $_" -ForegroundColor Red
    }
}

Write-Host "Checking for Python installation..." -ForegroundColor Yellow

# Method 1: Try 'python' command
try {
    $pythonVersion = python --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ Found Python using 'python' command" -ForegroundColor Green
        Write-Host "  Version: $pythonVersion" -ForegroundColor Gray
        Start-Analyzer "python"
        exit
    }
}
catch {
    # Continue to next method
}

# Method 2: Try 'py' launcher
try {
    $pyVersion = py --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ Found Python using 'py' launcher" -ForegroundColor Green
        Write-Host "  Version: $pyVersion" -ForegroundColor Gray
        Start-Analyzer "py"
        exit
    }
}
catch {
    # Continue to next method
}

# Method 3: Search common Python installation paths
$PythonPaths = @(
    "C:\Program Files\Python312\python.exe",
    "C:\Program Files\Python311\python.exe",
    "C:\Program Files\Python310\python.exe",
    "C:\Program Files\Python39\python.exe",
    "C:\Program Files (x86)\Python312\python.exe",
    "C:\Program Files (x86)\Python311\python.exe",
    "C:\Program Files (x86)\Python310\python.exe",
    "C:\Program Files (x86)\Python39\python.exe",
    "C:\Python312\python.exe",
    "C:\Python311\python.exe",
    "C:\Python310\python.exe",
    "C:\Python39\python.exe",
    "$env:USERPROFILE\AppData\Local\Programs\Python\Python312\python.exe",
    "$env:USERPROFILE\AppData\Local\Programs\Python\Python311\python.exe",
    "$env:USERPROFILE\AppData\Local\Programs\Python\Python310\python.exe",
    "$env:USERPROFILE\AppData\Local\Programs\Python\Python39\python.exe",
    "$env:USERPROFILE\AppData\Local\Microsoft\WindowsApps\python.exe"
)

foreach ($PythonPath in $PythonPaths) {
    if (Test-PythonExecutable $PythonPath) {
        Start-Analyzer $PythonPath
        break
    }
}

# If no Python found
Write-Host ""
Write-Host "❌ Python not found!" -ForegroundColor Red
Write-Host ""
Write-Host "Python installation not detected. Please:" -ForegroundColor Yellow
Write-Host "1. Install Python from https://python.org" -ForegroundColor White
Write-Host "2. Add Python to your PATH environment variable" -ForegroundColor White
Write-Host "3. Or place python.exe in this directory" -ForegroundColor White
Write-Host ""
Write-Host "See ADD_PYTHON_TO_PATH_GUIDE.txt for detailed instructions." -ForegroundColor Cyan
Write-Host ""

# Keep window open
Write-Host "Press any key to continue..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
