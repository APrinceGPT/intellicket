#!/usr/bin/env python3
"""
Focused Deep Security Agent Offline Research Script
Targets: Causes, Solutions, Log Samples for DS Agent going offline
"""

import requests
import json
import time
import base64
from datetime import datetime

class DSOfflineResearcher:
    def __init__(self):
        self.base_url = "https://trendmicro.atlassian.net/rest/api/3"
        self.auth_header = self._get_auth_header()
        self.results = []
        
    def _get_auth_header(self):
        email = input("Enter your Trend Micro email: ").strip()
        api_token = input("Enter your JIRA API token: ").strip()
        
        credentials = f"{email}:{api_token}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()
        return {"Authorization": f"Basic {encoded_credentials}"}
    
    def search_jira(self, jql, max_results=50):
        """Execute focused JQL search"""
        url = f"{self.base_url}/search"
        
        params = {
            'jql': jql,
            'maxResults': max_results,
            'fields': 'summary,description,assignee,status,created,updated,labels,components'
        }
        
        try:
            print(f"Searching: {jql[:80]}...")
            response = requests.get(url, headers=self.auth_header, params=params, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                issues = data.get('issues', [])
                print(f"  → Found {len(issues)} issues")
                return issues
            else:
                print(f"  → Error: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"  → Exception: {e}")
            return []
    
    def extract_text_from_content(self, content_obj):
        """Extract text from JIRA ADF content"""
        if not isinstance(content_obj, dict):
            return str(content_obj)
            
        text_parts = []
        
        def extract_text_recursive(obj):
            if isinstance(obj, dict):
                if obj.get('type') == 'text':
                    text_parts.append(obj.get('text', ''))
                elif 'content' in obj:
                    for item in obj['content']:
                        extract_text_recursive(item)
            elif isinstance(obj, list):
                for item in obj:
                    extract_text_recursive(item)
        
        extract_text_recursive(content_obj)
        return ' '.join(text_parts)
    
    def run_focused_research(self):
        """Execute focused searches for DS Agent offline issues"""
        
        # Core offline-related searches
        queries = [
            'project = "Deep Security" AND text ~ "agent offline" AND created >= -52w',
            'project = "Deep Security" AND text ~ "heartbeat" AND text ~ "fail" AND created >= -52w',
            'project = "Deep Security" AND text ~ "communication failure" AND created >= -52w',
            'project = "Deep Security" AND summary ~ "disconnect" AND created >= -52w',
            'text ~ "ds_agent" AND text ~ "offline" AND created >= -52w'
        ]
        
        print("=== Deep Security Agent Offline Research ===\n")
        
        for query in queries:
            issues = self.search_jira(query, max_results=20)
            self.results.extend(issues)
            time.sleep(2)  # Reduced delay
        
        # Remove duplicates
        seen_keys = set()
        unique_results = []
        for issue in self.results:
            key = issue.get('key')
            if key and key not in seen_keys:
                seen_keys.add(key)
                unique_results.append(issue)
        
        self.results = unique_results
        print(f"\nTotal unique issues found: {len(self.results)}")
        
        return self.generate_focused_report()
    
    def generate_focused_report(self):
        """Generate focused report on DS Agent offline causes and solutions"""
        
        offline_causes = []
        solutions = []
        log_samples = []
        
        for issue in self.results:
            fields = issue.get('fields', {})
            
            # Extract summary
            summary_field = fields.get('summary', '')
            summary = summary_field if isinstance(summary_field, str) else str(summary_field)
            
            # Extract description
            description_field = fields.get('description', '')
            if isinstance(description_field, dict):
                description = self.extract_text_from_content(description_field)
            else:
                description = str(description_field or '')
            
            combined_text = f"{summary} {description}".lower()
            
            # Categorize content
            if any(word in combined_text for word in ['cause', 'reason', 'why', 'because']):
                offline_causes.append({
                    'key': issue.get('key'),
                    'summary': summary,
                    'content': combined_text[:500]
                })
            
            if any(word in combined_text for word in ['solution', 'fix', 'resolve', 'troubleshoot']):
                solutions.append({
                    'key': issue.get('key'),
                    'summary': summary,
                    'content': combined_text[:500]
                })
            
            if any(word in combined_text for word in ['log', 'error', 'debug', 'trace']):
                log_samples.append({
                    'key': issue.get('key'),
                    'summary': summary,
                    'content': combined_text[:800]
                })
        
        # Generate report
        report = f"""
# Deep Security Agent Offline - Comprehensive Research Report
**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Total Issues Analyzed:** {len(self.results)}

## 🔍 OFFLINE CAUSES IDENTIFIED

"""
        
        for i, cause in enumerate(offline_causes[:10], 1):
            report += f"""
### {i}. {cause['summary']} ({cause['key']})
**Analysis:** {cause['content'][:300]}...

---
"""
        
        report += f"""
## 🛠️ SOLUTIONS AND FIXES

"""
        
        for i, solution in enumerate(solutions[:10], 1):
            report += f"""
### {i}. {solution['summary']} ({solution['key']})
**Solution:** {solution['content'][:300]}...

---
"""
        
        report += f"""
## 📋 LOG SAMPLES AND ERROR PATTERNS

"""
        
        for i, log in enumerate(log_samples[:8], 1):
            report += f"""
### {i}. {log['summary']} ({log['key']})
**Log Pattern:** {log['content'][:400]}...

---
"""
        
        report += f"""
## 📊 SUMMARY STATISTICS
- **Causes Identified:** {len(offline_causes)}
- **Solutions Found:** {len(solutions)}
- **Log Samples:** {len(log_samples)}
- **Total Issues:** {len(self.results)}

*Report focused strictly on Deep Security Agent offline scenarios*
"""
        
        # Save report
        filename = f"DS_Agent_Offline_Research_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"\n✅ Focused research complete! Report saved to: {filename}")
        print(f"📋 Found {len(offline_causes)} causes, {len(solutions)} solutions, {len(log_samples)} log samples")
        
        return filename

def main():
    researcher = DSOfflineResearcher()
    researcher.run_focused_research()

if __name__ == "__main__":
    main()
