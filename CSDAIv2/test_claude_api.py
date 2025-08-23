"""
Test Claude API call with simple prompt
"""

def test_claude_api():
    """Test Claude API with a simple prompt"""
    print("🧪 Testing Claude API connection...")
    
    try:
        from config import Config
        import requests
        
        api_key = Config.OPENAI_API_KEY
        base_url = Config.OPENAI_BASE_URL
        model = Config.OPENAI_MODEL
        
        print(f"🔑 API Key: {'✅ Found' if api_key else '❌ Missing'}")
        print(f"🔗 Base URL: {base_url}")
        print(f"🤖 Model: {model}")
        
        if not api_key or not base_url:
            print("❌ Configuration incomplete")
            return False
        
        # Simple test prompt
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            'model': model,
            'messages': [
                {
                    'role': 'user', 
                    'content': 'Hello, please respond with "API connection successful" if you can read this message.'
                }
            ],
            'max_tokens': 50,
            'temperature': 0.1
        }
        
        print("📡 Making API request...")
        
        try:
            response = requests.post(
                f"{base_url.rstrip('/')}/chat/completions",
                headers=headers,
                json=payload,
                timeout=60  # 1 minute timeout
            )
            
            print(f"📊 Response status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                ai_response = result['choices'][0]['message']['content']
                print(f"✅ Claude API response: {ai_response}")
                return True
            else:
                print(f"❌ API error: {response.status_code}")
                print(f"Response: {response.text[:500]}")
                return False
                
        except requests.exceptions.Timeout:
            print("⚠️ API request timed out after 1 minute")
            return False
            
        except requests.exceptions.ConnectionError as e:
            print(f"❌ Connection error: {str(e)[:200]}")
            return False
            
        except Exception as e:
            print(f"❌ Request failed: {str(e)[:200]}")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    test_claude_api()
