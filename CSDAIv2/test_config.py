"""
Simple test to verify API configuration loading
"""

def test_config_loading():
    """Test if configuration is loaded correctly"""
    print("🔍 Testing Configuration Loading...")
    
    try:
        from config import Config
        print(f"✅ Config class loaded successfully")
        
        api_key = Config.OPENAI_API_KEY
        base_url = Config.OPENAI_BASE_URL
        model = Config.OPENAI_MODEL
        
        print(f"🔑 API Key: {'✅ Found' if api_key else '❌ Missing'}")
        print(f"🔗 Base URL: {'✅ Found' if base_url else '❌ Missing'} - {base_url}")
        print(f"🤖 Model: {model}")
        
        if api_key and base_url:
            print("✅ Configuration is complete for AI responses")
            print(f"🔑 API Key preview: {api_key[:20]}..." if len(api_key) > 20 else f"🔑 API Key: {api_key}")
            return True
        else:
            print("⚠️ Configuration incomplete")
            return False
            
    except Exception as e:
        print(f"❌ Config loading failed: {e}")
        return False

if __name__ == "__main__":
    test_config_loading()
