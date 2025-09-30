# Intellicket AI Support Platform - Project Requirements

## 📖 Overview

Intellicket is a comprehensive cybersecurity log analysis platform designed for Trend Micro Deep Security troubleshooting. It combines advanced AI capabilities with modular analysis engines to provide intelligent log analysis, conflict detection, and automated recommendations.

## 🏗️ Architecture Components

### Triple-Stack Architecture
1. **Main Frontend**: Next.js 15.5 with App Router (TypeScript, Tailwind CSS, React 19)
2. **Admin Interface**: Unified admin dashboard (Next.js on port 3001)
3. **Backend**: Flask Python application with ML-enhanced Dynamic RAG system

### Key Features
- **7+ Modular Analyzers**: AMSP, Conflict, Resource, DS Agent, Diagnostic Package, Dual Path
- **AI-Enhanced Analysis**: Claude API integration with Dynamic RAG system
- **Machine Learning**: Pattern recognition and health scoring
- **Vector Database**: ChromaDB for knowledge base similarity search
- **Session Management**: Persistent analysis sessions with progress tracking

## 💻 System Requirements

### Hardware Requirements

#### Minimum Configuration
- **CPU**: 2-core processor (Intel i3 or AMD equivalent)
- **RAM**: 4GB (8GB recommended for ML operations)
- **Storage**: 2GB free space
- **Network**: Stable internet connection for AI API calls

#### Recommended Configuration
- **CPU**: 4-core processor (Intel i5/i7 or AMD Ryzen equivalent)
- **RAM**: 8GB+ (16GB for heavy workloads)
- **Storage**: 5GB+ free space (SSD recommended)
- **Network**: High-speed internet for model downloads

#### Production Configuration
- **CPU**: 8+ cores
- **RAM**: 16GB+
- **Storage**: 10GB+ SSD
- **Network**: Enterprise internet connection

### Operating System Support

#### Fully Supported
- **Windows**: 10, 11 (PowerShell 5.1+)
- **macOS**: 10.15+ (Catalina and newer)
- **Linux**: Ubuntu 20.04+, CentOS 8+, Debian 10+

#### Tested Configurations
- Windows 11 with PowerShell 7
- Ubuntu 22.04 LTS
- macOS Monterey (12.0+)

## 🔧 Software Dependencies

### Core Runtime Requirements

#### Python Environment
- **Version**: Python 3.8+ (3.9+ recommended, 3.11+ for best performance)
- **Package Manager**: pip 21.0+
- **Virtual Environment**: venv or conda recommended

#### Node.js Environment
- **Version**: Node.js 18.0+ (20.0+ recommended)
- **Package Manager**: npm 9.0+ (included with Node.js)
- **Alternative**: yarn 1.22+ (optional)

### Python Dependencies (Complete List)

#### Core Web Framework
```
Flask==2.3.3                    # Core web framework
Werkzeug==2.3.7                # WSGI utilities
Flask-CORS==4.0.0              # Cross-origin support
gunicorn==21.2.0               # Production server
```

#### AI/ML Stack
```
openai==1.3.5                  # Claude API integration
scikit-learn>=1.4.0            # Machine learning
numpy>=1.22.0                  # Numerical computing
pandas>=2.0.0                  # Data analysis
torch>=2.0.0                   # PyTorch for transformers
transformers>=4.30.0           # Hugging Face models
```

#### Dynamic RAG System
```
chromadb==0.4.18               # Vector database
sentence-transformers==2.2.2   # Text embeddings
faiss-cpu>=1.7.4              # Similarity search
```

#### Data Processing
```
lxml>=4.9.0                   # XML processing
beautifulsoup4>=4.12.0        # HTML/XML parsing
PyPDF2>=3.0.0                 # PDF processing
psutil>=5.9.0                 # System utilities
```

### Node.js Dependencies

#### Main Frontend
```json
{
  "next": "15.5.0",
  "react": "19.1.0",
  "react-dom": "19.1.0",
  "typescript": "^5",
  "tailwindcss": "^4",
  "lucide-react": "^0.544.0",
  "jszip": "^3.10.1",
  "class-variance-authority": "^0.7.1",
  "clsx": "^2.1.1",
  "tailwind-merge": "^3.3.1"
}
```

#### Admin Interface
```json
{
  "next": "15.5.0",
  "react": "19.1.0",
  "react-dom": "19.1.0",
  "recharts": "^2.13.0",
  "socket.io-client": "^4.8.1",
  "date-fns": "^3.6.0"
}
```

## 🔑 Configuration Requirements

### Environment Variables

#### Required Backend Variables
```env
# AI Configuration (REQUIRED for enhanced features)
OPENAI_API_KEY=your-claude-api-key
OPENAI_MODEL=claude-3-sonnet-20240229

# Flask Configuration
FLASK_ENV=development
FLASK_PORT=5003
SECRET_KEY=your-secure-secret-key

# File Upload Configuration
UPLOAD_FOLDER=temp
MAX_CONTENT_LENGTH=100000000

# RAG System Configuration
RAG_PDF_DIRECTORY=pdf
RAG_ANALYSIS_TIMEOUT=30
```

#### Optional Performance Variables
```env
# Redis (for caching)
REDIS_URL=redis://localhost:6379/0

# Celery (for async processing)
CELERY_BROKER_URL=redis://localhost:6379/0

# Database
DATABASE_URL=sqlite:///intellicket.db
```

### API Keys and External Services

#### Claude API (Anthropic)
- **Purpose**: AI-enhanced analysis and recommendations
- **Requirement**: Required for full functionality
- **Cost**: Pay-per-use (API calls)
- **Setup**: https://console.anthropic.com/

#### Optional Services
- **Redis**: For session caching and performance
- **PostgreSQL**: Alternative to SQLite for production

## 📁 Directory Structure Requirements

### Core Directories (Auto-created)
```
CSDAIv2/
├── temp/                      # Temporary file storage
├── exports/                   # Analysis exports
├── knowledge_base/            # SQLite database
├── ml_models/                 # Cached ML models
├── pdf/                       # Knowledge base PDFs
└── static/uploads/            # File uploads
```

### Knowledge Base Setup
- Place PDF documentation in `CSDAIv2/pdf/`
- System automatically indexes for RAG queries
- Supports multiple PDF formats

## 🌐 Network Requirements

### Outbound Connections Required

#### AI Services
- **Anthropic Claude API**: api.anthropic.com (HTTPS/443)
- **Hugging Face**: huggingface.co (HTTPS/443) - Model downloads

#### Package Repositories
- **PyPI**: pypi.org (HTTPS/443) - Python packages
- **npm Registry**: registry.npmjs.org (HTTPS/443) - Node packages

#### Optional Services
- **Redis**: localhost:6379 (if using caching)

### Firewall Configuration
- **Inbound**: Allow ports 3000, 3001, 5003 for local development
- **Outbound**: Allow HTTPS (443) for API calls and downloads

## 🔒 Security Requirements

### File System Permissions
- **CSDAIv2/temp/**: Read/Write access for file uploads
- **CSDAIv2/exports/**: Read/Write access for analysis exports
- **Knowledge base**: Read/Write access for database operations

### Security Features
- XML validation and sanitization
- Process name sanitization
- File type validation
- Secure temporary file handling
- Session-based access control

## 📊 Performance Specifications

### Response Time Targets
- **File Upload**: < 5 seconds for files up to 100MB
- **Analysis Processing**: 30-120 seconds depending on complexity
- **AI Enhancement**: 15-30 seconds (with timeout fallback)
- **Web Interface**: < 2 seconds page load

### Throughput Specifications
- **Concurrent Sessions**: 10+ simultaneous analysis sessions
- **File Processing**: 50+ files per analysis session
- **API Requests**: 100+ requests per minute

### Memory Usage
- **Base System**: ~200MB
- **Per Analysis Session**: ~50-100MB
- **ML Models**: ~500MB-1GB (cached)
- **Vector Database**: ~100MB per 1000 documents

## 🧪 Testing Requirements

### Test Suite Coverage
- **100+ Test Scripts**: Located in `Utilities/5. Test Files/`
- **Integration Tests**: Full API flow validation
- **Analyzer Tests**: Individual component testing
- **Performance Tests**: Load and stress testing

### Validation Scripts
- `test_config.py` - Configuration validation
- `test_claude_api.py` - AI integration testing
- `test_analyzers_comprehensive.py` - Full system testing

## 🚀 Deployment Options

### Development Environment
- **Single Machine**: All components on localhost
- **Hot Reload**: Automatic code refresh during development
- **Debug Mode**: Enhanced error reporting and logging

### Production Environment
- **Load Balancer**: Nginx or similar for scaling
- **Process Manager**: PM2 or systemd for service management
- **Database**: PostgreSQL recommended over SQLite
- **Caching**: Redis for session and query caching

### Docker Support (Future)
- Containerized deployment options
- Docker Compose for multi-service orchestration
- Kubernetes manifests for enterprise deployment

## 📈 Scalability Considerations

### Horizontal Scaling
- **Frontend**: Multiple Next.js instances behind load balancer
- **Backend**: Multiple Flask instances with shared database
- **AI Processing**: Queue-based processing with Celery

### Vertical Scaling
- **CPU**: Scales well with multi-core processors
- **Memory**: Linear scaling with concurrent sessions
- **Storage**: I/O optimization for large file processing

## 🔧 Maintenance Requirements

### Regular Updates
- **Security Patches**: Monthly for all dependencies
- **AI Models**: Quarterly model updates
- **Knowledge Base**: Regular PDF content updates

### Monitoring
- **System Health**: CPU, memory, disk usage
- **API Performance**: Response times and error rates
- **Session Management**: Active sessions and cleanup

### Backup Requirements
- **Database**: Regular SQLite/PostgreSQL backups
- **Knowledge Base**: PDF and vector index backups
- **Configuration**: Environment and settings backup

## 📚 Documentation Requirements

### User Documentation
- **Setup Guide**: Complete installation instructions
- **User Manual**: Feature usage and workflows
- **API Documentation**: REST endpoint specifications

### Developer Documentation
- **Architecture Guide**: System design and patterns
- **Contribution Guide**: Development workflow
- **Testing Guide**: Test execution and creation

## 🎯 Compliance and Standards

### Code Quality
- **TypeScript**: Strict type checking for frontend
- **Python Type Hints**: Type annotations for backend
- **ESLint**: JavaScript/TypeScript linting
- **Black**: Python code formatting

### Security Standards
- **OWASP**: Web application security guidelines
- **Input Validation**: All user inputs sanitized
- **API Security**: Rate limiting and authentication

---

**Note**: This document serves as the comprehensive requirements specification for the Intellicket AI Support Platform. All requirements listed are necessary for full functionality, though the system can operate with reduced features if certain optional components are unavailable.