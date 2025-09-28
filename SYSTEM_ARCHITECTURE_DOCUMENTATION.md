# 🏗️ Intellicket System Architecture Documentation

## 📊 **System Overview**

Intellicket is a **cybersecurity log analysis platform** with a comprehensive three-tier architecture designed for analyzing Deep Security, AMSP, and other security logs using AI-enhanced analysis.

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           INTELLICKET ECOSYSTEM                                │
└─────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────┐    ┌─────────────────────┐    ┌─────────────────────┐
│                     │    │                     │    │                     │
│  Admin Dashboard    │◄──►│  Main Frontend      │◄──►│  Backend Engine     │
│  (localhost:3001)   │    │  (localhost:3000)   │    │  (localhost:5003)   │
│                     │    │                     │    │                     │
│  Next.js Admin UI   │    │  Next.js 15.5       │    │  Flask + Python     │
│  System Management  │    │  TypeScript/React   │    │  AI/ML Analysis     │
│  Statistics & Logs  │    │  API Proxy Layer    │    │  7 Analyzers        │
│                     │    │                     │    │                     │
└─────────────────────┘    └─────────────────────┘    └─────────────────────┘
```

---

## 🎯 **Component Architecture**

### **1. Main Frontend (localhost:3000)**
**Technology**: Next.js 15.5 with App Router, TypeScript, Tailwind CSS, React 19

#### **Core Directories**:
```
src/
├── app/
│   ├── products/[product]/page.tsx     # Product-specific pages
│   ├── api/                           # API proxy routes
│   │   ├── csdai/                     # Backend proxy endpoints
│   │   ├── admin/                     # Admin proxy endpoints
│   │   └── ai/                        # AI analysis endpoints
│   └── portal/                        # Portal interface
├── components/
│   ├── deep-security/                 # Analysis components
│   ├── common/                        # Shared components
│   └── resource-analysis/             # Resource analysis UI
├── contexts/
│   └── BackendContext.tsx             # Global backend status
└── utils/                             # Utility functions
```

#### **Key Components**:
- **CSDAIv2Integration.tsx** (2626 lines): Main analysis interface
- **BackendContext.tsx**: Global backend connection management
- **API Proxy Routes**: All `/api/csdai/*` and `/api/admin/*` endpoints

---

### **2. Admin Dashboard (localhost:3001)**
**Technology**: Next.js with unified admin interface

#### **Core Features**:
- System health monitoring
- Statistics dashboard (file upload stats, analyzer performance)
- Session management
- Cache and maintenance controls
- Alert management

#### **Data Flow**: 
```
Admin Dashboard → localhost:3000/api/admin/* → localhost:5003/admin/*
```

---

### **3. Backend Engine (localhost:5003)**
**Technology**: Flask Python application with AI/ML enhancement

#### **Core Architecture**:
```
CSDAIv2/
├── app.py                    # Main Flask application
├── api_routes.py            # REST API for frontend integration (1452 lines)
├── routes.py                # Web UI routes (3689 lines)
├── simple_session_manager.py # Session management (replaces ui_components)
├── analyzers/               # Modular analyzer system
│   ├── amsp_analyzer.py     # Anti-malware analysis (764 lines)
│   ├── conflict_analyzer.py # AV conflict detection (450 lines)
│   ├── resource_analyzer.py # Resource usage analysis
│   ├── ds_agent_log_analyzer.py      # DS Agent logs
│   ├── ds_agent_offline_analyzer.py  # Offline diagnosis
│   ├── diagnostic_package_analyzer.py # Comprehensive analysis
│   └── base/standardizer.py # Output standardization
├── admin/
│   └── unified_admin_routes.py # Admin API (1548 lines)
├── dynamic_rag_system.py   # AI-powered knowledge retrieval
├── ml_analyzer.py          # ML pattern recognition (763 lines)
└── config.py               # Environment configuration
```

---

## 🔄 **Data Flow Architecture**

### **Complete Request/Response Cycle**

```
1. User Action (localhost:3000)
   └── Frontend Interface (React/TypeScript)

2. API Proxy Layer (localhost:3000/api/*)
   ├── CORS handling
   ├── Error management
   ├── Request formatting
   └── Response standardization

3. Backend Processing (localhost:5003)
   ├── File upload & validation
   ├── Session management
   ├── Analysis engine selection
   └── AI/ML enhancement

4. Analysis Pipeline
   ├── Content extraction
   ├── Pattern recognition
   ├── ML health scoring
   ├── Dynamic RAG enhancement
   └── Results formatting

5. Response Chain
   Backend → API Proxy → Frontend → User Interface
```

### **Session Management Flow**

```python
# Backend Session Lifecycle
session_id = session_manager.create_session()
session_manager.update_progress(session_id, stage, message, percentage)
session_manager.store_results(session_id, analysis_results)
session_manager.cleanup_old_sessions()
```

---

## 🌐 **API Endpoint Mapping**

### **Frontend API Proxy Routes (localhost:3000/api/)**

#### **Main Analysis Endpoints**:
```typescript
/api/csdai/                 # Backend health check
/api/csdai/upload           # File upload proxy
/api/csdai/status/[sessionId] # Analysis status polling
/api/csdai/results/[sessionId] # Results retrieval
/api/csdai/export/[sessionId] # Report export
/api/csdai/cleanup          # Cache cleanup
/api/csdai/analyze-extracted/[sessionId] # Start analysis
```

#### **Admin Proxy Endpoints**:
```typescript
/api/admin/stats            # Combined statistics
/api/admin/stats/uploads    # File upload statistics  
/api/admin/stats/analyzers  # Analyzer performance
/api/admin/health           # System health
/api/admin/system/overview  # System overview
```

#### **AI Analysis Endpoints**:
```typescript
/api/ai/analyze-case        # AI case analysis
/api/ai/analyze-description # Description analysis
/api/ai/search-knowledge    # Knowledge base search
/api/ai/assess-severity     # Severity assessment
```

---

### **Backend Direct Endpoints (localhost:5003/)**

#### **Core Analysis API**:
```python
POST /upload                # File upload
GET  /status/<session_id>   # Analysis status
GET  /results/<session_id>  # Analysis results
GET  /export/<session_id>   # Export results
POST /analyze-extracted/<session_id> # Start analysis
```

#### **Admin API**:
```python
GET  /admin/health             # Health check
GET  /admin/system/overview    # System overview
GET  /admin/stats/uploads      # Upload statistics
GET  /admin/stats/analyzers    # Analyzer statistics
GET  /admin/sessions/active    # Active sessions
POST /admin/actions/restart-backend # Backend restart
POST /admin/actions/clear-cache     # Cache management
```

#### **Legacy Web Interface**:
```python
GET  /                     # Main page
GET  /wizard/<step>        # Wizard interface
GET  /sessions             # Session list
GET  /session/<session_id> # Session details
```

---

## 🤖 **AI Enhancement Pipeline**

### **Dynamic RAG System**
```
User Upload → Content Analysis → Knowledge Retrieval → AI Enhancement
     ↓              ↓                    ↓                 ↓
  Log Files    Pattern Detection    PDF Knowledge Base   GPT-4 Analysis
              Error Classification   Vector Database    Expert Insights
```

### **ML Analysis Engine**
```python
analysis = self.ml_analyzer.enhance_analysis(base_analysis)
# Provides:
# - Anomaly detection (statistical analysis)
# - Component health scoring (0-100 rating)
# - Severity classification (critical/high/medium/low)
# - Pattern recognition (known issue signatures)
```

---

## 🔧 **Configuration & Environment**

### **Required Environment Variables**:
```bash
# CSDAIv2/.env
OPENAI_API_KEY=your-claude-api-key  # AI integration
OPENAI_MODEL=claude-4-sonnet        # AI model
RAG_PDF_DIRECTORY=pdf               # Knowledge base
BACKEND_URL=http://localhost:5003   # Backend URL
```

### **Development Startup**:
```powershell
# Option 1: Individual terminals
# Backend (Terminal 1)
Set-Location CSDAIv2; python app.py

# Main Frontend (Terminal 2) 
npm run dev

# Admin Interface (Terminal 3)
Set-Location intellicket-admin; npm run dev

# Option 2: Automated startup
.\start_intellicket.ps1
```

---

## 📊 **File Processing Pipeline**

### **Supported Analysis Types**:

1. **AMSP Anti-Malware**: `AMSP-Inst_LocalDebugLog` files
2. **AV Conflicts**: `RunningProcesses.xml` files  
3. **Resource Analysis**: `RunningProcesses.xml` + `TopNBusyProcess.txt`
4. **DS Agent Logs**: `ds_agent.log` files
5. **DS Agent Offline**: Specialized offline diagnosis
6. **Diagnostic Package**: ZIP files with comprehensive logs

### **Analysis Enhancement Stack**:
```
Base Analysis → ML Enhancement → Dynamic RAG → Formatted Output
     ↓               ↓                ↓              ↓
Pattern Detection  Health Scoring  AI Insights   HTML/JSON Export
Error Classification  Anomaly Detection  Expert Recommendations  Report Generation
```

---

## 🛡️ **Security & Validation**

### **File Security**:
- XML content validation (`validate_xml_content()`)
- Process name sanitization (`sanitize_process_name()`)
- Host access control (`validate_host_access()`)
- File extension whitelist (config.UPLOAD_EXTENSIONS)

### **Session Security**:
- UUID-based session IDs
- Temporary file cleanup
- Memory-based session storage (production: Redis/Database)
- Session timeout management

---

## 🧪 **Testing Infrastructure**

### **Test Organization**:
```
test_*.py                    # Root-level validation scripts
Utilities/5. Test Files/     # Comprehensive analyzer tests
CSDAIv2/test_config.py      # Configuration validation
sample_logs/                # Test data by analyzer type
```

### **Testing Pattern**:
```python
# Standard test workflow
BACKEND_URL = "http://localhost:5003"
1. Upload file with analysis_type
2. Poll /status/{session_id} for completion  
3. Fetch /results/{session_id} and validate
4. Check standardized output format
```

---

## 📈 **Performance & Monitoring**

### **Session Statistics (Fixed 0.0% Issue)**:
- **Data Flow**: Admin Dashboard → Main Frontend Proxy → Backend
- **Metrics**: Success rates, file counts, analyzer performance
- **Real-time**: Statistics update with each completed analysis

### **Background Processing**:
- Asynchronous analysis execution
- Progress tracking with percentage updates
- Memory-efficient session management
- Automatic cleanup of old sessions

---

## 🚀 **Deployment Architecture**

### **Development Environment**:
- **Frontend**: http://localhost:3000 (Next.js dev server)
- **Admin**: http://localhost:3001 (Admin dashboard)
- **Backend**: http://localhost:5003 (Flask dev server)

### **Production Considerations**:
- Replace memory-based sessions with Redis/Database
- Use production WSGI server (Gunicorn/uWSGI)
- Implement proper logging and monitoring
- Configure environment-specific variables
- Set up reverse proxy (Nginx)

---

## 📝 **Key Architectural Decisions**

1. **Proxy Architecture**: Frontend proxies all backend calls for CORS and error handling
2. **Session Management**: Moved from ui_components.py to simple_session_manager.py 
3. **Admin Integration**: Admin dashboard reads from main frontend, not directly from backend
4. **Modular Analyzers**: Each analyzer follows standardized interface pattern
5. **AI Enhancement**: Optional ML/RAG layers that gracefully degrade if unavailable

This architecture provides a robust, scalable foundation for cybersecurity log analysis with AI enhancement capabilities.