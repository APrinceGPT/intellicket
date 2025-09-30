# Intellicket AI Support Platform - Setup Guide

## 🚀 Quick Start

This guide will help you set up the complete Intellicket AI Support Platform from scratch. Intellicket is a comprehensive cybersecurity log analysis platform with AI-enhanced capabilities.

## 📋 System Requirements

### Minimum Requirements
- **Operating System**: Windows 10/11, macOS 10.15+, or Linux (Ubuntu 20.04+ recommended)
- **Memory**: 4GB RAM (8GB+ recommended for ML operations)
- **Storage**: 2GB+ free space
- **Internet**: Required for AI model downloads and API access

### Software Requirements
- **Python**: 3.8+ (3.9+ recommended)
- **Node.js**: 18.0+ (20.0+ recommended)
- **npm**: 9.0+ (included with Node.js)
- **Git**: Latest version

## 🔧 Installation Steps

### Step 1: Clone the Repository

```powershell
# Clone the repository
git clone https://github.com/your-repo/intellicket.git
cd intellicket
```

### Step 2: Python Environment Setup

#### Option A: Using Python Virtual Environment (Recommended)
```powershell
# Create virtual environment
python -m venv venv

# Activate virtual environment (Windows)
venv\Scripts\activate
# OR for macOS/Linux
source venv/bin/activate

# Upgrade pip
python -m pip install --upgrade pip

# Install Python dependencies
cd CSDAIv2
pip install -r requirements.txt
```

#### Option B: Using Conda
```powershell
# Create conda environment
conda create -n intellicket python=3.9
conda activate intellicket

# Install dependencies
cd CSDAIv2
pip install -r requirements.txt
```

### Step 3: Frontend Dependencies

#### Main Frontend (Next.js)
```powershell
# Return to root directory
cd ..

# Install main frontend dependencies
npm install

# Install additional dev dependencies if needed
npm audit fix --force
```

#### Admin Interface
```powershell
# Install admin interface dependencies
cd intellicket-admin
npm install
cd ..
```

### Step 4: Environment Configuration

#### Create Backend Environment File
Create `CSDAIv2/.env` file with the following content:

```env
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
SECRET_KEY=your-secret-key-here
UPLOAD_FOLDER=temp
MAX_CONTENT_LENGTH=100000000

# Database Configuration
DATABASE_URL=sqlite:///intellicket.db

# Optional: Performance Configuration
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/0
```

#### Important Environment Variables

1. **OPENAI_API_KEY**: Get your Claude API key from Anthropic
   - Visit: https://console.anthropic.com/
   - Create account and generate API key
   - **Note**: This is required for AI-enhanced analysis features

2. **SECRET_KEY**: Generate a secure secret key
   ```powershell
   python -c "import secrets; print(secrets.token_hex(32))"
   ```

### Step 5: Knowledge Base Setup

```powershell
# Create knowledge base directories
cd CSDAIv2
mkdir -p pdf knowledge_base ml_models exports temp static/uploads

# Copy any existing PDF documentation to CSDAIv2/pdf/
# The system will automatically index these for RAG queries
```

### Step 6: Database Initialization

```powershell
# Initialize database (if using SQLite)
cd CSDAIv2
python -c "
import sqlite3
import os
os.makedirs('knowledge_base', exist_ok=True)
conn = sqlite3.connect('knowledge_base/ds_knowledge.db')
conn.execute('CREATE TABLE IF NOT EXISTS documents (id INTEGER PRIMARY KEY, content TEXT, metadata TEXT)')
conn.commit()
conn.close()
print('Database initialized successfully')
"
```

## 🏃‍♂️ Running the Application

### Option 1: Automated Startup (Recommended)
```powershell
# Use the provided PowerShell script
.\start_intellicket.ps1
```

### Option 2: Manual Startup (3 Terminals)

#### Terminal 1 - Backend (Flask)
```powershell
cd CSDAIv2
# Activate virtual environment if not already active
venv\Scripts\activate  # Windows
# source venv/bin/activate  # macOS/Linux

python app.py
```

#### Terminal 2 - Main Frontend (Next.js)
```powershell
# In root directory
npm run dev
```

#### Terminal 3 - Admin Interface (Next.js)
```powershell
cd intellicket-admin
npm run dev
```

### Access URLs
- **Main Application**: http://localhost:3000
- **Backend API**: http://localhost:5003
- **Admin Interface**: http://localhost:3001

## 🧪 Verify Installation

### Test Backend Health
```powershell
# Test backend is running
curl http://localhost:5003/health
# Or visit: http://localhost:5003 in browser
```

### Test Frontend Connection
```powershell
# Test API proxy
curl http://localhost:3000/api/csdai/health
```

### Run Configuration Test
```powershell
cd CSDAIv2
python test_config.py
```

### Run API Integration Test
```powershell
cd CSDAIv2
python test_claude_api.py
```

## 🔍 Troubleshooting

### Common Issues

#### 1. Python Dependencies Failed
```powershell
# Update pip first
python -m pip install --upgrade pip setuptools wheel

# Install with no cache
pip install --no-cache-dir -r requirements.txt

# If specific packages fail, install individually:
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
```

#### 2. Node.js Dependencies Issues
```powershell
# Clear npm cache
npm cache clean --force

# Delete node_modules and reinstall
Remove-Item -Recurse -Force node_modules
Remove-Item package-lock.json
npm install
```

#### 3. Port Already in Use
```powershell
# Find and kill processes using ports
netstat -ano | findstr :3000
netstat -ano | findstr :5003
netstat -ano | findstr :3001

# Kill process by PID
taskkill /PID <PID_NUMBER> /F
```

#### 4. Python Virtual Environment Issues
```powershell
# Recreate virtual environment
Remove-Item -Recurse -Force venv
python -m venv venv
venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r CSDAIv2/requirements.txt
```

#### 5. AI/RAG Features Not Working
- Verify OPENAI_API_KEY is set in CSDAIv2/.env
- Check API key validity with test script
- Ensure internet connection for model downloads

### Log Locations
- **Backend Logs**: Console output from Flask app
- **Frontend Logs**: Browser console (F12)
- **Admin Logs**: Admin interface console

## 🛠️ Development Configuration

### VS Code Setup (Recommended)
1. Install recommended extensions:
   - Python
   - Pylance
   - ES7+ React/Redux/React-Native snippets
   - Tailwind CSS IntelliSense

2. Configure workspace settings in `.vscode/settings.json`:
```json
{
    "python.defaultInterpreterPath": "./venv/Scripts/python.exe",
    "python.terminal.activateEnvironment": true,
    "typescript.preferences.importModuleSpecifier": "relative"
}
```

### Hot Reload Configuration
- **Backend**: Uses Flask debug mode (auto-restart on changes)
- **Frontend**: Uses Next.js Turbopack (fast refresh)
- **Admin**: Uses Next.js Turbopack on port 3001

## 📦 Production Deployment

### Backend Production
```powershell
# Install production server
pip install gunicorn

# Run with gunicorn
cd CSDAIv2
gunicorn -w 4 -b 0.0.0.0:5003 app:app
```

### Frontend Production
```powershell
# Build main frontend
npm run build
npm start

# Build admin interface
cd intellicket-admin
npm run build
npm start
```

## 🚀 Next Steps

1. **Configure AI Features**: Add your Claude API key for enhanced analysis
2. **Add Knowledge Base**: Place PDF documents in `CSDAIv2/pdf/` for RAG
3. **Test Analysis**: Upload sample logs to verify analyzers work
4. **Customize**: Modify analyzers or add new ones as needed
5. **Monitor**: Use admin interface to monitor system health

## 📞 Support

If you encounter issues:

1. Check the troubleshooting section above
2. Verify all environment variables are set
3. Run the test scripts to identify specific issues
4. Check the comprehensive test suite in `Utilities/5. Test Files/`

## 🔄 Updates

To update the platform:

```powershell
# Update repository
git pull origin main

# Update Python dependencies
cd CSDAIv2
pip install -r requirements.txt --upgrade

# Update Node.js dependencies
cd ..
npm update
cd intellicket-admin
npm update
```

---

**🎉 Congratulations!** You should now have a fully functional Intellicket AI Support Platform running locally.