# -*- coding: utf-8 -*-
"""
Dynamic RAG System for Deep Security Log Analysis
Creates intelligent, context-aware prompts based on log content and external knowledge
"""

import os
import re
import json
import requests
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path

class DynamicRAGSystem:
    """Dynamic RAG system that creates intelligent prompts based on log content"""
    
    def __init__(self, pdf_dir: str = "pdf", config_file: str = "config.py"):
        self.pdf_dir = pdf_dir
        self.config_file = config_file
        self.load_config()
        
        # Initialize PDF Knowledge Integration
        try:
            from pdf_knowledge_integrator import PDFKnowledgeIntegrator
            self.pdf_integrator = PDFKnowledgeIntegrator(pdf_dir=pdf_dir)
            self.pdf_knowledge_available = True
            print("✅ Dynamic RAG system initialized with proprietary PDF knowledge base")
        except Exception as e:
            print(f"⚠️ PDF knowledge integration failed: {e}")
            self.pdf_knowledge_available = False
            self.pdf_integrator = None
        
        # Try legacy RAG system as fallback
        try:
            from rag_system import CybersecurityRAG
            self.rag_system = CybersecurityRAG(pdf_dir=pdf_dir)
            self.rag_available = True
            print("✅ Legacy RAG system also available for additional knowledge")
        except ImportError:
            if not self.pdf_knowledge_available:
                print("⚠️ No knowledge systems available - Dynamic RAG will work with Claude AI only")
            self.rag_available = False
            self.rag_system = None
        except Exception as e:
            self.rag_available = False
            self.rag_system = None
    
    def load_config(self):
        """Load configuration including API key for Claude/Anthropic"""
        try:
            from config import Config
            self.api_key = Config.OPENAI_API_KEY
            self.base_url = Config.OPENAI_BASE_URL
            self.model = Config.OPENAI_MODEL
            
            if self.api_key and self.base_url:
                self.ai_available = True
                print(f"✅ Claude API configured: {self.model}")
                print(f"🔗 Base URL: {self.base_url}")
            else:
                self.ai_available = False
                print("⚠️ Claude API key or base URL not found - dynamic prompting limited")
                
        except Exception as e:
            print(f"⚠️ Config loading failed: {e}")
            self.ai_available = False
    
    def extract_log_context(self, log_content: str) -> Dict[str, Any]:
        """Extract meaningful context from log content"""
        
        context = {
            'components': set(),
            'error_types': set(),
            'severity_levels': set(),
            'time_patterns': [],
            'ip_addresses': set(),
            'file_paths': set(),
            'service_names': set(),
            'main_issues': []
        }
        
        # Extract components
        component_patterns = {
            'amsp': r'amsp|anti-malware|scan.*engine',
            'dsm': r'dsm|deep.*security.*manager',
            'agent': r'ds.*agent|deep.*security.*agent',
            'notifier': r'notifier|notification.*service',
            'web_reputation': r'web.*reputation|trendx',
            'intrusion_prevention': r'ips|intrusion.*prevention',
            'integrity_monitoring': r'fim|file.*integrity|integrity.*monitoring'
        }
        
        for component, pattern in component_patterns.items():
            if re.search(pattern, log_content, re.IGNORECASE):
                context['components'].add(component)
        
        # Extract error types
        error_patterns = {
            'connection_error': r'connection.*(?:failed|timeout|refused|lost)',
            'authentication_error': r'authentication.*failed|auth.*error',
            'permission_error': r'permission.*denied|access.*denied',
            'service_error': r'service.*(?:failed|stopped|crashed)',
            'driver_error': r'driver.*(?:failed|load.*error|crash)',
            'memory_error': r'out.*of.*memory|memory.*exhausted',
            'disk_error': r'disk.*(?:full|error|fail)',
            'network_error': r'network.*(?:unreachable|timeout|error)'
        }
        
        for error_type, pattern in error_patterns.items():
            if re.search(pattern, log_content, re.IGNORECASE):
                context['error_types'].add(error_type)
        
        # Extract severity levels
        severity_patterns = r'\b(critical|error|warning|info|debug)\b'
        severities = re.findall(severity_patterns, log_content, re.IGNORECASE)
        context['severity_levels'].update([s.lower() for s in severities])
        
        # Extract IP addresses
        ip_pattern = r'\b(?:\d{1,3}\.){3}\d{1,3}\b'
        context['ip_addresses'].update(re.findall(ip_pattern, log_content))
        
        # Extract file paths
        path_patterns = [
            r'[A-Za-z]:\\(?:[^\\/:*?"<>|\r\n]+\\)*[^\\/:*?"<>|\r\n]*',  # Windows paths
            r'/(?:[^/\s]+/)*[^/\s]*'  # Unix paths
        ]
        for pattern in path_patterns:
            context['file_paths'].update(re.findall(pattern, log_content))
        
        # Extract service names
        service_pattern = r'service[:\s]+([A-Za-z][A-Za-z0-9_]+)'
        context['service_names'].update(re.findall(service_pattern, log_content, re.IGNORECASE))
        
        # Extract main issues (lines with error/critical)
        lines = log_content.split('\n')
        for line in lines:
            if re.search(r'\b(critical|error)\b', line, re.IGNORECASE):
                context['main_issues'].append(line.strip())
        
        # Convert sets to lists for JSON serialization
        for key, value in context.items():
            if isinstance(value, set):
                context[key] = list(value)
        
        return context
    
    def generate_dynamic_queries(self, log_context: Dict[str, Any], ml_insights: Optional[Dict[str, Any]] = None) -> List[str]:
        """Generate dynamic queries based on log content analysis and ML insights"""
        
        queries = []
        
        # Component-specific queries
        for component in log_context.get('components', []):
            queries.append(f"Deep Security {component} troubleshooting guide")
            queries.append(f"{component} performance optimization best practices")
        
        # Error-specific queries
        for error_type in log_context.get('error_types', []):
            queries.append(f"Deep Security {error_type.replace('_', ' ')} resolution")
        
        # Severity-based queries
        if 'critical' in log_context.get('severity_levels', []):
            queries.append("Deep Security critical issues emergency response")
        if 'error' in log_context.get('severity_levels', []):
            queries.append("Deep Security error troubleshooting procedures")
        
        # ML-Enhanced Queries (MAJOR ADDITION)
        if ml_insights:
            # Anomaly-driven queries
            anomaly_analysis = ml_insights.get('anomaly_analysis', {})
            if anomaly_analysis.get('anomaly_count', 0) > 0:
                queries.append("Deep Security anomaly detection troubleshooting unusual behavior patterns")
                queries.append("resolving anomalous log patterns and irregular system behavior")
            
            # Component health queries
            ds_analysis = ml_insights.get('ds_agent_analysis', {})
            if ds_analysis:
                component_health = ds_analysis.get('component_health', {})
                for component, health in component_health.items():
                    health_score = health.get('health_score', 100)
                    if health_score < 80:
                        queries.append(f"{component} component degradation health recovery procedures")
                        queries.append(f"improving {component} performance and stability")
            
            # Severity-based ML queries
            severity_analysis = ml_insights.get('severity_analysis', {})
            if severity_analysis.get('predictions'):
                predictions = severity_analysis['predictions']
                critical_count = predictions.count('CRITICAL')
                if critical_count > 0:
                    queries.append("Deep Security critical severity machine learning detected issues")
        
        # Service-specific queries
        for service in log_context.get('service_names', []):
            queries.append(f"Deep Security {service} service configuration")
        
        # Default queries if none found
        if not queries:
            queries.extend([
                "Deep Security agent troubleshooting",
                "Deep Security performance optimization",
                "Deep Security configuration best practices"
            ])
        
        return queries[:8]  # Limit to 8 queries
    
    def retrieve_contextual_knowledge(self, log_context: Dict[str, Any], ml_insights: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Retrieve relevant knowledge based on log context from all available sources"""
        
        dynamic_queries = self.generate_dynamic_queries(log_context, ml_insights)
        all_knowledge = []
        
        print(f"🔍 Generating {len(dynamic_queries)} ML-enhanced dynamic queries based on log content...")
        
        # First priority: Search proprietary PDF knowledge
        if self.pdf_knowledge_available and self.pdf_integrator:
            print("📖 Searching proprietary Deep Security documentation...")
            pdf_knowledge_count = 0
            
            for query in dynamic_queries:
                # Determine component for targeted search
                component = None
                for comp in log_context.get('components', []):
                    if comp in query.lower():
                        component = comp
                        break
                
                pdf_results = self.pdf_integrator.search_knowledge(query, component, max_results=2)
                
                # Convert PDF results to standard format
                for result in pdf_results:
                    formatted_result = {
                        'id': f"pdf_{result['source_file']}_{result['page_number']}",
                        'content': result['content'],
                        'metadata': {
                            'title': f"{result['document_title']} - {result['section_title']}",
                            'source': 'Proprietary Deep Security Documentation',
                            'document': result['document_title'],
                            'section': result['section_title'],
                            'page': result['page_number'],
                            'section_type': result['section_type'],
                            'source_file': result['source_file']
                        },
                        'relevance_score': result['relevance_score']
                    }
                    all_knowledge.append(formatted_result)
                    pdf_knowledge_count += 1
                
                print(f"  📚 '{query[:50]}...' → {len(pdf_results)} PDF sections")
            
            print(f"✅ Retrieved {pdf_knowledge_count} proprietary knowledge sections")
        
        # Second priority: Legacy RAG system (if available)
        if self.rag_available and self.rag_system:
            print("📖 Searching legacy knowledge base...")
            legacy_knowledge_count = 0
            
            for query in dynamic_queries:
                knowledge = self.rag_system.retrieve_relevant_knowledge(query, max_results=2)
                all_knowledge.extend(knowledge)
                legacy_knowledge_count += len(knowledge)
                print(f"  📚 '{query[:50]}...' → {len(knowledge)} legacy documents")
            
            print(f"✅ Retrieved {legacy_knowledge_count} legacy knowledge sources")
        
        # If no knowledge sources available
        if not self.pdf_knowledge_available and not self.rag_available:
            print("⚠️ No knowledge bases available - Dynamic RAG will rely on Claude AI intelligence only")
            return []
        
        # Remove duplicates and sort by relevance
        unique_knowledge = {}
        for doc in all_knowledge:
            doc_id = doc['id']
            if doc_id not in unique_knowledge or doc['relevance_score'] > unique_knowledge[doc_id]['relevance_score']:
                unique_knowledge[doc_id] = doc
        
        sorted_knowledge = sorted(unique_knowledge.values(), 
                                key=lambda x: x['relevance_score'], reverse=True)
        
        # Prioritize proprietary PDF knowledge
        pdf_knowledge = [k for k in sorted_knowledge if k['id'].startswith('pdf_')]
        other_knowledge = [k for k in sorted_knowledge if not k['id'].startswith('pdf_')]
        
        # Return top results with PDF knowledge prioritized
        final_knowledge = pdf_knowledge[:4] + other_knowledge[:2]  # 4 PDF + 2 others max
        
        return final_knowledge
    
    def create_dynamic_prompt(self, log_context: Dict[str, Any], 
                            knowledge_sources: List[Dict[str, Any]], 
                            log_content: str,
                            ml_insights: Optional[Dict[str, Any]] = None) -> str:
        """Create a dynamic, intelligent prompt based on log analysis and knowledge"""
        
        # Analyze log severity and scope
        total_issues = len(log_context.get('main_issues', []))
        components_affected = len(log_context.get('components', []))
        severity_levels = log_context.get('severity_levels', [])
        
        # Determine analysis focus (enhanced with ML insights)
        if 'critical' in severity_levels:
            analysis_priority = "EMERGENCY"
        elif 'error' in severity_levels and total_issues > 10:
            analysis_priority = "HIGH"
        elif components_affected > 2:
            analysis_priority = "MEDIUM"
        else:
            analysis_priority = "STANDARD"
        
        # Enhance priority with ML insights
        if ml_insights:
            anomaly_analysis = ml_insights.get('anomaly_analysis', {})
            if anomaly_analysis.get('anomaly_count', 0) > 0:
                anomaly_rate = anomaly_analysis.get('anomaly_score', 0)
                if anomaly_rate > 15:  # High anomaly rate
                    analysis_priority = "EMERGENCY" if analysis_priority != "EMERGENCY" else analysis_priority
        
        # Create concise dynamic prompt for better API performance
        prompt = f"""# Deep Security Log Analysis - {analysis_priority} Priority

## Context
- Components: {', '.join(log_context.get('components', ['Unknown']))}
- Error Types: {', '.join(log_context.get('error_types', ['General']))}
- Severity: {', '.join(severity_levels) if severity_levels else 'Mixed'}
- Issues Found: {total_issues}

## Critical Issues
"""
        
        # Add top 3 critical issues
        for i, issue in enumerate(log_context.get('main_issues', [])[:3], 1):
            prompt += f"{i}. {issue[:80]}...\n"

        # Add ML Intelligence Section (MAJOR ENHANCEMENT)
        if ml_insights:
            prompt += f"\n## 🤖 Machine Learning Intelligence\n"
            
            # Anomaly detection insights
            anomaly_analysis = ml_insights.get('anomaly_analysis', {})
            if anomaly_analysis.get('anomaly_count', 0) > 0:
                anomaly_count = anomaly_analysis['anomaly_count']
                anomaly_rate = anomaly_analysis.get('anomaly_score', 0)
                prompt += f"- **Anomalies Detected**: {anomaly_count} unusual patterns ({anomaly_rate:.1f}% anomaly rate)\n"
            
            # Component health analysis
            ds_analysis = ml_insights.get('ds_agent_analysis', {})
            if ds_analysis:
                component_health = ds_analysis.get('component_health', {})
                if component_health:
                    prompt += "- **Component Health Scores**:\n"
                    for component, health in component_health.items():
                        health_score = health.get('health_score', 100)
                        status_icon = "🔴" if health_score < 70 else "🟡" if health_score < 90 else "🟢"
                        prompt += f"  - {component}: {status_icon} {health_score:.1f}%\n"
            
            # Severity analysis from ML
            severity_analysis = ml_insights.get('severity_analysis', {})
            if severity_analysis.get('predictions'):
                predictions = severity_analysis['predictions']
                critical_count = predictions.count('CRITICAL')
                high_count = predictions.count('HIGH')
                if critical_count > 0 or high_count > 0:
                    prompt += f"- **ML Severity Classification**: {critical_count} Critical, {high_count} High priority\n"
        
        # Add expert knowledge (top 3 sources only for conciseness)
        if knowledge_sources:
            prompt += f"\n## Expert Knowledge (PDF Sources)\n"
            for i, knowledge in enumerate(knowledge_sources[:3], 1):
                title = knowledge['metadata']['title']
                content = knowledge['content'][:200]  # Limit content for API efficiency
                relevance = int(knowledge['relevance_score'] * 100)
                
                prompt += f"**{i}. {title}** ({relevance}% relevant)\n{content}...\n\n"
        
        # Analysis request (enhanced with ML context)
        ml_context = ""
        if ml_insights:
            ml_context = "Use the ML intelligence above to prioritize issues and focus on components with poor health scores. "
        
        prompt += f"""
## Analysis Request
{ml_context}Provide a {analysis_priority.lower()}-priority analysis with:

1. **Root Cause**: Identify the primary cause of each issue using ML insights
2. **Immediate Actions**: Next 15 minutes (critical items only)
3. **Resolution Steps**: Detailed troubleshooting for each component with health scores
4. **Prevention**: Steps to avoid future occurrences based on anomaly patterns

Focus on actionable guidance for Deep Security components: {', '.join(log_context.get('components', []))}.
Prioritize {analysis_priority.lower()}-level issues requiring immediate attention.
"""
        
        return prompt
    
    def process_log_with_dynamic_rag(self, log_content: str, 
                                   ml_insights: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Process log content with dynamic RAG analysis"""
        
        print("🧠 Starting Dynamic RAG Analysis...")
        
        # Step 1: Extract log context
        log_context = self.extract_log_context(log_content)
        print(f"📊 Extracted context: {len(log_context['components'])} components, {len(log_context['error_types'])} error types")
        
        # Step 2: Retrieve contextual knowledge (now with ML insights!)
        knowledge_sources = self.retrieve_contextual_knowledge(log_context, ml_insights)
        print(f"📚 Retrieved {len(knowledge_sources)} relevant knowledge sources using ML insights")
        
        # Step 3: Create dynamic prompt (now with ML insights!)
        dynamic_prompt = self.create_dynamic_prompt(log_context, knowledge_sources, log_content, ml_insights)
        print(f"🎯 Generated ML-enhanced dynamic prompt ({len(dynamic_prompt)} characters)")
        
        # Step 4: Generate AI response if available
        ai_response = None
        if self.ai_available:
            try:
                print("🤖 Generating Claude AI response with dynamic prompt...")
                
                # Prepare request for Claude API
                headers = {
                    'Authorization': f'Bearer {self.api_key}',
                    'Content-Type': 'application/json'
                }
                
                # Claude API request format with optimized settings
                payload = {
                    'model': self.model,
                    'messages': [
                        {
                            'role': 'user', 
                            'content': dynamic_prompt[:6000]  # Limit prompt size to prevent timeouts
                        }
                    ],
                    'max_tokens': 3000,  # Reduced for faster response
                    'temperature': 0.2   # Lower temperature for more focused responses
                }
                
                # Make API request with longer timeout and better error handling
                try:
                    response = requests.post(
                        f"{self.base_url.rstrip('/')}/chat/completions",
                        headers=headers,
                        json=payload,
                        timeout=120  # Increased timeout to 2 minutes
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        ai_response = result['choices'][0]['message']['content']
                        print(f"✅ Claude AI response generated ({len(ai_response)} characters)")
                    else:
                        print(f"⚠️ Claude API error: {response.status_code} - {response.text[:200]}")
                        ai_response = f"Claude API response failed (HTTP {response.status_code}). Please use the dynamic prompt below for manual analysis."
                        
                except requests.exceptions.Timeout:
                    print("⚠️ Claude API request timed out after 2 minutes")
                    ai_response = "Claude API request timed out. The dynamic prompt below contains comprehensive analysis for manual review."
                    
                except requests.exceptions.ConnectionError as e:
                    print(f"⚠️ Claude API connection error: {str(e)[:100]}")
                    ai_response = "Claude API connection failed. Please use the dynamic prompt below for manual analysis."
                    
                except requests.exceptions.RequestException as e:
                    print(f"⚠️ Claude API request error: {str(e)[:100]}")
                    ai_response = "Claude API request failed. Please use the dynamic prompt below for manual analysis."
                    
            except Exception as e:
                print(f"⚠️ Claude AI response generation failed: {e}")
                ai_response = "Claude AI response generation unavailable. Please use the dynamic prompt below for manual analysis."
        
        return {
            'log_context': log_context,
            'knowledge_sources': knowledge_sources,
            'dynamic_prompt': dynamic_prompt,
            'ai_response': ai_response,
            'analysis_metadata': {
                'components_analyzed': len(log_context['components']),
                'error_types_found': len(log_context['error_types']),
                'knowledge_sources_used': len(knowledge_sources),
                'prompt_length': len(dynamic_prompt),
                'ai_available': self.ai_available,
                'ml_enhanced': bool(ml_insights),
                'ml_insights_used': len(ml_insights.keys()) if ml_insights else 0,
                'timestamp': datetime.now().isoformat()
            }
        }

def apply_dynamic_rag_to_analysis(log_analysis: Dict[str, Any], 
                                log_content: str = "") -> Dict[str, Any]:
    """Apply dynamic RAG analysis to log analysis results"""
    
    try:
        dynamic_rag = DynamicRAGSystem()
        
        # Get ML insights if available
        ml_insights = log_analysis.get('ml_insights')
        
        # Process with dynamic RAG
        dynamic_results = dynamic_rag.process_log_with_dynamic_rag(log_content, ml_insights)
        
        # Add dynamic RAG results to analysis
        log_analysis['dynamic_rag_analysis'] = dynamic_results
        
        # Enhance recommendations with knowledge-based insights
        if dynamic_results['knowledge_sources']:
            knowledge_recommendations = []
            for knowledge in dynamic_results['knowledge_sources'][:3]:
                title = knowledge['metadata']['title']
                relevance = int(knowledge['relevance_score'] * 100)
                knowledge_recommendations.append(f"📚 **{title}** ({relevance}% relevant): Apply expert guidance")
            
            if 'recommendations' not in log_analysis:
                log_analysis['recommendations'] = []
            log_analysis['recommendations'].extend(knowledge_recommendations)
        
        print(f"✅ Dynamic RAG analysis completed successfully")
        return log_analysis
        
    except Exception as e:
        print(f"⚠️ Dynamic RAG analysis failed: {e}")
        log_analysis['dynamic_rag_analysis'] = {'error': str(e), 'status': 'failed'}
        return log_analysis

if __name__ == "__main__":
    # Test dynamic RAG system
    test_log_content = """
    2024-01-15 10:30:15 ERROR: AMSP scan engine crashed during file scan
    2024-01-15 10:30:16 CRITICAL: Firewall driver TMEBC.sys failed to load
    2024-01-15 10:30:17 WARNING: Connection timeout to DSM at 192.168.1.100
    2024-01-15 10:30:18 ERROR: Authentication failed for service ds_agent
    2024-01-15 10:30:19 INFO: Notifier service restarted successfully
    """
    
    print("🧠 Testing Dynamic RAG System...")
    
    dynamic_rag = DynamicRAGSystem()
    results = dynamic_rag.process_log_with_dynamic_rag(test_log_content)
    
    print(f"\n📊 Dynamic RAG Results:")
    print(f"Components Found: {results['log_context']['components']}")
    print(f"Error Types: {results['log_context']['error_types']}")
    print(f"Knowledge Sources: {len(results['knowledge_sources'])}")
    print(f"AI Response Available: {'Yes' if results['ai_response'] else 'No'}")
    
    if results['dynamic_prompt']:
        print(f"\n🎯 Dynamic Prompt Preview (first 300 chars):")
        print(results['dynamic_prompt'][:300] + "...")
