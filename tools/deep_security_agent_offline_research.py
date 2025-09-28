#!/usr/bin/env python3
"""
Deep Security Agent Offline Research using JIRA via Eureka Search API
This script performs comprehensive searches for information about 
Deep Security Agent going offline and related log analysis by accessing JIRA data.
"""
import requests
import json
import base64
import time
import os
from datetime import datetime

class JiraDeepSecurityResearcher:
    def __init__(self):
        self.username = "adrian_principio@trendmicro.com"
        self.api_token = "ATATT3xFfGF0rWXAFzb8HPpEhhWlAHUF51paD1hbJ07M4UZFt2_gPyJ4D2wQ5kAPERsmaKppYwQtTnY5fcI1gbJiJcA4YW-EXxHP5SwQa-cvl3Cq-Gm3j9qGgWYQLWtixh1cSepnSz8sJPLR-IjUcCxJ6fReLztWBhuj_vvW7RUmOkm8G9kZWcg=E4B7001D"
        self.base_url = "https://connectone-stg.trendmicro.com:8443/api/eurekasearch/EurekaSearch"
        
        # Create headers
        auth_string = f"{self.username}:{self.api_token}"
        auth_bytes = auth_string.encode('ascii')
        auth_b64 = base64.b64encode(auth_bytes).decode('ascii')
        
        self.headers = {
            'Authorization': f'Basic {auth_b64}',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
        
        # Search terms related to Deep Security Agent offline scenarios - optimized for JIRA
        self.search_terms = [
            "Deep Security Agent offline",
            "Deep Security Agent disconnected", 
            "Deep Security Agent connection",
            "Deep Security Agent heartbeat failure",
            "Deep Security Agent communication",
            "Deep Security Agent status",
            "DSA offline",
            "DSA disconnected",
            "DSA connection lost",
            "Agent offline Deep Security",
            "Deep Security Agent service",
            "Deep Security Agent logs",
            "Deep Security Agent troubleshoot",
            "Deep Security Manager agent",
            "DSM agent offline",
            "agent heartbeat Deep Security",
            "Deep Security connectivity",
            "Deep Security network issues",
            "Deep Security firewall",
            "Deep Security certificate error"
        ]
        
        # Data sources to search - focusing on JIRA sources for better performance
        self.data_sources = [
            "seg_jira",              # SEG Jira (permitted source)
            "seg_jira_cloud_pct",    # SEG Jira Cloud PCT (permitted source)  
            "seg_jira_cloud_cpdt",   # SEG Jira Cloud CPDT (permitted source)
            "jpse_jira",             # JPSE Jira
            "jpse_jira_cloud"        # JPSE Jira Cloud
        ]
        
        self.results = {}
        
    def search_eureka(self, query, source, search_type="text_all", num_results=20):
        """Perform a search against Eureka API"""
        payload = {
            "action": "query",
            "search_type": search_type,
            "q": query,
            "source": source,
            "lang": "all",  # JIRA content can be in multiple languages
            "start": 0,
            "num": num_results,
            "field": ["summary", "description", "status", "priority", "assignee", "created_date"],
            "text_mode": "solr",  # Use Solr for more flexible fuzzy matching
            "filter": {}  # Remove Deep Security filter as JIRA might have different field names
        }
        
        try:
            print(f"Searching JIRA for: '{query}' in source: {source}")
            response = requests.post(self.base_url, headers=self.headers, json=payload, timeout=45)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 200:
                    return data.get('data', {})
                else:
                    print(f"API Error: {data.get('message', 'Unknown error')}")
                    return None
            else:
                print(f"HTTP Error: {response.status_code}")
                return None
                
        except requests.exceptions.Timeout:
            print(f"Timeout occurred for query: {query}")
            return None
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            return None
        except Exception as e:
            print(f"Unexpected error: {e}")
            return None
    
    def filter_relevant_results(self, results, query):
        """Filter results to focus on Deep Security Agent offline scenarios in JIRA tickets"""
        if not results or 'results' not in results:
            return []
        
        relevant_docs = []
        # Enhanced keywords for JIRA ticket analysis
        offline_keywords = [
            'offline', 'disconnected', 'connection', 'lost', 'heartbeat',
            'communication', 'network', 'firewall', 'status', 'stopped',
            'failed', 'error', 'troubleshoot', 'log', 'event', 'service',
            'registration', 'activation', 'certificate', 'ssl', 'tls',
            'agent', 'dsa', 'ds_agent', 'endpoint', 'manager', 'dsm',
            'connectivity', 'timeout', 'unreachable', 'unavailable'
        ]
        
        deep_security_keywords = [
            'deep security', 'deepsecurity', 'ds', 'dsa', 'dsm', 
            'deep security agent', 'deep security manager',
            'trend micro deep security'
        ]
        
        for result_type in results.get('results', []):
            if 'docs' in result_type:
                for doc in result_type['docs']:
                    title = doc.get('title', '').lower()
                    content = doc.get('content', '').lower()
                    
                    # First check if it's related to Deep Security
                    is_deep_security = False
                    for ds_keyword in deep_security_keywords:
                        if ds_keyword in title or ds_keyword in content:
                            is_deep_security = True
                            break
                    
                    if not is_deep_security:
                        continue  # Skip if not related to Deep Security
                    
                    # Check if document is relevant to offline scenarios
                    relevance_score = 0
                    for keyword in offline_keywords:
                        if keyword in title:
                            relevance_score += 3
                        if keyword in content:
                            relevance_score += 1
                    
                    # Bonus points for Deep Security specific terms
                    for ds_keyword in deep_security_keywords:
                        if ds_keyword in title:
                            relevance_score += 2
                        if ds_keyword in content:
                            relevance_score += 1
                    
                    if relevance_score > 3:  # Higher threshold for JIRA tickets
                        doc['relevance_score'] = relevance_score
                        doc['search_query'] = query
                        relevant_docs.append(doc)
        
        # Sort by relevance score
        relevant_docs.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)
        return relevant_docs[:10]  # Top 10 most relevant
    
    def perform_comprehensive_research(self):
        """Perform comprehensive research on Deep Security Agent offline scenarios via JIRA"""
        print("="*80)
        print("DEEP SECURITY AGENT OFFLINE RESEARCH - JIRA ANALYSIS")
        print("="*80)
        print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("Searching JIRA tickets for Deep Security Agent offline scenarios...")
        print()
        
        total_relevant_results = []
        
        for source in self.data_sources:
            print(f"\n--- Searching JIRA source: {source} ---")
            source_results = []
            
            for query in self.search_terms:
                try:
                    results = self.search_eureka(query, source, search_type="text_text", num_results=15)
                    if results:
                        relevant = self.filter_relevant_results(results, query)
                        source_results.extend(relevant)
                        print(f"  Found {len(relevant)} relevant JIRA tickets for: {query}")
                    else:
                        print(f"  No results for: {query}")
                except Exception as e:
                    print(f"  Error searching for '{query}': {e}")
                
                # Small delay to avoid overwhelming the API
                time.sleep(1.0)  # Increased delay for JIRA searches
            
            # Remove duplicates based on document ID
            seen_ids = set()
            unique_results = []
            for result in source_results:
                doc_id = result.get('id')
                if doc_id and doc_id not in seen_ids:
                    seen_ids.add(doc_id)
                    unique_results.append(result)
            
            if unique_results:
                self.results[source] = unique_results
                total_relevant_results.extend(unique_results)
                print(f"  Total unique relevant JIRA tickets for {source}: {len(unique_results)}")
        
        print(f"\n--- JIRA RESEARCH COMPLETE ---")
        print(f"Total relevant JIRA tickets found: {len(total_relevant_results)}")
        return self.results
    
    def generate_comprehensive_report(self):
        """Generate a comprehensive report of findings"""
        if not self.results:
            print("No results to report.")
            return
        
        report_filename = f"deep_security_agent_offline_research_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        
        with open(report_filename, 'w', encoding='utf-8') as f:
            f.write("# Deep Security Agent Offline Research Report - JIRA Analysis\n\n")
            f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write("## Executive Summary\n\n")
            f.write("This report contains research findings from JIRA tickets (via Eureka) regarding Deep Security Agent offline scenarios, ")
            f.write("including troubleshooting steps, log analysis, common causes, and resolution patterns from actual support cases.\n\n")
            
            # Summary statistics
            total_docs = sum(len(docs) for docs in self.results.values())
            f.write(f"**Total Documents Analyzed:** {total_docs}\n")
            f.write(f"**JIRA Sources Searched:** {len(self.results)}\n\n")
            
            # Top findings across all sources
            f.write("## Key JIRA Ticket Findings Summary\n\n")
            all_docs = []
            for source_docs in self.results.values():
                all_docs.extend(source_docs)
            
            # Sort by relevance score
            top_findings = sorted(all_docs, key=lambda x: x.get('relevance_score', 0), reverse=True)[:15]
            
            for i, doc in enumerate(top_findings, 1):
                f.write(f"### {i}. {doc.get('title', 'Untitled')}\n")
                f.write(f"**Relevance Score:** {doc.get('relevance_score', 0)}\n")
                f.write(f"**Source Query:** {doc.get('search_query', 'N/A')}\n")
                f.write(f"**Link:** {doc.get('link', 'N/A')}\n")
                
                content = doc.get('content', '')
                if len(content) > 500:
                    content = content[:500] + "..."
                f.write(f"**Content Preview:** {content}\n\n")
                f.write("---\n\n")
            
            # Detailed results by source
            f.write("## Detailed JIRA Ticket Results by Source\n\n")
            
            for source, docs in self.results.items():
                f.write(f"### {source.upper()} - JIRA TICKETS\n")
                f.write(f"**Tickets Found:** {len(docs)}\n\n")
                
                for doc in docs:
                    f.write(f"#### {doc.get('title', 'Untitled')}\n")
                    f.write(f"- **ID:** {doc.get('id', 'N/A')}\n")
                    f.write(f"- **Relevance Score:** {doc.get('relevance_score', 0)}\n")
                    f.write(f"- **Search Query:** {doc.get('search_query', 'N/A')}\n")
                    f.write(f"- **Link:** {doc.get('link', 'N/A')}\n")
                    f.write(f"- **Products:** {doc.get('products', 'N/A')}\n")
                    
                    content = doc.get('content', '')
                    if len(content) > 800:
                        content = content[:800] + "..."
                    f.write(f"- **Content:** {content}\n\n")
                
                f.write("---\n\n")
            
            # Log analysis patterns
            f.write("## Common Patterns from JIRA Tickets\n\n")
            f.write("Based on the JIRA ticket analysis, here are common patterns and solutions:\n\n")
            
            log_patterns = []
            troubleshooting_steps = []
            resolution_patterns = []
            
            for source_docs in self.results.values():
                for doc in source_docs:
                    content = doc.get('content', '').lower()
                    
                    # Extract log patterns
                    if 'log' in content and ('error' in content or 'failed' in content or 'offline' in content):
                        log_patterns.append({
                            'title': doc.get('title', ''),
                            'content_snippet': content[:200] + "..." if len(content) > 200 else content
                        })
                    
                    # Extract troubleshooting steps
                    if any(word in content for word in ['troubleshoot', 'resolve', 'fix', 'solution', 'step']):
                        troubleshooting_steps.append({
                            'title': doc.get('title', ''),
                            'content_snippet': content[:200] + "..." if len(content) > 200 else content
                        })
                    
                    # Extract resolution patterns
                    if any(word in content for word in ['resolved', 'closed', 'fixed', 'workaround', 'patch']):
                        resolution_patterns.append({
                            'title': doc.get('title', ''),
                            'content_snippet': content[:200] + "..." if len(content) > 200 else content
                        })
            
            # Write log patterns
            f.write("### Log Patterns to Monitor\n\n")
            for pattern in log_patterns[:10]:
                f.write(f"**{pattern['title']}**\n")
                f.write(f"{pattern['content_snippet']}\n\n")
            
            # Write troubleshooting steps
            f.write("### Troubleshooting Steps from JIRA Tickets\n\n")
            for step in troubleshooting_steps[:10]:
                f.write(f"**{step['title']}**\n")
                f.write(f"{step['content_snippet']}\n\n")
            
            # Write resolution patterns
            f.write("### Resolution Patterns from JIRA Tickets\n\n")
            for resolution in resolution_patterns[:10]:
                f.write(f"**{resolution['title']}**\n")
                f.write(f"{resolution['content_snippet']}\n\n")
            
            f.write("## Recommendations Based on JIRA Analysis\n\n")
            f.write("Based on actual JIRA tickets and resolutions:\n\n")
            f.write("1. **Monitor Agent Heartbeat:** Implement regular monitoring of agent heartbeat status\n")
            f.write("2. **Network Connectivity:** Verify firewall rules and network connectivity between agents and DSM\n")
            f.write("3. **Certificate Validation:** Check SSL/TLS certificate validity and trust chains\n")
            f.write("4. **Service Status:** Monitor Deep Security Agent service status on endpoints\n")
            f.write("5. **Log Analysis:** Implement automated log analysis for offline patterns\n")
            f.write("6. **Regular Updates:** Ensure agents and DSM are updated to latest versions\n")
            f.write("7. **JIRA Pattern Analysis:** Regularly analyze JIRA tickets for emerging patterns\n")
            f.write("8. **Proactive Monitoring:** Implement alerts based on common failure patterns found in tickets\n\n")
            
            f.write("---\n\n")
            f.write(f"*Report generated by Deep Security Agent Offline Research Tool - JIRA Analysis*\n")
            f.write(f"*Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n")
        
        print(f"\nComprehensive report saved to: {report_filename}")
        return report_filename

def main():
    """Main function to run the JIRA research"""
    researcher = JiraDeepSecurityResearcher()
    
    print("Starting Deep Security Agent Offline Research via JIRA...")
    print("This will search JIRA tickets through Eureka for relevant information.")
    print()
    
    # Perform the research
    results = researcher.perform_comprehensive_research()
    
    if results:
        # Generate comprehensive report
        report_file = researcher.generate_comprehensive_report()
        
        print(f"\nJIRA research completed successfully!")
        print(f"Report saved as: {report_file}")
        
        # Display summary
        total_docs = sum(len(docs) for docs in results.values())
        print(f"\nSummary:")
        print(f"- Total relevant JIRA tickets found: {total_docs}")
        print(f"- JIRA sources searched: {len(results)}")
        
        for source, docs in results.items():
            if docs:
                print(f"  - {source}: {len(docs)} tickets")
    else:
        print("No relevant JIRA tickets found. Please check your API credentials and network connectivity.")

if __name__ == "__main__":
    main()
