#!/usr/bin/env powershell
<#
.SYNOPSIS
    Intellicket Dependency Installation Script
.DESCRIPTION
    Automatically installs all required dependencies for the Intellicket platform
.EXAMPLE
    .\install_dependencies.ps1
#>

Write-Host "🚀 Intellicket Dependency Installation Script" -ForegroundColor Cyan
Write-Host "=" * 50 -ForegroundColor Cyan

# Check if running as Administrator for some installations
$isAdmin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "⚠️  Running without administrator privileges. Some installations might require elevation." -ForegroundColor Yellow
}

# Function to check if a command exists
function Test-Command {
    param($Command)
    try {
        Get-Command $Command -ErrorAction Stop | Out-Null
        return $true
    } catch {
        return $false
    }
}

# Check and install Python
Write-Host "`n🐍 Checking Python..." -ForegroundColor Yellow
if (Test-Command "python") {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ Python found: $pythonVersion" -ForegroundColor Green
    
    # Check Python version
    $version = python -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')"
    if ([float]$version -lt 3.8) {
        Write-Host "❌ Python version $version is too old. Need Python 3.8+" -ForegroundColor Red
        Write-Host "Please install Python 3.8+ from https://python.org" -ForegroundColor Yellow
        exit 1
    }
} else {
    Write-Host "❌ Python not found" -ForegroundColor Red
    Write-Host "Please install Python 3.8+ from https://python.org" -ForegroundColor Yellow
    Write-Host "Make sure to add Python to PATH during installation" -ForegroundColor Yellow
    exit 1
}

# Check and install Node.js
Write-Host "`n🟢 Checking Node.js..." -ForegroundColor Yellow
if (Test-Command "node") {
    $nodeVersion = node --version
    Write-Host "✅ Node.js found: $nodeVersion" -ForegroundColor Green
} else {
    Write-Host "❌ Node.js not found" -ForegroundColor Red
    Write-Host "Please install Node.js 18+ from https://nodejs.org" -ForegroundColor Yellow
    exit 1
}

# Check npm
if (Test-Command "npm") {
    $npmVersion = npm --version
    Write-Host "✅ npm found: v$npmVersion" -ForegroundColor Green
} else {
    Write-Host "❌ npm not found (should be included with Node.js)" -ForegroundColor Red
    exit 1
}

# Install Python dependencies
Write-Host "`n📦 Installing Python dependencies..." -ForegroundColor Yellow
if (Test-Path "CSDAIv2/requirements.txt") {
    Write-Host "Installing from CSDAIv2/requirements.txt..." -ForegroundColor Cyan
    
    # Upgrade pip first
    python -m pip install --upgrade pip
    
    # Install requirements
    python -m pip install -r CSDAIv2/requirements.txt
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Python dependencies installed successfully" -ForegroundColor Green
    } else {
        Write-Host "❌ Some Python dependencies failed to install" -ForegroundColor Red
        Write-Host "Try running: python -m pip install -r CSDAIv2/requirements.txt --no-cache-dir" -ForegroundColor Yellow
    }
} else {
    Write-Host "❌ requirements.txt not found in CSDAIv2/" -ForegroundColor Red
    exit 1
}

# Install main frontend dependencies
Write-Host "`n📦 Installing main frontend dependencies..." -ForegroundColor Yellow
if (Test-Path "package.json") {
    npm install
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Main frontend dependencies installed successfully" -ForegroundColor Green
    } else {
        Write-Host "❌ Main frontend dependencies installation failed" -ForegroundColor Red
    }
} else {
    Write-Host "❌ package.json not found in root directory" -ForegroundColor Red
}

# Install admin interface dependencies
Write-Host "`n📦 Installing admin interface dependencies..." -ForegroundColor Yellow
if (Test-Path "intellicket-admin/package.json") {
    Set-Location "intellicket-admin"
    npm install
    Set-Location ".."
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Admin interface dependencies installed successfully" -ForegroundColor Green
    } else {
        Write-Host "❌ Admin interface dependencies installation failed" -ForegroundColor Red
    }
} else {
    Write-Host "❌ package.json not found in intellicket-admin/" -ForegroundColor Red
}

# Create necessary directories
Write-Host "`n📂 Creating required directories..." -ForegroundColor Yellow
$directories = @(
    "CSDAIv2/temp",
    "CSDAIv2/exports",
    "CSDAIv2/knowledge_base", 
    "CSDAIv2/ml_models",
    "CSDAIv2/pdf",
    "CSDAIv2/static",
    "CSDAIv2/static/uploads"
)

foreach ($dir in $directories) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
        Write-Host "✅ Created: $dir" -ForegroundColor Green
    } else {
        Write-Host "✅ Exists: $dir" -ForegroundColor Green
    }
}

# Check for environment file
Write-Host "`n🔧 Checking environment configuration..." -ForegroundColor Yellow
if (-not (Test-Path "CSDAIv2/.env")) {
    Write-Host "⚠️  Creating template .env file..." -ForegroundColor Yellow
    $envTemplate = @"
# AI/RAG Configuration
OPENAI_API_KEY=your-claude-api-key-here
OPENAI_MODEL=claude-3-sonnet-20240229
RAG_PDF_DIRECTORY=pdf
RAG_ANALYSIS_TIMEOUT=30

# Flask Configuration
FLASK_ENV=development
FLASK_DEBUG=True
FLASK_PORT=5003

# Security Configuration
SECRET_KEY=$(Get-Random -SetSeed (Get-Date).Ticks)
UPLOAD_FOLDER=temp
MAX_CONTENT_LENGTH=100000000

# Database Configuration
DATABASE_URL=sqlite:///intellicket.db
"@
    $envTemplate | Out-File -FilePath "CSDAIv2/.env" -Encoding UTF8
    Write-Host "✅ Template .env file created" -ForegroundColor Green
    Write-Host "⚠️  Please edit CSDAIv2/.env and add your Claude API key" -ForegroundColor Yellow
} else {
    Write-Host "✅ .env file already exists" -ForegroundColor Green
}

# Run validation
Write-Host "`n✅ Running setup validation..." -ForegroundColor Yellow
python validate_setup.py

Write-Host "`n🎉 Installation complete!" -ForegroundColor Green
Write-Host "=" * 50 -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Edit CSDAIv2/.env and add your Claude API key" -ForegroundColor White
Write-Host "2. Run: python validate_setup.py (to verify everything works)" -ForegroundColor White
Write-Host "3. Run: .\start_intellicket.ps1 (to start the application)" -ForegroundColor White
Write-Host ""
Write-Host "Access URLs:" -ForegroundColor Cyan
Write-Host "- Main App: http://localhost:3000" -ForegroundColor White
Write-Host "- Admin Panel: http://localhost:3001" -ForegroundColor White
Write-Host "- Backend API: http://localhost:5003" -ForegroundColor White