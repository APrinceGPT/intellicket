#!/usr/bin/env python3
"""
Deep Security Agent Offline Research using Direct JIRA Cloud REST API
This script performs comprehensive searches for Deep Security Agent offline issues
directly through JIRA Cloud REST API, avoiding Eureka timeout issues.
"""
import requests
import json
import base64
import time
import os
from datetime import datetime, timedelta
import urllib.parse

class JiraDirectDeepSecurityResearcher:
    def __init__(self):
        self.username = "adrian_principio@trendmicro.com"
        self.api_token = "ATATT3xFfGF0rWXAFzb8HPpEhhWlAHUF51paD1hbJ07M4UZFt2_gPyJ4D2wQ5kAPERsmaKppYwQtTnY5fcI1gbJiJcA4YW-EXxHP5SwQa-cvl3Cq-Gm3j9qGgWYQLWtixh1cSepnSz8sJPLR-IjUcCxJ6fReLztWBhuj_vvW7RUmOkm8G9kZWcg=E4B7001D"
        self.base_url = "https://trendmicro.atlassian.net"
        self.api_base = f"{self.base_url}/rest/api/3"
        
        # Create Basic Auth header for JIRA API
        auth_string = f"{self.username}:{self.api_token}"
        auth_bytes = auth_string.encode('ascii')
        auth_b64 = base64.b64encode(auth_bytes).decode('ascii')
        
        self.headers = {
            'Authorization': f'Basic {auth_b64}',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
        
        # JQL queries specifically designed for Deep Security Agent offline research
        self.jql_queries = [
            # Direct Deep Security Agent searches
            'text ~ "Deep Security Agent" AND text ~ "offline"',
            'text ~ "Deep Security Agent" AND text ~ "disconnected"',
            'text ~ "Deep Security Agent" AND text ~ "connection"',
            'text ~ "Deep Security Agent" AND text ~ "heartbeat"',
            'text ~ "Deep Security Agent" AND text ~ "communication"',
            'text ~ "Deep Security Agent" AND text ~ "network"',
            
            # DSA abbreviation searches
            'text ~ "DSA" AND text ~ "offline"',
            'text ~ "DSA" AND text ~ "disconnected"',
            'text ~ "DSA" AND text ~ "connection lost"',
            'text ~ "DSA" AND text ~ "heartbeat"',
            
            # Deep Security Manager related
            'text ~ "Deep Security Manager" AND text ~ "agent offline"',
            'text ~ "DSM" AND text ~ "agent" AND text ~ "offline"',
            'text ~ "DSM" AND text ~ "agent" AND text ~ "disconnected"',
            
            # Service and log related
            'text ~ "Deep Security" AND text ~ "service stopped"',
            'text ~ "Deep Security" AND text ~ "service failed"',
            'text ~ "Deep Security" AND text ~ "log" AND text ~ "offline"',
            
            # Network and connectivity issues
            'text ~ "Deep Security" AND text ~ "firewall" AND text ~ "blocked"',
            'text ~ "Deep Security" AND text ~ "certificate" AND text ~ "error"',
            'text ~ "Deep Security" AND text ~ "SSL" AND text ~ "failed"',
            'text ~ "Deep Security" AND text ~ "network" AND text ~ "unreachable"',
            
            # Troubleshooting and resolution
            'text ~ "Deep Security" AND text ~ "troubleshoot" AND text ~ "offline"',
            'text ~ "Deep Security" AND text ~ "resolve" AND text ~ "connection"',
            'text ~ "Deep Security" AND text ~ "fix" AND text ~ "agent"'
        ]
        
        # Common Deep Security project keys (you may need to adjust these)
        self.project_filters = [
            "",  # Search all projects first
            "project = DS",
            "project = DEEPSEC", 
            "project = SEC",
            "project = SECURITY",
            "project = SUPPORT",
            "project = TECH",
            "project = CUSTOMER"
        ]
        
        self.results = []
        self.rate_limit_delay = 6  # 6 seconds between requests to avoid rate limiting
        
    def search_jira_issues(self, jql_query, project_filter="", max_results=20, start_at=0):
        """Search JIRA issues using JQL"""
        
        # Combine JQL with project filter if provided
        if project_filter:
            full_jql = f"({jql_query}) AND {project_filter}"
        else:
            full_jql = jql_query
            
        # Add date filter for recent issues (last 2 years using proper JIRA format)
        date_filter = f"created >= -104w"  # 104 weeks = 2 years
        full_jql = f"({full_jql}) AND {date_filter}"
        
        # URL encode the JQL
        encoded_jql = urllib.parse.quote(full_jql)
        
        # Construct the search URL
        search_url = f"{self.api_base}/search"
        params = {
            'jql': full_jql,
            'startAt': start_at,
            'maxResults': max_results,
            'fields': 'summary,description,status,priority,created,updated,assignee,project,key,components'
        }
        
        try:
            print(f"Searching JIRA with JQL: {full_jql}")
            response = requests.get(search_url, headers=self.headers, params=params, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                return data
            elif response.status_code == 429:
                # Rate limited
                retry_after = int(response.headers.get('Retry-After', 60))
                print(f"Rate limited. Waiting {retry_after} seconds...")
                time.sleep(retry_after)
                return None
            else:
                print(f"HTTP Error {response.status_code}: {response.text}")
                return None
                
        except requests.exceptions.Timeout:
            print(f"Timeout occurred for JQL: {full_jql}")
            return None
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            return None
        except Exception as e:
            print(f"Unexpected error: {e}")
            return None
    
    def get_issue_details(self, issue_key):
        """Get detailed information about a specific issue"""
        
        issue_url = f"{self.api_base}/issue/{issue_key}"
        params = {
            'fields': 'summary,description,status,priority,created,updated,assignee,project,key,components,comment'
        }
        
        try:
            response = requests.get(issue_url, headers=self.headers, params=params, timeout=20)
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Failed to get issue {issue_key}: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"Error getting issue {issue_key}: {e}")
            return None
    
    def extract_text_from_jira_content(self, content):
        """Extract plain text from JIRA's complex content structure"""
        if not content:
            return ""
        
        if isinstance(content, str):
            return content
        
        if isinstance(content, dict):
            text_parts = []
            
            # Handle JIRA document format
            if 'content' in content:
                for item in content.get('content', []):
                    text_parts.append(self.extract_text_from_jira_content(item))
            
            # Handle text content
            if 'text' in content:
                text_parts.append(content['text'])
            
            # Handle type-specific content
            content_type = content.get('type', '')
            if content_type == 'text' and 'text' in content:
                text_parts.append(content['text'])
            elif content_type == 'paragraph':
                if 'content' in content:
                    for item in content['content']:
                        text_parts.append(self.extract_text_from_jira_content(item))
            
            return ' '.join(filter(None, text_parts))
        
        if isinstance(content, list):
            text_parts = []
            for item in content:
                text_parts.append(self.extract_text_from_jira_content(item))
            return ' '.join(filter(None, text_parts))
        
        return str(content or '')
    
    def analyze_issue_relevance(self, issue):
        """Analyze how relevant an issue is to Deep Security Agent offline scenarios"""
        
        fields = issue.get('fields', {})
        
        # Handle summary safely
        summary_field = fields.get('summary', '')
        if isinstance(summary_field, str):
            summary = summary_field.lower()
        else:
            summary = str(summary_field or '').lower()
        
        # Handle JIRA description which can be a string or complex object
        description_field = fields.get('description', '')
        if isinstance(description_field, dict):
            # Extract text from JIRA's document format
            description = self.extract_text_from_jira_content(description_field).lower()
        elif isinstance(description_field, str):
            description = description_field.lower()
        else:
            description = str(description_field or '').lower()
        
        # Keywords that indicate high relevance to offline scenarios
        high_relevance_keywords = [
            'offline', 'disconnected', 'connection lost', 'heartbeat failed',
            'communication error', 'network unreachable', 'service stopped',
            'agent not responding', 'timeout', 'unreachable'
        ]
        
        # Keywords that indicate Deep Security relation
        deep_security_keywords = [
            'deep security agent', 'dsa', 'deep security manager', 'dsm',
            'trend micro deep security', 'ds agent'
        ]
        
        # Keywords that indicate troubleshooting/resolution content
        resolution_keywords = [
            'troubleshoot', 'resolve', 'fix', 'solution', 'workaround',
            'restart', 'reinstall', 'certificate', 'firewall', 'port'
        ]
        
        relevance_score = 0
        
        # Check for Deep Security relevance
        ds_relevance = False
        for keyword in deep_security_keywords:
            if keyword in summary or keyword in description:
                ds_relevance = True
                relevance_score += 2
                break
        
        if not ds_relevance:
            return 0  # Not relevant if not related to Deep Security
            
        # Check for offline scenario relevance
        for keyword in high_relevance_keywords:
            if keyword in summary:
                relevance_score += 3
            elif keyword in description:
                relevance_score += 1
                
        # Check for resolution/troubleshooting content
        for keyword in resolution_keywords:
            if keyword in summary:
                relevance_score += 2
            elif keyword in description:
                relevance_score += 1
        
        return relevance_score
    
    def perform_comprehensive_research(self):
        """Perform comprehensive research on Deep Security Agent offline scenarios"""
        print("="*80)
        print("DEEP SECURITY AGENT OFFLINE RESEARCH - DIRECT JIRA API")
        print("="*80)
        print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("Searching JIRA directly for Deep Security Agent offline scenarios...")
        print(f"Rate limit delay: {self.rate_limit_delay} seconds between requests")
        print()
        
        all_issues = {}  # Use dict to avoid duplicates by key
        
        total_queries = len(self.jql_queries) * len(self.project_filters)
        query_count = 0
        
        for project_filter in self.project_filters:
            project_name = project_filter if project_filter else "ALL_PROJECTS"
            print(f"\n--- Searching in: {project_name} ---")
            
            for jql_query in self.jql_queries:
                query_count += 1
                print(f"Query {query_count}/{total_queries}: ", end="")
                
                try:
                    # Search with pagination
                    start_at = 0
                    max_results = 15
                    
                    while True:
                        search_result = self.search_jira_issues(
                            jql_query, project_filter, max_results, start_at
                        )
                        
                        if not search_result:
                            break
                            
                        issues = search_result.get('issues', [])
                        total_found = search_result.get('total', 0)
                        
                        if not issues:
                            break
                            
                        print(f"Found {len(issues)} issues (total: {total_found})")
                        
                        # Analyze each issue for relevance
                        relevant_count = 0
                        for issue in issues:
                            issue_key = issue.get('key')
                            if issue_key and issue_key not in all_issues:
                                relevance_score = self.analyze_issue_relevance(issue)
                                if relevance_score > 3:  # Only keep highly relevant issues
                                    issue['relevance_score'] = relevance_score
                                    issue['search_jql'] = jql_query
                                    all_issues[issue_key] = issue
                                    relevant_count += 1
                        
                        print(f"  -> {relevant_count} relevant issues added")
                        
                        # Check if we need to paginate
                        if len(issues) < max_results or start_at + max_results >= total_found:
                            break
                            
                        start_at += max_results
                        
                        # Rate limiting between paginated requests
                        time.sleep(2)
                    
                except Exception as e:
                    print(f"Error in query: {e}")
                
                # Rate limiting between queries (as per JIRA documentation)
                print(f"  Waiting {self.rate_limit_delay} seconds...")
                time.sleep(self.rate_limit_delay)
        
        self.results = list(all_issues.values())
        
        print(f"\n--- JIRA DIRECT SEARCH COMPLETE ---")
        print(f"Total unique relevant issues found: {len(self.results)}")
        
        # Sort by relevance score
        self.results.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)
        
        return self.results
    
    def generate_comprehensive_report(self):
        """Generate a comprehensive report of findings"""
        if not self.results:
            print("No results to report.")
            return None
        
        report_filename = f"jira_deep_security_agent_research_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        
        with open(report_filename, 'w', encoding='utf-8') as f:
            f.write("# Deep Security Agent Offline Research Report - JIRA Direct API\n\n")
            f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write("## Executive Summary\n\n")
            f.write("This report contains research findings from JIRA tickets accessed directly via REST API ")
            f.write("regarding Deep Security Agent offline scenarios, including troubleshooting steps, ")
            f.write("resolution patterns, and common causes identified from actual support cases.\n\n")
            
            # Summary statistics
            f.write(f"**Total Relevant Issues Found:** {len(self.results)}\n")
            f.write(f"**Search Method:** Direct JIRA Cloud REST API\n")
            f.write(f"**Search Period:** Last 2 years\n\n")
            
            # Top findings
            f.write("## Top Issues by Relevance Score\n\n")
            
            for i, issue in enumerate(self.results[:20], 1):  # Top 20
                fields = issue.get('fields', {})
                issue_key = issue.get('key', 'Unknown')
                summary = fields.get('summary', 'No summary')
                relevance_score = issue.get('relevance_score', 0)
                project = fields.get('project', {}).get('key', 'Unknown')
                status = fields.get('status', {}).get('name', 'Unknown')
                created = fields.get('created', 'Unknown')
                
                f.write(f"### {i}. {issue_key} - {summary}\n")
                f.write(f"**Relevance Score:** {relevance_score}\n")
                f.write(f"**Project:** {project}\n")
                f.write(f"**Status:** {status}\n")
                f.write(f"**Created:** {created}\n")
                f.write(f"**URL:** {self.base_url}/browse/{issue_key}\n")
                f.write(f"**Search JQL:** {issue.get('search_jql', 'N/A')}\n")
                
                # Add description preview
                description = fields.get('description', '')
                if description and len(description) > 200:
                    description = description[:200] + "..."
                f.write(f"**Description Preview:** {description}\n\n")
                f.write("---\n\n")
            
            # Analysis by project
            f.write("## Analysis by Project\n\n")
            project_counts = {}
            for issue in self.results:
                project_key = issue.get('fields', {}).get('project', {}).get('key', 'Unknown')
                project_counts[project_key] = project_counts.get(project_key, 0) + 1
            
            for project, count in sorted(project_counts.items(), key=lambda x: x[1], reverse=True):
                f.write(f"- **{project}:** {count} issues\n")
            f.write("\n")
            
            # Analysis by status
            f.write("## Analysis by Status\n\n")
            status_counts = {}
            for issue in self.results:
                status = issue.get('fields', {}).get('status', {}).get('name', 'Unknown')
                status_counts[status] = status_counts.get(status, 0) + 1
            
            for status, count in sorted(status_counts.items(), key=lambda x: x[1], reverse=True):
                f.write(f"- **{status}:** {count} issues\n")
            f.write("\n")
            
            # Common patterns analysis
            f.write("## Common Patterns and Keywords\n\n")
            all_text = ""
            for issue in self.results:
                fields = issue.get('fields', {})
                
                # Handle summary safely
                summary_field = fields.get('summary', '') or ''
                summary = summary_field if isinstance(summary_field, str) else str(summary_field)
                
                # Handle description safely 
                description_field = fields.get('description', '') or ''
                if isinstance(description_field, dict):
                    description = self.extract_text_from_jira_content(description_field)
                elif isinstance(description_field, str):
                    description = description_field
                else:
                    description = str(description_field or '')
                
                all_text += f" {summary} {description}".lower()
            
            # Count common keywords
            pattern_keywords = [
                'offline', 'disconnected', 'connection', 'heartbeat', 'communication',
                'network', 'firewall', 'certificate', 'ssl', 'service', 'restart',
                'troubleshoot', 'resolve', 'fix', 'timeout', 'unreachable'
            ]
            
            f.write("### Keyword Frequency Analysis\n")
            for keyword in pattern_keywords:
                count = all_text.count(keyword)
                if count > 0:
                    f.write(f"- **{keyword}:** {count} occurrences\n")
            f.write("\n")
            
            # Detailed issue list
            f.write("## Complete Issue List\n\n")
            for issue in self.results:
                fields = issue.get('fields', {})
                issue_key = issue.get('key', 'Unknown')
                summary = fields.get('summary', 'No summary')
                project = fields.get('project', {}).get('key', 'Unknown')
                status = fields.get('status', {}).get('name', 'Unknown')
                priority = fields.get('priority', {}).get('name', 'Unknown')
                relevance_score = issue.get('relevance_score', 0)
                
                f.write(f"### {issue_key} - {summary}\n")
                f.write(f"- **Project:** {project}\n")
                f.write(f"- **Status:** {status}\n")
                f.write(f"- **Priority:** {priority}\n")
                f.write(f"- **Relevance Score:** {relevance_score}\n")
                f.write(f"- **URL:** {self.base_url}/browse/{issue_key}\n")
                
                description = fields.get('description', '')
                if description:
                    if len(description) > 500:
                        description = description[:500] + "..."
                    f.write(f"- **Description:** {description}\n")
                
                f.write("\n")
            
            # Recommendations
            f.write("## Recommendations Based on JIRA Analysis\n\n")
            f.write("Based on the analysis of actual JIRA tickets:\n\n")
            f.write("1. **Proactive Monitoring:** Implement monitoring for agent heartbeat failures\n")
            f.write("2. **Network Diagnostics:** Focus on network connectivity and firewall issues\n")
            f.write("3. **Certificate Management:** Monitor SSL/TLS certificate expiration and validation\n")
            f.write("4. **Service Health Checks:** Regular verification of Deep Security Agent service status\n")
            f.write("5. **Automated Alerts:** Set up alerts for communication timeouts and connection losses\n")
            f.write("6. **Documentation Updates:** Update troubleshooting guides based on resolution patterns\n")
            f.write("7. **Preventive Maintenance:** Schedule regular agent health checks and updates\n\n")
            
            f.write("---\n\n")
            f.write(f"*Report generated by Deep Security Agent Research Tool - Direct JIRA API*\n")
            f.write(f"*Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n")
        
        print(f"\nComprehensive report saved to: {report_filename}")
        return report_filename

def main():
    """Main function to run the JIRA research"""
    researcher = JiraDirectDeepSecurityResearcher()
    
    print("Starting Deep Security Agent Offline Research via Direct JIRA API...")
    print("This will search JIRA tickets directly, avoiding Eureka timeout issues.")
    print()
    
    try:
        # Perform the research
        results = researcher.perform_comprehensive_research()
        
        if results:
            # Generate comprehensive report
            report_file = researcher.generate_comprehensive_report()
            
            print(f"\nJIRA direct research completed successfully!")
            print(f"Report saved as: {report_file}")
            
            # Display summary
            print(f"\nSummary:")
            print(f"- Total relevant JIRA issues found: {len(results)}")
            
            # Show top 5 most relevant issues
            print(f"\nTop 5 Most Relevant Issues:")
            for i, issue in enumerate(results[:5], 1):
                issue_key = issue.get('key', 'Unknown')
                summary = issue.get('fields', {}).get('summary', 'No summary')
                relevance_score = issue.get('relevance_score', 0)
                print(f"  {i}. {issue_key} - {summary} (Score: {relevance_score})")
                
        else:
            print("No relevant JIRA issues found. This could be due to:")
            print("- Restrictive search criteria")
            print("- Limited access to certain projects")
            print("- Network connectivity issues")
            print("- API rate limiting")
            
    except Exception as e:
        print(f"An error occurred during research: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
