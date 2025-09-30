# 🛡️ Intellicket - Advanced Cybersecurity Log Analysis Platform

**Intellicket** is a comprehensive, AI-powered cybersecurity log analysis platform designed specifically for **Trend Micro Deep Security** environments. It provides intelligent analysis of security logs, performance diagnostics, and actionable insights through a modern web interface.

![System Architecture](https://img.shields.io/badge/Architecture-Triple--Stack-blue) ![AI Powered](https://img.shields.io/badge/AI-Enhanced%20Analysis-green) ![Status](https://img.shields.io/badge/Status-Production%20Ready-brightgreen)

---

## � **New User Setup**

**🆕 First time setting up Intellicket?** Follow our comprehensive guides:

1. **📋 [PROJECT_REQUIREMENTS.md](PROJECT_REQUIREMENTS.md)** - Complete system requirements and dependencies
2. **🔧 [SETUP_GUIDE.md](SETUP_GUIDE.md)** - Step-by-step installation instructions
3. **✅ Validation Script** - Run `python validate_setup.py` to verify your setup

### **Quick Validation**
```powershell
# Validate your setup before starting
python validate_setup.py
```

## �🚀 **Quick Start**

### **Prerequisites**
- **Python 3.8+** (3.9+ recommended)
- **Node.js 18+** (with npm)
- **Windows PowerShell** (for startup scripts)

### **⚡ One-Command Startup**
```powershell
# Clone and start the entire ecosystem
git clone git@adc.github.trendmicro.com:adrianp/intellicket.git
cd intellicket
.\start_intellicket.ps1
```

### **Manual Startup (3 Terminals)**
```powershell
# Terminal 1: Backend (Flask)
Set-Location CSDAIv2; python app.py

# Terminal 2: Main Frontend (Next.js)
npm run dev

# Terminal 3: Admin Dashboard (Next.js)
Set-Location intellicket-admin; npm run dev
```

### **Access URLs**
- 🌐 **Main Application**: http://localhost:3000
- 🎛️ **Admin Dashboard**: http://localhost:3001
- 🔧 **Backend API**: http://localhost:5003

---

## 📋 **System Overview**

Intellicket is built on a **three-tier architecture** that provides scalable, intelligent cybersecurity analysis:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          INTELLICKET ECOSYSTEM                             │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────┐    ┌─────────────────────┐    ┌─────────────────────┐
│  Admin Dashboard    │◄──►│  Main Frontend      │◄──►│  Backend Engine     │
│  (Port 3001)        │    │  (Port 3000)        │    │  (Port 5003)        │
│                     │    │                     │    │                     │
│  • System Health    │    │  • Analysis UI      │    │  • 7 Analyzers      │
│  • Statistics       │    │  • File Upload      │    │  • AI/ML Engine     │
│  • Session Mgmt     │    │  • Results Display  │    │  • RAG System       │
│  • Maintenance      │    │  • API Proxy        │    │  • Session Mgmt     │
└─────────────────────┘    └─────────────────────┘    └─────────────────────┘
```

---

## 🎯 **Core Features**

### **🔍 Advanced Log Analysis**
- **7 Specialized Analyzers** for different log types
- **AI-Enhanced Analysis** with Claude 4 Sonnet integration
- **Machine Learning** pattern recognition and anomaly detection
- **Dynamic RAG** (Retrieval-Augmented Generation) for expert knowledge

### **📊 Analysis Types**
| Analyzer | File Type | Description | Frontend Access |
|----------|-----------|-------------|-----------------|
| **AMSP Anti-Malware** | `AMSP-Inst_LocalDebugLog.txt` | Performance & scan analysis | ✅ Yes |
| **AV Conflicts** | `RunningProcesses.xml` | Antivirus conflict detection | ✅ Yes |
| **Resource Analysis** | `RunningProcesses.xml + TopNBusyProcess.txt` | System resource diagnostics | ✅ Yes |
| **Diagnostic Package** | `.zip` files | Comprehensive log analysis | ✅ Yes |
| **DS Agent Logs** | `ds_agent.log` | Deep Security agent analysis | 🔧 API Only |
| **DS Agent Offline** | `ds_agent.log` | Specialized offline diagnosis | 🔧 API Only |
| **Dual Path Analysis** | Multiple formats | Multi-path routing analysis | 🔧 API Only |

### **🤖 AI & ML Features**
- **Smart Recommendations** based on log patterns
- **Severity Classification** (Critical/High/Medium/Low)
- **Component Health Scoring** (0-100 scale)
- **Knowledge Base Integration** with PDF documentation
- **Contextual Insights** from proprietary cybersecurity knowledge

---

## 🏗️ **Architecture Deep Dive**

### **Frontend (Next.js 15.5)**
- **Framework**: Next.js with App Router and Turbopack
- **Language**: TypeScript with React 19
- **Styling**: Tailwind CSS 4
- **Key Components**:
  - `CSDAIv2Integration.tsx` (2,626 lines) - Main analysis interface
  - `BackendContext.tsx` - Global backend status management
  - API proxy routes in `src/app/api/csdai/`

### **Backend (Flask + Python)**
- **Framework**: Flask with modular analyzer architecture
- **Key Files**:
  - `app.py` (221 lines) - Main application entry point
  - `api_routes.py` (1,566 lines) - REST API for frontend integration
  - `dynamic_rag_system.py` (550 lines) - AI knowledge retrieval
  - `ml_analyzer.py` (763 lines) - Machine learning analysis
  - `simple_session_manager.py` - Session and progress tracking

### **Admin Interface (Next.js)**
- **Purpose**: Unified system management dashboard
- **Features**: Health monitoring, statistics, session management
- **API**: Connects to backend via `/admin/*` endpoints

---

## 📁 **Project Structure**

```
intellicket/
├── 📄 README.md                 # This file
├── 📄 package.json              # Main frontend dependencies
├── 🚀 start_intellicket.ps1     # Complete system startup script
├── 🚀 start_intellicket.py      # Cross-platform startup script
├── 📊 test_*.py                 # Root-level validation scripts
├── 
├── 📂 src/                      # Main Frontend (Next.js)
│   ├── app/
│   │   ├── api/csdai/          # Backend proxy routes
│   │   ├── products/           # Product-specific analysis pages
│   │   └── portal/             # Portal interface
│   ├── components/
│   │   └── deep-security/      # Analysis UI components
│   └── contexts/               # Global state management
├── 
├── 📂 CSDAIv2/                 # Backend Engine (Flask)
│   ├── app.py                  # Main Flask application
│   ├── api_routes.py          # REST API endpoints
│   ├── config.py              # Environment configuration
│   ├── analyzers/             # Modular analyzer system
│   │   ├── amsp_analyzer.py   # Anti-malware analysis
│   │   ├── conflict_analyzer.py # AV conflict detection
│   │   ├── resource_analyzer.py # Resource analysis
│   │   ├── ds_agent_*_analyzer.py # DS Agent analyzers
│   │   └── base/standardizer.py # Output standardization
│   ├── admin/                 # Admin API endpoints
│   ├── dynamic_rag_system.py  # AI knowledge system
│   ├── ml_analyzer.py         # Machine learning engine
│   └── pdf/                   # Knowledge base documents
├── 
├── 📂 intellicket-admin/       # Admin Dashboard (Next.js)
│   ├── package.json           # Admin interface dependencies
│   └── src/                   # Admin UI components
├── 
├── 📂 Utilities/               # Testing & Development Tools
│   ├── 0. sample_logs/        # Test data organized by type
│   ├── 5. Test Files/         # Comprehensive test suite (100+ scripts)
│   └── 1-8. Various/          # Documentation, backups, fixes
└── 
└── 📂 tools/                   # Research and API tools
```

---

## ⚙️ **Configuration & Environment**

### **Environment Variables**
Create a `.env` file in the `CSDAIv2/` directory:

```env
# AI Configuration (Optional - enables enhanced analysis)
OPENAI_API_KEY=your-claude-api-key
OPENAI_MODEL=claude-4-sonnet
OPENAI_BASE_URL=https://api.rdsec.trendmicro.com/prod/aiendpoint/v1/

# RAG System Configuration
RAG_PDF_DIRECTORY=pdf
RAG_MAX_KNOWLEDGE_SOURCES=6
RAG_ANALYSIS_TIMEOUT=30

# Security Configuration
FLASK_SECRET_KEY=your-secret-key-change-in-production
ALLOWED_HOSTS=localhost,127.0.0.1

# Performance Settings
PORT=5003
TEMP_DIR=temp
```

### **Dependencies Installation**
```powershell
# Backend dependencies
Set-Location CSDAIv2; pip install -r requirements.txt

# Frontend dependencies
npm install

# Admin interface dependencies
Set-Location intellicket-admin; npm install
```

---

## 🔄 **Data Flow & Integration**

### **Analysis Workflow**
```
1. File Upload → Frontend (Next.js)
2. API Proxy → /api/csdai/upload
3. Backend Processing → Flask analyzers
4. AI Enhancement → RAG + ML analysis
5. Results Storage → Session management
6. Frontend Display → Formatted results
```

### **Session Management Pattern**
```python
# Backend session lifecycle
session_id = generate_unique_id()
session_manager.update_progress(session_id, stage, message, percentage)
session_manager.store_results(session_id, analysis_results)
# Frontend polls /status/{session_id} for updates
```

### **API Proxy Pattern**
All frontend-backend communication flows through Next.js API routes:
```typescript
// src/app/api/csdai/upload/route.ts
const response = await fetch(`${BACKEND_URL}/upload`, {
  method: 'POST', body: formData
});
return NextResponse.json(await response.json());
```

---

## 🧪 **Testing Infrastructure**

### **Test Organization**
- **Root Level**: Quick validation scripts (`test_admin_api.py`, `test_resource_upload.py`)
- **Utilities/5. Test Files/**: Comprehensive test suite (100+ test scripts)
- **Sample Data**: `Utilities/0. sample_logs/` organized by log type

### **Running Tests**
```powershell
# Backend functionality tests
python test_admin_api.py
python CSDAIv2/test_config.py

# Comprehensive analyzer tests
python "Utilities/5. Test Files/test_analyzers_comprehensive.py"

# Integration tests
python "Utilities/5. Test Files/test_complete_integration.py"
```

### **Backend Testing via HTTP**
```powershell
# Direct backend testing (ensure backend is running on port 5003)
curl http://localhost:5003/wizard/1  # Health check
# Upload and analyze files via REST API endpoints
```

---

## 🔧 **Development Guide**

### **Adding New Analyzers**
1. Create analyzer in `CSDAIv2/analyzers/your_analyzer.py`
2. Extend `AnalyzerOutputStandardizer` base class
3. Implement standardized constructor with ML/RAG support
4. Register in `analyzers/__init__.py`
5. Add corresponding test in `Utilities/5. Test Files/`

### **Analyzer Pattern**
```python
from .base.standardizer import AnalyzerOutputStandardizer

class YourAnalyzer(AnalyzerOutputStandardizer):
    def __init__(self, session_manager=None, session_id=None, rag_system=None, ml_analyzer=None):
        # Standard constructor pattern
        
    def analyze(self, content):
        # Core analysis logic
        analysis = self.perform_analysis(content)
        
        # ML Enhancement (optional)
        if self.ml_analyzer:
            analysis = self.ml_analyzer.enhance_analysis(analysis)
            
        # Dynamic RAG Enhancement (optional)  
        if self.rag_system:
            analysis = apply_dynamic_rag_to_analysis(analysis, content)
            
        return self.standardize_output(analysis)
```

### **Adding Frontend Features**
1. Extend `CSDAIv2Integration.tsx` component
2. Add new API proxy routes in `src/app/api/csdai/`
3. Update `BackendContext` for status management
4. Follow polling pattern for long-running operations

---

## 🚦 **Troubleshooting**

### **Common Issues**

**🔴 Backend Connection Failed**
```
Solution: Check if Flask backend is running on port 5003
Command: Set-Location CSDAIv2; python app.py
```

**🔴 Frontend Build Errors**
```
Solution: Clear Next.js cache and reinstall dependencies
Commands: 
rm -rf .next node_modules package-lock.json
npm install
npm run dev
```

**🔴 AI Features Not Working**
```
Solution: Check OPENAI_API_KEY in CSDAIv2/.env file
Backend will fall back to pattern-based analysis if AI unavailable
```

**🔴 Session Accumulation**
```
Solution: Use cleanup endpoint periodically
URL: GET http://localhost:3000/api/csdai/cleanup/cache
```

### **Debug Endpoints**
- **Backend Health**: `GET http://localhost:5003/wizard/1`  
- **Session Status**: `GET http://localhost:3000/api/csdai/status/{sessionId}`
- **Admin Statistics**: `GET http://localhost:3001/admin/statistics`

---

## 📚 **Knowledge Base**

### **Documentation Files**
- `SYSTEM_ARCHITECTURE_DOCUMENTATION.md` - Detailed technical architecture
- `.github/copilot-instructions.md` - Development guidelines and patterns
- `intellicket-admin/README.md` - Admin interface documentation
- Various `*_COMPLETE.md` reports - Implementation completion documentation

### **Research Tools**
- `tools/` directory contains API research scripts
- `Utilities/8. Ideas/` - Future enhancement concepts
- Root-level comprehensive reports for detailed analysis

---

## 🔐 **Security Features**

- **XML Security**: Validation via `validate_xml_content()` before parsing
- **Process Name Sanitization**: `sanitize_process_name()` prevents injection
- **Host Access Control**: `validate_host_access()` enforces allowed hosts
- **File Extension Validation**: Strict whitelist in `config.py`
- **Session Isolation**: Each analysis runs in isolated session context

---

## 🎯 **Use Cases**

### **For Security Analysts**
- Upload Deep Security logs for automated analysis
- Get AI-powered recommendations and insights
- Export detailed reports for documentation
- Monitor system resource performance

### **For System Administrators** 
- Diagnose antivirus conflicts and performance issues
- Analyze resource utilization patterns
- Get actionable remediation steps
- Track analysis history via admin dashboard

### **For DevOps Teams**
- Integrate via REST API for automated analysis
- Monitor backend health and performance
- Manage system resources and cleanup
- Access detailed logs and statistics

---

## 🚀 **Deployment**

### **Development Environment**
- Use provided startup scripts (`start_intellicket.ps1` or `start_intellicket.py`)
- All components run locally with hot reload enabled
- Comprehensive test suite available for validation

### **Production Considerations**
- Configure proper `FLASK_SECRET_KEY` and `ALLOWED_HOSTS`
- Set `FLASK_ENV=production` in environment
- Use reverse proxy (nginx) for frontend applications
- Configure persistent storage for sessions and exports
- Set up proper logging and monitoring

---

## 🤝 **Contributing**

1. **Follow Established Patterns**: Use analyzer standardization and proxy routing
2. **Test Thoroughly**: Add corresponding tests in `Utilities/5. Test Files/`
3. **Update Documentation**: Keep README and architecture docs current
4. **Security First**: Follow validation patterns and input sanitization

---

## 📞 **Support**

For technical support or questions about Intellicket:
- **Repository**: [git@adc.github.trendmicro.com:adrianp/intellicket.git](https://adc.github.trendmicro.com/adrianp/intellicket)
- **Issues**: Use the repository issue tracker
- **Documentation**: Check comprehensive reports in root directory

---

## 📈 **Roadmap**

- **Enhanced AI Integration**: Expand RAG knowledge base
- **Real-time Analysis**: WebSocket-based live log monitoring  
- **Multi-tenant Support**: Isolation for different organizational units
- **Advanced Visualization**: Interactive charts and trend analysis
- **API Expansion**: More granular REST endpoints for enterprise integration

---

*Built with ❤️ for cybersecurity professionals using modern web technologies and AI enhancement.*