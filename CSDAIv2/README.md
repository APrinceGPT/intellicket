# Deep Security Unified Analyzer v2 (CSDAIv2)

A comprehensive cybersecurity analysis platform with enhanced UI/UX, real-time progress tracking, and AI-powered insights.

## 🚀 Features

### Core Analysis Capabilities
- **Multi-Engine Analysis**: DSAgent Log Analyzer, AMSP Analyzer, Conflict Analyzer, Resource Analyzer
- **PDF Support**: Extract and analyze content from PDF documents
- **ML-Enhanced Analysis**: Machine learning integration for advanced threat detection
- **RAG-Enhanced Analysis**: Retrieval-Augmented Generation for contextual insights

### Enhanced User Experience
- **Wizard-Based Interface**: Step-by-step guided analysis process
- **Real-Time Progress Bar**: Live status updates with animated stages
- **Background Processing**: Non-blocking analysis with instant UI feedback
- **Drag & Drop Upload**: Multiple file upload with visual feedback
- **Export Functionality**: Download analysis results as formatted text files

### Technical Features
- **Session Management**: Persistent session tracking across analysis steps
- **Security**: Input validation, file type checking, and secure file handling
- **Responsive Design**: Mobile-friendly interface with Bootstrap 5
- **Error Handling**: Comprehensive error management and user feedback

## 🛠️ Installation & Setup

### **Prerequisites**
- **Python 3.8+** with pip package manager
- **Claude API Key** for AI-powered analysis features
- **2GB+ free disk space** for temporary files and knowledge base

### **Quick Setup**

1. **Install Dependencies:**
```bash
pip install -r requirements.txt
```

2. **Configure Environment:**
```bash
cp .env.example .env
# Edit .env file with your API keys and configuration
```

3. **Required Environment Variables:**
```env
# Essential: Claude AI API Key
OPENAI_API_KEY=your-claude-api-key-here

# Optional but recommended
FLASK_SECRET_KEY=your-unique-secret-key
OPENAI_BASE_URL=https://api.rdsec.trendmicro.com/prod/aiendpoint/v1/
```

4. **Run the Application:**
```bash
python app.py
```

5. **Access the Interface:**
- **Web UI**: http://localhost:5003  
- **API Endpoints**: http://localhost:5003/api/

### **Setup Notes**
- **First Run**: Knowledge base will be automatically initialized
- **Large Files**: Ensure sufficient disk space for log file processing
- **Firewall**: Allow port 5003 for local access
- **API Key**: Claude AI features require valid API key configuration

## 🔧 Configuration Options

### **Environment Variables (.env)**
```env
# Flask Application
FLASK_SECRET_KEY=your-secret-key-here
PORT=5003
DEBUG=false

# Claude AI Configuration
OPENAI_API_KEY=your-claude-api-key
OPENAI_BASE_URL=https://api.rdsec.trendmicro.com/prod/aiendpoint/v1/
OPENAI_MODEL=claude-4-sonnet

# File Handling
MAX_CONTENT_LENGTH=52428800  # 50MB
TEMP_DIR=temp

# Dynamic RAG System
RAG_PDF_DIRECTORY=pdf
RAG_MAX_KNOWLEDGE_SOURCES=6
RAG_MAX_DYNAMIC_QUERIES=8
RAG_ENABLE_AI_RESPONSES=true

# Security
ALLOWED_HOSTS=localhost,127.0.0.1
```

### **Knowledge Base Setup**
```bash
# Optional: Add custom PDF documentation
# Place PDF files in: CSDAIv2/pdf/
# System will automatically index them on startup
```

## 🚀 **Quick Start Guide**

### **1. Basic Log Analysis**
1. Navigate to http://localhost:5003
2. Select "DS Agent Log Analysis"
3. Upload your log files (.log, .txt, .xml)
4. Follow the 4-stage analysis process
5. Download comprehensive results

### **2. Resource Analysis**
1. Select "Resource Analysis" 
2. Upload RunningProcess.xml and TopNBusyProcess.txt
3. Get ML-enhanced exclusion recommendations
4. Export optimization suggestions

### **3. API Integration**
```python
import requests

# Upload file for analysis
files = {'file': open('ds_agent.log', 'rb')}
response = requests.post('http://localhost:5003/api/upload', files=files)

# Check analysis status
session_id = response.json()['session_id']
status = requests.get(f'http://localhost:5003/api/session/status/{session_id}')
```

## 📋 **Features Overview**

### **🤖 AI-Powered Analysis**
- **Claude-4 Sonnet**: Expert-level log analysis and recommendations
- **Dynamic RAG**: Context-aware knowledge retrieval from PDF documentation
- **ML Pattern Recognition**: Behavioral analysis and anomaly detection
- **Component Health Scoring**: Real-time system health assessment

### **🔍 Analysis Engines**
- **DS Agent Analyzer**: Deep Security agent log comprehensive analysis
- **Resource Analyzer**: Process optimization and exclusion recommendations  
- **AMSP Analyzer**: Anti-malware specific log analysis
- **Multi-file Processor**: Batch analysis for complex scenarios

### **💻 User Interface**
- **Wizard Interface**: Step-by-step guided analysis workflow
- **Real-time Progress**: 4-stage progress tracking with detailed messaging
- **Professional Reports**: HTML-formatted results with export functionality
- **Session Management**: Secure handling of analysis sessions

### **🔒 Security Features**
- **Secure File Handling**: Validated uploads with automatic cleanup
- **Environment Configuration**: No hardcoded secrets or API keys
- **Session Isolation**: Each analysis runs in isolated session
- **Input Validation**: Comprehensive file type and content validation

## 📁 Project Structure

```
CSDAIv2/
├── app.py                 # Main Flask application
├── routes.py              # Application routes and endpoints
├── analyzers.py           # Core analysis engines
├── ml_analyzer.py         # Machine learning analysis
├── rag_system.py          # RAG-enhanced analysis
├── extract_pdf.py         # PDF processing utilities
├── config.py              # Configuration management
├── security.py            # Security utilities
├── templates.py           # HTML template definitions
├── wizard_templates.py    # Wizard step templates
├── ui_components.py       # UI component library
├── static/
│   ├── css/
│   │   └── progress-bar.css    # Enhanced progress bar styles
│   └── js/
│       └── progress-bar.js     # Progress bar JavaScript
├── docs/                  # Documentation
├── shared/                # Shared utilities
└── requirements.txt       # Python dependencies
```

## 🎯 Usage

### Basic Analysis Workflow
1. **Step 1**: Upload files (drag & drop or file browser)
2. **Step 2**: Select analysis type and configure options
3. **Step 3**: Review settings and begin analysis
4. **Step 4**: Monitor real-time progress with live updates
5. **Step 5**: View results and export findings

### Supported File Types
- Log files (.log, .txt)
- Configuration files (.conf, .cfg, .ini)
- PDF documents (.pdf)
- XML files (.xml)
- CSV files (.csv)

### Analysis Types
- **DSAgent Log Analysis**: Comprehensive log file analysis
- **AMSP Analysis**: Application and system performance analysis
- **Conflict Analysis**: Antivirus conflict detection in running processes
- **Resource Analysis**: System resource utilization analysis

## 🔧 Configuration

### Environment Variables
Create a `.env` file based on `.env.template`:

```env
# Flask Configuration
FLASK_ENV=development
SECRET_KEY=your-secret-key-here

# Analysis Configuration
MAX_FILE_SIZE=50MB
ALLOWED_EXTENSIONS=log,txt,pdf,xml,csv,conf,cfg,ini

# ML/AI Configuration
ENABLE_ML_ANALYSIS=true
ENABLE_RAG_ANALYSIS=true
```

### Custom Configuration
Modify `config.py` to adjust:
- File upload limits
- Analysis timeouts
- UI themes and styling
- Security settings

## 🚀 Development

### Key Components

#### Progress Bar System
- **CSS**: `static/css/progress-bar.css` - Animated stages and shimmer effects
- **JavaScript**: `static/js/progress-bar.js` - Real-time status polling
- **Backend**: Session-based progress tracking with background threading

#### Analysis Engine
- **Multi-threaded Processing**: Background analysis with Flask session management
- **Real-time Updates**: AJAX polling for live progress updates
- **Error Handling**: Comprehensive error management and recovery

#### Session Management
- **Persistent Sessions**: Cross-step data persistence
- **Security**: Secure session handling and validation
- **Export Integration**: Session-based result export functionality

### Contributing
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📊 Recent Updates

### v2.0 Enhancement Summary
- ✅ Enhanced progress bar with real-time status tracking
- ✅ Background analysis processing with threading
- ✅ Instant UI feedback and eliminated artificial delays
- ✅ Fixed Flask session thread-local access issues
- ✅ Improved export functionality with session manager integration
- ✅ Mobile-responsive design improvements
- ✅ Comprehensive error handling and user feedback

## 🐛 Troubleshooting

### Common Issues
1. **Analysis Failed Error**: Ensure all dependencies are installed and files are accessible
2. **Upload Issues**: Check file size limits and supported formats
3. **Progress Bar Not Updating**: Verify JavaScript is enabled and check browser console
4. **Export Not Working**: Ensure analysis has completed successfully

### Debug Mode
Run with debug enabled:
```bash
FLASK_ENV=development python app.py
```

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Flask framework for web application foundation
- Bootstrap 5 for responsive UI components
- Font Awesome for professional iconography
- Contributors and beta testers for valuable feedback

## 📞 Support

For issues, questions, or contributions:
- Create an issue on GitHub
- Submit a pull request
- Contact the development team

---

**Deep Security Unified Analyzer v2** - Empowering cybersecurity analysis with enhanced user experience and AI-powered insights.
