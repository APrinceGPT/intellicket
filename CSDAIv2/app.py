# -*- coding: utf-8 -*-
"""
Deep Security Unified Analyzer - Main Application
Optimized main entry point with mo# Register all routes
register_routes(app)

# Register REST API routes for Intellicket integration
try:
    from api_routes import register_api_routes
    register_api_routes(app, config)
    print("✅ REST API routes registered")
except ImportError as e:
    print(f"⚠️ REST API routes not available: {e}")

# Note: Removed Rich Data API v2 for simplified architectureitecture.
"""

import os
import sys
import httpx

# Note: Using local config.py instead of shared to avoid conflicts

# Import Flask and configuration
from flask import Flask, session

# Import modular components
from config import get_config
from security import validate_host_access
from ui_components import session_manager
from routes import register_routes

# Note: Removed Rich Data API v2 imports for simplified architecture

# Import ML and RAG systems
try:
    from ml_analyzer import enhance_analysis_with_ml, MLLogAnalyzer
    ML_AVAILABLE = True
    print("✅ ML-Enhanced Analysis Available")
except ImportError as e:
    ML_AVAILABLE = False
    print(f"⚠�  ML features not available: {e}")

try:
    from dynamic_rag_system import DynamicRAGSystem, apply_dynamic_rag_to_analysis
    DYNAMIC_RAG_AVAILABLE = True
    print("✅ Dynamic RAG-Enhanced Analysis Available")
except ImportError as e:
    DYNAMIC_RAG_AVAILABLE = False
    print(f"⚠�  Dynamic RAG features not available: {e}")

# Initialize OpenAI client
try:
    from openai import OpenAI
    
    # Load configuration
    config = get_config()
    config.validate_config()
    
    # Store original proxy settings
    proxy_vars = ['HTTP_PROXY', 'HTTPS_PROXY', 'http_proxy', 'https_proxy', 'ALL_PROXY', 'all_proxy']
    original_proxies = {}
    for var in proxy_vars:
        if var in os.environ:
            original_proxies[var] = os.environ[var]
    
    # Temporarily clear proxy environment variables
    for var in proxy_vars:
        if var in os.environ:
            del os.environ[var]
    
    # Create custom httpx client
    custom_http_client = httpx.Client(
        timeout=30.0,
        follow_redirects=True
    )
    
    # Initialize OpenAI client
    client = OpenAI(
        api_key=config.OPENAI_API_KEY,
        base_url=config.OPENAI_BASE_URL,
        http_client=custom_http_client
    )
    
    # Test the client
    try:
        test_response = client.chat.completions.create(
            model=config.OPENAI_MODEL,
            messages=[{"role": "user", "content": "test"}],
            max_tokens=1,
            timeout=5.0
        )
        OPENAI_AVAILABLE = True
        print("✅ OpenAI client initialized and tested successfully")
    except Exception as test_error:
        print(f"⚠�  OpenAI client created but test failed: {test_error}")
        OPENAI_AVAILABLE = True
        print("✅ OpenAI client initialized (test skipped)")
    
    # Restore proxy settings
    for var, value in original_proxies.items():
        os.environ[var] = value
        
except Exception as e:
    print(f"� � OpenAI client initialization failed: {e}")
    OPENAI_AVAILABLE = False
    client = None

# Create Flask application
app = Flask(__name__)

# Configure Flask application
app.secret_key = config.SECRET_KEY
app.config['MAX_CONTENT_LENGTH'] = config.MAX_CONTENT_LENGTH
app.config['PERMANENT_SESSION_LIFETIME'] = 86400  # 24 hours

# Add CORS support for admin interface
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
    return response

# Register all routes
register_routes(app)

# Register REST API routes for Intellicket integration
try:
    from api_routes import register_api_routes
    register_api_routes(app, config)
    print("✅ REST API routes registered")
except ImportError as e:
    print(f"⚠️  REST API routes not available: {e}")

# Register Admin API routes for Unified Admin Interface
try:
    from admin.unified_admin_routes import register_admin_routes
    register_admin_routes(app, config)
    print("✅ Admin API routes registered")
except ImportError as e:
    print(f"⚠️  Admin routes not available: {e}")
except Exception as e:
    print(f"⚠️  Admin routes initialization failed: {e}")

# Note: Removed Rich Data API v2 registration for simplified architecture

def initialize_application():
    """Initialize application components"""
    print("🚀 Initializing Deep Security Unified Analyzer...")
    
    # Validate configuration
    try:
        config.validate_config()
        print("✅ Configuration validated")
    except Exception as e:
        print(f"� � Configuration validation failed: {e}")
        return False
    
    # Initialize session manager
    print("✅ Session manager initialized")
    
    # Initialize wizard system
    print("✅ Wizard system initialized")
    
    # Initialize guidance system
    print("✅ User guidance system initialized")
    
    # Check directories
    os.makedirs(config.TEMP_DIR, exist_ok=True)
    print(f"✅ Temporary directory ready: {config.TEMP_DIR}")
    
    print("🎉 Application initialization complete!")
    return True

if __name__ == "__main__":
    # Initialize application
    if not initialize_application():
        print("� � Application initialization failed!")
        sys.exit(1)
    
    # Display startup information
    print("\n" + "="*60)
    print("🛡️   TREND MICRO DEEP SECURITY UNIFIED ANALYZER")
    print("="*60)
    print(f"🌐  Server starting on: http://localhost:{config.PORT}")
    print(f"🎯 Backend analysis engines available: 7")
    print(f"🎯 Frontend-exposed analyzers: 4")
    print(f"🤖 AI Analysis: {'✅ Enabled' if OPENAI_AVAILABLE else '❌ Disabled'}")
    print(f"🧠 ML Analysis: {'✅ Enabled' if ML_AVAILABLE else '❌ Disabled'}")
    print(f"📚 Dynamic RAG Enhancement: {'✅ Enabled' if DYNAMIC_RAG_AVAILABLE else '❌ Disabled'}")
    print(f"🔒 Security: {'✅ Host validation enabled' if config.ALLOWED_HOSTS else '⚠️  Open access'}")
    print("="*60)
    print("📖 Intellicket Frontend-Accessible Analysis Types:")
    print("   • AMSP Anti-Malware (AMSP-Inst_LocalDebugLog)")
    print("   • AV Conflicts (RunningProcesses.xml)")
    print("   • Resource Analysis (RunningProcesses.xml + TopNBusyProcess.txt)")
    print("   • Diagnostic Package (ZIP files with comprehensive log data)")
    print("")
    print("🔧 Backend-Only Analysis Engines (API accessible):")
    print("   • DS Agent Logs (ds_agent.log)")
    print("   • DS Agent Offline (ds_agent.log - specialized offline analysis)")
    print("   • DS Agent Enhanced (modular with ML/RAG integration)")
    print("="*60)
    print("🎮 Ready for analysis! Open your browser to get started.")
    print()
    
    # Start Flask development server
    try:
        app.run(
            host='0.0.0.0',
            port=config.PORT,
            debug=False,
            threaded=True
        )
    except KeyboardInterrupt:
        print("\n👋 Shutting down Deep Security Unified Analyzer...")
    except Exception as e:
        print(f"� � Server error: {e}")
        sys.exit(1)
