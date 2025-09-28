# Intellicket AI Coding Agent Instructions

## Priorities
1. **Startup Protocol**: If starting development (`python CSDAIv2/app.py` and `npm run dev`), always request the user to manually start the backend and frontend in separate terminals.
2. **Change Management**: Request approval before modifying: architecture, technology stack, file structure, configurations, or environment variables
3. **Shell Commands**: Always use PowerShell syntax for Windows environment
4. **Testing Protocol**: Use existing test scripts in `Utilities/5. Test Files/` before implementing changes
5. **Code Standards**: Follow established patterns - proxy routes, standardized analyzers, session management


## 🏗️ Architecture Overview
Intellicket is a **cybersecurity log analysis platform** with triple-stack architecture:
- **Main Frontend**: Next.js 15.5 with App Router (`src/`) - TypeScript, Tailwind CSS, React 19
- **Admin Interface**: Unified admin dashboard (`intellicket-admin/`) - Next.js on port 3001
- **Backend**: Flask Python application (`CSDAIv2/`) - ML-enhanced Dynamic RAG system with modular analyzers
- **Integration**: REST API proxy layer (`src/app/api/csdai/`) bridges frontend-backend
- **Admin API**: Comprehensive admin endpoints (`CSDAIv2/admin/unified_admin_routes.py`) for system management
- **Testing**: Comprehensive test suite with `test_*.py` scripts in `Utilities/5. Test Files/` + root-level validation scripts
- **Knowledge Base**: PDF documents in `CSDAIv2/pdf/` and structured reports in root directory

## 🚀 Development Workflow

### Start Development Environment
```powershell
# Option 1: Individual terminals
# Backend (Terminal 1)
Set-Location CSDAIv2; python app.py
# Main Frontend (Terminal 2) 
npm run dev
# Admin Interface (Terminal 3)
Set-Location intellicket-admin; npm run dev

# Option 2: Use provided startup scripts
.\start_intellicket.ps1  # Complete ecosystem startup
# or
python start_intellicket.py  # Cross-platform version

# Access: 
# - Main App: http://localhost:3000 (frontend) + http://localhost:5003 (backend)
# - Admin Panel: http://localhost:3001 (unified admin interface)
```

### Key Commands
- `npm run dev` - Main frontend with Turbopack (fast refresh)
- `npm run build` - Production build with Turbopack
- `Set-Location intellicket-admin; npm run dev` - Admin interface on port 3001
- `python CSDAIv2/app.py` - Flask backend with ML+RAG features
- `python Utilities/5. Test Files/test_*.py` - Run specific analyzer tests
- `python test_*.py` - Root-level validation scripts (admin API, resource monitoring, etc.)
- `python CSDAIv2/test_config.py` - Validate environment configuration
- `python CSDAIv2/test_claude_api.py` - Test AI integration
- Backend testing via direct HTTP requests to `http://localhost:5003`

### Critical Development Patterns
- **Always check backend status** via `/api/csdai` health endpoint before operations
- **Use BackendContext** for consistent frontend-backend state management
- **Test analyzer changes** with corresponding test scripts in `Utilities/5. Test Files/`
- **Follow analyzer standardization** via `base/standardizer.py` for consistent output formats
- **Validate configuration** - Run `python CSDAIv2/test_config.py` before major changes
- **Session cleanup** - Backend sessions accumulate, use `/api/cleanup/cache` periodically

## 📁 Critical File Patterns

### Frontend Structure
- `src/app/products/[product]/page.tsx` - Product-specific analysis pages
- `src/components/deep-security/CSDAIv2Integration.tsx` - Main analysis component (2000+ lines)
- `src/app/api/csdai/**` - API proxy routes to Flask backend
- `src/contexts/BackendContext.tsx` - Global backend status management
- `intellicket-admin/` - Unified admin interface (Next.js on port 3001) for system management

### Backend Architecture  
- `CSDAIv2/app.py` - Flask app with ML+RAG initialization and feature availability checks
- `CSDAIv2/analyzers/` - Modular analyzer system with 7 specialized engines:
  - `amsp_analyzer.py` - Anti-malware scan performance analysis (764 lines)
  - `conflict_analyzer.py` - AV conflict detection (450 lines)  
  - `resource_analyzer.py` - Resource usage analysis
  - `ds_agent_log_analyzer.py` - DS Agent logs (backend-only)
  - `ds_agent_offline_analyzer.py` - Offline diagnosis
  - `diagnostic_package_analyzer.py` - Comprehensive analysis
  - `dual_path_analyzer.py` - Multi-path analysis routing
  - `base/standardizer.py` - Output standardization base class
- `CSDAIv2/admin/unified_admin_routes.py` - Admin API endpoints (1528 lines) for system management
- `CSDAIv2/dynamic_rag_system.py` - AI-powered knowledge retrieval with Claude integration
- `CSDAIv2/ml_analyzer.py` - Machine learning pattern recognition and health scoring (763 lines)
- `CSDAIv2/api_routes.py` - REST API endpoints for Intellicket integration (1452 lines)
- `CSDAIv2/config.py` - Environment-based configuration with validation
- `CSDAIv2/ui_components.py` - **SESSION & UX MANAGEMENT** (364 lines) - Wizard-based UI controller with contextual guidance

### Project Documentation Pattern
Root directory contains extensive analysis reports:
- `*_COMPREHENSIVE_REPORT.md` - Detailed technical analyses
- `*_FIX_COMPLETE.md` - Implementation completion reports  
- `*_ENHANCEMENT_PLAN.md` - Future development roadmaps
- `test_*.py` scripts - Validation and debugging utilities
- `Utilities/` - Organized testing infrastructure with `5. Test Files/` containing comprehensive test suite

## 🔌 Integration Patterns

### API Proxy Pattern
All frontend→backend communication flows through Next.js API routes that proxy to Flask:
```typescript
// src/app/api/csdai/upload/route.ts
const response = await fetch(`${BACKEND_URL}/upload`, {
  method: 'POST', body: formData
});
return NextResponse.json(await response.json());
```

### Session-Based Analysis Flow
1. Upload files → GET session_id from `/upload`
2. Poll status → GET `/status/{sessionId}` for progress
3. Fetch results → GET `/results/{sessionId}` when complete
4. Export analysis → GET `/export/{sessionId}` for download

### Dynamic RAG Integration
When modifying analysis features, understand the **three-tier enhancement stack**:
```python
# In analyzers.py - this is the standard pattern
try:
    from dynamic_rag_system import apply_dynamic_rag_to_analysis
    analysis = apply_dynamic_rag_to_analysis(analysis, log_content)
except ImportError:
    analysis['dynamic_rag_analysis'] = {'status': 'unavailable'}
```

## 🎯 Component-Specific Conventions

### CSDAIv2Integration.tsx (Main UI Component)
- **Progress Management**: Uses `ProgressStage[]` with animated stage transitions
- **Results Display**: Implements `formatBackendResults()` with ML insights, RAG analysis, and knowledge sources
- **Polling Pattern**: 2-second intervals for status updates during analysis
- **Error Boundaries**: Comprehensive error handling with user-friendly messages

### Backend Analyzers Pattern
Each analyzer follows this **standardized structure**:
```python
class AnalyzerName:
    def __init__(self, session_manager=None, session_id=None, rag_system=None, ml_analyzer=None):
        # Standardized constructor supporting:
        # - Progress tracking via session_manager
        # - AI enhancement via rag_system  
        # - ML analysis via ml_analyzer
    
    def analyze(self, content):
        # Core analysis logic
        analysis = self.perform_analysis(content)
        
        # ML Enhancement (optional)
        if self.ml_analyzer:
            analysis = self.ml_analyzer.enhance_analysis(analysis)
            
        # Dynamic RAG Enhancement (optional)  
        if self.rag_system:
            analysis = apply_dynamic_rag_to_analysis(analysis, content)
            
        return analysis
```

### Testing Infrastructure Pattern
All major features include corresponding test scripts:
- `test_analyzers_comprehensive.py` - End-to-end analyzer validation
- `test_*_fix.py` - Issue-specific verification scripts
- Backend testing via direct HTTP requests to `http://localhost:5003`
- Test files located in `sample_logs/` directory

## 🔧 Configuration & Environment

### Required Environment Variables (CSDAIv2/.env)
```bash
OPENAI_API_KEY=your-claude-api-key  # For Dynamic RAG AI responses
OPENAI_MODEL=claude-4-sonnet        # AI model selection
RAG_PDF_DIRECTORY=pdf               # Knowledge base location
```

### Backend URL Configuration
- Development: `http://localhost:5003` (hardcoded in API routes)
- Change in all `src/app/api/csdai/**` files simultaneously

## 🧠 AI Enhancement Features

### Dynamic RAG System
- **Knowledge Base**: PDF documents in `CSDAIv2/pdf/` automatically indexed
- **Smart Queries**: ML insights drive dynamic query generation for relevant knowledge retrieval  
- **AI Responses**: Claude-4 Sonnet generates expert recommendations based on log context + knowledge base
- **Frontend Display**: Results shown in expandable sections with relevance scores

### ML Analysis Features
- **Anomaly Detection**: Statistical analysis identifies unusual patterns
- **Component Health Scoring**: Deep Security components get 0-100 health ratings
- **Severity Classification**: Automatic critical/high/medium/low severity assignment
- **Pattern Recognition**: ML models detect known issue signatures

## ⚠️ Common Pitfalls

### Backend Integration
- **Always check backend status** before operations via `/api/csdai` health endpoint
- **Handle session cleanup** - sessions accumulate and need periodic cleanup via `/api/cleanup/cache`
- **File upload size limits** - Flask has default limits, check for large log files
- **UI Components State Management** - `ui_components.py` session_manager stores state in memory, can grow large with many sessions

### Frontend State Management
- **Progress polling can leak** - always cleanup intervals in useEffect cleanup
- **Backend status affects UI state** - use BackendContext for consistent status checking
- **Results can be large** - implement pagination/truncation for very large analysis results

### RAG/ML Integration
- **Graceful degradation required** - features should work even if ML/RAG unavailable
- **API key validation** - Claude API failures should not break core analysis
- **Knowledge base dependencies** - PDF directory structure matters for RAG functionality

## 📊 Data Flow & Session Management

### File Upload → Analysis Pipeline
1. **Upload**: Files processed via `/upload` → unique `session_id` generated
2. **Analysis Queue**: Background processing with progress tracking via `session_manager`
3. **Results Storage**: Analysis stored in session data, accessible via `/results/{sessionId}`
4. **Export**: Formatted output available via `/export/{sessionId}`

### Session Lifecycle Pattern
```python
# Backend session management pattern used across all analyzers
session_manager.update_progress(session_id, stage, message, percentage)
session_manager.store_results(session_id, analysis_results)
session_manager.cleanup_old_sessions()  # Periodic maintenance
```

### UI Components & Session Management (`CSDAIv2/ui_components.py`)
**⚠️ CRITICAL SYSTEM COMPONENT - FREQUENTLY MODIFIED**
- **AnalysisSession**: Core session management with state persistence (sessions accumulate in memory)
- **AnalysisWizard**: 5-step wizard controller (Type→Upload→Ready→Processing→Results)
- **UserGuidance**: Context-aware help for 6 analysis types (DS Agent, AMSP, Conflicts, etc.)
- **Global Instances**: `session_manager`, `wizard`, `guidance` used throughout backend
- **Usage Pattern**: Imported by `app.py`, `routes.py`, and test files
- **Modification Impact**: Changes affect wizard flow, session handling, and user guidance across entire platform
- **Testing Required**: Session management changes need validation with `test_progress_bar_fix.py` and session-related tests

### Security & Validation Patterns
- **XML Security**: All XML files validated via `validate_xml_content()` before parsing
- **Process Name Sanitization**: `sanitize_process_name()` prevents injection attacks
- **Host Access Control**: `validate_host_access()` enforces allowed hosts from config
- **File Extension Validation**: Strict whitelist in `config.py` UPLOAD_EXTENSIONS

## 🔍 Debugging Patterns

### Backend Logs
```bash
# Flask app shows ML/RAG availability on startup:
✅ ML-Enhanced Analysis Available  
✅ Dynamic RAG-Enhanced Analysis Available
```

### Frontend Development
- Use browser dev tools Network tab to monitor API proxy calls
- Check `BackendContext` state for connection issues
- Monitor console for polling interval cleanup warnings

### Analysis Debugging
- Use `/debug-html` route on backend for template rendering issues
- Check session data with `/sessions` route to verify analysis state
- Use `/api/session/status/{sessionId}` for detailed progress information
- **Test scripts**: Run `python test_analyzers_comprehensive.py` for full system validation

## 🧪 Testing & Debugging Strategies

### Test Organization
- **Root Level**: Quick validation scripts (`test_admin_api.py`, `test_enhanced_offline_analyzer.py`, `test_psutil_integration.py`, `test_realtime_analyzer_sync.py`, `test_resource_upload.py`)
- **Utilities/5. Test Files/**: Comprehensive test suite with specific analyzer tests
- **sample_logs/**: Test data organized by log type (ds_agent, amsp, conflict, etc.)

### Backend Testing Pattern
```python
# Standard test pattern used across all test scripts
BACKEND_URL = "http://localhost:5003"
def test_analyzer_endpoint(analysis_type, file_path):
    # 1. Upload file with analysis_type
    # 2. Poll /status/{session_id} for completion
    # 3. Fetch /results/{session_id} and validate structure
    # 4. Check standardized output format
```

### Performance Testing & Timeouts
- **AI Analysis Timeout**: 30s default (configurable via `RAG_ANALYSIS_TIMEOUT`)
- **Fallback Analysis**: Pattern-based analysis when AI times out
- **Performance Validation**: Monitor analyzer completion times via test scripts
- **Resource Monitoring**: Check memory usage during large file analysis