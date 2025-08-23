"""
Deep Security Analyzer Classes
Contains all analyzer classes for different log types and analysis functions.
"""

import os
import re
import json
import xml.etree.ElementTree as ET
from datetime import datetime
from typing import List, Dict, Any
import sys
sys.path.append('../shared')
from security import SecurityError, validate_xml_content, sanitize_process_name

# Import OpenAI for analysis
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

# Import ML and RAG systems
try:
    from ml_analyzer import enhance_analysis_with_ml, MLLogAnalyzer
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False

# Dynamic RAG Integration - the only RAG system
try:
    from dynamic_rag_system import DynamicRAGSystem, apply_dynamic_rag_to_analysis
    DYNAMIC_RAG_AVAILABLE = True
    print("✅ Dynamic RAG system loaded successfully")
except ImportError as e:
    DYNAMIC_RAG_AVAILABLE = False
    print(f"⚠️ Dynamic RAG system not available: {e}")

class DSAgentLogAnalyzer:
    """
    Deep Security Agent Log Analyzer with Dynamic RAG integration
    Now includes real-time progress tracking for better UX
    """
    
    def __init__(self, session_manager=None, session_id=None):
        """Initialize with optional progress tracking"""
        self.session_manager = session_manager
        self.session_id = session_id
        
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
        """Initialize connection patterns and configurations"""
        # Cloud One Workload Security Connection Patterns (Enhanced from DS20 Technical Documentation)
        self.connection_patterns = {
            'fqdn_connections': [
                r'workload\.([a-z]{2}-\d)\.cloudone\.trendmicro\.com',
                r'agents\.workload\.([a-z]{2}-\d)\.cloudone\.trendmicro\.com', 
                r'deepsecurity\.trendmicro\.com',
                r'agents\.deepsecurity\.trendmicro\.com'
            ],
            'connection_success': [
                r'connected to|connection established|heartbeat.*successful',
                r'authentication.*successful|login.*successful',
                r'policy.*received|update.*successful',
                r'SetSecurityConfiguration.*successful|GetAgentStatus.*ok',
                r'ActivateAgent.*successful|GetAgentEvents.*retrieved'
            ],
            'connection_failures': [
                r'connection.*failed|failed.*connect|timeout.*connecting',
                r'unable to connect|connection.*refused|connection.*reset',
                r'ssl.*error|certificate.*error|tls.*error',
                r'authentication.*failed|login.*failed|access.*denied',
                r'network.*unreachable|host.*unreachable|dns.*failed',
                r'heartbeat.*failed|GetAgentStatus.*failed',
                r'SetSecurityConfiguration.*failed|proxy.*authentication.*failed'
            ],
            'dns_issues': [
                r'dns.*resolution.*failed|cannot resolve|unknown host',
                r'name resolution.*failed|hostname.*not found',
                r'getaddrinfo.*failed|resolver.*error'
            ],
            'proxy_issues': [
                r'proxy.*authentication|proxy.*failed|proxy.*error',
                r'http.*407|proxy.*required|AssignDsmProxy.*failed',
                r'incorrect.*credentials.*proxy|proxy.*returned.*407'
            ],
            'firewall_issues': [
                r'port.*blocked|firewall.*blocking|connection.*blocked',
                r'port.*443.*failed|https.*blocked|port.*4120.*failed',
                r'connection.*timed.*out|network.*timeout'
            ],
            'ssl_certificate_issues': [
                r'certificate.*verification.*failed|certificate.*expired',
                r'certificate.*invalid|ssl.*handshake.*failed',
                r'certificate.*not.*trusted|certificate.*chain.*error',
                r'ds_agent\.crt.*error|ds_agent_dsm\.crt.*failed'
            ],
            'agent_communication_commands': [
                r'SetSecurityConfiguration|GetAgentStatus|GetAgentEvents',
                r'HeartbeatNow|ActivateAgent|GetComponentInfo',
                r'AssignDsmProxy|CreateDiagnostic|GetConfiguration'
            ]
        }
        
        # Deep Security Agent Communication Ports (from DS20 documentation)
        self.ds_communication_ports = {
            '4120': 'Agent-Manager Communication (HTTPS)',
            '4119': 'Agent Installation/Upgrade (HTTPS)', 
            '4118': 'Relay Commands (HTTPS)',
            '443': 'Cloud One/External Services (HTTPS)',
            '527': 'Smart Scan Server (if local)'
        }
        
        # Regional Cloud One endpoints for connection health analysis
        self.regional_endpoints = {
            'au-1': 'Australia',
            'ca-1': 'Canada', 
            'de-1': 'Germany',
            'in-1': 'India',
            'jp-1': 'Japan',
            'sg-1': 'Singapore',
            'gb-1': 'UK',
            'us-1': 'USA',
            'ae-1': 'UAE'
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
            'firewall': [r'firewall', r'fw'],
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

    def analyze_connection_health(self, log_entries: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Enhanced Deep Security Agent connection health analysis based on DS20 technical documentation"""
        connection_health = {
            'overall_status': 'unknown',
            'connected_regions': [],
            'connection_attempts': 0,
            'successful_connections': 0,
            'failed_connections': 0,
            'dns_issues': [],
            'ssl_certificate_issues': [],
            'proxy_issues': [],
            'firewall_issues': [],
            'agent_command_failures': [],
            'communication_port_issues': [],
            'heartbeat_status': 'unknown',
            'heartbeat_analysis': {
                'total_heartbeats': 0,
                'successful_heartbeats': 0,
                'failed_heartbeats': 0,
                'average_interval': 0
            },
            'last_successful_connection': None,
            'recommendations': []
        }
        
        heartbeat_timestamps = []
        
        for entry in log_entries:
            if not entry.get('parsed'):
                continue
                
            message = entry['message'].lower()
            timestamp = entry.get('timestamp', '')
            
            # Enhanced heartbeat analysis (DS agents send heartbeats every ~10 minutes)
            if re.search(r'heartbeat', message, re.IGNORECASE):
                connection_health['heartbeat_analysis']['total_heartbeats'] += 1
                if re.search(r'heartbeat.*successful|heartbeat.*ok|heartbeatnow.*completed', message, re.IGNORECASE):
                    connection_health['heartbeat_analysis']['successful_heartbeats'] += 1
                    connection_health['heartbeat_status'] = 'healthy'
                elif re.search(r'heartbeat.*failed|heartbeat.*error|heartbeat.*timeout', message, re.IGNORECASE):
                    connection_health['heartbeat_analysis']['failed_heartbeats'] += 1
                    connection_health['heartbeat_status'] = 'unhealthy'
                
                if timestamp:
                    heartbeat_timestamps.append(timestamp)
            
            # Enhanced DS Agent communication command tracking
            for pattern in self.connection_patterns['agent_communication_commands']:
                if re.search(pattern, message, re.IGNORECASE):
                    connection_health['connection_attempts'] += 1
                    
                    # Check if DS command was successful
                    if re.search(r'successful|completed|ok|retrieved|activated', message, re.IGNORECASE):
                        connection_health['successful_connections'] += 1
                        connection_health['last_successful_connection'] = timestamp
                    elif re.search(r'failed|error|timeout|denied|unable', message, re.IGNORECASE):
                        connection_health['failed_connections'] += 1
                        connection_health['agent_command_failures'].append({
                            'timestamp': timestamp,
                            'command': pattern,
                            'message': entry['message'][:200],
                            'line': entry.get('line', 'unknown')
                        })
            
            # Check for Cloud One FQDN connections with regional tracking
            for pattern in self.connection_patterns['fqdn_connections']:
                match = re.search(pattern, message, re.IGNORECASE)
                if match:
                    connection_health['connection_attempts'] += 1
                    if len(match.groups()) > 0 and match.group(1) in self.regional_endpoints:
                        region = self.regional_endpoints[match.group(1)]
                        if region not in connection_health['connected_regions']:
                            connection_health['connected_regions'].append(region)
            
            # Enhanced connection success detection
            for pattern in self.connection_patterns['connection_success']:
                if re.search(pattern, message, re.IGNORECASE):
                    connection_health['successful_connections'] += 1
                    connection_health['last_successful_connection'] = timestamp
                    break
            
            # Enhanced connection failure detection
            for pattern in self.connection_patterns['connection_failures']:
                if re.search(pattern, message, re.IGNORECASE):
                    connection_health['failed_connections'] += 1
                    break
            
            # Enhanced DNS issue detection
            for pattern in self.connection_patterns['dns_issues']:
                if re.search(pattern, message, re.IGNORECASE):
                    connection_health['dns_issues'].append({
                        'timestamp': timestamp,
                        'message': entry['message'],
                        'line': entry.get('line', 'unknown'),
                        'severity': 'high' if 'failed' in message else 'medium'
                    })
                    break
            
            # Enhanced proxy issue detection (DS-specific proxy patterns)
            for pattern in self.connection_patterns['proxy_issues']:
                if re.search(pattern, message, re.IGNORECASE):
                    connection_health['proxy_issues'].append({
                        'timestamp': timestamp,
                        'message': entry['message'],
                        'line': entry.get('line', 'unknown'),
                        'type': 'authentication' if '407' in message else 'configuration',
                        'command_related': 'AssignDsmProxy' in entry['message']
                    })
                    break
            
            # Enhanced firewall issue detection with DS communication port tracking
            for pattern in self.connection_patterns['firewall_issues']:
                if re.search(pattern, message, re.IGNORECASE):
                    # Identify specific DS communication port if mentioned
                    affected_port = 'unknown'
                    for port, description in self.ds_communication_ports.items():
                        if port in message:
                            affected_port = f"{port} ({description})"
                            break
                    
                    connection_health['firewall_issues'].append({
                        'timestamp': timestamp,
                        'message': entry['message'],
                        'line': entry.get('line', 'unknown'),
                        'affected_port': affected_port
                    })
                    
                    if affected_port != 'unknown':
                        connection_health['communication_port_issues'].append({
                            'port': affected_port,
                            'timestamp': timestamp,
                            'issue_type': 'blocked' if 'blocked' in message else 'timeout'
                        })
                    break
            
            # Enhanced SSL/Certificate issue detection (DS-specific certificate files)
            for pattern in self.connection_patterns['ssl_certificate_issues']:
                if re.search(pattern, message, re.IGNORECASE):
                    cert_type = 'unknown'
                    if 'ds_agent.crt' in message:
                        cert_type = 'Agent SSL Certificate (ds_agent.crt)'
                    elif 'ds_agent_dsm.crt' in message:
                        cert_type = 'Manager SSL Certificate (ds_agent_dsm.crt)'
                    elif 'certificate' in message:
                        cert_type = 'SSL Certificate'
                    
                    connection_health['ssl_certificate_issues'].append({
                        'timestamp': timestamp,
                        'message': entry['message'],
                        'line': entry.get('line', 'unknown'),
                        'certificate_type': cert_type
                    })
                    break
        
        # Calculate heartbeat interval analysis
        if len(heartbeat_timestamps) > 1:
            try:
                from datetime import datetime
                parsed_timestamps = []
                for ts in heartbeat_timestamps:
                    # Try different timestamp formats
                    for fmt in ['%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M:%S.%f', '%m/%d/%Y %H:%M:%S']:
                        try:
                            parsed_timestamps.append(datetime.strptime(ts, fmt))
                            break
                        except:
                            continue
                
                if len(parsed_timestamps) > 1:
                    intervals = [(parsed_timestamps[i+1] - parsed_timestamps[i]).total_seconds() 
                               for i in range(len(parsed_timestamps)-1)]
                    connection_health['heartbeat_analysis']['average_interval'] = sum(intervals) / len(intervals)
            except:
                pass  # If timestamp parsing fails, skip interval calculation
        
        # Enhanced overall connection health status determination
        total_attempts = connection_health['connection_attempts']
        successful_connections = connection_health['successful_connections']
        failed_connections = connection_health['failed_connections']
        
        if total_attempts > 0:
            success_rate = successful_connections / total_attempts
            if success_rate >= 0.8:
                connection_health['overall_status'] = 'healthy'
            elif success_rate >= 0.6:
                connection_health['overall_status'] = 'mostly_healthy'
            elif success_rate >= 0.3:
                connection_health['overall_status'] = 'unstable'
            else:
                connection_health['overall_status'] = 'unhealthy'
        elif connection_health['heartbeat_analysis']['total_heartbeats'] > 0:
            # If no explicit connection attempts but heartbeats present
            heartbeat_success_rate = (connection_health['heartbeat_analysis']['successful_heartbeats'] / 
                                    connection_health['heartbeat_analysis']['total_heartbeats'])
            if heartbeat_success_rate >= 0.8:
                connection_health['overall_status'] = 'healthy'
            elif heartbeat_success_rate >= 0.6:
                connection_health['overall_status'] = 'mostly_healthy'
            else:
                connection_health['overall_status'] = 'unstable'
        else:
            connection_health['overall_status'] = 'no_connection_activity'
        
        # Enhanced DS-specific recommendations based on technical documentation
        recommendations = []
        
        if connection_health['dns_issues']:
            recommendations.append(
                "🌐 DNS Resolution Issues: Verify DNS server can resolve Cloud One FQDNs. "
                "Test manual resolution: nslookup workload.us-1.cloudone.trendmicro.com. "
                "Check corporate DNS filtering and ensure wildcard *.cloudone.trendmicro.com is allowed."
            )
        
        if connection_health['firewall_issues'] or connection_health['communication_port_issues']:
            port_info = ""
            if connection_health['communication_port_issues']:
                affected_ports = list(set([issue['port'] for issue in connection_health['communication_port_issues']]))
                port_info = f" Affected ports: {', '.join(affected_ports)}."
            
            recommendations.append(
                f"�️ Firewall Configuration: Ensure outbound HTTPS (443, 4120, 4119, 4118) to *.cloudone.trendmicro.com is allowed. "
                f"DS Agent requires these ports for Manager communication, updates, and relay services.{port_info}"
            )
        
        if connection_health['proxy_issues']:
            proxy_commands = any(issue.get('command_related', False) for issue in connection_health['proxy_issues'])
            proxy_advice = " Use 'dsa_control -m proxy://server:port' to configure DS Agent proxy settings." if proxy_commands else ""
            
            recommendations.append(
                f"🔄 Proxy Configuration: Check proxy authentication and HTTPS inspection settings. "
                f"Ensure proxy allows connections to Trend Micro Cloud One services.{proxy_advice}"
            )
        
        if connection_health['ssl_certificate_issues']:
            cert_files = [issue['certificate_type'] for issue in connection_health['ssl_certificate_issues'] 
                         if 'ds_agent' in issue['certificate_type']]
            cert_advice = f" Check {', '.join(set(cert_files))} file integrity." if cert_files else ""
            
            recommendations.append(
                f"🔒 SSL Certificate Issues: Verify system time accuracy and certificate trust store. "
                f"Check if corporate SSL inspection interferes with DS Agent certificates.{cert_advice}"
            )
        
        if connection_health['agent_command_failures']:
            command_types = [failure['command'] for failure in connection_health['agent_command_failures']]
            recommendations.append(
                f"🤖 DS Agent Command Failures: Multiple agent commands failing. "
                f"Most affected: {', '.join(set(command_types)[:3])}. Check agent activation and manager connectivity."
            )
        
        # Heartbeat-specific recommendations
        heartbeat_data = connection_health['heartbeat_analysis']
        if heartbeat_data['total_heartbeats'] > 0:
            if heartbeat_data['failed_heartbeats'] > heartbeat_data['successful_heartbeats']:
                recommendations.append(
                    "💓 Heartbeat Failures: High heartbeat failure rate indicates DS Agent isolation from manager. "
                    "Standard heartbeat interval is ~10 minutes. Check network stability and manager availability."
                )
            elif heartbeat_data['average_interval'] > 900:  # More than 15 minutes
                recommendations.append(
                    "💓 Heartbeat Timing: Abnormal heartbeat intervals detected. "
                    "DS Agent standard heartbeat is ~10 minutes. Check for network latency or agent performance issues."
                )
        
        if connection_health['overall_status'] == 'unhealthy':
            recommendations.append(
                '<i class="fa-solid fa-triangle-exclamation text-warning"></i> Critical Connection Health: DS Agent cannot establish reliable connection to Cloud One Workload Security. '
                'This compromises security protection. Immediate network troubleshooting required for ports 443, 4120.'
            )
        elif connection_health['overall_status'] == 'no_connection_activity':
            recommendations.append(
                '<i class="fa-solid fa-chart-bar me-2"></i>No Connection Activity: Limited DS Agent communication detected in logs. '
                'This may be normal for short log periods or inactive agents. Extend log collection timeframe if needed.'
            )
        
        connection_health['recommendations'] = recommendations
        return connection_health

    def analyze_log_file(self, file_path: str) -> Dict[str, Any]:
        """Analyze the entire log file with ML enhancement and progress tracking"""
        
        # Stage 1: File Parsing
        self._update_progress("File Parsing", "Reading uploaded files...", 5)
        
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
            'ml_insights': None,
            'dynamic_rag_analysis': None
        }
        
        self._update_progress("File Parsing", "Validating file format...", 10)
        
        try:
            self._update_progress("File Parsing", "Extracting log entries...", 15)
            
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                for line_num, line in enumerate(f, 1):
                    if line_num > 10000:
                        break
                    
                    results['summary']['total_lines'] += 1
                    line = line.strip()
                    
                    if not line:
                        continue
                    
                    log_entry = self.parse_log_entry(line)
                    
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
            
            self._update_progress("File Parsing", "File parsing completed ✓", 25)
            
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
            
            connection_health = self.analyze_connection_health(all_log_entries)
            results['connection_health'] = connection_health
            
            # Add connection health recommendations to main recommendations
            results['recommendations'].extend(connection_health['recommendations'])
            
            # Stage 2: ML Pattern Recognition & Analysis
            self._update_progress("ML Pattern Recognition & Analysis", "Loading ML pattern recognition models...", 30)
            
            if ML_AVAILABLE:
                try:
                    self._update_progress("ML Pattern Recognition & Analysis", "Running behavioral analysis algorithms...", 32)
                    
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        log_content = f.read()
                    
                    self._update_progress("ML Pattern Recognition & Analysis", "Detecting anomalies and unusual patterns...", 34)
                    
                    ml_insights = enhance_analysis_with_ml(log_content, 'ds_logs')
                    results['ml_insights'] = ml_insights
                    
                    self._update_progress("ML Pattern Recognition & Analysis", "Analyzing component health scores...", 36)
                    
                    ml_recommendations = ml_insights.get('recommendations', [])
                    results['recommendations'].extend(ml_recommendations)
                    
                    self._update_progress("ML Pattern Recognition & Analysis", "Classifying severity levels with ML...", 38)
                    
                    print(f"✅ ML Analysis completed: {ml_insights.get('overview', {}).get('total_entries', 0)} entries analyzed")
                    
                    self._update_progress("ML Pattern Recognition & Analysis", "ML analysis enhancement completed ✓", 40)
                    
                except Exception as e:
                    print(f'⚠️ ML analysis failed: {e}')
                    results['ml_insights'] = {'error': str(e)}
            else:
                results['ml_insights'] = {'status': 'ML features not available'}
            
            # Stage 3: Dynamic RAG & AI Intelligence
            self._update_progress("Dynamic RAG & AI Intelligence", "Initializing Dynamic RAG system...", 45)
            
            if DYNAMIC_RAG_AVAILABLE:
                try:
                    self._update_progress("Dynamic RAG & AI Intelligence", "Loading Claude AI analysis engine...", 50)
                    
                    # Try Dynamic RAG first for intelligent prompt generation
                    try:
                        self._update_progress("Dynamic RAG & AI Intelligence", "Extracting log context and components...", 55)
                        
                        # Read log content for dynamic analysis
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            log_content = f.read()
                        
                        self._update_progress("Dynamic RAG & AI Intelligence", "Generating ML-enhanced dynamic queries...", 58)
                        
                        from dynamic_rag_system import apply_dynamic_rag_to_analysis
                        results = apply_dynamic_rag_to_analysis(results, log_content)
                        
                        self._update_progress("Dynamic RAG & AI Intelligence", "Searching proprietary PDF knowledge base...", 62)
                        
                        self._update_progress("Dynamic RAG & AI Intelligence", "Processing with Claude-4 Sonnet AI...", 68)
                        
                        dynamic_rag = results.get('dynamic_rag_analysis', {})
                        if dynamic_rag and 'error' not in dynamic_rag:
                            self._update_progress("Dynamic RAG & AI Intelligence", "Analyzing Deep Security patterns...", 72)
                            
                            print(f"✅ Dynamic RAG Analysis (DS Logs): {dynamic_rag.get('analysis_metadata', {}).get('knowledge_sources_used', 0)} sources")
                            
                            # Add dynamic insights to recommendations
                            if dynamic_rag.get('ai_response'):
                                ai_summary = dynamic_rag['ai_response'][:200] + "..." if len(dynamic_rag['ai_response']) > 200 else dynamic_rag['ai_response']
                                results['recommendations'].append(f'🧠 <strong>AI Analysis</strong>: {ai_summary}')
                            
                            self._update_progress("Dynamic RAG & AI Intelligence", "Dynamic RAG analysis completed ✓", 75)
                                
                    except Exception as dynamic_error:
                        print(f"⚠️ Dynamic RAG failed for DS Logs: {dynamic_error}")
                        print("ℹ️ No other RAG systems available")
                    
                except Exception as e:
                    print(f"⚠️ Dynamic RAG analysis failed: {e}")
                    results['dynamic_rag_analysis'] = {'error': str(e)}
            else:
                results['dynamic_rag_analysis'] = {'status': 'Dynamic RAG features not available'}
            
            # Final completion progress - Stage 4: Report Generation & Finalization
            self._update_progress("Report Generation & Finalization", "Compiling ML and AI analysis results...", 80)
            
        except Exception as e:
            raise SecurityError(f"Error analyzing log file: {str(e)}")
        
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
            'connection_health': {
                'overall_status': 'unknown',
                'connection_attempts': 0,
                'successful_connections': 0,
                'connected_regions': set(),
                'dns_issues': [],
                'firewall_issues': [],
                'proxy_issues': [],
                'ssl_certificate_issues': [],
                'recommendations': []
            },
            'ml_insights': None,
            'dynamic_rag_analysis': None,
            'file_analysis': {}
        }
        
        all_log_entries = []
        
        try:
            for i, file_path in enumerate(file_paths, 1):
                print(f'📊 Analyzing file {i}/{len(file_paths)}: {file_path}')
                
                # Analyze individual file
                file_results = self.analyze_log_file(file_path)
                file_name = file_path.split('\\')[-1] if '\\' in file_path else file_path.split('/')[-1]
                
                # Store individual file results
                consolidated_results['file_analysis'][file_name] = {
                    'summary': file_results['summary'],
                    'critical_count': file_results['summary']['critical_count'],
                    'error_count': file_results['summary']['error_count'],
                    'warning_count': file_results['summary']['warning_count']
                }
                
                consolidated_results['summary']['files_analyzed'].append(file_name)
                
                # Consolidate summaries
                consolidated_results['summary']['total_lines'] += file_results['summary']['total_lines']
                consolidated_results['summary']['parsed_lines'] += file_results['summary']['parsed_lines']
                consolidated_results['summary']['error_count'] += file_results['summary']['error_count']
                consolidated_results['summary']['warning_count'] += file_results['summary']['warning_count']
                consolidated_results['summary']['critical_count'] += file_results['summary']['critical_count']
                
                # Update timespan
                if file_results['summary']['timespan']['start']:
                    if not consolidated_results['summary']['timespan']['start'] or \
                       file_results['summary']['timespan']['start'] < consolidated_results['summary']['timespan']['start']:
                        consolidated_results['summary']['timespan']['start'] = file_results['summary']['timespan']['start']
                
                if file_results['summary']['timespan']['end']:
                    if not consolidated_results['summary']['timespan']['end'] or \
                       file_results['summary']['timespan']['end'] > consolidated_results['summary']['timespan']['end']:
                        consolidated_results['summary']['timespan']['end'] = file_results['summary']['timespan']['end']
                
                # Consolidate issues
                consolidated_results['errors'].extend(file_results['errors'])
                consolidated_results['warnings'].extend(file_results['warnings'])
                consolidated_results['critical_issues'].extend(file_results['critical_issues'])
                consolidated_results['known_issues'].extend(file_results['known_issues'])
                
                # Consolidate component analysis
                for component, stats in file_results['component_analysis'].items():
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
                file_connection = file_results.get('connection_health', {})
                if file_connection:
                    consolidated_results['connection_health']['connection_attempts'] += file_connection.get('connection_attempts', 0)
                    consolidated_results['connection_health']['successful_connections'] += file_connection.get('successful_connections', 0)
                    consolidated_results['connection_health']['connected_regions'].update(file_connection.get('connected_regions', []))
                    consolidated_results['connection_health']['dns_issues'].extend(file_connection.get('dns_issues', []))
                    consolidated_results['connection_health']['firewall_issues'].extend(file_connection.get('firewall_issues', []))
                    consolidated_results['connection_health']['proxy_issues'].extend(file_connection.get('proxy_issues', []))
                    consolidated_results['connection_health']['ssl_certificate_issues'].extend(file_connection.get('ssl_certificate_issues', []))
                
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
            
            # Convert connected_regions set to list
            consolidated_results['connection_health']['connected_regions'] = list(consolidated_results['connection_health']['connected_regions'])
            
            # Calculate overall connection health status
            total_attempts = consolidated_results['connection_health']['connection_attempts']
            successful_connections = consolidated_results['connection_health']['successful_connections']
            
            if total_attempts > 0:
                success_rate = successful_connections / total_attempts
                if success_rate >= 0.8:
                    consolidated_results['connection_health']['overall_status'] = 'healthy'
                elif success_rate >= 0.6:
                    consolidated_results['connection_health']['overall_status'] = 'mostly_healthy'
                elif success_rate >= 0.3:
                    consolidated_results['connection_health']['overall_status'] = 'unstable'
                else:
                    consolidated_results['connection_health']['overall_status'] = 'unhealthy'
            
            # Generate consolidated recommendations
            consolidated_results['recommendations'] = self.generate_recommendations(consolidated_results)
            
            # Add multi-file specific recommendations
            if len(file_paths) > 1:
                consolidated_results["recommendations"].insert(0, f'<i class="fa-solid fa-folder me-2"></i>Analyzed {len(file_paths)} log files covering {consolidated_results["summary"]["total_lines"]:,} total log entries')
                
                if consolidated_results['summary']['critical_count'] > 0:
                    consolidated_results["recommendations"].append(f'<i class="fa-solid fa-circle-exclamation me-2"></i>{consolidated_results["summary"]["critical_count"]} critical issues found across all files - prioritize by timestamp')
            
            # Consolidated ML Analysis (if available)
            if ML_AVAILABLE and len(all_log_entries) > 0:
                try:
                    # Combine log content from all files for ML analysis
                    combined_content = "\n".join([f"{entry.get('timestamp', '')} {entry.get('message', '')}" for entry in all_log_entries[:10000]])
                    ml_insights = enhance_analysis_with_ml(combined_content, 'ds_logs')
                    consolidated_results['ml_insights'] = ml_insights
                    
                    ml_recommendations = ml_insights.get('recommendations', [])
                    consolidated_results['recommendations'].extend(ml_recommendations)
                    
                    print(f"✅ Consolidated ML Analysis completed: {len(all_log_entries)} entries from {len(file_paths)} files")
                    
                except Exception as e:
                    print(f'⚠️ Consolidated ML analysis failed: {e}')
                    consolidated_results['ml_insights'] = {'error': str(e)}
            
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
                            print(f"⚠️ Could not read {file_path} for RAG: {e}")
                    
                    consolidated_results = apply_dynamic_rag_to_analysis(consolidated_results, combined_log_content)
                    
                    dynamic_rag = consolidated_results.get('dynamic_rag_analysis', {})
                    if dynamic_rag and 'error' not in dynamic_rag:
                        print(f"✅ Consolidated Dynamic RAG Analysis: {dynamic_rag.get('analysis_metadata', {}).get('knowledge_sources_used', 0)} sources")
                        
                        # Add dynamic insights to recommendations
                        if dynamic_rag.get('ai_response'):
                            ai_summary = dynamic_rag['ai_response'][:200] + "..." if len(dynamic_rag['ai_response']) > 200 else dynamic_rag['ai_response']
                            consolidated_results['recommendations'].append(f'🧠 <strong>Multi-file AI Analysis</strong>: {ai_summary}')
                    
                except Exception as e:
                    print(f"⚠️ Consolidated Dynamic RAG analysis failed: {e}")
                    consolidated_results['dynamic_rag_analysis'] = {'error': str(e)}
            
            print(f"✅ Multiple file analysis completed: {len(file_paths)} files, {consolidated_results['summary']['total_lines']:,} total lines")
            
        except Exception as e:
            raise SecurityError(f"Error analyzing multiple log files: {str(e)}")
        
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


class AMSPAnalyzer:
    """AMSP Anti-Malware Log Analyzer with Dynamic RAG integration and progress tracking"""
    
    def __init__(self, session_manager=None, session_id=None):
        """Initialize with optional progress tracking"""
        self.session_manager = session_manager
        self.session_id = session_id
        
        # Initialize error patterns
        self._initialize_error_patterns()
    
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

    def _initialize_error_patterns(self):
        """Initialize error pattern configurations"""
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
                r'policy.*failed'
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
                r'limited.*functionality'
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
        """Categorize AMSP log entry severity"""
        if not log_entry.get('parsed'):
            return 'unknown'
        
        message = log_entry['message'].lower()
        level = log_entry['level'].lower()
        
        if level in ['critical', 'fatal', 'error']:
            return 'critical'
        elif level in ['warning', 'warn']:
            return 'warning'
        elif level in ['info', 'information', 'debug', 'trace']:
            return 'info'
        
        for pattern in self.error_patterns['critical']:
            if re.search(pattern, message, re.IGNORECASE):
                return 'critical'
        
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
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                for line_num, line in enumerate(f, 1):
                    if line_num > 10000:
                        break
                    
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
            
            results['recommendations'] = self.generate_amsp_recommendations(results)
            
            # Dynamic RAG Integration for AMSP Analysis
            if DYNAMIC_RAG_AVAILABLE:
                try:
                    # Try Dynamic RAG first for intelligent prompt generation
                    try:
                        # Read log content for dynamic analysis
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            log_content = f.read()
                        
                        from dynamic_rag_system import apply_dynamic_rag_to_analysis
                        results = apply_dynamic_rag_to_analysis(results, log_content)
                        
                        dynamic_rag = results.get('dynamic_rag_analysis', {})
                        if dynamic_rag and 'error' not in dynamic_rag:
                            print(f"✅ Dynamic RAG Analysis (AMSP): {dynamic_rag.get('analysis_metadata', {}).get('knowledge_sources_used', 0)} sources")
                            
                            # Add dynamic insights to recommendations
                            if dynamic_rag.get('ai_response'):
                                ai_summary = dynamic_rag['ai_response'][:200] + "..." if len(dynamic_rag['ai_response']) > 200 else dynamic_rag['ai_response']
                                results['recommendations'].append(f'🧠 <strong>AI AMSP Analysis</strong>: {ai_summary}')
                                
                    except Exception as dynamic_error:
                        print(f"⚠️ Dynamic RAG failed for AMSP: {dynamic_error}")
                            
                except Exception as e:
                    print(f"⚠️ RAG integration failed for AMSP: {e}")
            
        except Exception as e:
            raise SecurityError(f"Error analyzing AMSP log file: {str(e)}")
        
        return results

    def generate_amsp_recommendations(self, analysis: Dict[str, Any]) -> List[str]:
        """Generate AMSP-specific recommendations"""
        recommendations = []
        
        if analysis['summary']['critical_count'] > 0:
            recommendations.append('<i class="fa-solid fa-circle-exclamation me-2"></i>Critical AMSP issues detected - immediate attention required')
        
        if analysis['installation_summary']['failures'] > 0:
            recommendations.append('<i class="fa-solid fa-triangle-exclamation me-2"></i>Installation failures detected - review AMSP setup')
        
        if analysis['summary']['error_count'] > 5:
            recommendations.append('<i class="fa-solid fa-wrench me-2"></i>Multiple AMSP errors detected - check service configuration')
        
        for operation, stats in analysis['operation_analysis'].items():
            if stats['errors'] > 2:
                recommendations.append(f'<i class="fa-solid fa-search me-2"></i>{operation}: High error count - investigate operation issues')
        
        if not recommendations:
            recommendations.append('<i class="fa-solid fa-check-circle text-success"></i> No critical AMSP issues detected - anti-malware appears to be functioning normally')
        
        return recommendations


class ConflictAnalyzer:
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
                import httpx
                custom_http_client = httpx.Client(timeout=30.0, follow_redirects=True)
                client = OpenAI(
                    api_key=config.OPENAI_API_KEY,
                    base_url=config.OPENAI_BASE_URL,
                    http_client=custom_http_client
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
        lines = response_text.split('\n')
        current_conflict = {}
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            if any(keyword in line.lower() for keyword in ['conflict', 'detected', 'found', 'identified']):
                if current_conflict:
                    conflicts.append(current_conflict)
                current_conflict = {'name': line, 'description': ''}
            elif line.startswith(('-', '*', '•')):
                conflict_name = line.lstrip('- *•').strip()
                conflicts.append({
                    'name': conflict_name,
                    'description': 'Potential antivirus conflict detected'
                })
        
        return conflicts

    def format_conflict_results(self, analysis_text: str, conflicts: List[Dict], status: str) -> str:
        """Format conflict analysis results"""
        
        if status == "error":
            status_color = "#dc3545"
            status_text = "ANALYSIS ERROR"
            status_icon = "❌"
        elif conflicts or "conflict" in analysis_text.lower():
            status_color = "#fd7e14"
            status_text = "CONFLICTS DETECTED"
            status_icon = '<i class="fa-solid fa-triangle-exclamation text-warning"></i>'
        elif status == "no_processes":
            status_color = "#6c757d"
            status_text = "NO PROCESSES TO ANALYZE"
            status_icon = "ℹ️"
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


class ResourceAnalyzer:
    """Resource Analyzer for exclusion recommendations with Dynamic RAG integration and progress tracking"""
    
    def __init__(self, session_manager=None, session_id=None):
        """Initialize with optional progress tracking"""
        self.session_manager = session_manager
        self.session_id = session_id
    
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
        
        analysis_result = {
            'analysis_text': '',
            'candidates': [],
            'status': 'unknown',
            'ml_insights': None,
            'dynamic_rag_analysis': None,
            'security_impact': {},
            'performance_metrics': {},
            'recommendations': []
        }
        
        try:
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
            
            # Performance metrics calculation
            total_scan_count = sum(int(str(c.get('count', '0')).replace(',', '')) for c in candidates)
            analysis_result['performance_metrics'] = {
                'total_scan_count': total_scan_count,
                'high_impact_processes': len([c for c in candidates if int(str(c.get('count', '0')).replace(',', '')) > 1000]),
                'process_types': list(set(c['process_type'] for c in candidates)),
                'optimization_potential': 'High' if total_scan_count > 5000 else 'Medium' if total_scan_count > 2000 else 'Low'
            }

            # ML-Enhanced Analysis
            if ML_AVAILABLE:
                try:
                    ml_data = self._prepare_ml_data(process_list, busy_processes, candidates)
                    ml_insights = self._perform_ml_analysis(ml_data)
                    analysis_result['ml_insights'] = ml_insights
                    print(f"✅ ML Resource Analysis completed: {len(candidates)} candidates analyzed")
                except Exception as e:
                    print(f"⚠️ ML resource analysis failed: {e}")
                    analysis_result['ml_insights'] = {'error': str(e)}

            # Dynamic RAG-Enhanced Analysis  
            if DYNAMIC_RAG_AVAILABLE:
                try:
                    # Read log content for dynamic analysis
                    process_content = '\n'.join([f"{proc['name']}: {proc.get('description', '')}" for proc in candidates[:20]])
                    
                    from dynamic_rag_system import apply_dynamic_rag_to_analysis
                    analysis_result = apply_dynamic_rag_to_analysis(analysis_result, process_content)
                    
                    dynamic_rag = analysis_result.get('dynamic_rag_analysis', {})
                    if dynamic_rag and 'error' not in dynamic_rag:
                        print(f"✅ Dynamic RAG Resource Analysis: {dynamic_rag.get('analysis_metadata', {}).get('knowledge_sources_used', 0)} sources")
                        
                        # Add dynamic insights to recommendations
                        if dynamic_rag.get('ai_response'):
                            ai_summary = dynamic_rag['ai_response'][:200] + "..." if len(dynamic_rag['ai_response']) > 200 else dynamic_rag['ai_response']
                            analysis_result['recommendations'].append(f'🧠 <strong>AI Resource Analysis</strong>: {ai_summary}')
                    
                except Exception as e:
                    print(f"⚠️ Dynamic RAG resource analysis failed: {e}")
                    analysis_result['dynamic_rag_analysis'] = {'error': str(e)}

            # Enhanced AI Analysis with Deep Security context (following AV Conflict analyzer pattern)
            analysis_text = self._perform_ai_analysis(process_list, busy_processes, candidates, total_scan_count, analysis_result['performance_metrics'])
            analysis_result['analysis_text'] = analysis_text
            
            # Set status based on analysis
            if candidates:
                analysis_result['status'] = 'candidates_found'
            else:
                analysis_result['status'] = 'optimal'
                
            # Generate structured recommendations
            analysis_result['recommendations'] = self._generate_enhanced_recommendations(
                candidates, analysis_result['performance_metrics'], analysis_result.get('ml_insights'), analysis_result.get('dynamic_rag_analysis')
            )
            
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
            
            # Try enhanced RAG first
            try:
                # Legacy Enhanced RAG import removed - using Dynamic RAG only
                # from enhanced_rag_integration import EnhancedRAGIntegration
                
                # Legacy Enhanced RAG usage removed - using Dynamic RAG only
                # enhanced_rag = EnhancedRAGIntegration()
                enhanced_rag = None  # Disabled for Dynamic RAG consolidation
                if enhanced_rag.available:
                    # Create a mock log analysis for RAG processing
                    mock_analysis = {
                        'summary': {
                            'total_lines': len(candidates),
                            'error_count': len([c for c in candidates if c.get('resource_usage', 0) > 80]),
                            'warning_count': len([c for c in candidates if c.get('resource_usage', 0) > 60])
                        },
                        'ml_insights': {
                            'ds_agent_analysis': {
                                'component_health': {
                                    'amsp': {'health_score': performance_metrics.get('scan_efficiency', 85)},
                                    'resource_monitor': {'health_score': performance_metrics.get('resource_score', 75)}
                                }
                            }
                        }
                    }
                    
                    # Apply enhanced RAG
                    enhanced_result = enhanced_rag.enhance_analysis_with_smart_rag(mock_analysis)
                    rag_insights = enhanced_result.get('intelligent_rag_insights', {})
                    
                    if rag_insights and 'error' not in rag_insights:
                        knowledge_count = rag_insights.get('knowledge_sources_used', 0)
                        best_practices = []
                        
                        # Extract recommendations from knowledge
                        for doc in rag_insights.get('relevant_knowledge', [])[:3]:
                            title = doc.get('metadata', {}).get('title', 'Best Practice')
                            best_practices.append({
                                'title': title,
                                'description': doc.get('content', '')[:150] + '...',
                                'category': doc.get('metadata', {}).get('category', 'Performance')
                            })
                        
                        return {
                            'knowledge_sources_used': knowledge_count,
                            'patterns_matched': len(rag_insights.get('pattern_matches', [])),
                            'confidence_score': min(100, knowledge_count * 20 + 60),
                            'rag_version': '2.0_enhanced',
                            'best_practices': best_practices,
                            'intelligence_level': 'enhanced'
                        }
            
            except ImportError:
                print("📋 Enhanced RAG not available, using standard RAG")
            
            # Fallback to standard RAG
            # Legacy Standard RAG import removed - using Dynamic RAG only  
            # from rag_system import CybersecurityRAG
            
            # Legacy Standard RAG system removed - using Dynamic RAG only
            # rag_system = CybersecurityRAG()
            rag_system = None  # Disabled for Dynamic RAG consolidation
            
            # Query knowledge base for exclusion best practices
            queries = [
                "Deep Security anti-malware exclusion best practices",
                "performance optimization exclusion recommendations",
                f"exclusion strategies for {performance_metrics.get('process_types', ['application'])[0] if performance_metrics.get('process_types') else 'application'} processes"
            ]
            
            best_practices = []
            knowledge_sources = 0
            
            for query in queries:
                try:
                    rag_response = rag_system.query(query)
                    if rag_response and 'documents' in rag_response:
                        knowledge_sources += len(rag_response['documents'])
                        for doc in rag_response['documents'][:2]:  # Top 2 matches per query
                            best_practices.append({
                                'title': f"Best Practice: {query.split()[-2:]}",
                                'description': doc.get('content', '')[:200] + '...',
                                'category': 'Performance Optimization'
                            })
                except Exception:
                    continue  # Skip failed queries
            
            # Calculate confidence based on knowledge matches
            confidence_score = min(100, (knowledge_sources / len(queries)) * 30 + 70)
            
            return {
                'knowledge_sources_used': knowledge_sources,
                'patterns_matched': len(best_practices),
                'confidence_score': confidence_score,
                'rag_version': '2.0',
                'best_practices': best_practices[:5]  # Limit to top 5
            }
            
        except Exception as e:
            return {'error': f'RAG analysis failed: {str(e)}'}

    def _generate_enhanced_recommendations(self, candidates: List[Dict], performance_metrics: Dict, ml_insights: Dict, dynamic_rag_insights: Dict) -> List[str]:
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
        if dynamic_rag_insights and dynamic_rag_insights.get('confidence_score', 0) > 80:
            recommendations.append('<i class="fas fa-database"></i> Knowledge Base: High-confidence best practices available for this configuration')
        
        # Implementation guidance
        top_candidates = sorted(candidates, key=lambda x: int(str(x.get('count', '0')).replace(',', '')), reverse=True)[:3]
        if top_candidates:
            recommendations.append(f'<i class="fas fa-star"></i> Priority exclusion candidates: {", ".join([c["name"] for c in top_candidates])}')
        
        return recommendations

    def _perform_ai_analysis(self, process_list: List[str], busy_processes: List[Dict], candidates: List[Dict], total_scan_count: int, performance_metrics: Dict) -> str:
        """Perform AI analysis with robust error handling (following AV Conflict analyzer pattern)"""
        try:
            print(f"🔍 ResourceAnalyzer AI Check - OPENAI_AVAILABLE: {OPENAI_AVAILABLE}")
            
            # Check if OpenAI is available
            if not OPENAI_AVAILABLE:
                print("❌ OpenAI not available - using fallback analysis")
                return self._generate_fallback_analysis(candidates, performance_metrics)
            
            from config import get_config
            config = get_config()
            
            print(f"🔍 API Key available: {bool(config.OPENAI_API_KEY)}")
            
            # Validate API configuration
            if not config.OPENAI_API_KEY:
                print("❌ OpenAI API key not configured - using fallback analysis")
                return self._generate_fallback_analysis(candidates, performance_metrics)
            
            try:
                print("🔄 Initializing OpenAI client for ResourceAnalyzer...")
                import httpx
                # Increase timeout for ResourceAnalyzer due to larger dataset processing
                custom_http_client = httpx.Client(timeout=120.0, follow_redirects=True)
                client = OpenAI(
                    api_key=config.OPENAI_API_KEY,
                    base_url=config.OPENAI_BASE_URL,
                    http_client=custom_http_client
                )
                print("✅ OpenAI client initialized successfully for ResourceAnalyzer (120s timeout)")
            except Exception as e:
                print(f"❌ Failed to initialize OpenAI client: {str(e)}")
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
                print(f"❌ AI analysis API call failed: {str(api_error)}")
                return f"AI analysis temporarily unavailable: {str(api_error)}\n\n{self._generate_fallback_analysis(candidates, performance_metrics)}"
                
        except Exception as e:
            print(f"❌ ResourceAnalyzer AI analysis exception: {str(e)}")
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
⚠️ **Performance Optimization Opportunities Detected**
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
