# 🚀 TrendAI - Intelligent Trend Micro Support System

[![Next.js](https://img.shields.io/badge/Next.js-15.5-black)](https://nextjs.org/)
[![React](https://img.shields.io/badge/React-19.1-blue)](https://reactjs.org/)
[![Flask](https://img.shields.io/badge/Flask-2.3-green)](https://flask.palletsprojects.com/)
[![Python](https://img.shields.io/badge/Python-3.8+-yellow)](https://python.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0-blue)](https://typescriptlang.org/)

> **AI-powered analysis platform for Trend Micro products with advanced ML-enhanced Dynamic RAG capabilities**

## 🌟 **Overview**

TrendAI is a sophisticated web application that provides intelligent support and analysis for Trend Micro security products. It features an intuitive frontend built with Next.js and a powerful backend analysis engine with ML-enhanced Dynamic RAG (Retrieval-Augmented Generation) capabilities.

### **Key Features**
- 🤖 **Claude-4 Sonnet AI Integration** - Expert-level analysis powered by advanced AI
- 🧠 **ML Pattern Recognition** - Behavioral analysis and anomaly detection
- 📚 **Dynamic RAG System** - Context-aware knowledge retrieval
- 📊 **Real-time Progress Tracking** - Professional progress visualization
- 🔒 **Security-First Design** - Secure file handling and analysis
- 🌐 **Multi-Product Support** - Deep Security, Apex One, Vision One, Service Gateway

## 🚀 **Quick Start**

### **Prerequisites**
- **Node.js** 18+ and npm
- **Python** 3.8+ and pip
- **Claude API Key** (for AI features)

### **1. Clone the Repository**
```bash
git clone https://github.com/yourusername/trendaiv2.git
cd trendaiv2
```

### **2. Setup Backend (CSDAIv2)**
```bash
cd CSDAIv2

# Install Python dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your API keys and configuration

# Start the backend server
python app.py
```

### **3. Setup Frontend**
```bash
# Navigate back to project root
cd ..

# Install Node.js dependencies
npm install

# Start the development server
npm run dev
```

### **4. Access the Application**
- **Frontend**: http://localhost:3000
- **Backend Admin**: http://localhost:5003
- **Deep Security Analysis**: http://localhost:3000/products/deep-security

## 📁 **Project Structure**

```
trendaiv2/
├── 🎨 Frontend (Next.js + TypeScript)
│   ├── src/
│   │   ├── app/                     # App router pages
│   │   │   ├── page.tsx            # Landing page
│   │   │   ├── products/           # Product-specific pages
│   │   │   └── api/                # API proxy routes
│   │   ├── components/             # Reusable components
│   │   └── contexts/               # Global state management
│   ├── public/                     # Static assets
│   └── package.json               # Frontend dependencies
│
├── 🔧 Backend (Flask + Python)
│   ├── CSDAIv2/
│   │   ├── app.py                  # Main Flask application
│   │   ├── api_routes.py           # REST API endpoints
│   │   ├── analyzers.py            # Core analysis engines
│   │   ├── dynamic_rag_system.py   # RAG implementation
│   │   ├── ml_analyzer.py          # ML pattern recognition
│   │   ├── config.py               # Configuration management
│   │   ├── static/                 # CSS/JS assets
│   │   ├── requirements.txt        # Python dependencies
│   │   └── .env.example           # Environment template
│
└── 📚 Documentation
    ├── README.md                   # This file
    ├── COMPLETE_PROJECT_GUIDE.md   # Detailed setup guide
    └── GITHUB_REPOSITORY_PREPARATION.md
```

## 🔧 **Configuration**

### **Environment Variables (CSDAIv2/.env)**
```env
# Required: Claude AI API Key
OPENAI_API_KEY=your-claude-api-key-here

# Optional: Custom configuration
FLASK_SECRET_KEY=your-secret-key
OPENAI_BASE_URL=https://api.rdsec.trendmicro.com/prod/aiendpoint/v1/
RAG_MAX_KNOWLEDGE_SOURCES=6
```

See `CSDAIv2/.env.example` for complete configuration options.

## 🎯 **Features**

### **🧠 AI-Powered Analysis**
- **ML Pattern Recognition**: Behavioral analysis and anomaly detection
- **Dynamic RAG**: Context-aware knowledge retrieval from proprietary docs
- **Claude-4 Sonnet**: Expert-level AI analysis and recommendations
- **Component Health**: Real-time system health assessment

### **📊 Advanced Progress Tracking**
- **4-Stage Workflow**: File Parsing → ML Analysis → Dynamic RAG → Report Generation
- **Real-time Updates**: Live progress with detailed stage messaging
- **Professional UI**: Polished progress visualization building user confidence

### **🔒 Security & Reliability**
- **Secure File Handling**: Validated uploads with automatic cleanup
- **Environment-based Config**: No hardcoded secrets or API keys
- **Error Recovery**: Robust error handling and user feedback
- **Session Management**: Secure analysis session tracking

## 🧪 **Usage Examples**

### **1. Deep Security Log Analysis**
1. Navigate to http://localhost:3000/products/deep-security
2. Upload DS Agent log files (.log, .txt, .xml)
3. Watch the 4-stage analysis process:
   - **File Parsing**: Log extraction and validation
   - **ML Analysis**: Pattern recognition and anomaly detection
   - **Dynamic RAG**: AI-powered analysis with knowledge retrieval
   - **Report Generation**: Comprehensive recommendations

### **2. Resource Analysis**
1. Upload RunningProcess.xml and TopNBusyProcess.txt
2. Get ML-enhanced resource analysis
3. Receive exclusion recommendations
4. Export results as formatted text

## 🚨 **Troubleshooting**

### **Backend Won't Start**
```bash
# Check Python version
python --version  # Should be 3.8+

# Install dependencies
pip install -r CSDAIv2/requirements.txt

# Check API key configuration
# Ensure OPENAI_API_KEY is set in .env
```

### **Frontend Build Errors**
```bash
# Clear cache and reinstall
npm cache clean --force
rm -rf node_modules package-lock.json
npm install
```

## 📄 **License**

This project is licensed under the MIT License.

## 🆘 **Support**

- **Documentation**: See `COMPLETE_PROJECT_GUIDE.md` for detailed setup
- **Issues**: Create GitHub issues for bugs or feature requests

---

**⭐ If this project helps you, please give it a star on GitHub!**

*TrendAI - Making Trend Micro support intelligent and efficient*

## Supported Products

- **Deep Security**: Server protection and security management
- **Apex One**: Endpoint security solution
- **Vision One**: Extended detection and response (XDR) platform
- **Service Gateway**: Secure service delivery platform

## Project Structure

```
src/
├── app/
│   ├── page.tsx                    # Landing page with product selection
│   ├── layout.tsx                  # Root layout
│   ├── globals.css                 # Global styles
│   └── products/
│       ├── deep-security/
│       │   └── page.tsx           # Deep Security support page
│       ├── apex-one/
│       │   └── page.tsx           # Apex One support page
│       ├── vision-one/
│       │   └── page.tsx           # Vision One support page
│       └── service-gateway/
│           └── page.tsx           # Service Gateway support page
```

## Getting Started

1. **Install dependencies:**
```bash
npm install
```

2. **Run the development server:**
```bash
npm run dev
```

3. **Open your browser:**
Navigate to [http://localhost:3000](http://localhost:3000) to see the application.

## Integration Points

Each product page is prepared for project integration with dedicated integration areas:

- **Deep Security**: Ready for Deep Security project integration
- **Apex One**: Ready for Apex One project integration  
- **Vision One**: Ready for Vision One project integration
- **Service Gateway**: Ready for Service Gateway project integration

When you need to integrate other projects, simply prompt the system and the integrated components will appear in the designated integration areas on each product page.

## Development

- **Framework**: Next.js 15 with App Router
- **Styling**: Tailwind CSS
- **Language**: TypeScript
- **Linting**: ESLint
- **Build Tool**: Turbopack for fast development

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run start` - Start production server
- `npm run lint` - Run ESLint

## Deployment

The easiest way to deploy this Next.js app is to use the [Vercel Platform](https://vercel.com/new?utm_medium=default-template&filter=next.js&utm_source=create-next-app&utm_campaign=create-next-app-readme).

For more deployment options, check out the [Next.js deployment documentation](https://nextjs.org/docs/app/building-your-application/deploying).
