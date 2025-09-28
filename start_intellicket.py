#!/usr/bin/env python3
"""
Intellicket System Startup Script
Comprehensive startup script for the complete Intellicket ecosystem including admin interface
"""

import os
import sys
import subprocess
import time
import requests
from pathlib import Path

def print_banner():
    """Print Intellicket startup banner"""
    print("\n" + "="*80)
    print("🚀  INTELLICKET UNIFIED SYSTEM STARTUP")
    print("="*80)
    print("Starting complete Intellicket ecosystem:")
    print("  • CSDAIv2 Backend (Flask) - Port 5003")
    print("  • Intellicket Frontend (Next.js) - Port 3000") 
    print("  • Admin Interface (Next.js) - Port 3001")
    print("="*80)

def check_dependencies():
    """Check if required dependencies are available"""
    print("🔍 Checking system dependencies...")
    
    # Check Python
    try:
        python_version = sys.version_info
        if python_version.major < 3 or python_version.minor < 8:
            print("❌ Python 3.8+ required")
            return False
        print(f"✅ Python {python_version.major}.{python_version.minor}.{python_version.micro}")
    except Exception as e:
        print(f"❌ Python check failed: {e}")
        return False
    
    # Check Node.js (Windows compatible)
    try:
        result = subprocess.run(['node', '--version'], capture_output=True, text=True, shell=True)
        if result.returncode == 0:
            print(f"✅ Node.js {result.stdout.strip()}")
        else:
            print("❌ Node.js not found")
            return False
    except (FileNotFoundError, subprocess.SubprocessError):
        print("❌ Node.js not found")
        return False
    
    # Check npm (Windows compatible)
    try:
        result = subprocess.run(['npm', '--version'], capture_output=True, text=True, shell=True)
        if result.returncode == 0:
            print(f"✅ npm {result.stdout.strip()}")
        else:
            print("❌ npm not found")
            return False
    except (FileNotFoundError, subprocess.SubprocessError):
        print("❌ npm not found")
        return False
        
    return True

def install_backend_dependencies():
    """Install Python backend dependencies"""
    print("\n📦 Installing Backend Dependencies...")
    
    csdai_path = Path("CSDAIv2")
    if not csdai_path.exists():
        print("❌ CSDAIv2 directory not found")
        return False
    
    requirements_path = csdai_path / "requirements.txt"
    if not requirements_path.exists():
        print("❌ requirements.txt not found in CSDAIv2")
        return False
    
    try:
        print("Installing Python packages...")
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", str(requirements_path)
        ], check=True, capture_output=True, text=True)
        print("✅ Backend dependencies installed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install backend dependencies: {e}")
        return False

def install_frontend_dependencies():
    """Install Node.js frontend dependencies"""
    print("\n📦 Installing Frontend Dependencies...")
    
    # Install main frontend dependencies
    if Path("package.json").exists():
        try:
            print("Installing main frontend packages...")
            subprocess.run(["npm", "install"], check=True, shell=True)
            print("✅ Main frontend dependencies installed")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install main frontend dependencies: {e}")
            return False
    
    # Install admin interface dependencies
    admin_path = Path("intellicket-admin")
    if admin_path.exists() and (admin_path / "package.json").exists():
        try:
            print("Installing admin interface packages...")
            original_dir = os.getcwd()
            os.chdir(admin_path)
            subprocess.run(["npm", "install"], check=True, shell=True)
            os.chdir(original_dir)
            print("✅ Admin interface dependencies installed")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install admin interface dependencies: {e}")
            return False
    
    return True

def start_backend():
    """Start the CSDAIv2 backend server"""
    print("\n🔥 Starting CSDAIv2 Backend Server...")
    
    csdai_path = Path("CSDAIv2")
    if not csdai_path.exists():
        print("❌ CSDAIv2 directory not found")
        return None
    
    app_path = csdai_path / "app.py"
    if not app_path.exists():
        print("❌ app.py not found in CSDAIv2")
        return None
    
    try:
        # Change to CSDAIv2 directory and start the server
        original_dir = os.getcwd()
        os.chdir(csdai_path)
        
        # Start backend server (Windows compatible)
        backend_process = subprocess.Popen(
            [sys.executable, "app.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0
        )
        
        os.chdir(original_dir)
        
        # Wait for backend to start
        print("⏳ Waiting for backend to initialize...")
        time.sleep(5)
        
        # Check if backend is responding
        try:
            response = requests.get("http://localhost:5003/health", timeout=10)
            if response.status_code == 200:
                print("✅ CSDAIv2 Backend started successfully on port 5003")
                return backend_process
            else:
                print(f"❌ Backend health check failed: {response.status_code}")
        except requests.RequestException as e:
            print(f"❌ Backend health check failed: {e}")
        
        return backend_process
        
    except Exception as e:
        print(f"❌ Failed to start backend: {e}")
        return None

def start_frontend():
    """Start the main Intellicket frontend"""
    print("\n🌐 Starting Intellicket Frontend...")
    
    if not Path("package.json").exists():
        print("❌ package.json not found in root directory")
        return None
    
    try:
        # Start frontend server (Windows compatible)
        frontend_process = subprocess.Popen(
            ["npm", "run", "dev"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            shell=True,
            creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0
        )
        
        # Wait for frontend to start
        print("⏳ Waiting for frontend to initialize...")
        time.sleep(8)
        
        # Check if frontend is responding
        try:
            response = requests.get("http://localhost:3000", timeout=10)
            if response.status_code == 200:
                print("✅ Intellicket Frontend started successfully on port 3000")
                return frontend_process
            else:
                print(f"⚠️  Frontend may still be starting (HTTP {response.status_code})")
                return frontend_process
        except requests.RequestException:
            print("⚠️  Frontend may still be starting...")
            return frontend_process
            
    except Exception as e:
        print(f"❌ Failed to start frontend: {e}")
        return None

def start_admin_interface():
    """Start the admin interface"""
    print("\n🎛️  Starting Admin Interface...")
    
    admin_path = Path("intellicket-admin")
    if not admin_path.exists():
        print("❌ intellicket-admin directory not found")
        return None
    
    admin_package_json = admin_path / "package.json"
    if not admin_package_json.exists():
        print("❌ package.json not found in intellicket-admin")
        return None
    
    try:
        original_dir = os.getcwd()
        os.chdir(admin_path)
        
        # Start admin interface (Windows compatible)
        admin_process = subprocess.Popen(
            ["npm", "run", "dev"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            shell=True,
            creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0
        )
        
        os.chdir(original_dir)
        
        # Wait for admin interface to start
        print("⏳ Waiting for admin interface to initialize...")
        time.sleep(6)
        
        print("✅ Admin Interface started on port 3001")
        return admin_process
        
    except Exception as e:
        print(f"❌ Failed to start admin interface: {e}")
        return None

def show_status():
    """Show system status and URLs"""
    print("\n" + "="*80)
    print("🎯 INTELLICKET SYSTEM STATUS")
    print("="*80)
    
    # Check backend
    try:
        response = requests.get("http://localhost:5003/health", timeout=5)
        if response.status_code == 200:
            print("✅ Backend (CSDAIv2):     http://localhost:5003")
        else:
            print("❌ Backend (CSDAIv2):     Not responding")
    except:
        print("❌ Backend (CSDAIv2):     Not responding")
    
    # Check frontend
    try:
        response = requests.get("http://localhost:3000", timeout=5)
        if response.status_code == 200:
            print("✅ Frontend (Intellicket): http://localhost:3000")
        else:
            print("❌ Frontend (Intellicket): Not responding")
    except:
        print("❌ Frontend (Intellicket): Not responding")
    
    # Check admin interface
    try:
        response = requests.get("http://localhost:3001", timeout=5)
        if response.status_code == 200:
            print("✅ Admin Interface:      http://localhost:3001")
        else:
            print("❌ Admin Interface:      Not responding")
    except:
        print("❌ Admin Interface:      Not responding")
    
    print("="*80)
    print("🌟 Ready to analyze cybersecurity logs!")
    print("📊 Access your Intellicket dashboard at: http://localhost:3000")
    print("🎛️  Access admin controls at: http://localhost:3001")
    print("="*80)

def main():
    """Main startup function"""
    print_banner()
    
    # Check dependencies
    if not check_dependencies():
        print("\n❌ Dependencies check failed. Please install required software.")
        sys.exit(1)
    
    # Install dependencies
    print("\n📦 Installing Dependencies...")
    if not install_backend_dependencies():
        print("❌ Backend dependency installation failed")
        sys.exit(1)
    
    if not install_frontend_dependencies():
        print("❌ Frontend dependency installation failed")
        sys.exit(1)
    
    # Start services
    processes = []
    
    # Start backend
    backend_process = start_backend()
    if backend_process:
        processes.append(("Backend", backend_process))
    
    # Start frontend
    frontend_process = start_frontend()
    if frontend_process:
        processes.append(("Frontend", frontend_process))
    
    # Start admin interface
    admin_process = start_admin_interface()
    if admin_process:
        processes.append(("Admin", admin_process))
    
    # Show final status
    time.sleep(2)
    show_status()
    
    if processes:
        print(f"\n🚀 {len(processes)} services started successfully!")
        print("\nPress Ctrl+C to stop all services...")
        
        try:
            # Keep the script running
            while True:
                time.sleep(30)
                # Optional: Add periodic health checks here
        except KeyboardInterrupt:
            print("\n\n🛑 Shutting down Intellicket services...")
            
            # Terminate all processes
            for name, process in processes:
                try:
                    process.terminate()
                    print(f"✅ {name} service stopped")
                except:
                    print(f"⚠️  {name} service may still be running")
            
            # Wait a bit for graceful shutdown
            time.sleep(2)
            
            # Force kill if needed (Windows compatible)
            for name, process in processes:
                try:
                    if process.poll() is None:  # Still running
                        process.kill()
                except:
                    pass
            
            print("\n👋 Intellicket system shutdown complete!")
    else:
        print("\n❌ No services started successfully")
        sys.exit(1)

if __name__ == "__main__":
    main()