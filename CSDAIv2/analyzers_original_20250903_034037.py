# -*- coding: utf-8 -*-
"""
Deep Security Analyzer Classes
Contains all analyzer classes for different log types and analysis functions.
"""

import os
import re
import xml.etree.ElementTree as ET
from datetime import datetime
from typing import List, Dict, Any, Union
from security import SecurityError, validate_xml_content, sanitize_process_name

# Import OpenAI for analysis
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

# Machine Learning Analysis - Backend Enhancement for Dynamic RAG
try:
    from ml_analyzer import enhance_analysis_with_ml
    ML_AVAILABLE = True
    print("✅ ML-Enhanced Analysis Available")
except ImportError as e:
    ML_AVAILABLE = False
    print(f"⚠️  ML enhancement not available: {e}")

# Dynamic RAG Integration - the only RAG system
try:
    from dynamic_rag_system import DynamicRAGSystem, apply_dynamic_rag_to_analysis
    DYNAMIC_RAG_AVAILABLE = True
    print("✅ Dynamic RAG system loaded successfully")
except ImportError as e:
    DYNAMIC_RAG_AVAILABLE = False
    print(f"⚠️ Dynamic RAG system not available: {e}")

class AnalyzerOutputStandardizer:
    """Mixin class for standardizing analyzer output structures"""
    
    def _standardize_analyzer_output(self, raw_results, analysis_type):
        """Standardize analyzer output structure for frontend compatibility"""
        try:
            # Handle None input - this is the critical fix
            if raw_results is None:
                print(f"⚠️ Warning: _standardize_analyzer_output received None for analysis_type: {analysis_type}")
                raw_results = {
                    'summary': {'error': 'Analysis returned no data'},
                    'errors': ['Analysis failed to produce results'],
                    'warnings': [],
                    'recommendations': ['Please check the log file format and try again']
                }
            
            # Ensure raw_results is a dictionary
            if not isinstance(raw_results, dict):
                print(f"⚠️ Warning: raw_results is not a dictionary: {type(raw_results)}")
                raw_results = {
                    'summary': {'error': f'Invalid result type: {type(raw_results)}'},
                    'errors': [f'Expected dictionary, got {type(raw_results)}'],
                    'warnings': [],
                    'recommendations': ['Please check the analysis method implementation']
                }
            
            # DEBUG: Check what we're actually receiving
            print(f"🔍 DEBUG: Standardizing {analysis_type} with result type: {type(raw_results)}")
            if isinstance(raw_results, dict):
                print(f"🔍 DEBUG: Result keys: {list(raw_results.keys())}")
            
            standardized = {
                'analysis_type': analysis_type,
                'status': 'completed',
                'timestamp': datetime.now().isoformat(),
                
                # Core data - standardized fields with safe extraction
                'summary': self._extract_summary(raw_results),
                'details': self._extract_details(raw_results),
                'recommendations': self._extract_recommendations(raw_results),
                'severity': self._determine_overall_severity(raw_results),
                
                # Extended data with safe extraction
                'statistics': self._extract_statistics(raw_results),
                'correlations': self._extract_correlations(raw_results),
                'ml_insights': raw_results.get('ml_insights') if isinstance(raw_results, dict) else None,
                'rag_insights': (raw_results.get('rag_insights') or raw_results.get('dynamic_rag_analysis')) if isinstance(raw_results, dict) else None,
                
                # Original raw data for backward compatibility
                'raw_data': raw_results,
                'formatted_html': None  # Will be populated by formatters if needed
            }
            
            return standardized
            
        except Exception as e:
            print(f"⚠️ Failed to standardize output: {e}")
            print(f"🔍 DEBUG: Exception details - raw_results type: {type(raw_results)}")
            print(f"🔍 DEBUG: Exception traceback: {e}")
            # Fallback to safe structure
            return {
                'analysis_type': analysis_type,
                'status': 'error',
                'summary': f'Standardization failed: {str(e)}',
                'details': ['Analysis standardization encountered an error'],
                'recommendations': ['Please try again or contact support'],
                'severity': 'medium',
                'statistics': {},
                'correlations': {},
                'ml_insights': None,
                'rag_insights': None,
                'raw_data': raw_results,
                'formatted_html': None
            }
    
    def _extract_summary(self, data):
        """Extract summary information from raw results"""
        if data is None or not isinstance(data, dict):
            return "Analysis completed successfully"
        
        try:
            if isinstance(data.get('summary'), dict):
                summary_data = data['summary']
                return f"Analyzed {summary_data.get('total_lines', 0)} log entries, found {summary_data.get('error_count', 0)} errors and {summary_data.get('warning_count', 0)} warnings"
            elif isinstance(data.get('summary'), str):
                return data['summary']
            else:
                return "Analysis completed successfully"
        except Exception as e:
            print(f"⚠️ Error extracting summary: {e}")
            return "Analysis completed with summary extraction error"
    
    def _extract_details(self, data):
        """Extract detail information as structured list"""
        if data is None or not isinstance(data, dict):
            return ["No significant issues detected"]
            
        try:
            details = []
            
            # Add error details
            if data.get('errors'):
                errors = data['errors'][:5]  # Limit to first 5
                for error in errors:
                    if isinstance(error, dict):
                        details.append(f"Error: {error.get('message', str(error))}")
                    else:
                        details.append(f"Error: {str(error)}")
            
            # Add warning details  
            if data.get('warnings'):
                warnings = data['warnings'][:5]  # Limit to first 5
                for warning in warnings:
                    if isinstance(warning, dict):
                        details.append(f"Warning: {warning.get('message', str(warning))}")
                    else:
                        details.append(f"Warning: {str(warning)}")
            
            # Add component analysis
            if data.get('components'):
                for component, info in data['components'].items():
                    if isinstance(info, dict) and info.get('count', 0) > 0:
                        details.append(f"Component {component}: {info['count']} entries")
            
            return details if details else ["No significant issues detected"]
        except Exception as e:
            print(f"⚠️ Error extracting details: {e}")
            return ["Error extracting analysis details"]
    
    def _extract_recommendations(self, data):
        """Extract recommendations as structured list"""
        if data is None or not isinstance(data, dict):
            return ["Monitor system for recurring issues"]
            
        try:
            recommendations = []
            
            if data.get('recommendations'):
                for rec in data['recommendations']:
                    if isinstance(rec, str):
                        recommendations.append(rec)
                    elif isinstance(rec, dict):
                        recommendations.append(rec.get('text', str(rec)))
            
            # Add ML-based recommendations
            ml_insights = data.get('ml_insights')
            if ml_insights and isinstance(ml_insights, dict) and ml_insights.get('recommendations'):
                for rec in ml_insights['recommendations']:
                    recommendations.append(f"ML Insight: {rec}")
            
            # Add RAG-based recommendations
            rag_data = data.get('rag_insights') or data.get('dynamic_rag_analysis')
            if rag_data and isinstance(rag_data, dict) and rag_data.get('ai_response'):
                ai_response = rag_data['ai_response']
                if isinstance(ai_response, str) and len(ai_response) > 200:
                    ai_response = ai_response[:200] + "..."
                recommendations.append(f"AI Analysis: {ai_response}")
            
            return recommendations if recommendations else ["Monitor system for recurring issues"]
        except Exception as e:
            print(f"⚠️ Error extracting recommendations: {e}")
            return ["Error extracting recommendations"]
    
    def _determine_overall_severity(self, data):
        """Determine overall severity level"""
        if data is None or not isinstance(data, dict):
            return 'low'
            
        try:
            critical_count = 0
            error_count = 0
            warning_count = 0
            
            if isinstance(data.get('summary'), dict):
                summary = data['summary']
                critical_count = summary.get('critical_count', 0)
                error_count = summary.get('error_count', 0)
                warning_count = summary.get('warning_count', 0)
            
            # Check individual items
            if data.get('errors'):
                error_count += len([e for e in data['errors'] if 'critical' not in str(e).lower()])
                critical_count += len([e for e in data['errors'] if 'critical' in str(e).lower()])
            
            if critical_count > 0:
                return 'critical'
            elif error_count > 5:
                return 'high'
            elif error_count > 0 or warning_count > 10:
                return 'medium'
            else:
                return 'low'
        except Exception as e:
            print(f"⚠️ Error determining severity: {e}")
            return 'medium'
    
    def _extract_statistics(self, data):
        """Extract statistical information"""
        if data is None or not isinstance(data, dict):
            return {}
            
        try:
            stats = {}
            
            if isinstance(data.get('summary'), dict):
                summary = data['summary']
                stats = {
                    'total_lines': summary.get('total_lines', 0),
                    'parsed_lines': summary.get('parsed_lines', 0),
                    'error_count': summary.get('error_count', 0),
                    'warning_count': summary.get('warning_count', 0),
                    'critical_count': summary.get('critical_count', 0)
                }
            
            if data.get('components'):
                stats['component_count'] = len(data['components'])
            
            return stats
        except Exception as e:
            print(f"⚠️ Error extracting statistics: {e}")
            return {}
    
    def _extract_correlations(self, data):
        """Extract correlation information"""
        if data is None or not isinstance(data, dict):
            return {
                'cross_log_correlations': {},
                'timing_correlations': [],
                'component_correlations': [],
                'issue_correlations': []
            }
            
        try:
            correlations = {
                'cross_log_correlations': {},
                'timing_correlations': [],
                'component_correlations': [],
                'issue_correlations': []
            }
            
            # Extract correlation data if present
            if data.get('correlation_analysis'):
                correlation_data = data['correlation_analysis']
                correlations.update({
                    'timing_correlations': correlation_data.get('timing_correlations', []),
                    'component_correlations': correlation_data.get('component_correlations', []),
                    'issue_correlations': correlation_data.get('issue_correlations', []),
                    'correlation_score': correlation_data.get('correlation_score', 0)
                })
            
            # For diagnostic package results
            if data.get('cross_log_correlations'):
                correlations['cross_log_correlations'] = data['cross_log_correlations']
            
            return correlations
        except Exception as e:
            print(f"⚠️ Error extracting correlations: {e}")
            return {
                'cross_log_correlations': {},
                'timing_correlations': [],
                'component_correlations': [],
                'issue_correlations': []
            }

class DSAgentLogAnalyzer(AnalyzerOutputStandardizer):
    """
    Deep Security Agent Log Analyzer with Dynamic RAG integration
    Now includes real-time progress tracking for better UX
    """
    
    def __init__(self, session_manager=None, session_id=None, rag_system=None, ml_analyzer=None):
        """Initialize with optional progress tracking, RAG system, and ML analyzer"""
        self.session_manager = session_manager
        self.session_id = session_id
        self.rag_system = rag_system
        self.ml_analyzer = ml_analyzer
        
        # Initialize patterns and configurations
        self._initialize_patterns()
    
    def _update_progress(self, stage, message, percentage=None):
        """Update analysis progress if session manager is available"""
        if self.session_manager and self.session_id:
            try:
                progress_data = {
                    'analysis_stage': stage,
                    'progress_message': message,
                    'status': 'processing'
                }
                if percentage is not None:
                    progress_data['progress_percentage'] = percentage
                
                self.session_manager.update_session(self.session_id, progress_data)
                print(f"📊 Progress Update - {stage}: {message}")
            except Exception as e:
                print(f"⚠️ Progress update failed: {e}")
        else:
            # Fallback to console logging
            print(f"📊 {stage}: {message}")

    def _initialize_patterns(self):
        """Initialize error patterns and configurations"""
        # DS Agent Communication Patterns (Focused on Core Analysis)
        self.communication_patterns = {
            'agent_commands': [
                r'SetSecurityConfiguration|GetAgentStatus|GetAgentEvents',
                r'HeartbeatNow|ActivateAgent|GetComponentInfo',
                r'AssignDsmProxy|CreateDiagnostic|GetConfiguration'
            ],
            'service_operations': [
                r'service.*start|service.*stop|service.*restart',
                r'component.*loaded|component.*unloaded',
                r'agent.*activated|agent.*deactivated'
            ]
        }
        
        # Enhanced DS communication ports for analysis
        self.ds_communication_ports = {
            '4120': 'Agent-Manager Communication (HTTPS)',
            '4119': 'Agent Installation/Upgrade (HTTPS)', 
            '4118': 'Relay Commands (HTTPS)',
            '443': 'Cloud One/External Services (HTTPS)',
            '527': 'Smart Scan Server (if local)'
        }
        
        self.error_patterns = {
            'critical': [
                r'(Critical|CRITICAL|Error|ERROR)',
                r'unable to open file',
                r'file not available',
                r'connection failed',
                r'authentication failed',
                r'permission denied',
                r'access denied',
                r'certificate error',
                r'ssl error',
                r'network error'
            ],
            'warning': [
                r'(Warning|WARNING)',
                r'failed',
                r'timeout',
                r'retry',
                r'deprecated',
                r'not supported',
                r'metrics failed'
            ],
            'info': [
                r'(Info|INFO)',
                r'starting',
                r'stopping',
                r'connecting',
                r'disconnecting'
            ]
        }
        
        self.component_patterns = {
            'anti_malware': [r'antimalware', r'amsp', r'aegis', r'adc'],
            'intrusion_prevention': [r'dpi', r'ips'],
            'integrity_monitoring': [r'integrity', r'fim'],
            'log_inspection': [r'loginspection', r'li'],
            'device_control': [r'device control', r'dc'],
            'web_reputation': [r'web reputation', r'wr'],
            'application_control': [r'application control', r'ac'],
            'connection_handler': [r'connectionhandler', r'heartbeat'],
            'agent_core': [r'dsa', r'agent', r'core']
        }
        
        self.known_issues = {
            'AMSP_FUNC_NOT_SUPPORT': {
                'severity': 'warning',
                'description': 'Device Control adapter metrics function not supported',
                'resolution': 'This is expected if Device Control is not enabled or not supported on this platform',
                'impact': 'Low - Metrics collection only'
            },
            'unable to open file': {
                'severity': 'error',
                'description': 'File access permission or path issue',
                'resolution': 'Check file permissions and verify file paths exist',
                'impact': 'Medium - May affect monitoring capabilities'
            },
            'file not available': {
                'severity': 'warning',
                'description': 'Expected file is not present',
                'resolution': 'Verify if the file should exist and check configuration',
                'impact': 'Low-Medium - Depends on file importance'
            }
        }

    def parse_log_entry(self, line: str) -> Dict[str, Any]:
        """Parse a single log line into structured data"""
        pattern = r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d+) \[([^\]]+)\]: \[([^\]]+)\] \| ([^|]+) \| ([^|]*) \| (.+)'
        
        match = re.match(pattern, line)
        if not match:
            return {'raw_line': line, 'parsed': False}
        
        timestamp, timezone, component_level, message, location, thread = match.groups()
        
        comp_level_parts = component_level.split('/')
        component = comp_level_parts[0] if comp_level_parts else 'unknown'
        level = comp_level_parts[1] if len(comp_level_parts) > 1 else '5'
        
        return {
            'timestamp': timestamp,
            'timezone': timezone,
            'component': component,
            'level': level,
            'message': message.strip(),
            'location': location.strip(),
            'thread': thread.strip(),
            'raw_line': line,
            'parsed': True
        }

    def categorize_severity(self, log_entry: Dict[str, Any]) -> str:
        """Categorize log entry severity"""
        if not log_entry.get('parsed'):
            return 'unknown'
        
        message = log_entry['message'].lower()
        
        for pattern in self.error_patterns['critical']:
            if re.search(pattern, message, re.IGNORECASE):
                return 'critical'
        
        for pattern in self.error_patterns['warning']:
            if re.search(pattern, message, re.IGNORECASE):
                return 'warning'
        
        for pattern in self.error_patterns['info']:
            if re.search(pattern, message, re.IGNORECASE):
                return 'info'
        
        return 'normal'

    def identify_component(self, log_entry: Dict[str, Any]) -> str:
        """Identify which DS component the log entry relates to"""
        if not log_entry.get('parsed'):
            return 'unknown'
        
        message = log_entry['message'].lower()
        component = log_entry['component'].lower()
        location = log_entry['location'].lower()
        
        full_text = f"{message} {component} {location}"
        
        for comp_name, patterns in self.component_patterns.items():
            for pattern in patterns:
                if re.search(pattern, full_text, re.IGNORECASE):
                    return comp_name.replace('_', ' ').title()
        
        return 'Agent Core'

    def analyze_known_issues(self, log_entry: Dict[str, Any]) -> Dict[str, Any]:
        """Check if log entry matches known issues"""
        if not log_entry.get('parsed'):
            return None
        
        message = log_entry['message']
        
        for issue_key, issue_info in self.known_issues.items():
            if issue_key.lower() in message.lower():
                return {
                    'issue_type': issue_key,
                    'severity': issue_info['severity'],
                    'description': issue_info['description'],
                    'resolution': issue_info['resolution'],
                    'impact': issue_info['impact']
                }
        
        return None

    # Connection Health Analysis Method Removed - Cloud One Workload Security Connection Health component eliminated

    def analyze_log_file(self, file_path: str) -> Dict[str, Any]:
        """Analyze the entire log file with ML enhancement"""
        # Progress: 5% - File parsing started
        self._update_progress('File Parsing & Initial Analysis', 'Reading uploaded log files...', 5)
        
        results = {
            'summary': {
                'total_lines': 0,
                'parsed_lines': 0,
                'error_count': 0,
                'warning_count': 0,
                'critical_count': 0,
                'timespan': {'start': None, 'end': None}
            },
            'errors': [],
            'warnings': [],
            'critical_issues': [],
            'component_analysis': {},
            'known_issues': [],
            'recommendations': [],
            'ml_insights': None,  # ML insights for Dynamic RAG enhancement (backend only)
            'rag_insights': None
        }
        
        try:
            # Progress: 10% - File reading and validation
            self._update_progress('File Parsing & Initial Analysis', 'Validating file format and structure...', 10)
            
            # Debug: Check if file exists and is readable
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"Log file not found: {file_path}")
            
            file_size = os.path.getsize(file_path)
            file_name = os.path.basename(file_path)
            print(f"🔍 DEBUG: Analyzing file: {file_path} (size: {file_size} bytes)")
            
            # Check if this is the wrong file type
            if 'topnbusyprocess' in file_name.lower() or 'runningprocess' in file_name.lower():
                raise SecurityError(f"File {file_name} should be analyzed by ResourceAnalyzer, not DSAgentLogAnalyzer")
            
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                total_lines_processed = 0
                first_few_lines = []
                
                # Check first line for file type validation
                first_line = f.readline().strip()
                f.seek(0)  # Reset file pointer
                
                if first_line and ('top' in first_line.lower() and 'busy' in first_line.lower() and 'process' in first_line.lower()):
                    raise SecurityError(f"File appears to be a TopNBusyProcess file, should be analyzed by ResourceAnalyzer")
                
                # Progress: 15% - Extracting log entries
                self._update_progress('File Parsing & Initial Analysis', 'Extracting log entries and timestamps...', 15)
                
                for line_num, line in enumerate(f, 1):
                    if line_num > 10000:
                        break
                    
                    results['summary']['total_lines'] += 1
                    line = line.strip()
                    
                    # Collect first few lines for debugging
                    if line_num <= 5:
                        first_few_lines.append(f"Line {line_num}: {line[:100]}...")
                    
                    if not line:
                        continue
                    
                    log_entry = self.parse_log_entry(line)
                    
                    # Update progress every 1000 lines
                    if line_num % 1000 == 0:
                        progress = min(15 + (line_num / 10000) * 10, 25)  # 15% to 25%
                        self._update_progress('File Parsing & Initial Analysis', f'Processing log entries... ({line_num} processed)', progress)
                    
                    if log_entry['parsed']:
                        results['summary']['parsed_lines'] += 1
                        
                        if not results['summary']['timespan']['start']:
                            results['summary']['timespan']['start'] = log_entry['timestamp']
                        results['summary']['timespan']['end'] = log_entry['timestamp']
                        
                        severity = self.categorize_severity(log_entry)
                        component = self.identify_component(log_entry)
                        
                        if severity == 'critical':
                            results['summary']['critical_count'] += 1
                            results['critical_issues'].append({
                                'line': line_num,
                                'timestamp': log_entry['timestamp'],
                                'component': component,
                                'message': log_entry['message'],
                                'location': log_entry['location']
                            })
                        elif severity == 'warning':
                            results['summary']['warning_count'] += 1
                            results['warnings'].append({
                                'line': line_num,
                                'timestamp': log_entry['timestamp'],
                                'component': component,
                                'message': log_entry['message'],
                                'location': log_entry['location']
                            })
                        elif 'error' in severity:
                            results['summary']['error_count'] += 1
                            results['errors'].append({
                                'line': line_num,
                                'timestamp': log_entry['timestamp'],
                                'component': component,
                                'message': log_entry['message'],
                                'location': log_entry['location']
                            })
                        
                        if component not in results['component_analysis']:
                            results['component_analysis'][component] = {
                                'total_entries': 0,
                                'errors': 0,
                                'warnings': 0
                            }
                        
                        results['component_analysis'][component]['total_entries'] += 1
                        if severity in ['critical', 'error']:
                            results['component_analysis'][component]['errors'] += 1
                        elif severity == 'warning':
                            results['component_analysis'][component]['warnings'] += 1
                        
                        known_issue = self.analyze_known_issues(log_entry)
                        if known_issue:
                            known_issue['line'] = line_num
                            known_issue['timestamp'] = log_entry['timestamp']
                            known_issue['component'] = component
                            results['known_issues'].append(known_issue)
            
            results['recommendations'] = self.generate_recommendations(results)
            
            # Connection Health Analysis for Cloud One Workload Security
            all_log_entries = []
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                for line_num, line in enumerate(f, 1):
                    if line_num > 10000:  # Same limit as main loop
                        break
                    log_entry = self.parse_log_entry(line.strip())
                    if log_entry['parsed']:
                        log_entry['line'] = line_num
                        all_log_entries.append(log_entry)
            
            # ML Enhancement for Dynamic RAG (Backend Processing)
            ml_insights = None
            if ML_AVAILABLE and all_log_entries:
                try:
                    # Generate ML insights for Dynamic RAG enhancement
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        log_content = f.read()
                    from ml_analyzer import enhance_analysis_with_ml
                    ml_insights = enhance_analysis_with_ml(log_content, 'ds_logs')
                    print(f"✅ ML insights generated for Dynamic RAG enhancement")
                except Exception as e:
                    print(f"⚠️  ML enhancement failed: {e}")
                    ml_insights = None
            
            # Store ML insights for Dynamic RAG (not for frontend display)
            results['ml_insights'] = ml_insights
            
            # Dynamic RAG Integration - 60% progress
            self._update_progress('Dynamic RAG & AI Intelligence', 'Starting Dynamic RAG analysis...', 60)
            if DYNAMIC_RAG_AVAILABLE:
                try:
                    # Try Dynamic RAG first for intelligent prompt generation
                    try:
                        # Read log content for dynamic analysis
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            log_content = f.read()
                        
                        from dynamic_rag_system import apply_dynamic_rag_to_analysis
                        self._update_progress('Dynamic RAG & AI Intelligence', 'Processing with Claude AI...', 65)
                        results = apply_dynamic_rag_to_analysis(results, log_content)
                        self._update_progress('Dynamic RAG & AI Intelligence', 'Dynamic RAG analysis completed', 70)
                        
                        dynamic_rag = results.get('dynamic_rag_analysis', {})
                        if dynamic_rag and 'error' not in dynamic_rag:
                            print(f"✅ Dynamic RAG Analysis (DS Logs): {dynamic_rag.get('analysis_metadata', {}).get('knowledge_sources_used', 0)} sources")
                            
                            # Add dynamic insights to recommendations
                            if dynamic_rag.get('ai_response'):
                                ai_summary = dynamic_rag['ai_response'][:200] + "..." if len(dynamic_rag['ai_response']) > 200 else dynamic_rag['ai_response']
                                results['recommendations'].append(f'🧠 <strong>AI Analysis</strong>: {ai_summary}')
                                
                    except Exception as dynamic_error:
                        print(f"⚠️  Dynamic RAG failed for DS Logs: {dynamic_error}")
                        print("ℹ️  No other RAG systems available")
                    
                except Exception as e:
                    print(f"⚠️  Dynamic RAG analysis failed: {e}")
                    results['rag_insights'] = {'error': str(e)}
            else:
                results['rag_insights'] = {'status': 'RAG features not available'}
            
            # Analysis completion - 95% progress
            self._update_progress('Report Generation & Finalization', 'Generating comprehensive HTML report...', 95)
            
        except Exception as e:
            raise SecurityError(f"Error analyzing log file: {str(e)}")
        
        # Analysis complete - 100% progress
        self._update_progress('Report Generation & Finalization', 'Analysis completed successfully!', 100)
        
        # Add debugging output
        print(f"🔍 DEBUG: Analysis complete - Total lines: {results['summary']['total_lines']}, Parsed: {results['summary']['parsed_lines']}")
        print(f"🔍 DEBUG: First few lines: {first_few_lines}")
        
        # Return raw results (will be standardized by the analyze() method)
        return results

    def analyze_multiple_log_files(self, file_paths: List[str]) -> Dict[str, Any]:
        """Analyze multiple DS Agent log files and consolidate results"""
        consolidated_results = {
            'summary': {
                'total_lines': 0,
                'parsed_lines': 0,
                'error_count': 0,
                'warning_count': 0,
                'critical_count': 0,
                'timespan': {'start': None, 'end': None},
                'file_count': len(file_paths),
                'files_analyzed': []
            },
            'errors': [],
            'warnings': [],
            'critical_issues': [],
            'component_analysis': {},
            'known_issues': [],
            'recommendations': [],
            'connection_health': None,  # Connection Health Analysis Removed - Cloud One Workload Security Connection Health component eliminated
            'ml_insights': None,
            'rag_insights': None,
            'file_analysis': {}
        }
        
        all_log_entries = []
        
        try:
            for i, file_path in enumerate(file_paths, 1):
                print(f'📊 Analyzing file {i}/{len(file_paths)}: {file_path}')
                
                # Analyze individual file
                file_results = self.analyze_log_file(file_path)
                file_name = file_path.split('\\')[-1] if '\\' in file_path else file_path.split('/')[-1]
                
                # Extract summary data safely - handle both standardized and raw results
                if isinstance(file_results, dict):
                    # Check if this is a standardized result
                    if 'raw_data' in file_results and isinstance(file_results['raw_data'], dict):
                        # Use raw_data for detailed analysis
                        raw_summary = file_results['raw_data'].get('summary', {})
                        file_summary = raw_summary
                    elif 'summary' in file_results:
                        # Direct summary access
                        file_summary = file_results['summary']
                    else:
                        # Create default summary if none exists
                        file_summary = {'total_lines': 0, 'critical_count': 0, 'error_count': 0, 'warning_count': 0}
                else:
                    # Fallback for unexpected structure
                    file_summary = {'total_lines': 0, 'critical_count': 0, 'error_count': 0, 'warning_count': 0}
                
                # Store individual file results
                consolidated_results['file_analysis'][file_name] = {
                    'summary': file_summary,
                    'critical_count': file_summary.get('critical_count', 0),
                    'error_count': file_summary.get('error_count', 0),
                    'warning_count': file_summary.get('warning_count', 0)
                }
                
                consolidated_results['summary']['files_analyzed'].append(file_name)
                
                # Consolidate summaries using safe file_summary
                consolidated_results['summary']['total_lines'] += file_summary.get('total_lines', 0)
                consolidated_results['summary']['parsed_lines'] += file_summary.get('parsed_lines', 0)
                consolidated_results['summary']['error_count'] += file_summary.get('error_count', 0)
                consolidated_results['summary']['warning_count'] += file_summary.get('warning_count', 0)
                consolidated_results['summary']['critical_count'] += file_summary.get('critical_count', 0)
                
                # Update timespan using safe file_summary
                timespan = file_summary.get('timespan', {})
                if timespan.get('start'):
                    if not consolidated_results['summary']['timespan']['start'] or \
                       timespan['start'] < consolidated_results['summary']['timespan']['start']:
                        consolidated_results['summary']['timespan']['start'] = timespan['start']
                
                if timespan.get('end'):
                    if not consolidated_results['summary']['timespan']['end'] or \
                       timespan['end'] > consolidated_results['summary']['timespan']['end']:
                        consolidated_results['summary']['timespan']['end'] = timespan['end']
                
                # Safely extract file data for consolidation
                if 'raw_data' in file_results and isinstance(file_results['raw_data'], dict):
                    raw_data = file_results['raw_data']
                else:
                    raw_data = file_results if isinstance(file_results, dict) else {}
                
                # Consolidate issues
                consolidated_results['errors'].extend(raw_data.get('errors', []))
                consolidated_results['warnings'].extend(raw_data.get('warnings', []))
                consolidated_results['critical_issues'].extend(raw_data.get('critical_issues', []))
                consolidated_results['known_issues'].extend(raw_data.get('known_issues', []))
                
                # Consolidate component analysis
                for component, stats in raw_data.get('component_analysis', {}).items():
                    if component not in consolidated_results['component_analysis']:
                        consolidated_results['component_analysis'][component] = {
                            'total_entries': 0,
                            'errors': 0,
                            'warnings': 0
                        }
                    consolidated_results['component_analysis'][component]['total_entries'] += stats['total_entries']
                    consolidated_results['component_analysis'][component]['errors'] += stats['errors']
                    consolidated_results['component_analysis'][component]['warnings'] += stats['warnings']
                
                # Consolidate connection health
                # Connection Health Analysis Removed - Cloud One Workload Security Connection Health component eliminated
                
                # Collect all log entries for consolidated ML/RAG analysis
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    for line_num, line in enumerate(f, 1):
                        if line_num > 5000:  # Limit per file for performance
                            break
                        log_entry = self.parse_log_entry(line.strip())
                        if log_entry['parsed']:
                            log_entry['source_file'] = file_name
                            log_entry['line'] = line_num
                            all_log_entries.append(log_entry)
            
            # Connection Health Analysis Removed - Cloud One Workload Security Connection Health component eliminated
            
            # Generate consolidated recommendations
            consolidated_results['recommendations'] = self.generate_recommendations(consolidated_results)
            
            # Add multi-file specific recommendations
            if len(file_paths) > 1:
                consolidated_results["recommendations"].insert(0, f'<i class="fa-solid fa-folder me-2"></i>Analyzed {len(file_paths)} log files covering {consolidated_results["summary"]["total_lines"]:,} total log entries')
                
                if consolidated_results['summary']['critical_count'] > 0:
                    consolidated_results["recommendations"].append(f'<i class="fa-solid fa-circle-exclamation me-2"></i>{consolidated_results["summary"]["critical_count"]} critical issues found across all files - prioritize by timestamp')
            
            # ML Enhancement for Dynamic RAG (Consolidated Analysis)
            if ML_AVAILABLE and len(all_log_entries) > 0:
                try:
                    # Combine log content from all files for ML analysis
                    combined_content = "\n".join([f"{entry.get('timestamp', '')} {entry.get('message', '')}" for entry in all_log_entries[:10000]])
                    from ml_analyzer import enhance_analysis_with_ml
                    ml_insights = enhance_analysis_with_ml(combined_content, 'ds_logs')
                    consolidated_results['ml_insights'] = ml_insights
                    print(f"✅ Consolidated ML Analysis completed: {len(all_log_entries)} entries from {len(file_paths)} files")
                except Exception as e:
                    print(f"⚠️  Consolidated ML analysis failed: {e}")
                    consolidated_results['ml_insights'] = None
            else:
                consolidated_results['ml_insights'] = None
            
            # Consolidated Dynamic RAG Analysis (if available)
            if DYNAMIC_RAG_AVAILABLE:
                try:
                    # Apply dynamic RAG to consolidated results
                    from dynamic_rag_system import apply_dynamic_rag_to_analysis
                    
                    # Create combined log content from all files
                    combined_log_content = ""
                    for file_path in file_paths:
                        try:
                            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                                combined_log_content += f"\n=== {file_path} ===\n"
                                combined_log_content += f.read()[:5000]  # Limit per file
                        except Exception as e:
                            print(f"⚠�  Could not read {file_path} for RAG: {e}")
                    
                    consolidated_results = apply_dynamic_rag_to_analysis(consolidated_results, combined_log_content)
                    
                    dynamic_rag = consolidated_results.get('dynamic_rag_analysis', {})
                    if dynamic_rag and 'error' not in dynamic_rag:
                        print(f"✅ Consolidated Dynamic RAG Analysis: {dynamic_rag.get('analysis_metadata', {}).get('knowledge_sources_used', 0)} sources")
                        
                        # Add dynamic insights to recommendations
                        if dynamic_rag.get('ai_response'):
                            ai_summary = dynamic_rag['ai_response'][:200] + "..." if len(dynamic_rag['ai_response']) > 200 else dynamic_rag['ai_response']
                            consolidated_results['recommendations'].append(f'🧠 <strong>Multi-file AI Analysis</strong>: {ai_summary}')
                    
                except Exception as e:
                    print(f"⚠�  Consolidated Dynamic RAG analysis failed: {e}")
                    consolidated_results['dynamic_rag_analysis'] = {'error': str(e)}
            
            print(f"✅ Multiple file analysis completed: {len(file_paths)} files, {consolidated_results['summary']['total_lines']:,} total lines")
            
        except Exception as e:
            raise SecurityError(f"Error analyzing multiple log files: {str(e)}")
        
        # Standardize return structure for frontend compatibility
        return consolidated_results

    def generate_recommendations(self, analysis: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on analysis"""
        recommendations = []
        
        if analysis['summary']['critical_count'] > 0:
            recommendations.append('<i class="fa-solid fa-circle-exclamation me-2"></i>Critical issues detected - immediate attention required')
        
        if analysis['summary']['error_count'] > 10:
            recommendations.append('<i class="fa-solid fa-triangle-exclamation me-2"></i>High number of errors detected - review agent configuration')
        
        if analysis['summary']['warning_count'] > 50:
            recommendations.append('<i class="fa-solid fa-triangle-exclamation me-2"></i>Many warnings detected - consider reviewing agent policies')
        
        for component, stats in analysis['component_analysis'].items():
            if stats['errors'] > 5:
                recommendations.append(f'<i class="fa-solid fa-wrench me-2"></i>{component}: High error count - check component configuration')
        
        issue_counts = {}
        for issue in analysis['known_issues']:
            issue_type = issue['issue_type']
            issue_counts[issue_type] = issue_counts.get(issue_type, 0) + 1
        
        for issue_type, count in issue_counts.items():
            if count > 10:
                issue_info = self.known_issues.get(issue_type, {})
                recommendations.append(f'<i class="fa-solid fa-search"></i> Recurring issue "{issue_type}" ({count} occurrences): {issue_info.get("resolution", "Review configuration")}')
        
        if not recommendations:
            recommendations.append('<i class="fa-solid fa-check-circle text-success"></i> No critical issues detected - agent appears to be functioning normally')
        
        return recommendations

    def analyze(self, file_paths: Union[str, List[str]]) -> Dict[str, Any]:
        """Standardized analysis entry point for DS Agent logs with enhanced progress tracking"""
        try:
            self._update_progress("Initialization", "Starting DS Agent log analysis", 1)
            
            # Normalize input to list
            if isinstance(file_paths, str):
                file_paths = [file_paths]
            
            if not file_paths:
                raise ValueError("No log files provided for analysis")
            
            self._update_progress("File Validation", f"Validating {len(file_paths)} log files", 5)
            
            # Determine if single or multiple file analysis
            if len(file_paths) == 1:
                self._update_progress("Single File Analysis", "Analyzing single DS Agent log file", 20)
                analysis_results = self.analyze_log_file(file_paths[0])
                is_multiple = False
            else:
                self._update_progress("Multiple File Analysis", f"Processing {len(file_paths)} DS Agent log files", 20)
                
                # Add progress updates during file processing
                for i, file_path in enumerate(file_paths):
                    progress = 20 + (i / len(file_paths)) * 60  # 20% to 80% during processing
                    self._update_progress("File Processing", f"Processing file {i+1}/{len(file_paths)}: {os.path.basename(file_path)}", int(progress))
                
                analysis_results = self.analyze_multiple_log_files(file_paths)
                is_multiple = True
            
            self._update_progress("Pattern Analysis", "Analyzing patterns and generating insights", 85)
            
            # Apply standardized output format
            self._update_progress("Standardization", "Converting to standardized format", 90)
            standardized_result = self._standardize_analyzer_output(analysis_results, 'ds_logs')
            
            # Add metadata with enhanced tracking
            self._update_progress("Metadata Generation", "Generating analysis metadata", 95)
            if analysis_results and isinstance(analysis_results, dict):
                summary = analysis_results.get('summary', {})
                standardized_result['metadata'] = {
                    'files_processed': len(file_paths),
                    'file_count': len(file_paths),
                    'analysis_type': 'single' if not is_multiple else 'multiple',
                    'log_entries_processed': summary.get('total_lines', 0),
                    'errors_found': len(analysis_results.get('errors', [])),
                    'warnings_found': len(analysis_results.get('warnings', [])),
                    'critical_issues': len(analysis_results.get('critical_issues', []))
                }
            else:
                standardized_result['metadata'] = {
                    'files_processed': len(file_paths),
                    'file_count': len(file_paths),
                    'analysis_type': 'single' if not is_multiple else 'multiple',
                    'log_entries_processed': 0,
                    'errors_found': 0,
                    'warnings_found': 0,
                    'critical_issues': 0
                }
            
            # Generate formatted output using existing formatter
            self._update_progress("Output Formatting", "Generating formatted HTML output", 98)
            from routes import format_ds_log_results
            formatted_html = format_ds_log_results(analysis_results, is_multiple)
            standardized_result['formatted_output'] = formatted_html
            
            self._update_progress("Completion", "DS Agent log analysis completed", 100)
            return standardized_result
            
        except Exception as e:
            error_msg = f"DS Agent log analysis failed: {str(e)}"
            self._update_progress("Error", error_msg, None)
            return {
                'analysis_type': 'ds_logs',
                'status': 'error',
                'summary': error_msg,
                'details': [error_msg],
                'recommendations': ['Please ensure valid DS Agent log files are provided'],
                'severity': 'high',
                'error': True,
                'metadata': {
                    'files_processed': len(file_paths) if 'file_paths' in locals() else 0,
                    'error_type': 'analysis_failure'
                }
            }


class AMSPAnalyzer(AnalyzerOutputStandardizer):
    """AMSP Anti-Malware Log Analyzer with progress tracking"""
    
    def __init__(self, session_manager=None, session_id=None):
        """Initialize with optional progress tracking"""
        self.session_manager = session_manager
        self.session_id = session_id
        
        self._initialize_amsp_patterns()
    
    def _update_progress(self, stage, message, percentage=None):
        """Update analysis progress if session manager is available"""
        if self.session_manager and self.session_id:
            try:
                progress_data = {
                    'analysis_stage': stage,
                    'progress_message': message,
                    'status': 'processing'
                }
                if percentage is not None:
                    progress_data['progress_percentage'] = percentage
                
                self.session_manager.update_session(self.session_id, progress_data)
                print(f"📊 AMSP Progress - {stage}: {message}")
            except Exception as e:
                print(f"⚠�  AMSP Progress update failed: {e}")
        else:
            # Fallback to console logging
            print(f"📊 AMSP {stage}: {message}")

    def _initialize_amsp_patterns(self):
        """Initialize AMSP patterns and configurations with enhanced ds_am.log root cause detection"""
        self.error_patterns = {
            'critical': [
                r'(Critical|CRITICAL|Fatal|FATAL|Error|ERROR)',
                r'installation failed',
                r'service startup failed',
                r'driver load failed',
                r'driver.*failed',
                r'tmcomm.*failed',
                r'tmebc.*failed',
                r'configuration error',
                r'dependency missing',
                r'access denied',
                r'permission denied',
                r'signature verification failed',
                r'certificate error',
                r'kernel.*error',
                r'registry.*error',
                r'file.*error',
                r'startup.*failed',
                r'initialization.*failed',
                r'communication.*failed',
                r'connection.*failed',
                r'authentication.*failed',
                r'policy.*failed',
                # Enhanced ds_am.log specific critical patterns
                r'VSReadVirusPattern.*failed.*ret=-2',
                r'VSGetPatternProperty.*failed.*rc=-99',
                r'ReadPatternVersions.*failed.*rc.*-99',
                r'bmtrap.*cannot find pattern',
                r'bm_load_pattern_buf.*failed.*-17',
                r'_bm_native__find_bpf_prog_ctx.*cannot find',
                r'VSScanResource.*failed.*error code.*-94',
                r'trx_engine_new.*failed',
                r'CreateTrendXScanConfig.*failed',
                r'stat\(.*tmbmf\.ptn\.local\).*failed',
                r'No such file or directory.*\.ptn',
                r'BPF.*program.*failed|eBPF.*failed'
            ],
            'warning': [
                r'(Warning|WARNING|Warn)',
                r'pattern update failed',
                r'connectivity issue',
                r'timeout',
                r'retry',
                r'performance',
                r'slow response',
                r'memory usage high',
                r'disk space low',
                r'deprecated',
                r'fallback',
                r'partial.*success',
                r'limited.*functionality',
                # Enhanced ds_am.log specific warning patterns
                r'Skip.*by filtering features.*rc=-38',
                r'ICRC.*ERROR.*timeout',
                r'iCRCChkServerStatus.*timeout.*reached',
                r'dsaas\.icrc\.trendmicro\.com.*timeout',
                r'bm_native_bpf_pin_iter.*rc=-2',
                r'TRENDX.*Get metrics.*enabled=0',
                r'No Sensor Metrics',
                r'fstat\(-2\).*-1',
                r'MetaInvUtil.*failed.*rc=1'
            ],
            'info': [
                r'(Info|INFO|Information)',
                r'starting',
                r'stopping',
                r'initialization',
                r'configuration loaded',
                r'update completed',
                r'scan completed',
                r'successfully',
                r'completed',
                r'enabled',
                r'disabled',
                r'registered',
                r'unregistered'
            ]
        }
        
        self.installation_patterns = {
            'driver_installation': [
                r'driver.*install',
                r'tmcomm.*install',
                r'tmebc.*install',
                r'kernel.*module',
                r'kernel.*driver',
                r'loading.*driver',
                r'driver.*signature',
                r'driver.*verification',
                r'inf.*install',
                r'sys.*file.*copy'
            ],
            'service_startup': [
                r'service.*start',
                r'amsp.*service',
                r'real.*time.*protection',
                r'service.*init',
                r'service.*control.*manager',
                r'scm.*communication',
                r'service.*registration',
                r'service.*configuration',
                r'startup.*type',
                r'service.*dependencies'
            ],
            'pattern_updates': [
                r'pattern.*update',
                r'signature.*update',
                r'virus.*definition',
                r'pattern.*download',
                r'pattern.*verification',
                r'pattern.*install',
                r'engine.*update',
                r'definition.*update',
                r'download.*pattern',
                r'pattern.*file'
            ],
            'behavioral_monitoring': [
                r'bmtrap.*load|bmtrap.*pattern',
                r'BPF.*program|eBPF.*load',
                r'bm_native.*ctx|bm_load_pattern',
                r'behavioral.*monitoring|bmevt_monitor',
                r'bm_register_callback|bm_native_register',
                r'BMEvtMonitor.*pattern|BMNatMonitor.*pattern',
                r'BMPTNUTIL.*loaded.*features',
                r'bmptn_util.*pattern'
            ],
            'trendx_engine': [
                r'TRENDX.*engine|VSRead.*Pattern',
                r'trx_engine|scanctx.*config',
                r'virus.*pattern.*property|VSGetPatternProperty',
                r'trendx_scanctx_config|trxhandler_module',
                r'VSReadVirusPattern|ReadPatternVersions',
                r'CreateTrendXScanConfig|TrendXScanConfig',
                r'SCAN.*sctrl_engine|VSScanResource',
                r'scanctrl_am_engine'
            ],
            'pattern_file_system': [
                r'tmbmf\.ptn.*pattern|\.ptn\.local',
                r'pattern.*file.*system|pattern.*directory',
                r'FindLocalPattern|stat.*\.ptn',
                r'pattern.*path|pattern.*location',
                r'patterns/.*\.ptn'
            ],
            'feature_filtering': [
                r'filtering features|feature.*filter',
                r'Skip.*by filtering|on_mask.*off_mask',
                r'feature.*disabled|feature.*enabled',
                r'bm_load.*filtering'
            ],
            'configuration': [
                r'config.*load',
                r'policy.*apply',
                r'setting.*change',
                r'configuration.*update',
                r'registry.*write',
                r'registry.*read',
                r'policy.*download',
                r'configuration.*parse',
                r'xml.*configuration',
                r'parameter.*set'
            ],
            'communication': [
                r'dsm.*connect',
                r'heartbeat',
                r'relay.*connect',
                r'communication.*establish',
                r'ssl.*handshake',
                r'certificate.*exchange',
                r'agent.*communication',
                r'manager.*connect',
                r'network.*communication',
                r'proxy.*configuration'
            ],
            'cloud_connectivity': [
                r'ICRC.*server|icrc\.trendmicro\.com',
                r'dsaas\.icrc|iCRCChkServerStatus',
                r'cloud.*connectivity|cloud.*server',
                r'ICRC_HTTP_ERROR|ICRC.*timeout'
            ],
            'file_operations': [
                r'file.*copy',
                r'file.*create',
                r'file.*delete',
                r'directory.*create',
                r'temp.*file',
                r'backup.*file',
                r'restore.*file',
                r'file.*permission',
                r'file.*lock',
                r'file.*unlock'
            ]
        }
        
        self.known_issues = {
            'DRIVER_LOAD_FAILED': {
                'severity': 'critical',
                'description': 'AMSP kernel driver (tmcomm.sys/tmebc.sys) failed to load',
                'resolution': 'Check driver signing, disable secure boot temporarily, reboot system, or reinstall DS Agent with latest version',
                'impact': 'High - Real-time protection completely disabled',
                'ds_reference': 'KB: Driver Load Failures - Check Windows Event Log System for additional details'
            },
            'SERVICE_START_FAILED': {
                'severity': 'critical',
                'description': 'AMSP service failed to start or register with SCM',
                'resolution': 'Check service dependencies (RPC, Windows Firewall), verify permissions, restart in safe mode if needed',
                'impact': 'High - Anti-malware protection unavailable',
                'ds_reference': 'DS Best Practices: Service Dependencies and Windows Compatibility'
            },
            'PATTERN_UPDATE_FAILED': {
                'severity': 'warning',
                'description': 'Pattern update process failed or incomplete',
                'resolution': 'Check network connectivity, proxy settings, and DSM/Relay communication. Verify pattern server accessibility',
                'impact': 'Medium - Using outdated malware signatures',
                'ds_reference': 'Pattern Update Troubleshooting Guide - Network and Connectivity Requirements'
            },
            'CONFIGURATION_ERROR': {
                'severity': 'error',
                'description': 'Invalid or corrupted AMSP configuration detected',
                'resolution': 'Review policy settings in DSM, clear local configuration cache, and reapply policies',
                'impact': 'Medium - May affect protection effectiveness and feature availability',
                'ds_reference': 'Policy Configuration Best Practices - AMSP Module Settings'
            },
            # Enhanced ds_am.log specific root cause issues
            'TRENDX_ENGINE_FAILURE': {
                'severity': 'critical',
                'description': 'TrendX scanning engine cannot read virus patterns (VSReadVirusPattern failed: ret=-2)',
                'resolution': 'Verify pattern file integrity, check file permissions, download latest patterns manually, restart AMSP service',
                'impact': 'Critical - Malware scanning completely disabled',
                'ds_reference': 'TrendX Engine Troubleshooting - Pattern File Management and Virus Pattern Recovery'
            },
            'BEHAVIORAL_MONITORING_FAILED': {
                'severity': 'critical',
                'description': 'bmtrap behavioral monitoring system cannot load BPF programs (bm_load_pattern_buf failed: -17)',
                'resolution': 'Check kernel BPF support (4.4+), verify eBPF capabilities, restart DS Agent, check ulimit settings',
                'impact': 'High - Behavioral threat detection disabled',
                'ds_reference': 'Behavioral Monitoring Requirements - Linux Kernel Compatibility and BPF Program Loading'
            },
            'PATTERN_FILE_MISSING': {
                'severity': 'critical',
                'description': 'Local pattern file missing (tmbmf.ptn.local not found)',
                'resolution': 'Check pattern file location, verify file permissions, download patterns manually, restore from backup',
                'impact': 'Critical - Anti-malware engine cannot function without pattern files',
                'ds_reference': 'Pattern File Management - Local Pattern File Recovery and Restoration Procedures'
            },
            'BPF_PROGRAM_LOADING_FAILED': {
                'severity': 'critical',
                'description': 'BPF program context not found (_bm_native__find_bpf_prog_ctx: cannot find pattern)',
                'resolution': 'Verify kernel eBPF support, check BPF program permissions, restart behavioral monitoring service',
                'impact': 'High - Advanced behavioral analysis unavailable',
                'ds_reference': 'eBPF Program Troubleshooting - BPF Context and Program Loading Issues'
            },
            'FEATURE_FILTERING_MISCONFIGURED': {
                'severity': 'warning',
                'description': 'Multiple security features disabled by filtering (Skip [feature] by filtering features)',
                'resolution': 'Review feature mask configuration, check policy settings, verify feature compatibility with current system',
                'impact': 'Medium - Reduced detection capabilities due to disabled features',
                'ds_reference': 'Feature Configuration Guide - Anti-Malware Feature Mask Settings'
            },
            'CLOUD_CONNECTIVITY_FAILED': {
                'severity': 'warning',
                'description': 'ICRC cloud connectivity timeout (dsaas.icrc.trendmicro.com timeout)',
                'resolution': 'Check network connectivity, verify proxy settings, configure firewall rules, test DNS resolution',
                'impact': 'Medium - Cannot receive cloud-based threat intelligence updates',
                'ds_reference': 'Cloud Connectivity Troubleshooting - ICRC Service Communication Requirements'
            },
            'PATTERN_PROPERTY_ACCESS_FAILED': {
                'severity': 'critical',
                'description': 'Pattern version verification failed (VSGetPatternProperty failed: rc=-99)',
                'resolution': 'Verify pattern file integrity, check pattern corruption, re-download patterns, restart TrendX engine',
                'impact': 'Critical - Cannot verify pattern versions or detect pattern corruption',
                'ds_reference': 'Pattern Integrity Verification - VSGetPatternProperty Error Resolution'
            },
            'SCAN_ENGINE_RESOURCE_FAILED': {
                'severity': 'error',
                'description': 'Scanning engine resource access failed (VSScanResource failed: error code -94)',
                'resolution': 'Check file system permissions, verify scan target accessibility, restart scanning service',
                'impact': 'High - Cannot scan specific files or resources',
                'ds_reference': 'Scan Engine Resource Management - File Access and Permission Issues'
            }
        }

    def parse_amsp_log_entry(self, line: str) -> Dict[str, Any]:
        """Parse AMSP-Inst_LocalDebugLog entry with enhanced format support"""
        patterns = [
            r'\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d+)\]\s*\[(\w+)\]\s*\[.*?\]\s*(.+)',
            r'\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\]\s+(\w+):\s+(.+)',
            r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d+)\s+\[(\w+)\]\s+(.+)',
            r'(\d{2}/\d{2}/\d{4} \d{1,2}:\d{2}:\d{2} (?:AM|PM))\s+-\s+(\w+)\s+-\s+(.+)',
            r'\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\]\s+\[\d+:\d+\]\s+(\w+)\s+(.+)',
            r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\s+(\w+)\s+(.+)',
            r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d+)\s+\[(\w+)\]\s+\[.*?\]\s+\[.*?\]\s+(.+)'
        ]
        
        for pattern in patterns:
            match = re.match(pattern, line.strip())
            if match:
                timestamp, level, message = match.groups()
                
                context = self.extract_log_context(message)
                
                return {
                    'timestamp': timestamp,
                    'level': level.upper(),
                    'message': message.strip(),
                    'raw_line': line,
                    'parsed': True,
                    'context': context
                }
        
        return {'raw_line': line, 'parsed': False}

    def extract_log_context(self, message: str) -> Dict[str, str]:
        """Extract additional context from AMSP log message"""
        context = {}
        
        file_match = re.search(r'[A-Za-z]:[\\\/][^\\\/\s]+(?:[\\\/][^\\\/\s]+)*', message)
        if file_match:
            context['file_path'] = file_match.group()
        
        op_id_match = re.search(r'(?:Operation|Op|ID)[\s:]+([A-F0-9]{8,})', message, re.IGNORECASE)
        if op_id_match:
            context['operation_id'] = op_id_match.group(1)
        
        error_code_match = re.search(r'(?:Error|Code|Err)[\s:]+([0-9x][0-9A-Fa-f]+)', message, re.IGNORECASE)
        if error_code_match:
            context['error_code'] = error_code_match.group(1)
        
        component_match = re.search(r'(tmcomm|tmebc|amsp|dsm|relay|agent)', message, re.IGNORECASE)
        if component_match:
            context['component'] = component_match.group(1).lower()
        
        return context

    def categorize_amsp_severity(self, log_entry: Dict[str, Any]) -> str:
        """Categorize AMSP log entry severity with enhanced ds_am.log specific detection"""
        if not log_entry.get('parsed'):
            return 'unknown'
        
        message = log_entry['message'].lower()
        level = log_entry['level'].lower()
        
        # First check for known critical patterns from ds_am.log analysis
        critical_indicators = [
            # Pattern loading failures (most critical)
            r'vsreadviruspattern.*failed.*ret=-2',
            r'bm_load_pattern_buf.*failed.*-17',
            r'bmtrap.*cannot find pattern',
            # TrendX engine failures
            r'trendx.*engine.*failed',
            r'trendx.*initialization.*failed',
            r'trendx.*startup.*error',
            # BPF program issues
            r'bpf.*program.*failed',
            r'bpf.*load.*error',
            r'behavioral.*monitoring.*failed',
            # Service critical failures
            r'service.*failed.*to.*start',
            r'daemon.*initialization.*failed',
            r'core.*engine.*unavailable'
        ]
        
        for pattern in critical_indicators:
            if re.search(pattern, message, re.IGNORECASE):
                return 'critical'
        
        # Standard level-based categorization
        if level in ['critical', 'fatal', 'error']:
            return 'critical'
        elif level in ['warning', 'warn']:
            return 'warning'
        elif level in ['info', 'information', 'debug', 'trace']:
            return 'info'
        
        # Check standard error patterns
        for pattern in self.error_patterns['critical']:
            if re.search(pattern, message, re.IGNORECASE):
                return 'critical'
        
        # Enhanced warning detection for ds_am.log specific issues
        warning_indicators = [
            r'icrc.*timeout',
            r'feature.*filtering.*failed',
            r'metrics.*collection.*failed',
            r'pattern.*file.*not.*found',
            r'cloud.*connectivity.*timeout',
            r'configuration.*validation.*failed'
        ]
        
        for pattern in warning_indicators:
            if re.search(pattern, message, re.IGNORECASE):
                return 'warning'
        
        for pattern in self.error_patterns['warning']:
            if re.search(pattern, message, re.IGNORECASE):
                return 'warning'
        
        return 'info'

    def identify_amsp_operation(self, log_entry: Dict[str, Any]) -> str:
        """Identify AMSP operation type"""
        if not log_entry.get('parsed'):
            return 'unknown'
        
        message = log_entry['message'].lower()
        
        for operation, patterns in self.installation_patterns.items():
            for pattern in patterns:
                if re.search(pattern, message, re.IGNORECASE):
                    return operation.replace('_', ' ').title()
        
        return 'General Operation'

    def analyze_log_file(self, file_path: str) -> Dict[str, Any]:
        """Analyze AMSP log file comprehensively"""
        # Analysis initialization - 5% progress
        self._update_progress('File Parsing & Initial Analysis', 'Starting AMSP log analysis...', 5)
        
        results = {
            'summary': {
                'total_lines': 0,
                'parsed_lines': 0,
                'error_count': 0,
                'warning_count': 0,
                'critical_count': 0,
                'installation_operations': 0,
                'service_operations': 0,
                'update_operations': 0,
                'timespan': {'start': None, 'end': None}
            },
            'installation_summary': {
                'driver_installations': 0,
                'service_startups': 0,
                'pattern_updates': 0,
                'configuration_changes': 0,
                'failures': 0
            },
            'errors': [],
            'warnings': [],
            'critical_issues': [],
            'operation_analysis': {},
            'known_issues': [],
            'recommendations': []
        }

        # File parsing phase - 10% progress
        self._update_progress('File Parsing & Initial Analysis', 'Reading AMSP log file...', 10)
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
                total_lines = len(lines)
                
                # Progress tracking for file parsing (10%-50%)
                for line_num, line in enumerate(lines, 1):
                    if line_num > 10000:
                        break
                    
                    # Update progress during parsing
                    if line_num % max(1, total_lines // 20) == 0:  # Update every 5% of file
                        progress = 10 + int((line_num / min(total_lines, 10000)) * 40)
                        self._update_progress('File Parsing & Initial Analysis', f'Processing AMSP log entries... ({line_num}/{total_lines})', progress)
                    
                    results['summary']['total_lines'] += 1
                    line = line.strip()
                    
                    if not line:
                        continue
                    
                    log_entry = self.parse_amsp_log_entry(line)
                    
                    if log_entry['parsed']:
                        results['summary']['parsed_lines'] += 1
                        
                        if not results['summary']['timespan']['start']:
                            results['summary']['timespan']['start'] = log_entry['timestamp']
                        results['summary']['timespan']['end'] = log_entry['timestamp']
                        
                        severity = self.categorize_amsp_severity(log_entry)
                        operation = self.identify_amsp_operation(log_entry)
                        
                        if severity == 'critical':
                            results['summary']['critical_count'] += 1
                            results['critical_issues'].append({
                                'line': line_num,
                                'timestamp': log_entry['timestamp'],
                                'operation': operation,
                                'message': log_entry['message'],
                                'level': log_entry['level']
                            })
                        elif severity == 'warning':
                            results['summary']['warning_count'] += 1
                            results['warnings'].append({
                                'line': line_num,
                                'timestamp': log_entry['timestamp'],
                                'operation': operation,
                                'message': log_entry['message'],
                                'level': log_entry['level']
                            })
                        elif severity == 'error':
                            results['summary']['error_count'] += 1
                            results['errors'].append({
                                'line': line_num,
                                'timestamp': log_entry['timestamp'],
                                'operation': operation,
                                'message': log_entry['message'],
                                'level': log_entry['level']
                            })
                        
                        if operation not in results['operation_analysis']:
                            results['operation_analysis'][operation] = {
                                'total_entries': 0,
                                'errors': 0,
                                'warnings': 0,
                                'successes': 0
                            }
                        
                        results['operation_analysis'][operation]['total_entries'] += 1
                        if severity in ['critical', 'error']:
                            results['operation_analysis'][operation]['errors'] += 1
                        elif severity == 'warning':
                            results['operation_analysis'][operation]['warnings'] += 1
                        else:
                            results['operation_analysis'][operation]['successes'] += 1
                        
                        if 'driver' in operation.lower() or 'install' in operation.lower():
                            results['summary']['installation_operations'] += 1
                            results['installation_summary']['driver_installations'] += 1
                        elif 'service' in operation.lower():
                            results['summary']['service_operations'] += 1
                            results['installation_summary']['service_startups'] += 1
                        elif 'pattern' in operation.lower() or 'update' in operation.lower():
                            results['summary']['update_operations'] += 1
                            results['installation_summary']['pattern_updates'] += 1
                        elif 'config' in operation.lower():
                            results['installation_summary']['configuration_changes'] += 1
            
            # Analysis and recommendations generation - 60% progress
            self._update_progress('ML Pattern Recognition & Analysis', 'Generating AMSP recommendations...', 60)
            results['recommendations'] = self.generate_amsp_recommendations(results)
            
            # Dynamic RAG Integration for AMSP Analysis - 70% progress
            self._update_progress('Dynamic RAG & AI Intelligence', 'Starting Dynamic RAG analysis...', 70)
            if DYNAMIC_RAG_AVAILABLE:
                try:
                    # Try Dynamic RAG first for intelligent prompt generation
                    try:
                        # Read log content for dynamic analysis
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            log_content = f.read()
                        
                        from dynamic_rag_system import apply_dynamic_rag_to_analysis
                        self._update_progress('Dynamic RAG & AI Intelligence', 'Processing with Claude AI...', 80)
                        results = apply_dynamic_rag_to_analysis(results, log_content)
                        self._update_progress('Dynamic RAG & AI Intelligence', 'Dynamic RAG analysis completed', 90)
                        
                        dynamic_rag = results.get('dynamic_rag_analysis', {})
                        if dynamic_rag and 'error' not in dynamic_rag:
                            print(f"✅ Dynamic RAG Analysis (AMSP): {dynamic_rag.get('analysis_metadata', {}).get('knowledge_sources_used', 0)} sources")
                            
                            # Add dynamic insights to recommendations
                            if dynamic_rag.get('ai_response'):
                                ai_summary = dynamic_rag['ai_response'][:200] + "..." if len(dynamic_rag['ai_response']) > 200 else dynamic_rag['ai_response']
                                results['recommendations'].append(f'🧠 <strong>AI AMSP Analysis</strong>: {ai_summary}')
                                
                    except Exception as dynamic_error:
                        print(f"⚠️  Dynamic RAG failed for AMSP: {dynamic_error}")
                            
                except Exception as e:
                    print(f"⚠️  RAG integration failed for AMSP: {e}")
            
        except Exception as e:
            raise SecurityError(f"Error analyzing AMSP log file: {str(e)}")
        
        # Analysis complete - 100% progress
        self._update_progress('Report Generation & Finalization', 'AMSP analysis completed successfully!', 100)
        
        # Standardize return structure for frontend compatibility
        return results

    def generate_amsp_recommendations(self, analysis: Dict[str, Any]) -> List[str]:
        """Generate AMSP-specific recommendations with ds_am.log root cause analysis"""
        recommendations = []
        
        # Analyze critical issues and provide specific root cause analysis
        critical_issues = analysis.get('critical_errors', [])
        error_issues = analysis.get('errors', [])
        warning_issues = analysis.get('warnings', [])
        
        # Pattern loading failures analysis
        pattern_failures = []
        bpf_failures = []
        trendx_failures = []
        feature_filtering_issues = []
        cloud_connectivity_issues = []
        
        # Analyze all critical and error messages for specific root causes
        all_issues = critical_issues + error_issues + warning_issues
        
        for issue in all_issues:
            message = issue.get('message', '').lower()
            
            # VSReadVirusPattern failures
            if re.search(r'vsreadviruspattern.*failed.*ret=-2', message, re.IGNORECASE):
                pattern_failures.append({
                    'type': 'VSReadVirusPattern failure',
                    'error_code': 'ret=-2',
                    'timestamp': issue.get('timestamp', ''),
                    'line': issue.get('line', '')
                })
            
            # BPF/bmtrap issues
            if re.search(r'bmtrap.*cannot find pattern|bm_load_pattern_buf.*failed.*-17', message, re.IGNORECASE):
                bpf_failures.append({
                    'type': 'BPF program loading failure',
                    'error_code': 'ENOENT (-17)' if '-17' in message else 'Pattern not found',
                    'timestamp': issue.get('timestamp', ''),
                    'line': issue.get('line', '')
                })
            
            # TrendX engine issues
            if re.search(r'trendx.*engine.*failed|trendx.*initialization.*failed', message, re.IGNORECASE):
                trendx_failures.append({
                    'type': 'TrendX engine failure',
                    'timestamp': issue.get('timestamp', ''),
                    'line': issue.get('line', '')
                })
            
            # Feature filtering issues
            if re.search(r'feature.*filtering.*failed', message, re.IGNORECASE):
                feature_filtering_issues.append({
                    'type': 'Feature filtering misconfiguration',
                    'timestamp': issue.get('timestamp', ''),
                    'line': issue.get('line', '')
                })
            
            # Cloud connectivity timeouts
            if re.search(r'icrc.*timeout|cloud.*connectivity.*timeout', message, re.IGNORECASE):
                cloud_connectivity_issues.append({
                    'type': 'Cloud connectivity timeout',
                    'timestamp': issue.get('timestamp', ''),
                    'line': issue.get('line', '')
                })
        
        # Generate specific root cause analysis based on detected patterns
        if pattern_failures:
            recommendations.append('<i class="fa-solid fa-circle-exclamation text-danger me-2"></i><strong>CRITICAL: Pattern Loading Failures Detected</strong>')
            recommendations.append(f'🔍 <strong>Root Cause Analysis</strong>: {len(pattern_failures)} VSReadVirusPattern failures with error code ret=-2')
            recommendations.append('💡 <strong>Resolution</strong>: Pattern files may be corrupted or missing. Check /opt/TrendMicro/amsp/pattern/ directory and reload patterns')
            recommendations.append('📋 <strong>Action Items</strong>: 1) Verify pattern file integrity 2) Check disk space 3) Restart AMSP service 4) Update pattern files')
        
        if bpf_failures:
            recommendations.append('<i class="fa-solid fa-triangle-exclamation text-warning me-2"></i><strong>CRITICAL: BPF Program Loading Failures</strong>')
            recommendations.append(f'🔍 <strong>Root Cause Analysis</strong>: {len(bpf_failures)} BPF/bmtrap failures - behavioral monitoring unavailable')
            recommendations.append('💡 <strong>Resolution</strong>: BPF patterns missing or kernel compatibility issues. Check behavioral monitoring configuration')
            recommendations.append('📋 <strong>Action Items</strong>: 1) Verify kernel BPF support 2) Check bmtrap configuration 3) Reload behavioral patterns 4) Review system compatibility')
        
        if trendx_failures:
            recommendations.append('<i class="fa-solid fa-engine text-danger me-2"></i><strong>CRITICAL: TrendX Engine Failures</strong>')
            recommendations.append(f'🔍 <strong>Root Cause Analysis</strong>: {len(trendx_failures)} TrendX engine initialization failures detected')
            recommendations.append('💡 <strong>Resolution</strong>: Core scanning engine unavailable. Critical service dependency failure')
            recommendations.append('📋 <strong>Action Items</strong>: 1) Restart TrendX service 2) Check engine dependencies 3) Verify installation integrity 4) Review system resources')
        
        if feature_filtering_issues:
            recommendations.append('<i class="fa-solid fa-filter text-warning me-2"></i><strong>WARNING: Feature Filtering Misconfiguration</strong>')
            recommendations.append(f'🔍 <strong>Root Cause Analysis</strong>: {len(feature_filtering_issues)} feature filtering failures - security features may be disabled')
            recommendations.append('💡 <strong>Resolution</strong>: Feature configuration mismatch. Review AMSP feature settings')
            recommendations.append('📋 <strong>Action Items</strong>: 1) Check feature configuration 2) Validate license permissions 3) Review policy settings 4) Restart configuration service')
        
        if cloud_connectivity_issues:
            recommendations.append('<i class="fa-solid fa-cloud-exclamation text-info me-2"></i><strong>INFO: Cloud Connectivity Issues</strong>')
            recommendations.append(f'🔍 <strong>Root Cause Analysis</strong>: {len(cloud_connectivity_issues)} ICRC timeout events - offline operation mode')
            recommendations.append('💡 <strong>Resolution</strong>: Expected behavior in offline environments. Monitor for extended connectivity loss')
            recommendations.append('📋 <strong>Action Items</strong>: 1) Verify network connectivity 2) Check proxy settings 3) Review firewall rules 4) Validate cloud service status')
        
        # Standard analysis for general issues
        if analysis['summary']['critical_count'] > 0 and not any([pattern_failures, bpf_failures, trendx_failures]):
            recommendations.append('<i class="fa-solid fa-circle-exclamation me-2"></i>Critical AMSP issues detected - immediate attention required')
        
        if analysis['installation_summary']['failures'] > 0:
            recommendations.append('<i class="fa-solid fa-triangle-exclamation me-2"></i>Installation failures detected - review AMSP setup')
        
        if analysis['summary']['error_count'] > 5:
            recommendations.append('<i class="fa-solid fa-wrench me-2"></i>Multiple AMSP errors detected - check service configuration')
        
        # Operation-specific analysis
        for operation, stats in analysis['operation_analysis'].items():
            if stats['errors'] > 2:
                recommendations.append(f'<i class="fa-solid fa-search me-2"></i>{operation}: High error count - investigate operation issues')
        
        # Overall system health assessment
        if not recommendations:
            recommendations.append('<i class="fa-solid fa-check-circle text-success"></i> No critical AMSP issues detected - anti-malware appears to be functioning normally')
        else:
            # Add summary recommendation
            total_critical = len(pattern_failures) + len(bpf_failures) + len(trendx_failures)
            if total_critical > 0:
                recommendations.insert(0, f'<i class="fa-solid fa-exclamation-triangle text-danger me-2"></i><strong>SYSTEM STATUS: {total_critical} Critical Anti-Malware Issues Requiring Immediate Attention</strong>')
        
        return recommendations

    def analyze(self, file_paths: Union[str, List[str]]) -> Dict[str, Any]:
        """Standardized analysis entry point for AMSP logs"""
        try:
            self._update_progress("Initialization", "Starting AMSP log analysis", 1)
            
            # Normalize input to list and validate
            if isinstance(file_paths, str):
                file_paths = [file_paths]
            
            if not file_paths:
                raise ValueError("No AMSP log files provided for analysis")
            
            # AMSP analyzer currently only supports single file analysis
            log_file = file_paths[0]
            
            self._update_progress("Log Analysis", "Analyzing AMSP log file", 30)
            analysis_results = self.analyze_log_file(log_file)
            
            self._update_progress("Standardization", "Converting to standardized format", 90)
            
            # Apply standardized output format
            standardized_result = self._standardize_analyzer_output(analysis_results, 'amsp')
            
            # Add metadata
            standardized_result['metadata'] = {
                'files_processed': len(file_paths),
                'log_file': os.path.basename(log_file),
                'total_lines': analysis_results.get('total_lines', 0),
                'errors_found': len(analysis_results.get('errors', [])),
                'warnings_found': len(analysis_results.get('warnings', [])),
                'pattern_failures': len(analysis_results.get('pattern_failures', [])),
                'bpf_failures': len(analysis_results.get('bpf_failures', [])),
                'trendx_failures': len(analysis_results.get('trendx_failures', []))
            }
            
            # Generate formatted output using existing formatter
            from routes import format_amsp_results
            formatted_html = format_amsp_results(analysis_results)
            standardized_result['formatted_output'] = formatted_html
            
            self._update_progress("Completion", "AMSP log analysis completed", 100)
            return standardized_result
            
        except Exception as e:
            error_msg = f"AMSP log analysis failed: {str(e)}"
            self._update_progress("Error", error_msg, None)
            return {
                'analysis_type': 'amsp',
                'status': 'error',
                'summary': error_msg,
                'details': [error_msg],
                'recommendations': ['Please ensure valid AMSP log files are provided'],
                'severity': 'high',
                'error': True,
                'metadata': {
                    'files_processed': len(file_paths) if 'file_paths' in locals() else 0,
                    'error_type': 'analysis_failure'
                }
            }


class ConflictAnalyzer(AnalyzerOutputStandardizer):
    """AntiVirus Conflict Analyzer"""
    
    def extract_processes_from_xml(self, xml_path: str) -> List[str]:
        """Extract process names from RunningProcess.xml"""
        try:
            validate_xml_content(xml_path)
            
            with open(xml_path, 'rb') as f:
                content = f.read()
            
            root = ET.fromstring(content)
            processes = []
            
            host_metadata_elements = root.findall(".//HostMetaData")
            
            for host in host_metadata_elements:
                for attr in host.findall(".//Attribute"):
                    if attr.attrib.get("name") == "process":
                        proc_name = attr.attrib.get("value")
                        if proc_name:
                            sanitized_name = sanitize_process_name(proc_name)
                            if sanitized_name:
                                processes.append(sanitized_name)
            
            return processes
            
        except SecurityError as e:
            raise SecurityError(f"XML processing failed: {str(e)}")
        except Exception as e:
            raise SecurityError(f"Unexpected error processing XML: {str(e)}")

    def analyze_conflicts(self, process_list: List[str]) -> str:
        """Analyze for AV conflicts"""
        try:
            if not process_list:
                return "No processes found to analyze"
            
            # Limit process list to prevent API overload
            if len(process_list) > 500:  # Reduced from 1000 for better performance
                process_list = process_list[:500]
            
            # Check if OpenAI is available
            if not OPENAI_AVAILABLE:
                return "OpenAI library not available for analysis"
            
            from config import get_config
            config = get_config()
            
            # Validate API configuration
            if not config.OPENAI_API_KEY:
                return "OpenAI API key not configured"
            
            try:
                # Use basic OpenAI client without httpx dependency
                client = OpenAI(
                    api_key=config.OPENAI_API_KEY,
                    base_url=config.OPENAI_BASE_URL,
                    timeout=30.0
                )
            except Exception as e:
                return f"Failed to initialize OpenAI client: {str(e)}"
                
            prompt = (
                "You are a Trend Micro Deep Security Anti-Malware expert. "
                "Given this list of running processes from a RunningProcess.xml file, "
                "analyze and identify if there are any conflicting anti-virus or security software "
                "that could prevent Trend Micro Deep Security Anti-Malware from installing or operating normally. "
                "Format your response as follows:\n"
                "1. Start with a summary (CONFLICTS DETECTED or NO CONFLICTS DETECTED)\n"
                "2. List each conflicting software with details and reasoning\n\n"
                f"Running Processes ({len(process_list)} total):\n{chr(10).join(process_list)}"
            )
            
            try:
                response = client.chat.completions.create(
                    model=config.OPENAI_MODEL,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=4000,
                    temperature=0.3,
                    timeout=30  # Add timeout to prevent hanging
                )
                
                text = response.choices[0].message.content
                
            except Exception as api_error:
                return f"API call failed: {str(api_error)}"
            
            conflicts = self.parse_conflict_response(text)
            
            # Return just the raw AI response text, not HTML formatted
            return text
            
        except Exception as e:
            return f"Unexpected error analyzing conflicts: {str(e)}"

    def parse_conflict_response(self, response_text: str) -> List[Dict[str, str]]:
        """Parse AI response to extract conflict information"""
        conflicts = []
        
        # Safety check for None or empty response
        if not response_text:
            return conflicts
            
        lines = response_text.split('\n')
        current_conflict = {}
        
        # First check if this is actually a conflicts detected response
        has_conflicts = False
        for line in lines:
            if "CONFLICTS DETECTED" in line.upper() and "NO CONFLICTS DETECTED" not in line.upper():
                has_conflicts = True
                break
            if "NO CONFLICTS DETECTED" in line.upper():
                has_conflicts = False
                break
        
        # Only parse conflicts if we actually detected conflicts
        if not has_conflicts:
            return []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Look for numbered conflict sections (### 1. Norton, etc.)
            if line.startswith("###") and any(char.isdigit() for char in line):
                if current_conflict:
                    conflicts.append(current_conflict)
                
                # Extract software name
                software_name = line.replace("###", "").strip()
                if "." in software_name:
                    software_name = software_name.split(".", 1)[1].strip()
                software_name = software_name.replace("*", "").strip()
                
                current_conflict = {'name': software_name, 'description': ''}
            elif line.startswith(('-', '*', '•')) and current_conflict:
                # Only add details to existing conflict, don't create new ones
                detail = line.lstrip('- *•').strip()
                if current_conflict.get('description'):
                    current_conflict['description'] += f" {detail}"
                else:
                    current_conflict['description'] = detail
        
        # Add final conflict if exists
        if current_conflict:
            conflicts.append(current_conflict)
        
        return conflicts

    def format_conflict_results(self, analysis_text: str, conflicts: List[Dict], status: str) -> str:
        """Format conflict analysis results"""
        
        if status == "error":
            status_color = "#dc3545"
            status_text = "ANALYSIS ERROR"
            status_icon = "� �"
        elif conflicts:  # Only check conflicts list, not text content
            status_color = "#fd7e14"
            status_text = "CONFLICTS DETECTED"
            status_icon = '<i class="fa-solid fa-triangle-exclamation text-warning"></i>'
        elif status == "no_processes":
            status_color = "#6c757d"
            status_text = "NO PROCESSES TO ANALYZE"
            status_icon = "i� "
        else:
            status_color = "#198754"
            status_text = "NO CONFLICTS DETECTED"
            status_icon = '<i class="fa-solid fa-check-circle text-success"></i>'
        
        html = f"""
        <div class="mb-4">
            <h4 style="color: {status_color};">{status_icon} AntiVirus Conflict Analysis - Status: {status_text}</h4>
        </div>
        
        <div class="row mb-4">
            <div class="col-md-6">
                <div class="card">
                    <div class="card-header"><i class="fa-solid fa-chart-bar me-2"></i>Analysis Summary</div>
                    <div class="card-body">
                        <p><strong>Status:</strong> <span style="color: {status_color};">{status_text}</span></p>
                        <p><strong>Conflicts Found:</strong> {len(conflicts)}</p>
                        <p><strong>Analysis Date:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                    </div>
                </div>
            </div>
            <div class="col-md-6">
                <div class="card">
                    <div class="card-header"><i class="fa-solid fa-info-circle me-2"></i>Analysis Summary</div>
                    <div class="card-body">
        """
        
        if conflicts:
            html += f'<p><i class="fa-solid fa-triangle-exclamation me-2 text-warning"></i>{len(conflicts)} conflicting software detected</p>'
            html += '<ul>'
            for conflict in conflicts[:3]:
                html += f'<li class="mb-2">{conflict.get("name", "Unknown software")}</li>'
            html += '</ul>'
        else:
            html += '<p><i class="fa-solid fa-check-circle me-2 text-success"></i>No conflicts detected - system appears compatible</p>'
        
        html += """
                    </div>
                </div>
            </div>
        </div>
        """
        
        html += """
        <div class="row mb-4">
            <div class="col-12">
                <div class="card">
                    <div class="card-header"><i class="fa-solid fa-search"></i> Detailed Analysis Results</div>
                    <div class="card-body">
                        <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; border-left: 4px solid #007bff;">
        """
        
        lines = analysis_text.splitlines()
        for line in lines:
            line = line.strip()
            if line:
                if line.startswith(("-", "*", "•")):
                    html += f'<p style="margin-bottom: 8px;"><strong>• {line[1:].strip()}</strong></p>'
                elif ":" in line and len(line) < 100:
                    html += f'<h6 style="color: #495057; margin-top: 15px; margin-bottom: 8px;">{line}</h6>'
                else:
                    html += f'<p style="margin-bottom: 8px;">{line}</p>'
        
        html += """
        #                         </div>
        #                     </div>
        #                 </div>
        #             </div>
        #         </div>
        """
        
        if conflicts:
            html += """
            <div class="row mb-4">
                <div class="col-12">
                    <div class="card">
                        <div class="card-header"><i class="fa-solid fa-triangle-exclamation text-warning"></i> Detected Conflicts</div>
                        <div class="card-body">
                            <div class="table-responsive">
                                <table class="table table-striped">
        #                                     <thead>
        #                                         <tr>
        #                                             <th>Software/Process</th>
        #                                             <th>Description</th>
        #                                             <th>Recommended Action</th>
        #                                         </tr>
        #                                     </thead>
        #                                     <tbody>
            """
            
            for conflict in conflicts:
                name = conflict.get('name', 'Unknown')
                description = conflict.get('description', 'Potential conflict detected')
                recommendation = conflict.get('recommendation', 'Review compatibility')
                
                html += f"""
        #                                         <tr>
        #                                             <td><strong>{name}</strong></td>
        #                                             <td>{description}</td>
        #                                             <td>{recommendation}</td>
        #                                         </tr>
                """
            
            html += """
        #                                     </tbody>
        #                                 </table>
        #                             </div>
        #                         </div>
        #                     </div>
        #                 </div>
        #             </div>
            """
        
        return html

    def analyze(self, file_paths: Union[str, List[str]]) -> Dict[str, Any]:
        """Standardized analysis entry point for conflict analysis"""
        try:
            self._update_progress("Initialization", "Starting conflict analysis", 1)
            
            # Normalize input to list and validate
            if isinstance(file_paths, str):
                file_paths = [file_paths]
            
            if not file_paths:
                raise ValueError("No files provided for conflict analysis")
            
            # Find RunningProcesses.xml file
            xml_file = None
            for file_path in file_paths:
                if file_path.lower().endswith('.xml') and 'runningprocess' in file_path.lower():
                    xml_file = file_path
                    break
            
            if not xml_file:
                return {
                    'analysis_type': 'conflict',
                    'status': 'error',
                    'summary': 'No RunningProcesses.xml file found',
                    'details': ['Conflict analysis requires RunningProcesses.xml file'],
                    'recommendations': ['Please provide the RunningProcesses.xml file from the diagnostic package'],
                    'severity': 'medium',
                    'error': True,
                    'metadata': {
                        'files_processed': len(file_paths),
                        'error_type': 'missing_xml_file'
                    }
                }
            
            self._update_progress("XML Processing", "Extracting process information", 30)
            processes = self.extract_processes_from_xml(xml_file)
            
            self._update_progress("Conflict Analysis", "Analyzing for AV conflicts", 70)
            analysis_html = self.analyze_conflicts(processes)
            
            self._update_progress("Standardization", "Converting to standardized format", 90)
            
            # Convert HTML analysis to structured format
            conflicts_found = "POTENTIAL CONFLICTS DETECTED" in analysis_html or "conflict" in analysis_html.lower()
            severity = 'high' if conflicts_found else 'low'
            
            # Extract key insights from HTML
            details = []
            recommendations = []
            
            if conflicts_found:
                details.append("Potential antivirus conflicts detected in running processes")
                recommendations.extend([
                    "Review conflicting antivirus software and consider removal",
                    "Ensure only one real-time antivirus solution is active",
                    "Add Deep Security Agent to exclusions in other security products",
                    "Contact support for assistance with conflict resolution"
                ])
            else:
                details.append("No significant antivirus conflicts detected")
                recommendations.extend([
                    "Monitor system performance regularly",
                    "Keep security software updated",
                    "Review exclusions if performance issues occur"
                ])
            
            # Apply standardized output format
            standardized_result = self._standardize_analyzer_output({
                'conflicts_detected': conflicts_found,
                'processes_analyzed': len(processes),
                'analysis_html': analysis_html
            }, 'conflict')
            
            # Override with specific conflict analysis details
            standardized_result.update({
                'summary': f"Conflict analysis completed - {'Conflicts detected' if conflicts_found else 'No conflicts found'}",
                'details': details,
                'recommendations': recommendations,
                'severity': severity,
                'formatted_output': analysis_html,
                'metadata': {
                    'files_processed': len(file_paths),
                    'xml_file': os.path.basename(xml_file),
                    'processes_analyzed': len(processes),
                    'conflicts_detected': conflicts_found
                }
            })
            
            self._update_progress("Completion", "Conflict analysis completed", 100)
            return standardized_result
            
        except Exception as e:
            error_msg = f"Conflict analysis failed: {str(e)}"
            self._update_progress("Error", error_msg, None)
            return {
                'analysis_type': 'conflict',
                'status': 'error',
                'summary': error_msg,
                'details': [error_msg],
                'recommendations': ['Please ensure valid RunningProcesses.xml file is provided'],
                'severity': 'high',
                'error': True,
                'metadata': {
                    'files_processed': len(file_paths) if 'file_paths' in locals() else 0,
                    'error_type': 'analysis_failure'
                }
            }


class ResourceAnalyzer(AnalyzerOutputStandardizer):
    """Resource Analyzer for exclusion recommendations with progress tracking"""
    
    def __init__(self, session_manager=None, session_id=None, rag_system=None, ml_analyzer=None):
        """Initialize with optional progress tracking, RAG system, and ML analyzer"""
        self.session_manager = session_manager
        self.session_id = session_id
        self.rag_system = rag_system
        self.ml_analyzer = ml_analyzer
    
    def _update_progress(self, percentage):
        """Update analysis progress if session manager is available"""
        if self.session_manager and self.session_id:
            try:
                progress_data = {
                    'analysis_stage': 'Resource Analysis',
                    'progress_message': f'Analyzing resource conflicts and exclusions... ({percentage}%)',
                    'status': 'processing',
                    'progress_percentage': percentage
                }
                
                self.session_manager.update_session(self.session_id, progress_data)
                print(f"📊 Resource Analysis Progress: {percentage}%")
            except Exception as e:
                print(f"⚠️ Resource Analysis Progress update failed: {e}")
        else:
            # Fallback to console logging
            print(f"📊 Resource Analysis: {percentage}%")
    
    def extract_processes_from_xml(self, xml_path: str) -> List[str]:
        """Extract process names from RunningProcess.xml"""
        try:
            validate_xml_content(xml_path)
            
            with open(xml_path, 'rb') as f:
                content = f.read()
            
            root = ET.fromstring(content)
            processes = []
            
            host_metadata_elements = root.findall(".//HostMetaData")
            
            for host in host_metadata_elements:
                for attr in host.findall(".//Attribute"):
                    if attr.attrib.get("name") == "process":
                        proc_name = attr.attrib.get("value")
                        if proc_name:
                            sanitized_name = sanitize_process_name(proc_name)
                            if sanitized_name:
                                processes.append(sanitized_name)
            
            return processes
            
        except SecurityError as e:
            raise SecurityError(f"XML processing failed: {str(e)}")
        except Exception as e:
            raise SecurityError(f"Unexpected error processing XML: {str(e)}")

    def parse_top_n_busy_process(self, txt_path: str) -> List[Dict]:
        """Parse TopNBusyProcess.txt"""
        try:
            busy_processes = []
            with open(txt_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
            
            proc = {}
            for line in lines:
                line = line.strip()
                if line.startswith("Top 10 Busy Proc"):
                    if proc:
                        busy_processes.append(proc)
                        proc = {}
                elif "=" in line and len(line) < 1000:  # Prevent extremely long lines
                    try:
                        key, val = line.split("=", 1)
                        key = key.strip()
                        val = val.strip()
                        
                        # Sanitize values
                        if key and val:
                            proc[sanitize_process_name(key)] = sanitize_process_name(val)
                    except ValueError:
                        # Skip malformed lines
                        continue
            
            # Add the last process if exists
            if proc:
                busy_processes.append(proc)
            
            return busy_processes
            
        except Exception as e:
            raise SecurityError(f"Error parsing TopNBusyProcess.txt: {str(e)}")

    def analyze_resource_conflicts(self, process_list: List[str], busy_processes: List[Dict]) -> Dict[str, Any]:
        """Analyze for resource conflicts and exclusion recommendations with enhanced ML/RAG support"""
        
        # Analysis initialization - 5% progress
        self._update_progress(5)
        
        analysis_result = {
            'analysis_text': '',
            'candidates': [],
            'status': 'unknown',
            'ml_insights': None,
            'rag_insights': None,
            'security_impact': {},
            'performance_metrics': {},
            'recommendations': []
        }
        
        try:
            # Process filtering - 15% progress
            self._update_progress(15)
            
            def is_trend_micro(proc_name):
                name = proc_name.lower()
                tm_indicators = [
                    "trend micro", "pccnt", "dsagent", "deep security", "tmcomm", 
                    "tmebc", "amsp", "aegis", "dsa_", "tmansrv", "tmlisten", 
                    "tmpfw", "tmproxy", "ntrtscan", "pccntmon", "tmbmsrv"
                ]
                return any(indicator in name for indicator in tm_indicators)

            # Validate inputs
            if not process_list or not busy_processes:
                analysis_result['status'] = 'no_files'
                analysis_result['analysis_text'] = "Insufficient data: Both RunningProcess.xml and TopNBusyProcess.txt are required for resource analysis."
                return analysis_result

            # Process correlation analysis - 30% progress
            self._update_progress(30)
            
            running_set = set()
            for proc in process_list:
                base = os.path.basename(proc).lower()
                running_set.add(base)

            candidates = []
            for proc in busy_processes:
                name = proc.get("Name", "").strip().lower()
                base = os.path.basename(name)
                if not name or is_trend_micro(name):
                    continue
                if base in running_set:
                    candidate = {
                        "name": name,
                        "count": proc.get("Count", "N/A"),
                        "details": {k: v for k, v in proc.items() if k not in ("Name", "Count")},
                        "process_type": self._classify_process_type(name),
                        "security_assessment": self._assess_security_risk(name)
                    }
                    candidates.append(candidate)

            analysis_result['candidates'] = candidates
            
            # Performance metrics calculation - 50% progress
            self._update_progress(50)
            total_scan_count = sum(int(str(c.get('count', '0')).replace(',', '')) for c in candidates)
            analysis_result['performance_metrics'] = {
                'total_scan_count': total_scan_count,
                'high_impact_processes': len([c for c in candidates if int(str(c.get('count', '0')).replace(',', '')) > 1000]),
                'process_types': list(set(c['process_type'] for c in candidates)),
                'optimization_potential': 'High' if total_scan_count > 5000 else 'Medium' if total_scan_count > 2000 else 'Low'
            }

            # ML Enhancement for Dynamic RAG (Resource Analysis)
            if self.ml_analyzer and ML_AVAILABLE:
                try:
                    # Convert process data to text format for ML analysis
                    process_text = '\n'.join([
                        f"{proc['name']}: {proc.get('count', 'N/A')} scans" 
                        for proc in candidates[:50]
                    ])
                    
                    # Generate ML insights using the standalone function
                    from ml_analyzer import enhance_analysis_with_ml
                    ml_insights = enhance_analysis_with_ml(process_text, 'resource_conflicts')
                    
                    analysis_result['ml_insights'] = ml_insights
                    print(f"✅ ML Resource Analysis completed: {len(candidates)} candidates analyzed")
                except Exception as e:
                    print(f"⚠️  ML resource analysis failed: {e}")
                    analysis_result['ml_insights'] = None
            else:
                analysis_result['ml_insights'] = None

            # Dynamic RAG-Enhanced Analysis - 85% progress
            self._update_progress(85)
            if DYNAMIC_RAG_AVAILABLE:
                try:
                    # Read log content for dynamic analysis
                    process_content = '\n'.join([f"{proc['name']}: {proc.get('description', '')}" for proc in candidates[:20]])
                    
                    from dynamic_rag_system import apply_dynamic_rag_to_analysis
                    # Enhanced with ML insights for Dynamic RAG
                    analysis_result = apply_dynamic_rag_to_analysis(
                        analysis_result, 
                        process_content,
                        ml_insights=analysis_result.get('ml_insights')
                    )
                    
                    dynamic_rag = analysis_result.get('dynamic_rag_analysis', {})
                    if dynamic_rag and 'error' not in dynamic_rag:
                        print(f"✅ Dynamic RAG Resource Analysis: {dynamic_rag.get('analysis_metadata', {}).get('knowledge_sources_used', 0)} sources")
                        
                        # Add dynamic insights to recommendations
                        if dynamic_rag.get('ai_response'):
                            ai_summary = dynamic_rag['ai_response'][:200] + "..." if len(dynamic_rag['ai_response']) > 200 else dynamic_rag['ai_response']
                            analysis_result['recommendations'].append(f'🧠 <strong>AI Resource Analysis</strong>: {ai_summary}')
                    
                except Exception as e:
                    print(f"⚠️  Dynamic RAG resource analysis failed: {e}")
                    analysis_result['dynamic_rag_analysis'] = {'error': str(e)}

            # Enhanced AI Analysis with Deep Security context (following AV Conflict analyzer pattern)
            analysis_text = self._perform_ai_analysis(process_list, busy_processes, candidates, total_scan_count, analysis_result['performance_metrics'])
            analysis_result['analysis_text'] = analysis_text
            
            # Set status based on analysis
            if candidates:
                analysis_result['status'] = 'candidates_found'
            else:
                analysis_result['status'] = 'optimal'
                
            # Generate structured recommendations - 95% progress
            self._update_progress(95)
            analysis_result['recommendations'] = self._generate_enhanced_recommendations(
                candidates, analysis_result['performance_metrics'], analysis_result.get('ml_insights'), analysis_result.get('rag_insights')
            )
            
            # Analysis complete - 100% progress
            self._update_progress(100)
            return analysis_result
            
        except Exception as e:
            analysis_result['status'] = 'error'
            analysis_result['analysis_text'] = f"Error analyzing resource conflicts: {str(e)}"
            return analysis_result

    def _classify_process_type(self, process_name: str) -> str:
        """Classify process type for better analysis"""
        name_lower = process_name.lower()
        
        # Database processes
        if any(db in name_lower for db in ['sql', 'mysql', 'postgres', 'oracle', 'mongodb']):
            return 'Database'
        
        # Web servers and application servers
        if any(web in name_lower for web in ['apache', 'nginx', 'tomcat', 'iis', 'httpd']):
            return 'Web Server'
        
        # Development tools
        if any(dev in name_lower for dev in ['visual studio', 'devenv', 'code', 'eclipse', 'intellij']):
            return 'Development Tool'
        
        # System processes
        if any(sys in name_lower for sys in ['svchost', 'lsass', 'csrss', 'winlogon', 'services']):
            return 'System Process'
        
        # Backup software
        if any(backup in name_lower for backup in ['backup', 'veeam', 'acronis', 'carbonite']):
            return 'Backup Software'
        
        # Virtualization
        if any(vm in name_lower for vm in ['vmware', 'virtualbox', 'hyper-v', 'docker']):
            return 'Virtualization'
        
        # Office applications
        if any(office in name_lower for office in ['excel', 'word', 'outlook', 'powerpoint', 'winword']):
            return 'Office Application'
        
        return 'Application'

    def _assess_security_risk(self, process_name: str) -> str:
        """Assess security risk of excluding a process"""
        name_lower = process_name.lower()
        
        # High risk processes (should rarely be excluded)
        high_risk_indicators = ['powershell', 'cmd', 'script', 'python', 'java', 'node']
        if any(indicator in name_lower for indicator in high_risk_indicators):
            return 'High'
        
        # Medium risk processes  
        medium_risk_indicators = ['service', 'daemon', 'server', 'engine']
        if any(indicator in name_lower for indicator in medium_risk_indicators):
            return 'Medium'
        
        # Low risk processes (typically safe to exclude)
        low_risk_indicators = ['notepad', 'calculator', 'paint', 'media player']
        if any(indicator in name_lower for indicator in low_risk_indicators):
            return 'Low'
        
        return 'Medium'  # Default to medium risk

    def _prepare_ml_data(self, process_list: List[str], busy_processes: List[Dict], candidates: List[Dict]) -> Dict:
        """Prepare data for ML analysis"""
        return {
            'total_processes': len(process_list),
            'busy_processes': len(busy_processes),
            'candidates': candidates,
            'scan_counts': [int(str(c.get('count', '0')).replace(',', '')) for c in candidates],
            'process_types': [c.get('process_type', 'Unknown') for c in candidates],
            'security_risks': [c.get('security_assessment', 'Unknown') for c in candidates]
        }

    def _perform_ml_analysis(self, ml_data: Dict) -> Dict:
        """Perform ML-enhanced analysis on resource usage patterns"""
        try:
            from ml_analyzer import MLLogAnalyzer
            
            ml_analyzer = MLLogAnalyzer()
            
            # Calculate performance score based on scan patterns
            total_scans = sum(ml_data['scan_counts']) if ml_data['scan_counts'] else 0
            avg_scans = total_scans / len(ml_data['scan_counts']) if ml_data['scan_counts'] else 0
            
            # Performance scoring (100 = optimal, 0 = poor)
            if total_scans < 1000:
                performance_score = 100
            elif total_scans < 5000:
                performance_score = 80
            elif total_scans < 10000:
                performance_score = 60
            else:
                performance_score = 40
            
            # Identify resource patterns
            resource_patterns = []
            
            # High frequency pattern
            if avg_scans > 1000:
                resource_patterns.append({
                    'pattern_name': 'High Frequency Scanning',
                    'description': f'Average scan count of {avg_scans:.0f} per process indicates intensive file activity',
                    'impact': 'High performance impact - consider exclusions'
                })
            
            # Process type distribution pattern
            type_counts = {}
            for ptype in ml_data['process_types']:
                type_counts[ptype] = type_counts.get(ptype, 0) + 1
            
            dominant_type = max(type_counts, key=type_counts.get) if type_counts else 'Unknown'
            if type_counts.get(dominant_type, 0) > len(ml_data['candidates']) * 0.6:
                resource_patterns.append({
                    'pattern_name': f'{dominant_type} Dominance',
                    'description': f'{dominant_type} processes represent {type_counts[dominant_type]} of {len(ml_data["candidates"])} busy processes',
                    'impact': f'Consider {dominant_type.lower()}-specific exclusion strategies'
                })
            
            return {
                'total_processes': ml_data['total_processes'],
                'features_analyzed': ['scan_frequency', 'process_type', 'security_risk'],
                'performance_score': performance_score,
                'optimization_potential': 'High' if performance_score < 70 else 'Medium' if performance_score < 85 else 'Low',
                'resource_patterns': resource_patterns,
                'recommendations': [
                    f'Performance optimization potential: {performance_score:.0f}% efficient',
                    f'Focus on {dominant_type} processes for maximum impact' if dominant_type != 'Unknown' else 'Review individual process patterns'
                ]
            }
            
        except Exception as e:
            return {'error': f'ML analysis failed: {str(e)}'}

    def _perform_rag_analysis(self, candidates: List[Dict], performance_metrics: Dict) -> Dict:
        """Perform enhanced RAG analysis using Deep Security knowledge base with dynamic prompting"""
        try:
            # Try Dynamic RAG first for intelligent prompt generation
            try:
                from dynamic_rag_system import DynamicRAGSystem
                
                # Create log content from candidates for dynamic analysis
                log_lines = []
                for candidate in candidates[:50]:  # Limit to avoid excessive processing
                    file_path = candidate.get('file_path', 'unknown')
                    resource_usage = candidate.get('resource_usage', 0)
                    scan_time = candidate.get('scan_time', 0)
                    
                    # Simulate log entries based on candidate data
                    if resource_usage > 90:
                        log_lines.append(f"CRITICAL: High resource usage {resource_usage}% detected in {file_path}")
                    elif resource_usage > 70:
                        log_lines.append(f"WARNING: Elevated resource usage {resource_usage}% for {file_path}")
                    
                    if scan_time > 5000:
                        log_lines.append(f"ERROR: Slow scan performance {scan_time}ms for {file_path}")
                    
                log_content = '\n'.join(log_lines) if log_lines else "INFO: Performance analysis in progress"
                
                # Initialize dynamic RAG
                dynamic_rag = DynamicRAGSystem()
                
                # Process with dynamic analysis
                dynamic_results = dynamic_rag.process_log_with_dynamic_rag(log_content)
                
                if dynamic_results and 'error' not in dynamic_results:
                    knowledge_sources = dynamic_results.get('knowledge_sources', [])
                    log_context = dynamic_results.get('log_context', {})
                    
                    return {
                        'knowledge_sources_used': len(knowledge_sources),
                        'patterns_matched': len(log_context.get('error_types', [])),
                        'confidence_score': min(100, len(knowledge_sources) * 15 + 70),
                        'rag_version': '3.0_dynamic',
                        'dynamic_prompt_generated': bool(dynamic_results.get('dynamic_prompt')),
                        'ai_response_available': bool(dynamic_results.get('ai_response')),
                        'components_analyzed': log_context.get('components', []),
                        'error_types_found': log_context.get('error_types', []),
                        'intelligence_level': 'dynamic'
                    }
                    
            except Exception as dynamic_error:
                print(f"⚠️ Dynamic RAG failed: {dynamic_error}")
            
            # Skip enhanced RAG as module is not available
            try:
                # Enhanced RAG integration is not available, using fallback
                raise ImportError("Enhanced RAG not available")
            except ImportError:
                print("📋 Enhanced RAG not available, falling back to basic analysis")            # Fallback to basic analysis without external dependencies
            return {
                'knowledge_sources_used': 0,
                'patterns_matched': len([p for p in candidates if p['security_assessment'] != 'High']),
                'confidence_score': 60,  # Basic score without RAG enhancement
                'rag_version': 'fallback',
                'intelligence_level': 'basic',
                'best_practices': [
                    {
                        'title': 'Monitor Resource Usage',
                        'description': 'Keep track of high resource consumption files for exclusion candidates',
                        'category': 'Performance'
                    },
                    {
                        'title': 'Regular Scan Optimization',
                        'description': 'Implement scan exclusions for files that consistently show high scan times',
                        'category': 'Optimization'
                    }
                ]
            }
            
        except Exception as e:
            print(f"⚠️ RAG system error: {e}")
            
            # Return basic fallback analysis
            return self._generate_fallback_analysis(candidates, performance_metrics)
            
        except Exception as e:
            return {'error': f'RAG analysis failed: {str(e)}'}

    def _generate_enhanced_recommendations(self, candidates: List[Dict], performance_metrics: Dict, ml_insights: Dict, rag_insights: Dict) -> List[str]:
        """Generate enhanced recommendations based on all analysis components"""
        recommendations = []
        
        if len(candidates) == 0:
            recommendations.append('<i class="fas fa-check-circle text-success"></i> System Performance: Optimal - No exclusions needed')
            recommendations.append('<i class="fas fa-clock"></i> Scan Efficiency: All processes showing normal resource usage patterns')
            return recommendations
        
        # Performance-based recommendations
        total_scans = sum(int(str(c.get('count', '0')).replace(',', '')) for c in candidates)
        if total_scans > 5000:
            recommendations.append('<i class="fas fa-exclamation-triangle text-warning"></i> High scan volume detected - immediate performance optimization recommended')
        
        # Process type specific recommendations
        if performance_metrics.get('process_types'):
            dominant_type = max(set(performance_metrics['process_types']), key=performance_metrics['process_types'].count)
            recommendations.append(f'<i class="fas fa-cogs"></i> Focus on {dominant_type} processes for maximum performance impact')
        
        # Security-aware recommendations
        high_risk_count = len([c for c in candidates if c.get('security_assessment') == 'High'])
        if high_risk_count > 0:
            recommendations.append(f'<i class="fas fa-shield-alt text-danger"></i> {high_risk_count} high-risk processes detected - security review required before exclusion')
        
        # ML-based recommendations
        if ml_insights and ml_insights.get('performance_score', 0) < 70:
            recommendations.append('<i class="fas fa-brain"></i> ML Analysis: System performance below optimal - consider implementing exclusions')
        
        # RAG-based recommendations
        if rag_insights and rag_insights.get('confidence_score', 0) > 80:
            recommendations.append('<i class="fas fa-database"></i> Knowledge Base: High-confidence best practices available for this configuration')
        
        # Implementation guidance
        top_candidates = sorted(candidates, key=lambda x: int(str(x.get('count', '0')).replace(',', '')), reverse=True)[:3]
        if top_candidates:
            recommendations.append(f'<i class="fas fa-star"></i> Priority exclusion candidates: {", ".join([c["name"] for c in top_candidates])}')
        
        return recommendations

    def _perform_ai_analysis(self, process_list: List[str], busy_processes: List[Dict], candidates: List[Dict], total_scan_count: int, performance_metrics: Dict) -> str:
        """Perform AI analysis with robust error handling (following AV Conflict analyzer pattern)"""
        try:
            print(f"�  ResourceAnalyzer AI Check - OPENAI_AVAILABLE: {OPENAI_AVAILABLE}")
            
            # Check if OpenAI is available
            if not OPENAI_AVAILABLE:
                print("� � OpenAI not available - using fallback analysis")
                return self._generate_fallback_analysis(candidates, performance_metrics)
            
            from config import get_config
            config = get_config()
            
            print(f"�  API Key available: {bool(config.OPENAI_API_KEY)}")
            
            # Validate API configuration
            if not config.OPENAI_API_KEY:
                print("� � OpenAI API key not configured - using fallback analysis")
                return self._generate_fallback_analysis(candidates, performance_metrics)
            
            try:
                print("🔄 Initializing OpenAI client for ResourceAnalyzer...")
                # Use basic OpenAI client without httpx dependency
                client = OpenAI(
                    api_key=config.OPENAI_API_KEY,
                    base_url=config.OPENAI_BASE_URL,
                    timeout=120.0  # Increase timeout for ResourceAnalyzer
                )
                print("✅ OpenAI client initialized successfully for ResourceAnalyzer")
            except Exception as e:
                print(f"� � Failed to initialize OpenAI client: {str(e)}")
                return f"Failed to initialize OpenAI client: {str(e)}\n\n{self._generate_fallback_analysis(candidates, performance_metrics)}"
            
            # Enhanced AI prompt with Deep Security expertise
            prompt = (
                "You are a Trend Micro Deep Security performance optimization expert specializing in anti-malware exclusion strategies.\n\n"
                "CONTEXT:\n"
                "- Deep Security Anti-Malware (AMSP) scans files and processes in real-time\n"
                "- High scan counts indicate processes frequently accessing files or creating new processes\n"
                "- Exclusions can improve performance but may create security gaps\n"
                "- Trend Micro processes should NEVER be excluded\n\n"
                "ANALYSIS TASK:\n"
                "Given the correlated busy processes below, provide:\n"
                "1. Why each process has high scan activity\n"
                "2. Security assessment for potential exclusions\n"
                "3. Deep Security policy recommendations\n"
                "4. Performance vs security trade-offs\n"
                "5. Implementation guidance for exclusions\n\n"
                f"SYSTEM METRICS:\n"
                f"- Total Processes Running: {len(process_list)}\n"
                f"- Busy Processes Detected: {len(busy_processes)}\n"
                f"- Non-Trend Micro Candidates: {len(candidates)}\n"
                f"- Total Scan Count: {total_scan_count:,}\n"
                f"- Optimization Potential: {performance_metrics['optimization_potential']}\n\n"
                f"CORRELATED BUSY PROCESSES:\n"
            )
            
            if candidates:
                for c in candidates:
                    prompt += f"• {c['name']} (Scan Count: {c['count']}, Type: {c['process_type']}, Security Risk: {c['security_assessment']})\n"
                    for k, v in c["details"].items():
                        prompt += f"    {k}: {v}\n"
                prompt += "\nPROVIDE DETAILED ANALYSIS WITH ACTIONABLE RECOMMENDATIONS:\n"
            else:
                prompt += "\nNo high-impact non-Trend Micro processes detected.\n"
                prompt += "PROVIDE ASSESSMENT OF CURRENT PERFORMANCE STATE:\n"

            try:
                print("🚀 Making OpenAI API call for ResourceAnalyzer (extended timeout for large datasets)...")
                response = client.chat.completions.create(
                    model=config.OPENAI_MODEL,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=4000,
                    temperature=0.3,
                    timeout=120  # Extended timeout for resource analysis with large datasets
                )
                
                print("✅ OpenAI API call successful for ResourceAnalyzer")
                return response.choices[0].message.content
                
            except Exception as api_error:
                print(f"� � AI analysis API call failed: {str(api_error)}")
                return f"AI analysis temporarily unavailable: {str(api_error)}\n\n{self._generate_fallback_analysis(candidates, performance_metrics)}"
                
        except Exception as e:
            print(f"� � ResourceAnalyzer AI analysis exception: {str(e)}")
            return f"Analysis error: {str(e)}\n\n{self._generate_fallback_analysis(candidates, performance_metrics)}"

    def _generate_fallback_analysis(self, candidates: List[Dict], performance_metrics: Dict) -> str:
        """Generate fallback analysis when AI is unavailable"""
        if not candidates:
            return """
## Deep Security Resource Analysis Results

### Summary
✅ **Optimal Performance Detected**
- No high-impact processes requiring exclusions
- System running efficiently with current configuration
- Anti-malware scanning within normal parameters

### Recommendations
1. **Continue Monitoring**: Current performance levels are optimal
2. **Regular Review**: Check resource usage monthly for any changes
3. **Baseline Established**: Use current metrics as performance baseline

### Next Steps
- No immediate action required
- Consider performance monitoring tools for ongoing optimization
"""

        total_scans = sum(int(str(c.get('count', '0')).replace(',', '')) for c in candidates)
        high_impact = [c for c in candidates if int(str(c.get('count', '0')).replace(',', '')) > 1000]
        
        analysis = f"""
## Deep Security Resource Analysis Results

### Summary
⚠�  **Performance Optimization Opportunities Detected**
- {len(candidates)} processes with high scan activity
- Total scan events: {total_scans:,}
- {len(high_impact)} high-impact processes identified
- Optimization potential: {performance_metrics.get('optimization_potential', 'Medium')}

### High-Impact Processes Analysis

"""
        
        for i, candidate in enumerate(sorted(candidates, key=lambda x: int(str(x.get('count', '0')).replace(',', '')), reverse=True)[:5], 1):
            count = int(str(candidate.get('count', '0')).replace(',', ''))
            analysis += f"""
#### {i}. {candidate['name']}
- **Scan Count**: {candidate['count']} events
- **Process Type**: {candidate['process_type']}
- **Security Risk**: {candidate['security_assessment']}
- **Analysis**: {'High-frequency file access pattern' if count > 1000 else 'Moderate scan activity'}
- **Recommendation**: {'Consider for exclusion with security review' if candidate['security_assessment'] != 'High' else 'Monitor only - high security risk'}
"""

        analysis += f"""

### Performance Recommendations

1. **Immediate Actions**:
   - Review top {min(3, len(high_impact))} processes for exclusion candidates
   - Implement exclusions during maintenance window
   - Monitor performance improvements post-implementation

2. **Security Considerations**:
   - Never exclude Trend Micro processes
   - Review exclusions with security team
   - Implement exclusions gradually and monitor for issues

3. **Implementation Strategy**:
   - Start with lowest-risk, highest-impact processes
   - Document all exclusions for audit purposes
   - Establish rollback procedures

### Deep Security Policy Configuration

To implement exclusions:
1. Access Deep Security Manager console
2. Navigate to Computer → [Target Computer] → Anti-Malware
3. Add process exclusions in the "Exclusions" section
4. Test thoroughly before production deployment

**Note**: This analysis was generated using built-in logic. For enhanced AI-powered recommendations, ensure OpenAI connectivity is available.
"""
        
        return analysis

    def analyze(self, file_paths: List[str]) -> Dict[str, Any]:
        """Main entry point for resource analysis - standardized API"""
        try:
            self._update_progress(1)
            
            if not file_paths or len(file_paths) == 0:
                raise ValueError("No files provided for resource analysis")
            
            # Determine file types and extract data
            xml_files = []
            txt_files = []
            
            for file_path in file_paths:
                try:
                    # Try to identify file type by content
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        first_line = f.readline().strip()
                        if first_line.startswith('<?xml') or '<' in first_line:
                            xml_files.append(file_path)
                        else:
                            txt_files.append(file_path)
                except Exception:
                    # Fallback to file extension
                    if file_path.lower().endswith('.xml'):
                        xml_files.append(file_path)
                    elif file_path.lower().endswith('.txt'):
                        txt_files.append(file_path)
            
            self._update_progress(20)
            
            # Extract process data
            processes = []
            busy_processes = []
            
            # Process XML files (RunningProcesses.xml)
            for xml_file in xml_files:
                try:
                    processes.extend(self.extract_processes_from_xml(xml_file))
                except Exception as e:
                    print(f"Warning: Failed to process XML file {xml_file}: {e}")
            
            self._update_progress(50)
            
            # Process TXT files (TopNBusyProcess.txt)
            for txt_file in txt_files:
                try:
                    busy_processes.extend(self.parse_top_n_busy_process(txt_file))
                except Exception as e:
                    print(f"Warning: Failed to process TXT file {txt_file}: {e}")
            
            self._update_progress(70)
            
            # Perform resource conflict analysis
            analysis_result = self.analyze_resource_conflicts(processes, busy_processes)
            
            # Apply standardized output format
            standardized_result = self.standardize_output(analysis_result, 'resource_analysis')
            
            # Add metadata
            standardized_result['metadata'] = {
                'files_processed': len(file_paths),
                'xml_files': len(xml_files),
                'txt_files': len(txt_files),
                'processes_found': len(processes),
                'busy_processes_found': len(busy_processes),
                'exclusion_candidates': len(analysis_result.get('candidates', []))
            }
            
            self._update_progress(100)
            return standardized_result
            
        except Exception as e:
            error_msg = f"Resource analysis failed: {str(e)}"
            self._update_progress(None)
            return {
                'analysis_type': 'resource_analysis',
                'status': 'error',
                'summary': error_msg,
                'details': [error_msg],
                'recommendations': ['Please ensure both RunningProcesses.xml and TopNBusyProcess.txt files are provided'],
                'severity': 'high',
                'error': True,
                'metadata': {
                    'files_processed': len(file_paths) if 'file_paths' in locals() else 0,
                    'error_type': 'analysis_failure'
                }
            }


class DSAgentOfflineAnalyzer(AnalyzerOutputStandardizer):
    """Deep Security Agent Offline Analyzer - Specialized analyzer for DS Agent connectivity and offline issues"""
    
    def __init__(self, rag_system=None, ml_analyzer=None, session_manager=None, session_id=None):
        """Initialize the DS Agent Offline Analyzer"""
        self.rag_system = rag_system
        self.ml_analyzer = ml_analyzer
        self.session_manager = session_manager
        self.session_id = session_id
        
        # Initialize offline detection patterns
        self._initialize_offline_patterns()

    def _update_progress(self, stage, message, percentage=None):
        """Update analysis progress if session manager is available"""
        if self.session_manager and self.session_id:
            try:
                progress_data = {
                    'analysis_stage': stage,
                    'progress_message': message,
                    'status': 'processing'
                }
                if percentage is not None:
                    progress_data['progress_percentage'] = percentage
                
                self.session_manager.update_session(self.session_id, progress_data)
                print(f"📊 DS Agent Offline Progress - {stage}: {message}")
            except Exception as e:
                print(f"⚠️  DS Agent Offline Progress update failed: {e}")
        else:
            # Fallback to console logging
            print(f"📊 DS Agent Offline {stage}: {message}")

    def _initialize_offline_patterns(self):
        """Initialize patterns for detecting DS Agent offline issues"""
        # Core DS Agent communication patterns
        self.communication_patterns = {
            'heartbeat_failures': [
                r'heartbeat.*failed|heartbeat.*timeout|heartbeat.*error',
                r'failed.*send.*heartbeat|heartbeat.*not.*sent',
                r'no.*heartbeat.*response|heartbeat.*response.*timeout',
                r'manager.*heartbeat.*failed|heartbeat.*communication.*failed'
            ],
            'connection_failures': [
                r'connection.*failed|failed.*connect.*manager',
                r'unable.*connect.*manager|manager.*connection.*failed',
                r'connection.*timeout|connection.*refused',
                r'connection.*reset|connection.*aborted',
                r'ssl.*handshake.*failed|tls.*connection.*failed',
                r'certificate.*verification.*failed|certificate.*error'
            ],
            'dns_resolution_issues': [
                r'dns.*resolution.*failed|dns.*lookup.*failed',
                r'host.*not.*found|hostname.*resolution.*failed',
                r'gethostbyname.*failed|dns.*timeout',
                r'name.*resolution.*failed|dns.*query.*failed'
            ],
            'authentication_failures': [
                r'authentication.*failed|auth.*failed|login.*failed',
                r'invalid.*credentials|access.*denied',
                r'token.*expired|token.*invalid|authorization.*failed',
                r'certificate.*authentication.*failed'
            ],
            'port_connectivity_issues': [
                r'port.*4119.*blocked|port.*4120.*blocked|port.*4118.*blocked',
                r'connection.*refused.*4119|connection.*refused.*4120',
                r'timeout.*connecting.*4119|timeout.*connecting.*4120',
                r'firewall.*blocking.*port|port.*unreachable'
            ],
            'proxy_issues': [
                r'proxy.*authentication.*failed|proxy.*connection.*failed',
                r'proxy.*timeout|proxy.*error|proxy.*refused',
                r'proxy.*configuration.*error|invalid.*proxy.*settings'
            ],
            'network_infrastructure': [
                r'network.*unreachable|network.*down|network.*error',
                r'route.*not.*found|routing.*table.*error',
                r'interface.*down|adapter.*disabled|network.*adapter.*error',
                r'icmp.*timeout|ping.*failed|traceroute.*failed'
            ],
            'manager_unavailable': [
                r'manager.*not.*responding|manager.*unavailable',
                r'manager.*down|manager.*offline|manager.*unreachable',
                r'manager.*service.*stopped|manager.*not.*running',
                r'manager.*maintenance.*mode|manager.*database.*error'
            ]
        }
        
        # DS Agent service and process patterns
        self.service_patterns = {
            'service_startup_failures': [
                r'service.*failed.*start|failed.*start.*service',
                r'service.*startup.*error|service.*initialization.*failed',
                r'ds_agent.*service.*failed|deepsecurity.*service.*failed',
                r'service.*dependency.*failed|dependent.*service.*failed'
            ],
            'service_crashes': [
                r'service.*crashed|service.*terminated.*unexpectedly',
                r'application.*error|access.*violation|memory.*violation',
                r'exception.*in.*service|unhandled.*exception',
                r'service.*stopped.*unexpectedly'
            ],
            'driver_issues': [
                r'driver.*failed.*load|driver.*initialization.*failed',
                r'driver.*not.*found|driver.*signature.*error',
                r'kernel.*driver.*error|system.*driver.*failed',
                r'tmcomm.*driver.*failed|tmebc.*driver.*failed'
            ]
        }
        
        # Cloud One Workload Security specific patterns (based on documentation)
        self.cloud_one_patterns = {
            'cloud_one_connectivity': [
                r'workload\.([a-z]{2}-\d)\.cloudone\.trendmicro\.com.*failed',
                r'agents\.workload\.([a-z]{2}-\d)\.cloudone\.trendmicro\.com.*timeout',
                r'deepsecurity\.trendmicro\.com.*unreachable',
                r'agents\.deepsecurity\.trendmicro\.com.*connection.*failed'
            ],
            'cloud_one_endpoints': [
                r'ds2000-en-census\.trendmicro\.com.*failed',
                r'deepsec20-en\.gfrbridge\.trendmicro\.com.*timeout',
                r'ds200-en\.fbs25\.trendmicro\.com.*error',
                r'ds20\.icrc\.trendmicro\.com.*unreachable'
            ],
            'update_servers': [
                r'iaus\.activeupdate\.trendmicro\.com.*failed',
                r'iaus\.trendmicro\.com.*timeout',
                r'files\.trendmicro\.com.*unreachable',
                r'licenseupdate\.trendmicro\.com.*error'
            ]
        }
        
        # Critical system patterns that can cause offline status
        self.system_patterns = {
            'system_resources': [
                r'out.*of.*memory|insufficient.*memory|memory.*low',
                r'disk.*full|disk.*space.*low|no.*space.*left',
                r'cpu.*usage.*high|system.*overloaded|performance.*degraded',
                r'file.*handle.*limit|too.*many.*open.*files'
            ],
            'system_security': [
                r'access.*denied|permission.*denied|insufficient.*privileges',
                r'security.*policy.*blocking|group.*policy.*restriction',
                r'firewall.*rule.*blocking|security.*software.*interference',
                r'antivirus.*quarantine|security.*scan.*blocking'
            ],
            'time_sync_issues': [
                r'time.*synchronization.*failed|ntp.*sync.*failed',
                r'clock.*skew|time.*drift|system.*time.*incorrect',
                r'certificate.*expired.*time|timestamp.*validation.*failed'
            ]
        }
        
        # Known resolution patterns
        self.resolution_patterns = {
            'connectivity_resolutions': [
                "Check network connectivity to Deep Security Manager",
                "Verify firewall rules allow ports 4119, 4120, 4118",
                "Test DNS resolution for manager hostname",
                "Validate proxy configuration if using proxy",
                "Check certificate validity and trust chain"
            ],
            'service_resolutions': [
                "Restart Deep Security Agent service",
                "Check service dependencies and startup type",
                "Verify driver installation and signatures",
                "Review Windows Event Logs for service errors",
                "Reinstall agent if service corruption detected"
            ],
            'cloud_one_resolutions': [
                "Verify Cloud One Workload Security endpoints accessibility",
                "Check regional endpoint configuration",
                "Validate tenant permissions and access tokens",
                "Test connectivity to update and census servers",
                "Review network policies for Cloud One URLs"
            ],
            'system_resolutions': [
                "Check system resources (memory, disk, CPU)",
                "Verify sufficient privileges for agent operation",
                "Review time synchronization and NTP configuration",
                "Check for conflicting security software",
                "Validate system date/time for certificate validation"
            ]
        }

    def parse_ds_agent_log_entry(self, line: str) -> Dict[str, Any]:
        """Parse DS Agent log entry with multiple format support"""
        patterns = [
            # Standard DS Agent format
            r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d+) \[([^\]]+)\]: \[([^\]]+)\] \| ([^|]+) \| ([^|]*) \| (.+)',
            # Alternative format without timezone
            r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) \[([^\]]+)\] ([^:]+): (.+)',
            # Simple timestamp format
            r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) (.+)',
            # Windows Event Log style
            r'(\d{1,2}/\d{1,2}/\d{4} \d{1,2}:\d{2}:\d{2} [AP]M) (.+)'
        ]
        
        for pattern in patterns:
            match = re.match(pattern, line)
            if match:
                groups = match.groups()
                
                if len(groups) >= 6:  # Full format
                    return {
                        'timestamp': groups[0],
                        'timezone': groups[1],
                        'component': groups[2].split('/')[0] if '/' in groups[2] else groups[2],
                        'level': groups[2].split('/')[1] if '/' in groups[2] else '5',
                        'message': groups[3].strip(),
                        'location': groups[4].strip() if len(groups) > 4 else '',
                        'thread': groups[5].strip() if len(groups) > 5 else '',
                        'raw_line': line,
                        'parsed': True
                    }
                elif len(groups) >= 4:  # Alternative format
                    return {
                        'timestamp': groups[0],
                        'component': groups[2] if len(groups) > 2 else 'unknown',
                        'message': groups[3] if len(groups) > 3 else groups[1],
                        'raw_line': line,
                        'parsed': True
                    }
                else:  # Simple format
                    return {
                        'timestamp': groups[0],
                        'message': groups[1],
                        'raw_line': line,
                        'parsed': True
                    }
        
        return {'raw_line': line, 'parsed': False, 'message': line}

    def detect_offline_causes(self, log_entries: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Detect potential causes for DS Agent offline status"""
        offline_analysis = {
            'communication_issues': [],
            'service_issues': [],
            'system_issues': [],
            'cloud_one_issues': [],
            'severity_summary': {
                'critical': 0,
                'high': 0,
                'medium': 0,
                'low': 0
            },
            'root_cause_analysis': [],
            'timeline_analysis': []
        }
        
        for entry in log_entries:
            if not entry.get('parsed'):
                continue
                
            message = entry.get('message', '').lower()
            timestamp = entry.get('timestamp', '')
            
            # Check communication patterns
            for category, patterns in self.communication_patterns.items():
                for pattern in patterns:
                    if re.search(pattern, message, re.IGNORECASE):
                        severity = self._determine_severity(category, pattern, message)
                        issue = {
                            'type': 'communication',
                            'category': category,
                            'pattern': pattern,
                            'message': entry.get('message', ''),
                            'timestamp': timestamp,
                            'severity': severity,
                            'component': entry.get('component', 'unknown')
                        }
                        offline_analysis['communication_issues'].append(issue)
                        offline_analysis['severity_summary'][severity] += 1
                        break
            
            # Check service patterns
            for category, patterns in self.service_patterns.items():
                for pattern in patterns:
                    if re.search(pattern, message, re.IGNORECASE):
                        severity = self._determine_severity(category, pattern, message)
                        issue = {
                            'type': 'service',
                            'category': category,
                            'pattern': pattern,
                            'message': entry.get('message', ''),
                            'timestamp': timestamp,
                            'severity': severity,
                            'component': entry.get('component', 'unknown')
                        }
                        offline_analysis['service_issues'].append(issue)
                        offline_analysis['severity_summary'][severity] += 1
                        break
            
            # Check Cloud One patterns
            for category, patterns in self.cloud_one_patterns.items():
                for pattern in patterns:
                    if re.search(pattern, message, re.IGNORECASE):
                        severity = self._determine_severity(category, pattern, message)
                        issue = {
                            'type': 'cloud_one',
                            'category': category,
                            'pattern': pattern,
                            'message': entry.get('message', ''),
                            'timestamp': timestamp,
                            'severity': severity,
                            'component': entry.get('component', 'unknown')
                        }
                        offline_analysis['cloud_one_issues'].append(issue)
                        offline_analysis['severity_summary'][severity] += 1
                        break
            
            # Check system patterns
            for category, patterns in self.system_patterns.items():
                for pattern in patterns:
                    if re.search(pattern, message, re.IGNORECASE):
                        severity = self._determine_severity(category, pattern, message)
                        issue = {
                            'type': 'system',
                            'category': category,
                            'pattern': pattern,
                            'message': entry.get('message', ''),
                            'timestamp': timestamp,
                            'severity': severity,
                            'component': entry.get('component', 'unknown')
                        }
                        offline_analysis['system_issues'].append(issue)
                        offline_analysis['severity_summary'][severity] += 1
                        break
        
        # Perform root cause analysis
        offline_analysis['root_cause_analysis'] = self._perform_root_cause_analysis(offline_analysis)
        
        # Perform timeline analysis
        offline_analysis['timeline_analysis'] = self._perform_timeline_analysis(
            offline_analysis['communication_issues'] + 
            offline_analysis['service_issues'] + 
            offline_analysis['cloud_one_issues'] + 
            offline_analysis['system_issues']
        )
        
        # Standardize return structure for frontend compatibility
        return offline_analysis

    def _determine_severity(self, category: str, pattern: str, message: str) -> str:
        """Determine severity level based on category and pattern"""
        critical_categories = ['heartbeat_failures', 'service_crashes', 'driver_issues']
        high_categories = ['connection_failures', 'service_startup_failures', 'authentication_failures']
        medium_categories = ['dns_resolution_issues', 'proxy_issues', 'cloud_one_connectivity']
        
        if category in critical_categories:
            return 'critical'
        elif category in high_categories:
            return 'high'
        elif category in medium_categories:
            return 'medium'
        else:
            return 'low'

    def _perform_root_cause_analysis(self, offline_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Perform root cause analysis based on detected issues"""
        root_causes = []
        
        # Analyze communication issues
        if offline_analysis['communication_issues']:
            heartbeat_issues = [i for i in offline_analysis['communication_issues'] if 'heartbeat' in i['category']]
            connection_issues = [i for i in offline_analysis['communication_issues'] if 'connection' in i['category']]
            
            if heartbeat_issues:
                root_causes.append({
                    'type': 'heartbeat_failure',
                    'description': 'Agent unable to send heartbeat to manager',
                    'impact': 'Manager marks agent as offline',
                    'count': len(heartbeat_issues),
                    'severity': 'critical',
                    'recommendations': self.resolution_patterns['connectivity_resolutions']
                })
            
            if connection_issues:
                root_causes.append({
                    'type': 'connection_failure',
                    'description': 'Agent cannot establish connection to manager',
                    'impact': 'Agent appears offline to manager',
                    'count': len(connection_issues),
                    'severity': 'critical',
                    'recommendations': self.resolution_patterns['connectivity_resolutions']
                })
        
        # Analyze service issues
        if offline_analysis['service_issues']:
            service_crashes = [i for i in offline_analysis['service_issues'] if 'crash' in i['category']]
            startup_failures = [i for i in offline_analysis['service_issues'] if 'startup' in i['category']]
            
            if service_crashes:
                root_causes.append({
                    'type': 'service_crash',
                    'description': 'DS Agent service crashed or terminated unexpectedly',
                    'impact': 'Agent offline until service restart',
                    'count': len(service_crashes),
                    'severity': 'critical',
                    'recommendations': self.resolution_patterns['service_resolutions']
                })
            
            if startup_failures:
                root_causes.append({
                    'type': 'startup_failure',
                    'description': 'DS Agent service failed to start properly',
                    'impact': 'Agent cannot come online',
                    'count': len(startup_failures),
                    'severity': 'critical',
                    'recommendations': self.resolution_patterns['service_resolutions']
                })
        
        # Analyze Cloud One issues
        if offline_analysis['cloud_one_issues']:
            root_causes.append({
                'type': 'cloud_one_connectivity',
                'description': 'Connectivity issues with Cloud One Workload Security endpoints',
                'impact': 'Agent cannot communicate with Cloud One services',
                'count': len(offline_analysis['cloud_one_issues']),
                'severity': 'high',
                'recommendations': self.resolution_patterns['cloud_one_resolutions']
            })
        
        # Analyze system issues
        if offline_analysis['system_issues']:
            system_resource_issues = [i for i in offline_analysis['system_issues'] if 'resources' in i['category']]
            if system_resource_issues:
                root_causes.append({
                    'type': 'system_resources',
                    'description': 'System resource constraints affecting agent operation',
                    'impact': 'Agent performance degraded or offline',
                    'count': len(system_resource_issues),
                    'severity': 'medium',
                    'recommendations': self.resolution_patterns['system_resolutions']
                })
        
        return root_causes

    def _perform_timeline_analysis(self, all_issues: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Perform timeline analysis of issues"""
        if not all_issues:
            return {'timeline': [], 'patterns': []}
        
        # Sort issues by timestamp
        sorted_issues = sorted(all_issues, key=lambda x: x.get('timestamp', ''))
        
        timeline = []
        for issue in sorted_issues:
            timeline.append({
                'timestamp': issue.get('timestamp', ''),
                'type': issue.get('type', ''),
                'category': issue.get('category', ''),
                'severity': issue.get('severity', ''),
                'message': issue.get('message', '')[:100] + '...' if len(issue.get('message', '')) > 100 else issue.get('message', '')
            })
        
        # Identify patterns
        patterns = []
        if len(sorted_issues) > 1:
            # Check for recurring issues
            category_counts = {}
            for issue in sorted_issues:
                category = issue.get('category', 'unknown')
                category_counts[category] = category_counts.get(category, 0) + 1
            
            for category, count in category_counts.items():
                if count > 2:
                    patterns.append(f"Recurring {category} issues ({count} occurrences)")
        
        return {
            'timeline': timeline,
            'patterns': patterns
        }

    def analyze_log_file(self, file_path: str) -> Dict[str, Any]:
        """Analyze DS Agent log file for offline issues"""
        self._update_progress("Initialization", "Starting DS Agent offline analysis", 10)
        
        results = {
            'summary': {
                'file_path': file_path,
                'total_lines': 0,
                'parsed_lines': 0,
                'offline_issues': 0,
                'critical_issues': 0,
                'timespan': {'start': None, 'end': None}
            },
            'offline_analysis': {},
            'recommendations': [],
            'ml_insights': None,
            'rag_insights': None
        }
        
        try:
            self._update_progress("File Reading", "Reading and parsing DS Agent log file", 20)
            
            log_entries = []
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                for line_num, line in enumerate(f, 1):
                    if line_num > 15000:  # Limit for performance
                        break
                    
                    results['summary']['total_lines'] += 1
                    line = line.strip()
                    
                    if not line:
                        continue
                    
                    log_entry = self.parse_ds_agent_log_entry(line)
                    log_entry['line_number'] = line_num
                    
                    if log_entry['parsed']:
                        results['summary']['parsed_lines'] += 1
                        
                        if not results['summary']['timespan']['start']:
                            results['summary']['timespan']['start'] = log_entry.get('timestamp', '')
                        results['summary']['timespan']['end'] = log_entry.get('timestamp', '')
                        
                        log_entries.append(log_entry)
            
            self._update_progress("Issue Detection", "Detecting offline causes and issues", 50)
            
            # Detect offline causes
            results['offline_analysis'] = self.detect_offline_causes(log_entries)
            
            # Calculate summary statistics
            total_issues = (len(results['offline_analysis']['communication_issues']) +
                          len(results['offline_analysis']['service_issues']) +
                          len(results['offline_analysis']['cloud_one_issues']) +
                          len(results['offline_analysis']['system_issues']))
            
            results['summary']['offline_issues'] = total_issues
            results['summary']['critical_issues'] = results['offline_analysis']['severity_summary']['critical']
            
            self._update_progress("Recommendations", "Generating recommendations", 70)
            
            # Generate recommendations
            results['recommendations'] = self._generate_offline_recommendations(results['offline_analysis'])
            
            # ML Analysis - Enhanced backend ML analysis for Dynamic RAG
            if self.ml_analyzer and ML_AVAILABLE:
                try:
                    self._update_progress("ML Analysis", "Running ML-enhanced offline analysis", 80)
                    
                    # Convert log entries to text format for ML analysis
                    log_text = '\n'.join([entry.get('raw_line', '') for entry in log_entries[:500]])
                    
                    # Generate ML insights using the standalone function
                    from ml_analyzer import enhance_analysis_with_ml
                    ml_insights = enhance_analysis_with_ml(log_text, 'ds_agent_offline')
                    
                    results['ml_insights'] = ml_insights
                    print(f"✅ ML offline analysis completed with {len(ml_insights.get('anomalies', []))} anomalies detected")
                except Exception as e:
                    print(f"⚠️  ML analysis failed: {e}")
                    results['ml_insights'] = None
            
            # RAG Analysis - Enhanced with ML insights
            if self.rag_system:
                try:
                    self._update_progress("RAG Analysis", "Running ML-enhanced AI analysis", 90)
                    rag_context = self._prepare_rag_context(results)
                    results['rag_insights'] = self.rag_system.analyze_with_context(
                        rag_context, 
                        "ds_agent_offline",
                        ml_insights=results.get('ml_insights')
                    )
                except Exception as e:
                    print(f"⚠️  RAG analysis failed: {e}")
                    results['rag_insights'] = {'error': str(e)}
            
            self._update_progress("Complete", "DS Agent offline analysis completed", 100)
            
        except Exception as e:
            error_msg = f"Failed to analyze DS Agent log: {str(e)}"
            print(f"❌ {error_msg}")
            results['error'] = error_msg
        
        return results

    def _generate_offline_recommendations(self, offline_analysis: Dict[str, Any]) -> List[str]:
        """Generate specific recommendations based on offline analysis"""
        recommendations = []
        
        # Communication issue recommendations
        if offline_analysis['communication_issues']:
            heartbeat_issues = [i for i in offline_analysis['communication_issues'] if 'heartbeat' in i['category']]
            connection_issues = [i for i in offline_analysis['communication_issues'] if 'connection' in i['category']]
            dns_issues = [i for i in offline_analysis['communication_issues'] if 'dns' in i['category']]
            
            if heartbeat_issues:
                recommendations.extend([
                    "🔥 CRITICAL: Heartbeat failures detected - check manager connectivity",
                    "• Verify Deep Security Manager is running and accessible on port 4120",
                    "• Test network connectivity: telnet <manager> 4120",
                    "• Check agent configuration for correct manager hostname/IP"
                ])
            
            if connection_issues:
                recommendations.extend([
                    "🔥 CRITICAL: Connection failures detected - network connectivity issues",
                    "• Verify firewall rules allow ports 4119, 4120, 4118",
                    "• Check proxy configuration if using corporate proxy",
                    "• Test SSL/TLS connectivity and certificate validity"
                ])
            
            if dns_issues:
                recommendations.extend([
                    "⚠️  DNS resolution issues detected",
                    "• Verify DNS server configuration",
                    "• Test DNS resolution: nslookup <manager-hostname>",
                    "• Consider using IP address instead of hostname temporarily"
                ])
        
        # Service issue recommendations
        if offline_analysis['service_issues']:
            service_crashes = [i for i in offline_analysis['service_issues'] if 'crash' in i['category']]
            startup_failures = [i for i in offline_analysis['service_issues'] if 'startup' in i['category']]
            
            if service_crashes:
                recommendations.extend([
                    "🔥 CRITICAL: DS Agent service crashes detected",
                    "• Check Windows Event Logs for application errors",
                    "• Verify system stability and available resources",
                    "• Consider reinstalling agent if crashes persist"
                ])
            
            if startup_failures:
                recommendations.extend([
                    "🔥 CRITICAL: Service startup failures detected",
                    "• Check service dependencies and startup configuration",
                    "• Verify driver installation and signatures",
                    "• Run as administrator: sc query ds_agent"
                ])
        
        # Cloud One issue recommendations
        if offline_analysis['cloud_one_issues']:
            recommendations.extend([
                "☁️  Cloud One connectivity issues detected",
                "• Verify access to Cloud One Workload Security endpoints",
                "• Check regional endpoint configuration",
                "• Test connectivity to: workload.<region>.cloudone.trendmicro.com:443",
                "• Validate tenant permissions and access tokens"
            ])
        
        # System issue recommendations
        if offline_analysis['system_issues']:
            recommendations.extend([
                "🖥️  System-level issues detected",
                "• Check system resources: memory, disk space, CPU usage",
                "• Verify time synchronization (critical for certificates)",
                "• Review system security policies and permissions",
                "• Check for conflicting security software"
            ])
        
        # Root cause specific recommendations
        for root_cause in offline_analysis.get('root_cause_analysis', []):
            if root_cause['type'] == 'heartbeat_failure':
                recommendations.append(f"🎯 Root Cause: {root_cause['description']} ({root_cause['count']} occurrences)")
            elif root_cause['type'] == 'service_crash':
                recommendations.append(f"🎯 Root Cause: {root_cause['description']} ({root_cause['count']} occurrences)")
        
        # General recommendations if no specific issues found
        if not recommendations:
            recommendations.extend([
                "✅ No critical offline issues detected in log analysis",
                "• Monitor agent status in Deep Security Manager",
                "• Check agent last contact time and heartbeat status",
                "• Verify agent policies are applied correctly"
            ])
        
        return recommendations

    def _prepare_rag_context(self, results: Dict[str, Any]) -> str:
        """Prepare context for RAG analysis"""
        context_parts = []
        
        context_parts.append("DS AGENT OFFLINE ANALYSIS CONTEXT:")
        context_parts.append(f"File: {results['summary']['file_path']}")
        context_parts.append(f"Total Lines: {results['summary']['total_lines']}")
        context_parts.append(f"Offline Issues: {results['summary']['offline_issues']}")
        context_parts.append(f"Critical Issues: {results['summary']['critical_issues']}")
        
        if results['offline_analysis']['root_cause_analysis']:
            context_parts.append("\nROOT CAUSE ANALYSIS:")
            for cause in results['offline_analysis']['root_cause_analysis']:
                context_parts.append(f"- {cause['type']}: {cause['description']} (Count: {cause['count']})")
        
        if results['offline_analysis']['timeline_analysis']['patterns']:
            context_parts.append("\nTIMELINE PATTERNS:")
            for pattern in results['offline_analysis']['timeline_analysis']['patterns']:
                context_parts.append(f"- {pattern}")
        
        context_parts.append("\nSEVERITY SUMMARY:")
        severity = results['offline_analysis']['severity_summary']
        context_parts.append(f"Critical: {severity['critical']}, High: {severity['high']}, Medium: {severity['medium']}, Low: {severity['low']}")
        
        return "\n".join(context_parts)

    def analyze(self, file_paths: Union[str, List[str]]) -> Dict[str, Any]:
        """Standardized analysis entry point for DS Agent offline logs"""
        try:
            self._update_progress("Initialization", "Starting DS Agent offline analysis", 1)
            
            # Normalize input to list and validate
            if isinstance(file_paths, str):
                file_paths = [file_paths]
            
            if not file_paths:
                raise ValueError("No DS Agent log files provided for offline analysis")
            
            # DS Agent offline analyzer currently only supports single file analysis
            log_file = file_paths[0]
            
            self._update_progress("Log Analysis", "Analyzing DS Agent offline status", 30)
            analysis_results = self.analyze_offline_status(log_file)
            
            self._update_progress("Standardization", "Converting to standardized format", 90)
            
            # Apply standardized output format
            standardized_result = self._standardize_analyzer_output(analysis_results, 'ds_agent_offline')
            
            # Add metadata
            standardized_result['metadata'] = {
                'files_processed': len(file_paths),
                'log_file': os.path.basename(log_file),
                'total_lines': analysis_results.get('summary', {}).get('total_lines', 0),
                'offline_issues': analysis_results.get('summary', {}).get('offline_issues', 0),
                'critical_issues': analysis_results.get('summary', {}).get('critical_issues', 0),
                'connectivity_errors': len(analysis_results.get('offline_analysis', {}).get('connectivity_errors', [])),
                'service_crashes': len(analysis_results.get('offline_analysis', {}).get('service_crashes', [])),
                'authentication_failures': len(analysis_results.get('offline_analysis', {}).get('authentication_failures', []))
            }
            
            # Generate formatted output using existing formatter
            from routes import format_offline_results
            formatted_html = format_offline_results(analysis_results)
            standardized_result['formatted_output'] = formatted_html
            
            self._update_progress("Completion", "DS Agent offline analysis completed", 100)
            return standardized_result
            
        except Exception as e:
            error_msg = f"DS Agent offline analysis failed: {str(e)}"
            self._update_progress("Error", error_msg, None)
            return {
                'analysis_type': 'ds_agent_offline',
                'status': 'error',
                'summary': error_msg,
                'details': [error_msg],
                'recommendations': ['Please ensure valid DS Agent log files are provided'],
                'severity': 'high',
                'error': True,
                'metadata': {
                    'files_processed': len(file_paths) if 'file_paths' in locals() else 0,
                    'error_type': 'analysis_failure'
                }
            }


class DiagnosticPackageAnalyzer(AnalyzerOutputStandardizer):
    """Deep Security Diagnostic Package Analyzer - Comprehensive analysis of diagnostic packages with multi-log correlation"""
    
    def __init__(self, session_manager=None, session_id=None, rag_system=None, ml_analyzer=None):
        """Initialize the Diagnostic Package Analyzer with enhanced ML/RAG support"""
        self.session_manager = session_manager
        self.session_id = session_id
        self.rag_system = rag_system
        self.ml_analyzer = ml_analyzer
        
        # Initialize analyzers for different log types
        self.ds_analyzer = DSAgentLogAnalyzer(session_manager, session_id, rag_system, ml_analyzer)
        self.amsp_analyzer = AMSPAnalyzer(session_manager, session_id)
        self.conflict_analyzer = ConflictAnalyzer()
        self.resource_analyzer = ResourceAnalyzer(session_manager, session_id, rag_system, ml_analyzer)
        self.offline_analyzer = DSAgentOfflineAnalyzer(rag_system, ml_analyzer, session_manager, session_id)
        
        # Package analysis patterns
        self._initialize_package_patterns()

    def _update_progress(self, stage, message, percentage=None):
        """Update analysis progress if session manager is available"""
        if self.session_manager and self.session_id:
            try:
                progress_data = {
                    'analysis_stage': stage,
                    'progress_message': message,
                    'status': 'processing'
                }
                if percentage is not None:
                    progress_data['progress_percentage'] = percentage
                
                self.session_manager.update_session(self.session_id, progress_data)
                print(f"📊 Diagnostic Package Progress - {stage}: {message}")
            except Exception as e:
                print(f"⚠️  Diagnostic Package Progress update failed: {e}")
        else:
            # Fallback to console logging
            print(f"📊 Diagnostic Package {stage}: {message}")

    def _initialize_package_patterns(self):
        """Initialize patterns for diagnostic package analysis"""
        self.package_patterns = {
            'ds_agent_logs': [
                r'^ds_agent\.log$',           # Only exact ds_agent.log
                r'^ds_agent-err\.log$',       # Only exact ds_agent-err.log
                r'deepsecurity.*\.log$'       # Keep other Deep Security logs
            ],
            'amsp_logs': [
                r'^AMSPInstallDebuglog\.log$',      # Only exact AMSP install log
                r'^ds_am\.log$',                    # Only exact ds_am.log
                r'^AMSP-Inst_LocalDebugLog\.log$',  # Only exact AMSP install debug log
                r'^AMSP-UnInst_LocalDebugLog\.log$', # Only exact AMSP uninstall debug log
                r'^ds_am-01\.log$',                 # Only exact ds_am-01.log
                r'^ds_am-02\.log$'                  # Only exact ds_am-02.log
            ],
            'system_info': [
                r'RunningProcess\.xml$',
                r'TopNBusyProcess\.txt$',
                r'SystemInfo\.txt$',
                r'DiagnosticInfo\.xml$'
            ],
            'configuration_files': [
                r'.*\.xml$',
                r'.*\.cfg$',
                r'.*\.conf$',
                r'policy.*\.txt$'
            ]
        }
        
        self.correlation_patterns = {
            'timing_correlation': [
                r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})',
                r'(\d{2}/\d{2}/\d{4} \d{1,2}:\d{2}:\d{2})'
            ],
            'component_correlation': [
                r'(amsp|anti.*malware)',
                r'(dpi|intrusion)',
                r'(integrity|fim)',
                r'(agent|dsa)'
            ],
            'issue_correlation': [
                r'(error|critical|failed)',
                r'(warning|warn)',
                r'(timeout|connection)',
                r'(startup|initialization)'
            ]
        }

    def analyze(self, zip_path: str) -> Dict[str, Any]:
        """Main entry point for diagnostic package analysis - matches API expectations"""
        import os
        
        try:
            self._update_progress("Initialization", "Starting diagnostic package analysis", 1)
            
            # Validate input
            if not zip_path or not os.path.exists(zip_path):
                raise ValueError(f"Invalid zip file path: {zip_path}")
            
            # Perform comprehensive analysis
            results = self.analyze_diagnostic_package(zip_path)
            
            self._update_progress("Completion", "Diagnostic package analysis completed", 100)
            return results
            
        except Exception as e:
            error_msg = f"Diagnostic package analysis failed: {str(e)}"
            self._update_progress("Error", error_msg, None)
            raise Exception(error_msg)

    def extract_zip_contents(self, zip_path: str) -> Dict[str, Any]:
        """Extract ZIP contents and return file list - convenience method for testing"""
        import tempfile
        import os
        
        try:
            # Create temporary extraction directory
            temp_dir = tempfile.mkdtemp(prefix="ds_diagnostic_test_")
            
            # Extract package
            extraction_result = self.extract_diagnostic_package(zip_path, temp_dir)
            
            return {
                'success': True,
                'extract_path': temp_dir,
                'extracted_files': extraction_result.get('extracted_files', []),
                'file_count': len(extraction_result.get('extracted_files', []))
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'extract_path': None,
                'extracted_files': [],
                'file_count': 0
            }

    def extract_diagnostic_package(self, zip_path: str, extract_path: str) -> Dict[str, Any]:
        """Extract and validate diagnostic package contents"""
        import zipfile
        import tempfile
        import shutil
        
        try:
            self._update_progress("Package Extraction", "Extracting diagnostic package contents", 5)
            
            extracted_files = {
                'ds_agent_logs': [],
                'amsp_logs': [],
                'system_info': [],
                'configuration_files': [],
                'other_files': []
            }
            
            extraction_stats = {
                'total_files': 0,
                'processed_files': 0,
                'skipped_files': 0,
                'errors': []
            }
            
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                file_list = zip_ref.namelist()
                extraction_stats['total_files'] = len(file_list)
                
                for i, file_name in enumerate(file_list):
                    # Update progress during extraction
                    if i % 10 == 0:
                        progress = 5 + int((i / len(file_list)) * 20)  # 5% to 25%
                        self._update_progress("Package Extraction", f"Extracting files... ({i}/{len(file_list)})", progress)
                    
                    try:
                        # Skip directories and very large files (>100MB)
                        file_info = zip_ref.getinfo(file_name)
                        if file_info.is_dir() or file_info.file_size > 100 * 1024 * 1024:
                            extraction_stats['skipped_files'] += 1
                            continue
                        
                        # Skip encrypted files - check if file is password protected
                        try:
                            # Try to read the file info to detect if it's encrypted
                            with zip_ref.open(file_name) as test_file:
                                # Try to read first few bytes to verify accessibility
                                test_file.read(10)
                        except RuntimeError as e:
                            if "password" in str(e).lower() or "encrypted" in str(e).lower():
                                print(f"⚠️  Skipping encrypted file: {file_name}")
                                extraction_stats['skipped_files'] += 1
                                extraction_stats['errors'].append(f"Skipped encrypted file: {file_name}")
                                continue
                            else:
                                # Re-raise other RuntimeErrors
                                raise e
                        except Exception as e:
                            # For other exceptions, try to continue
                            print(f"⚠️  Warning: Could not verify file {file_name}: {e}")
                        
                        # Extract file
                        extracted_path = zip_ref.extract(file_name, extract_path)
                        extraction_stats['processed_files'] += 1
                        
                        # Categorize file based on patterns
                        categorized = False
                        for category, patterns in self.package_patterns.items():
                            for pattern in patterns:
                                if re.search(pattern, file_name, re.IGNORECASE):
                                    extracted_files[category].append({
                                        'file_name': file_name,
                                        'file_path': extracted_path,
                                        'file_size': file_info.file_size,
                                        'category': category
                                    })
                                    categorized = True
                                    break
                            if categorized:
                                break
                        
                        if not categorized:
                            extracted_files['other_files'].append({
                                'file_name': file_name,
                                'file_path': extracted_path,
                                'file_size': file_info.file_size,
                                'category': 'other'
                            })
                            
                    except Exception as e:
                        extraction_stats['errors'].append(f"Failed to extract {file_name}: {str(e)}")
                        continue
            
            self._update_progress("Package Extraction", "Diagnostic package extraction completed", 25)
            
            return {
                'extracted_files': extracted_files,
                'extraction_stats': extraction_stats,
                'extract_path': extract_path
            }
            
        except Exception as e:
            raise SecurityError(f"Failed to extract diagnostic package: {str(e)}")

    def analyze_diagnostic_package(self, zip_path: str) -> Dict[str, Any]:
        """Comprehensive analysis of diagnostic package with multi-log correlation"""
        import tempfile
        import shutil
        import os
        
        self._update_progress("Initialization", "Starting diagnostic package analysis", 1)
        
        # Create temporary extraction directory
        temp_dir = tempfile.mkdtemp(prefix="ds_diagnostic_")
        
        comprehensive_results = {
            'package_summary': {
                'package_path': zip_path,
                'extraction_path': temp_dir,
                'total_files_analyzed': 0,
                'analysis_timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'analysis_duration': None
            },
            'extraction_results': {},
            'individual_analyses': {},
            'correlation_analysis': {},
            'consolidated_summary': {},
            'ml_insights': None,
            'rag_insights': None,
            'recommendations': [],
            'executive_summary': {}
        }
        
        start_time = datetime.now()
        
        try:
            # Extract diagnostic package
            extraction_results = self.extract_diagnostic_package(zip_path, temp_dir)
            comprehensive_results['extraction_results'] = extraction_results
            
            extracted_files = extraction_results['extracted_files']
            total_files = sum(len(files) for files in extracted_files.values())
            comprehensive_results['package_summary']['total_files_analyzed'] = total_files
            
            # Analyze each file category
            self._update_progress("Individual Analysis", "Analyzing DS Agent logs", 30)
            
            # DS Agent Log Analysis
            if extracted_files['ds_agent_logs']:
                ds_files = [f['file_path'] for f in extracted_files['ds_agent_logs']]
                if len(ds_files) == 1:
                    comprehensive_results['individual_analyses']['ds_agent'] = self.ds_analyzer.analyze_log_file(ds_files[0])
                else:
                    comprehensive_results['individual_analyses']['ds_agent'] = self.ds_analyzer.analyze_multiple_log_files(ds_files)
            
            self._update_progress("Individual Analysis", "Analyzing AMSP logs", 40)
            
            # AMSP Log Analysis
            if extracted_files['amsp_logs']:
                amsp_files = [f['file_path'] for f in extracted_files['amsp_logs']]
                amsp_results = []
                for amsp_file in amsp_files:
                    try:
                        result = self.amsp_analyzer.analyze_log_file(amsp_file)
                        amsp_results.append(result)
                    except Exception as e:
                        print(f"⚠️  AMSP analysis failed for {amsp_file}: {e}")
                        continue
                comprehensive_results['individual_analyses']['amsp'] = amsp_results if len(amsp_results) > 1 else (amsp_results[0] if amsp_results else None)
            
            self._update_progress("Individual Analysis", "Analyzing system information", 50)
            
            # System Analysis (AV Conflicts and Resource Analysis)
            running_process_files = [f for f in extracted_files['system_info'] if 'RunningProcess.xml' in f['file_name']]
            busy_process_files = [f for f in extracted_files['system_info'] if 'TopNBusyProcess.txt' in f['file_name']]
            
            if running_process_files:
                # AV Conflict Analysis
                try:
                    processes = self.conflict_analyzer.extract_processes_from_xml(running_process_files[0]['file_path'])
                    conflict_analysis = self.conflict_analyzer.analyze_conflicts(processes)
                    comprehensive_results['individual_analyses']['av_conflicts'] = {
                        'analysis_text': conflict_analysis,
                        'process_count': len(processes)
                    }
                except Exception as e:
                    print(f"⚠️  AV conflict analysis failed: {e}")
                    comprehensive_results['individual_analyses']['av_conflicts'] = {'error': str(e)}
                
                # Resource Analysis
                if busy_process_files:
                    try:
                        busy_processes = self.resource_analyzer.parse_top_n_busy_process(busy_process_files[0]['file_path'])
                        resource_analysis = self.resource_analyzer.analyze_resource_conflicts(processes, busy_processes)
                        comprehensive_results['individual_analyses']['resource_analysis'] = resource_analysis
                    except Exception as e:
                        print(f"⚠️  Resource analysis failed: {e}")
                        comprehensive_results['individual_analyses']['resource_analysis'] = {'error': str(e)}
            
            self._update_progress("Correlation Analysis", "Performing multi-log correlation", 60)
            
            # Multi-log correlation analysis
            comprehensive_results['correlation_analysis'] = self._perform_correlation_analysis(
                comprehensive_results['individual_analyses']
            )
            
            self._update_progress("ML Enhancement", "Running ML-enhanced analysis", 70)
            
            # ML Enhancement for comprehensive analysis
            if self.ml_analyzer and ML_AVAILABLE:
                try:
                    # Combine all log data for ML analysis
                    combined_log_data = self._prepare_combined_log_data(extracted_files, temp_dir)
                    
                    from ml_analyzer import enhance_analysis_with_ml
                    ml_insights = enhance_analysis_with_ml(combined_log_data, 'diagnostic_package')
                    
                    comprehensive_results['ml_insights'] = ml_insights
                    print(f"✅ ML diagnostic package analysis completed with {len(ml_insights.get('patterns', []))} patterns detected")
                except Exception as e:
                    print(f"⚠️  ML analysis failed: {e}")
                    comprehensive_results['ml_insights'] = None
            
            self._update_progress("Dynamic RAG Analysis", "Applying AI-enhanced analysis", 80)
            
            # Dynamic RAG Analysis for comprehensive insights
            if DYNAMIC_RAG_AVAILABLE:
                try:
                    # Prepare comprehensive context for Dynamic RAG
                    combined_context = self._prepare_comprehensive_rag_context(comprehensive_results, extracted_files, temp_dir)
                    
                    from dynamic_rag_system import apply_dynamic_rag_to_analysis
                    comprehensive_results = apply_dynamic_rag_to_analysis(
                        comprehensive_results, 
                        combined_context
                    )
                    
                    dynamic_rag = comprehensive_results.get('dynamic_rag_analysis', {})
                    if dynamic_rag and 'error' not in dynamic_rag:
                        print(f"✅ Dynamic RAG Diagnostic Package Analysis: {dynamic_rag.get('analysis_metadata', {}).get('knowledge_sources_used', 0)} sources")
                        
                        # Add dynamic insights to recommendations
                        if dynamic_rag.get('ai_response'):
                            ai_summary = dynamic_rag['ai_response'][:200] + "..." if len(dynamic_rag['ai_response']) > 200 else dynamic_rag['ai_response']
                            comprehensive_results['recommendations'].append(f'🧠 <strong>AI Diagnostic Package Analysis</strong>: {ai_summary}')
                    
                except Exception as e:
                    print(f"⚠️  Dynamic RAG analysis failed: {e}")
                    comprehensive_results['dynamic_rag_analysis'] = {'error': str(e)}
            
            self._update_progress("Consolidation", "Generating consolidated summary", 90)
            
            # Generate consolidated summary and recommendations
            comprehensive_results['consolidated_summary'] = self._generate_consolidated_summary(comprehensive_results)
            comprehensive_results['recommendations'] = self._generate_comprehensive_recommendations(comprehensive_results)
            comprehensive_results['executive_summary'] = self._generate_executive_summary(comprehensive_results)
            
            # Calculate analysis duration
            end_time = datetime.now()
            comprehensive_results['package_summary']['analysis_duration'] = str(end_time - start_time)
            
            self._update_progress("Complete", "Diagnostic package analysis completed", 100)
            
        except Exception as e:
            error_msg = f"Diagnostic package analysis failed: {str(e)}"
            print(f"❌ {error_msg}")
            comprehensive_results['error'] = error_msg
        finally:
            # Cleanup temporary directory
            try:
                shutil.rmtree(temp_dir)
            except Exception as e:
                print(f"⚠️ Failed to cleanup temporary directory: {e}")
        
        # Standardize return structure for frontend compatibility
        return comprehensive_results

    def _perform_correlation_analysis(self, individual_analyses: Dict[str, Any]) -> Dict[str, Any]:
        """Perform correlation analysis across multiple log sources"""
        correlation_results = {
            'timing_correlations': [],
            'component_correlations': [],
            'issue_correlations': [],
            'cross_log_patterns': [],
            'correlation_score': 0
        }
        
        try:
            # Extract events from all analyses for correlation
            all_events = []
            
            # Extract DS Agent events
            if 'ds_agent' in individual_analyses and individual_analyses['ds_agent']:
                ds_analysis = individual_analyses['ds_agent']
                for error in ds_analysis.get('errors', []):
                    all_events.append({
                        'source': 'ds_agent',
                        'type': 'error',
                        'timestamp': error.get('timestamp', ''),
                        'component': error.get('component', ''),
                        'message': error.get('message', ''),
                        'severity': 'error'
                    })
                for warning in ds_analysis.get('warnings', []):
                    all_events.append({
                        'source': 'ds_agent',
                        'type': 'warning',
                        'timestamp': warning.get('timestamp', ''),
                        'component': warning.get('component', ''),
                        'message': warning.get('message', ''),
                        'severity': 'warning'
                    })
            
            # Extract AMSP events
            if 'amsp' in individual_analyses and individual_analyses['amsp']:
                amsp_analysis = individual_analyses['amsp']
                if isinstance(amsp_analysis, list):
                    amsp_analysis = amsp_analysis[0]  # Take first analysis if multiple
                
                for error in amsp_analysis.get('errors', []):
                    all_events.append({
                        'source': 'amsp',
                        'type': 'error',
                        'timestamp': error.get('timestamp', ''),
                        'operation': error.get('operation', ''),
                        'message': error.get('message', ''),
                        'severity': 'error'
                    })
            
            # Timing correlation analysis
            if len(all_events) > 1:
                # Sort events by timestamp for timeline analysis
                sorted_events = sorted(all_events, key=lambda x: x.get('timestamp', ''))
                
                # Look for events within 5-minute windows
                correlation_windows = []
                current_window = []
                
                for i, event in enumerate(sorted_events):
                    if not current_window:
                        current_window.append(event)
                    else:
                        # Check if event is within 5 minutes of the last event in current window
                        if self._events_within_timeframe(current_window[-1], event, minutes=5):
                            current_window.append(event)
                        else:
                            if len(current_window) > 1:
                                correlation_windows.append(current_window)
                            current_window = [event]
                
                # Add final window if it has multiple events
                if len(current_window) > 1:
                    correlation_windows.append(current_window)
                
                # Analyze correlation windows
                for window in correlation_windows:
                    if len(window) > 1:
                        correlation_results['timing_correlations'].append({
                            'timeframe': f"{window[0]['timestamp']} - {window[-1]['timestamp']}",
                            'event_count': len(window),
                            'sources': list(set(event['source'] for event in window)),
                            'severity_mix': list(set(event['severity'] for event in window)),
                            'description': f"Correlated events across {len(set(event['source'] for event in window))} components"
                        })
            
            # Component correlation analysis
            component_issues = {}
            for event in all_events:
                component = event.get('component', event.get('operation', 'unknown'))
                if component not in component_issues:
                    component_issues[component] = []
                component_issues[component].append(event)
            
            # Look for components with issues across multiple sources
            for component, events in component_issues.items():
                sources = set(event['source'] for event in events)
                if len(sources) > 1:
                    correlation_results['component_correlations'].append({
                        'component': component,
                        'affected_sources': list(sources),
                        'event_count': len(events),
                        'severity_levels': list(set(event['severity'] for event in events)),
                        'description': f"{component} issues detected across {len(sources)} different log sources"
                    })
            
            # Calculate overall correlation score
            correlation_score = 0
            correlation_score += len(correlation_results['timing_correlations']) * 10
            correlation_score += len(correlation_results['component_correlations']) * 15
            correlation_score = min(100, correlation_score)  # Cap at 100
            
            correlation_results['correlation_score'] = correlation_score
            
        except Exception as e:
            print(f"⚠️  Correlation analysis failed: {e}")
            correlation_results['error'] = str(e)
        
        return correlation_results

    def _events_within_timeframe(self, event1: Dict[str, Any], event2: Dict[str, Any], minutes: int = 5) -> bool:
        """Check if two events occurred within the specified timeframe"""
        try:
            from datetime import datetime, timedelta
            
            # Parse timestamps (handle different formats)
            time1_str = event1.get('timestamp', '')
            time2_str = event2.get('timestamp', '')
            
            if not time1_str or not time2_str:
                return False
            
            # Try different timestamp formats
            formats = [
                '%Y-%m-%d %H:%M:%S.%f',
                '%Y-%m-%d %H:%M:%S',
                '%m/%d/%Y %I:%M:%S %p',
                '%d/%m/%Y %H:%M:%S'
            ]
            
            time1 = None
            time2 = None
            
            for fmt in formats:
                try:
                    time1 = datetime.strptime(time1_str, fmt)
                    break
                except ValueError:
                    continue
            
            for fmt in formats:
                try:
                    time2 = datetime.strptime(time2_str, fmt)
                    break
                except ValueError:
                    continue
            
            if time1 and time2:
                time_diff = abs((time2 - time1).total_seconds())
                return time_diff <= (minutes * 60)
            
        except Exception as e:
            print(f"⚠️  Timestamp comparison failed: {e}")
        
        return False

    def _prepare_combined_log_data(self, extracted_files: Dict[str, List], temp_dir: str) -> str:
        """Prepare combined log data for ML analysis"""
        combined_data = []
        
        try:
            # Combine DS Agent logs
            for ds_file in extracted_files.get('ds_agent_logs', []):
                try:
                    with open(ds_file['file_path'], 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()[:10000]  # Limit to first 10KB per file
                        combined_data.append(f"=== DS AGENT LOG: {ds_file['file_name']} ===\n{content}\n")
                except Exception as e:
                    print(f"⚠️  Failed to read DS Agent log {ds_file['file_name']}: {e}")
            
            # Combine AMSP logs
            for amsp_file in extracted_files.get('amsp_logs', []):
                try:
                    with open(amsp_file['file_path'], 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()[:10000]  # Limit to first 10KB per file
                        combined_data.append(f"=== AMSP LOG: {amsp_file['file_name']} ===\n{content}\n")
                except Exception as e:
                    print(f"⚠️  Failed to read AMSP log {amsp_file['file_name']}: {e}")
            
            # Combine system info files
            for sys_file in extracted_files.get('system_info', []):
                if sys_file['file_name'].endswith('.txt'):  # Only text files for ML
                    try:
                        with open(sys_file['file_path'], 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()[:5000]  # Limit to first 5KB per file
                            combined_data.append(f"=== SYSTEM INFO: {sys_file['file_name']} ===\n{content}\n")
                    except Exception as e:
                        print(f"⚠️  Failed to read system info {sys_file['file_name']}: {e}")
            
        except Exception as e:
            print(f"⚠️  Failed to prepare combined log data: {e}")
        
        return '\n'.join(combined_data)

    def _prepare_comprehensive_rag_context(self, comprehensive_results: Dict[str, Any], extracted_files: Dict[str, List], temp_dir: str) -> str:
        """Prepare comprehensive context for RAG analysis"""
        context_parts = []
        
        context_parts.append("DEEP SECURITY DIAGNOSTIC PACKAGE ANALYSIS CONTEXT:")
        context_parts.append(f"Package: {comprehensive_results['package_summary']['package_path']}")
        context_parts.append(f"Files Analyzed: {comprehensive_results['package_summary']['total_files_analyzed']}")
        context_parts.append(f"Analysis Timestamp: {comprehensive_results['package_summary']['analysis_timestamp']}")
        
        # Add file category summary
        context_parts.append("\nFILE CATEGORIES:")
        for category, files in extracted_files.items():
            if files:
                context_parts.append(f"- {category}: {len(files)} files")
        
        # Add individual analysis summaries
        context_parts.append("\nINDIVIDUAL ANALYSIS RESULTS:")
        
        if 'ds_agent' in comprehensive_results['individual_analyses']:
            ds_analysis = comprehensive_results['individual_analyses']['ds_agent']
            if ds_analysis and 'summary' in ds_analysis:
                summary = ds_analysis['summary']
                context_parts.append(f"DS Agent: {summary.get('error_count', 0)} errors, {summary.get('warning_count', 0)} warnings, {summary.get('critical_count', 0)} critical")
        
        if 'amsp' in comprehensive_results['individual_analyses']:
            amsp_analysis = comprehensive_results['individual_analyses']['amsp']
            if amsp_analysis:
                if isinstance(amsp_analysis, list):
                    amsp_analysis = amsp_analysis[0]
                if 'summary' in amsp_analysis:
                    summary = amsp_analysis['summary']
                    context_parts.append(f"AMSP: {summary.get('error_count', 0)} errors, {summary.get('warning_count', 0)} warnings, {summary.get('critical_count', 0)} critical")
        
        # Add correlation analysis summary
        if 'correlation_analysis' in comprehensive_results:
            correlation = comprehensive_results['correlation_analysis']
            context_parts.append("\nCORRELATION ANALYSIS:")
            context_parts.append(f"Correlation Score: {correlation.get('correlation_score', 0)}/100")
            context_parts.append(f"Timing Correlations: {len(correlation.get('timing_correlations', []))}")
            context_parts.append(f"Component Correlations: {len(correlation.get('component_correlations', []))}")
        
        # Add sample log entries for context
        context_parts.append("\nSAMPLE LOG CONTENT:")
        try:
            sample_content = self._prepare_combined_log_data(extracted_files, temp_dir)[:2000]  # First 2KB for context
            context_parts.append(sample_content)
        except Exception as e:
            context_parts.append(f"Sample content unavailable: {e}")
        
        return '\n'.join(context_parts)

    def _generate_consolidated_summary(self, comprehensive_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate consolidated summary across all analyses"""
        consolidated = {
            'overall_health_score': 0,
            'total_issues': 0,
            'critical_issues': 0,
            'component_status': {},
            'key_findings': [],
            'risk_assessment': 'Unknown'
        }
        
        try:
            total_errors = 0
            total_warnings = 0
            total_critical = 0
            
            # Aggregate DS Agent results
            if 'ds_agent' in comprehensive_results['individual_analyses']:
                ds_analysis = comprehensive_results['individual_analyses']['ds_agent']
                if ds_analysis and 'summary' in ds_analysis:
                    summary = ds_analysis['summary']
                    total_errors += summary.get('error_count', 0)
                    total_warnings += summary.get('warning_count', 0)
                    total_critical += summary.get('critical_count', 0)
                    
                    consolidated['component_status']['ds_agent'] = {
                        'status': 'Critical' if summary.get('critical_count', 0) > 0 else 'Warning' if summary.get('error_count', 0) > 0 else 'Healthy',
                        'issues': summary.get('error_count', 0) + summary.get('warning_count', 0)
                    }
            
            # Aggregate AMSP results
            if 'amsp' in comprehensive_results['individual_analyses']:
                amsp_analysis = comprehensive_results['individual_analyses']['amsp']
                if amsp_analysis:
                    if isinstance(amsp_analysis, list):
                        amsp_analysis = amsp_analysis[0]
                    if 'summary' in amsp_analysis:
                        summary = amsp_analysis['summary']
                        total_errors += summary.get('error_count', 0)
                        total_warnings += summary.get('warning_count', 0)
                        total_critical += summary.get('critical_count', 0)
                        
                        consolidated['component_status']['amsp'] = {
                            'status': 'Critical' if summary.get('critical_count', 0) > 0 else 'Warning' if summary.get('error_count', 0) > 0 else 'Healthy',
                            'issues': summary.get('error_count', 0) + summary.get('warning_count', 0)
                        }
            
            # Set consolidated totals
            consolidated['total_issues'] = total_errors + total_warnings
            consolidated['critical_issues'] = total_critical
            
            # Calculate overall health score (100 = perfect, 0 = critical)
            if total_critical > 0:
                consolidated['overall_health_score'] = max(0, 30 - (total_critical * 10))
            elif total_errors > 10:
                consolidated['overall_health_score'] = max(30, 70 - (total_errors * 2))
            elif total_warnings > 20:
                consolidated['overall_health_score'] = max(70, 90 - total_warnings)
            else:
                consolidated['overall_health_score'] = 95
            
            # Risk assessment
            if consolidated['overall_health_score'] < 40:
                consolidated['risk_assessment'] = 'High'
            elif consolidated['overall_health_score'] < 70:
                consolidated['risk_assessment'] = 'Medium'
            else:
                consolidated['risk_assessment'] = 'Low'
            
            # Generate key findings
            if total_critical > 0:
                consolidated['key_findings'].append(f"🔥 {total_critical} critical issues require immediate attention")
            if total_errors > 5:
                consolidated['key_findings'].append(f"⚠️ {total_errors} errors detected across components")
            
            # Add correlation findings
            if 'correlation_analysis' in comprehensive_results:
                correlation_score = comprehensive_results['correlation_analysis'].get('correlation_score', 0)
                if correlation_score > 50:
                    consolidated['key_findings'].append(f"🔗 High correlation detected ({correlation_score}%) - systemic issues likely")
            
        except Exception as e:
            print(f"⚠️  Consolidated summary generation failed: {e}")
            consolidated['error'] = str(e)
        
        return consolidated

    def _generate_comprehensive_recommendations(self, comprehensive_results: Dict[str, Any]) -> List[str]:
        """Generate comprehensive recommendations based on all analyses"""
        recommendations = []
        
        try:
            consolidated = comprehensive_results.get('consolidated_summary', {})
            
            # High-level system recommendations
            overall_health = consolidated.get('overall_health_score', 0)
            if overall_health < 40:
                recommendations.append("🚨 <strong>CRITICAL SYSTEM STATUS</strong>: Immediate intervention required - Deep Security environment compromised")
            elif overall_health < 70:
                recommendations.append("⚠️ <strong>DEGRADED SYSTEM STATUS</strong>: Multiple issues detected - schedule maintenance window")
            else:
                recommendations.append("✅ <strong>STABLE SYSTEM STATUS</strong>: System functioning within normal parameters")
            
            # Component-specific recommendations
            for component, status in consolidated.get('component_status', {}).items():
                if status['status'] == 'Critical':
                    recommendations.append(f"🔥 <strong>{component.upper()}</strong>: Critical issues detected - {status['issues']} problems require immediate resolution")
                elif status['status'] == 'Warning':
                    recommendations.append(f"⚠️ <strong>{component.upper()}</strong>: Performance degraded - {status['issues']} issues need attention")
            
            # Correlation-based recommendations
            correlation_analysis = comprehensive_results.get('correlation_analysis', {})
            correlation_score = correlation_analysis.get('correlation_score', 0)
            
            if correlation_score > 75:
                recommendations.append("🔗 <strong>SYSTEMIC ISSUES DETECTED</strong>: High correlation suggests root cause analysis needed")
            elif correlation_score > 50:
                recommendations.append("🔍 <strong>PATTERN ANALYSIS</strong>: Multiple components affected - investigate common dependencies")
            
            # Timing correlation recommendations
            timing_correlations = correlation_analysis.get('timing_correlations', [])
            if timing_correlations:
                recommendations.append(f"⏰ <strong>TEMPORAL PATTERNS</strong>: {len(timing_correlations)} time-correlated event clusters detected")
            
            # ML-based recommendations
            ml_insights = comprehensive_results.get('ml_insights')
            if ml_insights and 'recommendations' in ml_insights:
                for ml_rec in ml_insights['recommendations'][:2]:  # Top 2 ML recommendations
                    recommendations.append(f"🧠 <strong>ML INSIGHT</strong>: {ml_rec}")
            
            # RAG-based recommendations
            dynamic_rag = comprehensive_results.get('dynamic_rag_analysis', {})
            if dynamic_rag and dynamic_rag.get('ai_response'):
                ai_response = dynamic_rag['ai_response'][:150] + "..." if len(dynamic_rag['ai_response']) > 150 else dynamic_rag['ai_response']
                recommendations.append(f"📚 <strong>KNOWLEDGE BASE INSIGHT</strong>: {ai_response}")
            
            # Implementation guidance
            if consolidated.get('critical_issues', 0) > 0:
                recommendations.extend([
                    "📋 <strong>IMMEDIATE ACTIONS</strong>:",
                    "  1. Address all critical issues before proceeding with other changes",
                    "  2. Implement changes during maintenance window",
                    "  3. Monitor system stability after each change",
                    "  4. Document all resolution steps for future reference"
                ])
            
            if not recommendations:
                recommendations.append("✅ No specific issues detected - continue regular monitoring and maintenance")
            
        except Exception as e:
            print(f"⚠️  Comprehensive recommendations generation failed: {e}")
            recommendations.append(f"⚠️ Recommendation generation error: {str(e)}")
        
        return recommendations

    def _generate_executive_summary(self, comprehensive_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate executive summary for management reporting"""
        executive_summary = {
            'system_status': 'Unknown',
            'business_impact': 'Unknown',
            'action_required': 'Unknown',
            'timeline': 'Unknown',
            'key_metrics': {},
            'executive_recommendations': []
        }
        
        try:
            consolidated = comprehensive_results.get('consolidated_summary', {})
            health_score = consolidated.get('overall_health_score', 0)
            
            # System status assessment
            if health_score >= 85:
                executive_summary['system_status'] = 'Optimal'
                executive_summary['business_impact'] = 'No Impact'
                executive_summary['action_required'] = 'Routine Monitoring'
                executive_summary['timeline'] = 'No Immediate Action Required'
            elif health_score >= 70:
                executive_summary['system_status'] = 'Stable'
                executive_summary['business_impact'] = 'Minimal Impact'
                executive_summary['action_required'] = 'Scheduled Maintenance'
                executive_summary['timeline'] = 'Within 30 Days'
            elif health_score >= 40:
                executive_summary['system_status'] = 'At Risk'
                executive_summary['business_impact'] = 'Moderate Impact'
                executive_summary['action_required'] = 'Immediate Attention'
                executive_summary['timeline'] = 'Within 7 Days'
            else:
                executive_summary['system_status'] = 'Critical'
                executive_summary['business_impact'] = 'High Impact'
                executive_summary['action_required'] = 'Emergency Response'
                executive_summary['timeline'] = 'Within 24 Hours'
            
            # Key metrics
            executive_summary['key_metrics'] = {
                'overall_health_score': f"{health_score}%",
                'total_issues': consolidated.get('total_issues', 0),
                'critical_issues': consolidated.get('critical_issues', 0),
                'components_analyzed': len(consolidated.get('component_status', {})),
                'files_analyzed': comprehensive_results['package_summary']['total_files_analyzed']
            }
            
            # Executive recommendations
            if health_score < 40:
                executive_summary['executive_recommendations'] = [
                    "Engage security team immediately",
                    "Initiate emergency response procedures",
                    "Consider temporary service isolation",
                    "Schedule immediate expert consultation"
                ]
            elif health_score < 70:
                executive_summary['executive_recommendations'] = [
                    "Schedule maintenance window",
                    "Assign dedicated resources",
                    "Implement monitoring enhancements",
                    "Review system architecture"
                ]
            else:
                executive_summary['executive_recommendations'] = [
                    "Continue regular monitoring",
                    "Schedule routine maintenance",
                    "Update documentation",
                    "Review preventive measures"
                ]
            
        except Exception as e:
            print(f"⚠️  Executive summary generation failed: {e}")
            executive_summary['error'] = str(e)
        
        return executive_summary
