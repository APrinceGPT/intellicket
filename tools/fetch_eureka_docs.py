#!/usr/bin/env python3
"""
Script to fetch JIRA Cloud REST API documentation from Atlassian
"""
import requests
import base64
import json
import sys

def fetch_atlassian_page():
    """Fetch the JIRA Cloud REST API documentation page"""
    
    # API credentials
    username = "adrian_principio@trendmicro.com"  # Fixed typo
    api_token = "ATATT3xFfGF0rWXAFzb8HPpEhhWlAHUF51paD1hbJ07M4UZFt2_gPyJ4D2wQ5kAPERsmaKppYwQtTnY5fcI1gbJiJcA4YW-EXxHP5SwQa-cvl3Cq-Gm3j9qGgWYQLWtixh1cSepnSz8sJPLR-IjUcCxJ6fReLztWBhuj_vvW7RUmOkm8G9kZWcg=E4B7001D"
    
    # Create basic auth header
    auth_string = f"{username}:{api_token}"
    auth_bytes = auth_string.encode('ascii')
    auth_b64 = base64.b64encode(auth_bytes).decode('ascii')
    
    headers = {
        'Authorization': f'Basic {auth_b64}',
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }
    
    # The page URL - convert to API endpoint
    page_id = "33630321"  # JIRA Cloud REST API page
    base_url = "https://trendmicro.atlassian.net"
    api_url = f"{base_url}/wiki/rest/api/content/{page_id}?expand=body.storage,space,version"
    
    try:
        print(f"Fetching JIRA Cloud REST API documentation...")
        print(f"API URL: {api_url}")
        
        response = requests.get(api_url, headers=headers, timeout=30)
        
        print(f"Response Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            # Extract content
            title = data.get('title', 'Unknown Title')
            content = data.get('body', {}).get('storage', {}).get('value', '')
            
            print(f"\n=== {title} ===\n")
            
            # Save full JSON response
            with open('jira_api_docs_full.json', 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            # Save just the content
            with open('jira_api_docs_content.html', 'w', encoding='utf-8') as f:
                f.write(content)
            
            print("Content saved to:")
            print("- jira_api_docs_full.json (complete API response)")
            print("- jira_api_docs_content.html (page content)")
            
            # Try to extract key information
            if 'REST API' in content or 'jira' in content.lower() or 'endpoint' in content.lower():
                print("\n=== Key JIRA API Information Found ===")
                # Look for API endpoints and methods
                lines = content.split('\n')
                for i, line in enumerate(lines):
                    if any(keyword in line.lower() for keyword in ['rest', 'api', 'endpoint', 'search', 'jql', 'issue']):
                        print(f"Line {i}: {line.strip()[:100]}...")
            
            return True
            
        else:
            print(f"Error: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False

if __name__ == "__main__":
    success = fetch_atlassian_page()
    if not success:
        sys.exit(1)
