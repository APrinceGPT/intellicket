"""
Configuration file for CSD AntiVirus Conflict Analyzer
Separates sensitive configuration from main application code
"""
import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Application configuration with security best practices"""
    
    # Security settings
    SECRET_KEY = os.environ.get('FLASK_SECRET_KEY', 'your-secret-key-here-change-in-production')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    UPLOAD_EXTENSIONS = {'.xml'}
    
    # Claude/Anthropic API configuration - Load from environment variables
    OPENAI_BASE_URL = os.environ.get('OPENAI_BASE_URL', 'https://api.rdsec.trendmicro.com/prod/aiendpoint/v1/')
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')  # NEVER hardcode API keys
    OPENAI_MODEL = os.environ.get('OPENAI_MODEL', 'claude-4-sonnet')
    
    # File handling
    TEMP_DIR = os.environ.get('TEMP_DIR', 'temp')
    ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')
    PORT = int(os.environ.get('PORT', '5003'))  # Default port 5003
    
    # Debug mode (should be False in production)
    DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() in ('true', '1', 'yes')
    
    @classmethod
    def validate_config(cls) -> bool:
        """Validate that required configuration is present"""
        if not cls.OPENAI_API_KEY:
            print("WARNING: OPENAI_API_KEY environment variable is not set. Claude AI features will be disabled.")
            print("Please create a .env file based on .env.template and configure your Claude API key.")
            # Don't raise error for testing purposes
            cls.OPENAI_API_KEY = "dummy-key-for-testing"
        return True

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = False

class ProductionConfig(Config):
    """Production configuration with enhanced security"""
    DEBUG = False
    # Add additional production-specific settings here
    
def get_config() -> Config:
    """Get configuration based on environment"""
    env = os.environ.get('FLASK_ENV', 'development')
    if env == 'production':
        return ProductionConfig()
    return DevelopmentConfig()
