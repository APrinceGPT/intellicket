# Intellicket System Startup Script for Windows PowerShell
# Comprehensive startup script for the complete Intellicket ecosystem

Write-Host ""
Write-Host "=" * 80 -ForegroundColor Blue
Write-Host "🚀  INTELLICKET UNIFIED SYSTEM STARTUP" -ForegroundColor Yellow
Write-Host "=" * 80 -ForegroundColor Blue
Write-Host "Starting complete Intellicket ecosystem:"
Write-Host "  • CSDAIv2 Backend (Flask) - Port 5003" -ForegroundColor Green
Write-Host "  • Intellicket Frontend (Next.js) - Port 3000" -ForegroundColor Green
Write-Host "  • Admin Interface (Next.js) - Port 3001" -ForegroundColor Green
Write-Host "=" * 80 -ForegroundColor Blue

# Function to check dependencies
function Test-Dependencies {
    Write-Host "🔍 Checking system dependencies..." -ForegroundColor Cyan
    
    # Check Python
    try {
        $pythonVersion = python --version 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ $pythonVersion" -ForegroundColor Green
        } else {
            Write-Host "❌ Python not found" -ForegroundColor Red
            return $false
        }
    } catch {
        Write-Host "❌ Python not found" -ForegroundColor Red
        return $false
    }
    
    # Check Node.js
    try {
        $nodeVersion = node --version 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Node.js $nodeVersion" -ForegroundColor Green
        } else {
            Write-Host "❌ Node.js not found" -ForegroundColor Red
            return $false
        }
    } catch {
        Write-Host "❌ Node.js not found" -ForegroundColor Red
        return $false
    }
    
    # Check npm
    try {
        $npmVersion = npm --version 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ npm $npmVersion" -ForegroundColor Green
        } else {
            Write-Host "❌ npm not found" -ForegroundColor Red
            return $false
        }
    } catch {
        Write-Host "❌ npm not found" -ForegroundColor Red
        return $false
    }
    
    return $true
}

# Function to install backend dependencies
function Install-BackendDependencies {
    Write-Host ""
    Write-Host "📦 Installing Backend Dependencies..." -ForegroundColor Cyan
    
    if (-not (Test-Path "CSDAIv2")) {
        Write-Host "❌ CSDAIv2 directory not found" -ForegroundColor Red
        return $false
    }
    
    if (-not (Test-Path "CSDAIv2\requirements.txt")) {
        Write-Host "❌ requirements.txt not found in CSDAIv2" -ForegroundColor Red
        return $false
    }
    
    try {
        Write-Host "Installing Python packages..." -ForegroundColor Yellow
        python -m pip install -r CSDAIv2\requirements.txt
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Backend dependencies installed" -ForegroundColor Green
            return $true
        } else {
            Write-Host "❌ Failed to install backend dependencies" -ForegroundColor Red
            return $false
        }
    } catch {
        Write-Host "❌ Failed to install backend dependencies" -ForegroundColor Red
        return $false
    }
}

# Function to install frontend dependencies
function Install-FrontendDependencies {
    Write-Host ""
    Write-Host "📦 Installing Frontend Dependencies..." -ForegroundColor Cyan
    
    # Install main frontend dependencies
    if (Test-Path "package.json") {
        try {
            Write-Host "Installing main frontend packages..." -ForegroundColor Yellow
            npm install
            if ($LASTEXITCODE -eq 0) {
                Write-Host "✅ Main frontend dependencies installed" -ForegroundColor Green
            } else {
                Write-Host "❌ Failed to install main frontend dependencies" -ForegroundColor Red
                return $false
            }
        } catch {
            Write-Host "❌ Failed to install main frontend dependencies" -ForegroundColor Red
            return $false
        }
    }
    
    # Install admin interface dependencies
    if ((Test-Path "intellicket-admin") -and (Test-Path "intellicket-admin\package.json")) {
        try {
            Write-Host "Installing admin interface packages..." -ForegroundColor Yellow
            Set-Location "intellicket-admin"
            npm install
            Set-Location ".."
            if ($LASTEXITCODE -eq 0) {
                Write-Host "✅ Admin interface dependencies installed" -ForegroundColor Green
            } else {
                Write-Host "❌ Failed to install admin interface dependencies" -ForegroundColor Red
                return $false
            }
        } catch {
            Write-Host "❌ Failed to install admin interface dependencies" -ForegroundColor Red
            Set-Location ".."
            return $false
        }
    }
    
    return $true
}

# Function to start backend
function Start-Backend {
    Write-Host ""
    Write-Host "🔥 Starting CSDAIv2 Backend Server..." -ForegroundColor Cyan
    
    if (-not (Test-Path "CSDAIv2")) {
        Write-Host "❌ CSDAIv2 directory not found" -ForegroundColor Red
        return $null
    }
    
    if (-not (Test-Path "CSDAIv2\app.py")) {
        Write-Host "❌ app.py not found in CSDAIv2" -ForegroundColor Red
        return $null
    }
    
    try {
        # Get current directory for the new terminal
        $currentDir = Get-Location
        
        # Start backend in new PowerShell terminal window
        $backendProcess = Start-Process -FilePath "powershell" -ArgumentList "-NoExit", "-Command", "Set-Location '$currentDir'; Write-Host '🔥 CSDAIv2 Backend Server - Port 5003' -ForegroundColor Green; Write-Host 'Press Ctrl+C to stop this service' -ForegroundColor Yellow; Write-Host ''; python CSDAIv2\app.py" -WindowStyle Normal -PassThru
        
        Write-Host "⏳ Waiting for backend to initialize..." -ForegroundColor Yellow
        Start-Sleep -Seconds 5
        
        # Check if backend is responding
        try {
            $response = Invoke-WebRequest -Uri "http://localhost:5003/health" -TimeoutSec 10 -UseBasicParsing
            if ($response.StatusCode -eq 200) {
                Write-Host "✅ CSDAIv2 Backend started successfully on port 5003" -ForegroundColor Green
            } else {
                Write-Host "❌ Backend health check failed: $($response.StatusCode)" -ForegroundColor Red
            }
        } catch {
            Write-Host "❌ Backend health check failed: $($_.Exception.Message)" -ForegroundColor Red
        }
        
        return $backendProcess
        
    } catch {
        Write-Host "❌ Failed to start backend: $($_.Exception.Message)" -ForegroundColor Red
        return $null
    }
}

# Function to start frontend
function Start-Frontend {
    Write-Host ""
    Write-Host "🌐 Starting Intellicket Frontend..." -ForegroundColor Cyan
    
    if (-not (Test-Path "package.json")) {
        Write-Host "❌ package.json not found in root directory" -ForegroundColor Red
        return $null
    }
    
    try {
        # Get current directory for the new terminal
        $currentDir = Get-Location
        
        # Start frontend in new PowerShell terminal window
        $frontendProcess = Start-Process -FilePath "powershell" -ArgumentList "-NoExit", "-Command", "Set-Location '$currentDir'; Write-Host '🌐 Intellicket Frontend - Port 3000' -ForegroundColor Green; Write-Host 'Press Ctrl+C to stop this service' -ForegroundColor Yellow; Write-Host ''; npm run dev" -WindowStyle Normal -PassThru
        
        Write-Host "⏳ Waiting for frontend to initialize..." -ForegroundColor Yellow
        Start-Sleep -Seconds 8
        
        # Check if frontend is responding
        try {
            $response = Invoke-WebRequest -Uri "http://localhost:3000" -TimeoutSec 10 -UseBasicParsing
            if ($response.StatusCode -eq 200) {
                Write-Host "✅ Intellicket Frontend started successfully on port 3000" -ForegroundColor Green
            } else {
                Write-Host "⚠️  Frontend may still be starting (HTTP $($response.StatusCode))" -ForegroundColor Yellow
            }
        } catch {
            Write-Host "⚠️  Frontend may still be starting..." -ForegroundColor Yellow
        }
        
        return $frontendProcess
        
    } catch {
        Write-Host "❌ Failed to start frontend: $($_.Exception.Message)" -ForegroundColor Red
        return $null
    }
}

# Function to start admin interface
function Start-AdminInterface {
    Write-Host ""
    Write-Host "🎛️  Starting Admin Interface..." -ForegroundColor Cyan
    
    if (-not (Test-Path "intellicket-admin")) {
        Write-Host "❌ intellicket-admin directory not found" -ForegroundColor Red
        return $null
    }
    
    if (-not (Test-Path "intellicket-admin\package.json")) {
        Write-Host "❌ package.json not found in intellicket-admin" -ForegroundColor Red
        return $null
    }
    
    try {
        # Get current directory for the new terminal
        $currentDir = Get-Location
        
        # Start admin interface in new PowerShell terminal window
        $adminProcess = Start-Process -FilePath "powershell" -ArgumentList "-NoExit", "-Command", "Set-Location '$currentDir'; Write-Host '🎛️ Admin Interface - Port 3001' -ForegroundColor Green; Write-Host 'Press Ctrl+C to stop this service' -ForegroundColor Yellow; Write-Host ''; Set-Location intellicket-admin; npm run dev" -WindowStyle Normal -PassThru
        
        Write-Host "⏳ Waiting for admin interface to initialize..." -ForegroundColor Yellow
        Start-Sleep -Seconds 6
        
        Write-Host "✅ Admin Interface started on port 3001" -ForegroundColor Green
        return $adminProcess
        
    } catch {
        Write-Host "❌ Failed to start admin interface: $($_.Exception.Message)" -ForegroundColor Red
        return $null
    }
}

# Function to show system status
function Show-Status {
    Write-Host ""
    Write-Host "=" * 80 -ForegroundColor Blue
    Write-Host "🎯 INTELLICKET SYSTEM STATUS" -ForegroundColor Yellow
    Write-Host "=" * 80 -ForegroundColor Blue
    
    # Check backend
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:5003/health" -TimeoutSec 5 -UseBasicParsing
        if ($response.StatusCode -eq 200) {
            Write-Host "✅ Backend (CSDAIv2):     http://localhost:5003" -ForegroundColor Green
        } else {
            Write-Host "❌ Backend (CSDAIv2):     Not responding" -ForegroundColor Red
        }
    } catch {
        Write-Host "❌ Backend (CSDAIv2):     Not responding" -ForegroundColor Red
    }
    
    # Check frontend
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:3000" -TimeoutSec 5 -UseBasicParsing
        if ($response.StatusCode -eq 200) {
            Write-Host "✅ Frontend (Intellicket): http://localhost:3000" -ForegroundColor Green
        } else {
            Write-Host "❌ Frontend (Intellicket): Not responding" -ForegroundColor Red
        }
    } catch {
        Write-Host "❌ Frontend (Intellicket): Not responding" -ForegroundColor Red
    }
    
    # Check admin interface
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:3001" -TimeoutSec 5 -UseBasicParsing
        if ($response.StatusCode -eq 200) {
            Write-Host "✅ Admin Interface:      http://localhost:3001" -ForegroundColor Green
        } else {
            Write-Host "❌ Admin Interface:      Not responding" -ForegroundColor Red
        }
    } catch {
        Write-Host "❌ Admin Interface:      Not responding" -ForegroundColor Red
    }
    
    Write-Host "=" * 80 -ForegroundColor Blue
    Write-Host "🌟 Ready to analyze cybersecurity logs!" -ForegroundColor Yellow
    Write-Host "📊 Access your Intellicket dashboard at: http://localhost:3000" -ForegroundColor Cyan
    Write-Host "🎛️  Access admin controls at: http://localhost:3001" -ForegroundColor Cyan
    Write-Host "=" * 80 -ForegroundColor Blue
}

# Main execution
try {
    # Check dependencies
    if (-not (Test-Dependencies)) {
        Write-Host ""
        Write-Host "❌ Dependencies check failed. Please install required software." -ForegroundColor Red
        exit 1
    }
    
    # Install dependencies
    Write-Host ""
    Write-Host "📦 Installing Dependencies..." -ForegroundColor Cyan
    if (-not (Install-BackendDependencies)) {
        Write-Host "❌ Backend dependency installation failed" -ForegroundColor Red
        exit 1
    }
    
    if (-not (Install-FrontendDependencies)) {
        Write-Host "❌ Frontend dependency installation failed" -ForegroundColor Red
        exit 1
    }
    
    # Start services
    $processes = @()
    
    # Start backend
    $backendProcess = Start-Backend
    if ($backendProcess) {
        $processes += @{Name="Backend"; Process=$backendProcess}
    }
    
    # Start frontend
    $frontendProcess = Start-Frontend
    if ($frontendProcess) {
        $processes += @{Name="Frontend"; Process=$frontendProcess}
    }
    
    # Start admin interface
    $adminProcess = Start-AdminInterface
    if ($adminProcess) {
        $processes += @{Name="Admin"; Process=$adminProcess}
    }
    
    # Show final status
    Start-Sleep -Seconds 2
    Show-Status
    
    if ($processes.Count -gt 0) {
        Write-Host ""
        Write-Host "🚀 $($processes.Count) services started successfully in separate terminal windows!" -ForegroundColor Green
        Write-Host ""
        Write-Host "📋 TERMINAL WINDOWS OPENED:" -ForegroundColor Cyan
        Write-Host "  • Backend Terminal:    python CSDAIv2\app.py (Port 5003)" -ForegroundColor White
        Write-Host "  • Frontend Terminal:   npm run dev (Port 3000)" -ForegroundColor White
        Write-Host "  • Admin Terminal:      npm run dev (Port 3001)" -ForegroundColor White
        Write-Host ""
        Write-Host "🔧 To stop individual services:" -ForegroundColor Yellow
        Write-Host "  • Go to each terminal window and press Ctrl+C" -ForegroundColor White
        Write-Host ""
        Write-Host "🔧 To stop all services at once:" -ForegroundColor Yellow
        Write-Host "  • Press Ctrl+C in this window" -ForegroundColor White
        Write-Host ""
        Write-Host "⏳ Monitoring services... Press Ctrl+C to stop all" -ForegroundColor Yellow
        
        # Keep script running for monitoring and cleanup
        try {
            while ($true) {
                Start-Sleep -Seconds 30
                # Optional: Add periodic health checks here
            }
        } catch {
            Write-Host ""
            Write-Host "🛑 Shutting down Intellicket services..." -ForegroundColor Yellow
            
            # Stop all processes
            foreach ($svc in $processes) {
                try {
                    if (-not $svc.Process.HasExited) {
                        $svc.Process.Kill()
                        Write-Host "✅ $($svc.Name) service stopped" -ForegroundColor Green
                    }
                } catch {
                    Write-Host "⚠️  $($svc.Name) service may still be running" -ForegroundColor Yellow
                }
            }
            
            Write-Host ""
            Write-Host "👋 Intellicket system shutdown complete!" -ForegroundColor Green
            Write-Host "💡 Note: You may need to manually close the terminal windows if they're still open." -ForegroundColor Cyan
        }
    } else {
        Write-Host ""
        Write-Host "❌ No services started successfully" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "❌ Script execution failed: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}