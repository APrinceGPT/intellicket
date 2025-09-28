# -*- coding: utf-8 -*-
"""
DSAgentOfflineAnalyzer - Deep Security Agent Offline Analyzer
Enhanced comprehensive analyzer for DS Agent connectivity and offline root cause analysis
Based on Deep Security 20.0 architecture and network communications analysis
"""

from .shared_imports import *
from .base.standardizer import AnalyzerOutputStandardizer

class DSAgentOfflineAnalyzer(AnalyzerOutputStandardizer):
    """
    Enhanced Deep Security Agent Offline Analyzer
    
    Comprehensive analysis of DS Agent offline scenarios including:
    - Network communication failures (heartbeat, connection, DNS)
    - Certificate and authentication issues  
    - Service and process failures
    - Smart Protection Network connectivity
    - Manager-Agent communication patterns
    - Platform-specific diagnostic indicators
    """
    
    def __init__(self, session_manager=None, session_id=None, rag_system=None, ml_analyzer=None):
        """Initialize the Enhanced DS Agent Offline Analyzer"""
        self.session_manager = session_manager
        self.session_id = session_id
        self.rag_system = rag_system
        self.ml_analyzer = ml_analyzer
        
        # Initialize comprehensive offline detection patterns
        self._initialize_offline_patterns()
        self._initialize_event_ids()
        self._initialize_diagnostic_commands()
        self._initialize_communication_flows()
        self._initialize_platform_patterns()

    
    def _initialize_event_ids(self):
        """Initialize Deep Security Event IDs for offline analysis (from JSON research)"""
        self.critical_offline_events = {
            730: {'description': 'Offline - Manager cannot communicate with Computer', 'severity': 'critical'},
            731: {'description': 'Back Online - Communication restored', 'severity': 'info'},
            120: {'description': 'Heartbeat Server Failed - Manager heartbeat service issue', 'severity': 'critical'},
            742: {'description': 'Communications Problem - Network congestion or issues', 'severity': 'high'},
            743: {'description': 'Communications Problem Resolved - Communication restored', 'severity': 'info'},
            770: {'description': 'Agent/Appliance Heartbeat Rejected', 'severity': 'high'},
            771: {'description': 'Contact by Unrecognized Client', 'severity': 'high'}
        }
        
        self.authentication_certificate_events = {
            930: {'description': 'Certificate Accepted', 'severity': 'info'},
            931: {'description': 'Certificate Deleted', 'severity': 'warning'},
            734: {'description': 'Time Synchronization Issue - Clock drift affecting certificate validation', 'severity': 'high'}
        }
        
        self.service_driver_events = {
            1008: {'description': 'Kernel Unsupported', 'severity': 'critical'},
            1112: {'description': 'Kernel Unsupported (Driver cannot be installed)', 'severity': 'critical'},
            5000: {'description': 'Agent/Appliance Started', 'severity': 'info'},
            5003: {'description': 'Agent/Appliance Stopped', 'severity': 'high'},
            1000: {'description': 'Unable To Open Engine', 'severity': 'high'},
            1001: {'description': 'Engine Command Failed', 'severity': 'high'},
            5008: {'description': 'Filter Driver Connection Failed', 'severity': 'high'},
            5009: {'description': 'Filter Driver Connection Success', 'severity': 'info'}
        }
        
        self.communication_agent_events = {
            4011: {'description': 'Failure to Contact Manager', 'severity': 'critical'},
            4012: {'description': 'Heartbeat Failed', 'severity': 'critical'},
            4002: {'description': 'Command Session Initiated', 'severity': 'info'},
            4003: {'description': 'Configuration Session Initiated', 'severity': 'info'},
            4004: {'description': 'Command Received', 'severity': 'info'},
            6012: {'description': 'Insufficient Disk Space', 'severity': 'high'},
            724:  {'description': 'Insufficient Disk Space - Event logging affected', 'severity': 'high'}
        }
        
        self.configuration_policy_events = {
            2085: {'description': 'Policy Corruption', 'severity': 'high'},
            2090: {'description': 'Policy Corruption', 'severity': 'high'},
            2091: {'description': 'Policy Corruption', 'severity': 'high'},
            762:  {'description': 'Incompatible Agent-Manager Versions', 'severity': 'high'},
            763:  {'description': 'Incompatible Agent-Manager Versions', 'severity': 'high'},
            764:  {'description': 'Incompatible Agent-Manager Versions', 'severity': 'high'}
        }
    
    def _initialize_diagnostic_commands(self):
        """Initialize diagnostic commands for different platforms"""
        self.diagnostic_commands = {
            'windows': {
                'connectivity_test': 'Test-NetConnection -ComputerName <manager_host> -Port 4119',
                'dns_resolution': 'nslookup <manager_hostname>',
                'certificate_check': 'certlm.msc',
                'service_status': 'Get-Service ds_agent',
                'service_restart': 'Restart-Service ds_agent',
                'firewall_check': 'Get-NetFirewallRule | Where-Object {$_.DisplayName -like "*Deep Security*"}',
                'port_check': 'netstat -an | findstr :4119'
            },
            'linux': {
                'connectivity_test': 'telnet <manager_host> 4119',
                'dns_resolution': 'nslookup <manager_hostname>',
                'service_status': 'systemctl status ds_agent',
                'service_restart': 'systemctl restart ds_agent',
                'service_logs': 'journalctl -u ds_agent',
                'network_test': 'ping <manager_host>',
                'port_check': 'ss -tlnp | grep :4119'
            },
            'general': {
                'manager_ports': [4119, 4120, 4118],
                'spn_ports': [443],
                'relay_ports': [4122],
                'required_domains': [
                    '*.trendmicro.com',
                    'deepsec20-*.gfrbridge.trendmicro.com',
                    'ds20*.icrc.trendmicro.com',
                    'ds20-*-*.trx.trendmicro.com'
                ]
            }
        }
    
    def _initialize_communication_flows(self):
        """Initialize communication flow analysis patterns"""
        self.communication_flows = {
            'agent_to_manager': {
                'primary_port': 4119,
                'protocol': 'HTTPS',
                'purpose': 'Primary communication and API calls',
                'data_types': ['events', 'status_reports', 'security_logs']
            },
            'manager_to_agent': {
                'primary_port': 4120,
                'protocol': 'HTTPS', 
                'purpose': 'Heartbeat and policy distribution',
                'data_types': ['policies', 'commands', 'configuration_changes']
            },
            'agent_heartbeat': {
                'primary_port': 4120,
                'frequency': 'configurable_default_10_minutes',
                'protocol': 'HTTPS',
                'purpose': 'Status reporting and keep alive'
            },
            'smart_protection_network': {
                'primary_port': 443,
                'protocol': 'HTTPS',
                'purpose': 'Cloud intelligence services',
                'endpoints': [
                    'deepsec20-*.gfrbridge.trendmicro.com',
                    'ds20*.icrc.trendmicro.com',
                    'ds20-*-*.trx.trendmicro.com'
                ]
            }
        }
    
    def _initialize_platform_patterns(self):
        """Initialize platform-specific patterns and requirements"""
        self.platform_patterns = {
            'windows': {
                'service_name': 'ds_agent',
                'process_name': 'ds_agent.exe',
                'log_locations': ['%ProgramFiles%\\Trend Micro\\Deep Security Agent\\dsa_core\\logs\\'],
                'key_files': ['ds_agent.log', 'ds_agent-err.log'],
                'drivers': ['tmlwf'],
                'registry_keys': [
                    'HKLM\\SOFTWARE\\TrendMicro\\Deep Security Agent',
                    'HKLM\\SYSTEM\\CurrentControlSet\\Services\\ds_agent'
                ]
            },
            'linux': {
                'service_name': 'ds_agent',
                'process_name': 'ds_agent',
                'log_locations': ['/opt/ds_agent/logs/', '/var/log/'],
                'key_files': ['ds_agent.log', 'ds_agent-err.log'],
                'drivers': ['tm_netfilter'],
                'system_logs': ['/var/log/messages', '/var/log/syslog'],
                'systemd_logs': 'journalctl -u ds_agent'
            }
        }

    def _initialize_offline_patterns(self):
        """Initialize comprehensive patterns for detecting DS Agent offline issues based on Deep Security 20.0 analysis"""
        
        # Primary Network Communication Patterns (Based on JSON analysis)
        self.network_communication_patterns = {
            'heartbeat_failures': {
                'patterns': [
                    r'heartbeat.*failed|heartbeat.*timeout|heartbeat.*error',
                    r'failed.*send.*heartbeat|heartbeat.*not.*sent',
                    r'no.*heartbeat.*response|heartbeat.*response.*timeout', 
                    r'manager.*heartbeat.*failed|heartbeat.*communication.*failed',
                    r'heartbeat.*rejected|heartbeat.*server.*failed',
                    r'agent.*heartbeat.*rejected|contact.*by.*unrecognized.*client'
                ],
                'severity': 'critical',
                'category': 'heartbeat_communication',
                'ports_affected': [4120],
                'communication_direction': 'agent_to_manager'
            },
            'connection_failures': {
                'patterns': [
                    r'connection.*failed|failed.*connect.*manager',
                    r'unable.*connect.*manager|manager.*connection.*failed',
                    r'connection.*timeout|connection.*refused|connection.*reset',
                    r'connection.*aborted|connection.*dropped',
                    r'ssl.*handshake.*failed|tls.*connection.*failed',
                    r'certificate.*verification.*failed|certificate.*error',
                    r'tcp.*connection.*failed|socket.*connection.*failed'
                ],
                'severity': 'critical',
                'category': 'network_connectivity', 
                'ports_affected': [4119, 4120, 4118],
                'communication_direction': 'bidirectional'
            },
            'dns_resolution_issues': {
                'patterns': [
                    r'dns.*resolution.*failed|dns.*lookup.*failed',
                    r'host.*not.*found|hostname.*resolution.*failed',
                    r'gethostbyname.*failed|dns.*timeout',
                    r'name.*resolution.*failed|dns.*query.*failed',
                    r'cannot.*resolve.*manager.*hostname',
                    r'dns.*server.*unreachable'
                ],
                'severity': 'high',
                'category': 'dns_resolution',
                'ports_affected': [53],
                'communication_direction': 'outbound'
            },
            'authentication_failures': {
                'patterns': [
                    r'authentication.*failed|auth.*failed|login.*failed',
                    r'invalid.*credentials|access.*denied',
                    r'token.*expired|token.*invalid|authorization.*failed',
                    r'certificate.*authentication.*failed|certificate.*rejected',
                    r'pki.*certificate.*expired|certificate.*chain.*validation',
                    r'mutual.*authentication.*failed|client.*certificate.*error'
                ],
                'severity': 'high',
                'category': 'authentication',
                'ports_affected': [4119, 4120],
                'communication_direction': 'bidirectional'
            },
            'proxy_configuration_issues': {
                'patterns': [
                    r'proxy.*authentication.*failed|proxy.*error|http.*407',
                    r'proxy.*connection.*failed|proxy.*timeout',
                    r'proxy.*configuration.*error|proxy.*server.*unreachable',
                    r'socks.*proxy.*failed|proxy.*denied',
                    r'proxy.*authentication.*required'
                ],
                'severity': 'high',
                'category': 'proxy_configuration',
                'ports_affected': [8080, 3128, 1080],
                'communication_direction': 'outbound'
            },
            'firewall_blocking': {
                'patterns': [
                    r'connection.*blocked.*by.*firewall|firewall.*blocking',
                    r'port.*blocked|port.*filtered',
                    r'icmp.*unreachable|host.*unreachable',
                    r'network.*unreachable|route.*not.*found',
                    r'connection.*refused.*immediately'
                ],
                'severity': 'high', 
                'category': 'firewall_blocking',
                'ports_affected': [4119, 4120, 4118, 443],
                'communication_direction': 'outbound'
            }
        }
        
        # Service and Process Patterns (Enhanced)
        self.service_patterns = {
            'service_startup_failures': {
                'patterns': [
                    r'service.*failed.*start|failed.*start.*service',
                    r'service.*startup.*error|service.*initialization.*failed',
                    r'ds_agent.*service.*failed|deepsecurity.*service.*failed',
                    r'service.*dependency.*failed|dependent.*service.*failed',
                    r'service.*timeout.*starting|service.*start.*timeout'
                ],
                'severity': 'critical',
                'category': 'service_lifecycle',
                'impact': 'agent_offline_until_service_restart'
            },
            'service_crashes': {
                'patterns': [
                    r'service.*crashed|service.*terminated.*unexpectedly',
                    r'application.*error|access.*violation|memory.*violation',
                    r'exception.*in.*service|unhandled.*exception',
                    r'service.*stopped.*unexpectedly|fatal.*error',
                    r'segmentation.*fault|core.*dump'
                ],
                'severity': 'critical',
                'category': 'service_stability',
                'impact': 'immediate_offline_status'
            },
            'driver_failures': {
                'patterns': [
                    r'driver.*failed.*load|driver.*initialization.*failed',
                    r'kernel.*module.*failed|tmlwf.*driver.*failed',
                    r'filter.*driver.*connection.*failed|driver.*not.*responding',
                    r'tm_netfilter.*failed|driver.*signature.*validation.*failed',
                    r'kernel.*unsupported|driver.*cannot.*be.*installed'
                ],
                'severity': 'critical',
                'category': 'platform_drivers',
                'impact': 'protection_modules_disabled'
            },
            'amsp_platform_issues': {
                'patterns': [
                    r'failed.*install.*upgrade.*amsp|amsp.*initialization.*failed',
                    r'trend.*micro.*solution.*platform.*failed',
                    r'amsp.*service.*crashed|amsp.*not.*responding',
                    r'amenableselfprotection.*failed|amsp.*func.*not.*support'
                ],
                'severity': 'high',
                'category': 'amsp_platform',
                'impact': 'anti_malware_functionality_affected'
            }
        }
        
        # Smart Protection Network Patterns (Based on Cloud Endpoints)
        self.smart_protection_patterns = {
            'file_reputation_failures': {
                'patterns': [
                    r'deepsec20.*gfrbridge.*trendmicro.*com.*failed',
                    r'file.*reputation.*service.*unreachable',
                    r'gfrbridge.*connection.*failed|smart.*protection.*network.*failed'
                ],
                'severity': 'medium',
                'category': 'spn_file_reputation',
                'endpoints': ['deepsec20-*.gfrbridge.trendmicro.com'],
                'ports_affected': [443]
            },
            'smart_scan_failures': {
                'patterns': [
                    r'ds20.*icrc.*trendmicro.*com.*failed',
                    r'smart.*scan.*service.*unreachable',
                    r'icrc.*connection.*failed|cloud.*scanning.*failed'
                ],
                'severity': 'medium',
                'category': 'spn_smart_scan',
                'endpoints': ['ds20*.icrc.trendmicro.com'],
                'ports_affected': [443]
            },
            'predictive_ml_failures': {
                'patterns': [
                    r'ds20.*trx.*trendmicro.*com.*failed',
                    r'predictive.*ml.*service.*unreachable',
                    r'machine.*learning.*analytics.*failed'
                ],
                'severity': 'medium',
                'category': 'spn_predictive_ml',
                'endpoints': ['ds20-*-*.trx.trendmicro.com'],
                'ports_affected': [443]
            }
        }
    
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
                print(f"⚠️ DS Agent Offline Progress update failed: {e}")
        else:
            # Fallback to console logging
            print(f"📊 DS Agent Offline {stage}: {message}")

    def parse_ds_agent_log_entry(self, line: str) -> Dict[str, Any]:
        """
        Enhanced DS Agent log entry parser supporting multiple formats found in real logs
        
        Supported formats:
        1. 2025-07-26 14:34:47.505346 [+0100]: [Cmd/5] | Received command GetEvents | dsa/ConnectionHandler.lua:1577:LogDsmCommand | 480C:27DC:dsa.Scheduler_0006
        2. 2022-03-17 10:50:42.000000 [+0100]: [Error/1] | Failed to install or upgrade AMSP | Amsp\AmInterface.cpp:260:dsam_init | 528:2FA0:dsp.am.service
        3. 2025-07-26 14:37:01.000000 [+0100]: [Warning/2] | Get device control adapter metrics failed AMSP_FUNC_NOT_SUPPORT | Amsp\AMSP_DSDCMetricsHelper.cpp:102:DSDCMetricsHelper::GetMetrics | 480C:27DC:dsa.Scheduler_0006
        """
        
        # Primary DS Agent log format with timezone
        primary_pattern = r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d+) \[([+-]\d{4})\]: \[([^/]+)/(\d+)\] \| ([^|]+) \| ([^|]*) \| (.+)'
        match = re.match(primary_pattern, line.strip())
        
        if match:
            timestamp_str, timezone, log_level, priority, message, location, thread_info = match.groups()
            return {
                'timestamp': timestamp_str,
                'timezone': timezone,
                'log_level': log_level,
                'priority': int(priority),
                'message': message.strip(),
                'location': location.strip() if location else None,
                'thread_info': thread_info.strip(),
                'raw_line': line,
                'parsed': True,
                'format': 'ds_agent_primary'
            }
        
        # Alternative format without microseconds
        alt_pattern = r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) \[([+-]\d{4})\]: \[([^/]+)/(\d+)\] \| ([^|]+) \| ([^|]*) \| (.+)'
        match = re.match(alt_pattern, line.strip())
        
        if match:
            timestamp_str, timezone, log_level, priority, message, location, thread_info = match.groups()
            return {
                'timestamp': timestamp_str,
                'timezone': timezone,
                'log_level': log_level,
                'priority': int(priority),
                'message': message.strip(),
                'location': location.strip() if location else None,
                'thread_info': thread_info.strip(),
                'raw_line': line,
                'parsed': True,
                'format': 'ds_agent_alt'
            }
        
        # Simple format for basic entries
        simple_pattern = r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}[.\d]*) \[([+-]\d{4})\]: (.+)'
        match = re.match(simple_pattern, line.strip())
        
        if match:
            timestamp_str, timezone, message = match.groups()
            
            # Extract log level from message if present
            level_match = re.search(r'\[([^/]+)/(\d+)\]', message)
            log_level = level_match.group(1) if level_match else 'Unknown'
            priority = int(level_match.group(2)) if level_match else 5
            
            return {
                'timestamp': timestamp_str,
                'timezone': timezone,
                'log_level': log_level,
                'priority': priority,
                'message': message.strip(),
                'location': None,
                'thread_info': None,
                'raw_line': line,
                'parsed': True,
                'format': 'ds_agent_simple'
            }
        
        # Windows Event Log style format
        windows_pattern = r'(\d{1,2}/\d{1,2}/\d{4} \d{1,2}:\d{2}:\d{2} [AP]M) (.+)'
        match = re.match(windows_pattern, line.strip())
        
        if match:
            timestamp_str, message = match.groups()
            return {
                'timestamp': timestamp_str,
                'timezone': None,
                'log_level': 'Info',
                'priority': 3,
                'message': message.strip(),
                'location': None,
                'thread_info': None,
                'raw_line': line,
                'parsed': True,
                'format': 'windows_event'
            }
        
        # Fallback for unparsed lines
        return {
            'raw_line': line,
            'parsed': False,
            'message': line.strip(),
            'timestamp': None,
            'log_level': 'Unknown',
            'priority': 5,
            'format': 'unknown'
        }

    def detect_offline_causes(self, log_entries: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Enhanced detection of DS Agent offline root causes with comprehensive analysis
        """
        offline_analysis = {
            'network_issues': [],
            'service_issues': [],
            'authentication_issues': [],
            'spn_issues': [],
            'configuration_issues': [],
            'resource_issues': [],
            'event_correlation': [],
            'severity_summary': {
                'critical': 0,
                'high': 0,
                'medium': 0,
                'low': 0
            },
            'root_cause_analysis': []
        }
        
        # Event ID tracking for correlation
        event_tracking = {}
        timeline_events = []
        
        for entry in log_entries:
            if not entry.get('parsed'):
                continue
            
            message = entry.get('message', '').lower()
            timestamp = entry.get('timestamp', '')
            log_level = entry.get('log_level', 'Unknown')
            priority = entry.get('priority', 5)
            
            # Add to timeline for correlation analysis
            timeline_events.append({
                'timestamp': timestamp,
                'message': message,
                'log_level': log_level,
                'priority': priority,
                'entry': entry
            })
            
            # Check network communication patterns
            for pattern_name, pattern_info in self.network_communication_patterns.items():
                for pattern in pattern_info['patterns']:
                    if re.search(pattern, message, re.IGNORECASE):
                        issue = {
                            'type': pattern_name,
                            'category': pattern_info['category'],
                            'severity': pattern_info['severity'],
                            'message': entry.get('message', ''),
                            'timestamp': timestamp,
                            'log_level': log_level,
                            'ports_affected': pattern_info['ports_affected'],
                            'communication_direction': pattern_info['communication_direction'],
                            'pattern_matched': pattern,
                            'raw_line': entry.get('raw_line', '')
                        }
                        
                        # Categorize the issue
                        if pattern_info['category'] in ['heartbeat_communication', 'network_connectivity']:
                            offline_analysis['network_issues'].append(issue)
                        elif pattern_info['category'] == 'authentication':
                            offline_analysis['authentication_issues'].append(issue)
                        elif pattern_info['category'] in ['dns_resolution', 'proxy_configuration', 'firewall_blocking']:
                            offline_analysis['configuration_issues'].append(issue)
                        
                        # Update severity counts
                        if pattern_info['severity'] in offline_analysis['severity_summary']:
                            offline_analysis['severity_summary'][pattern_info['severity']] += 1
                        break
            
            # Check service patterns
            for pattern_name, pattern_info in self.service_patterns.items():
                for pattern in pattern_info['patterns']:
                    if re.search(pattern, message, re.IGNORECASE):
                        issue = {
                            'type': pattern_name,
                            'category': pattern_info['category'],
                            'severity': pattern_info['severity'],
                            'message': entry.get('message', ''),
                            'timestamp': timestamp,
                            'log_level': log_level,
                            'impact': pattern_info['impact'],
                            'pattern_matched': pattern,
                            'raw_line': entry.get('raw_line', '')
                        }
                        offline_analysis['service_issues'].append(issue)
                        
                        # Update severity counts
                        if pattern_info['severity'] in offline_analysis['severity_summary']:
                            offline_analysis['severity_summary'][pattern_info['severity']] += 1
                        break
            
            # Check Smart Protection Network patterns
            for pattern_name, pattern_info in self.smart_protection_patterns.items():
                for pattern in pattern_info['patterns']:
                    if re.search(pattern, message, re.IGNORECASE):
                        issue = {
                            'type': pattern_name,
                            'category': pattern_info['category'],
                            'severity': pattern_info['severity'],
                            'message': entry.get('message', ''),
                            'timestamp': timestamp,
                            'log_level': log_level,
                            'endpoints': pattern_info['endpoints'],
                            'ports_affected': pattern_info['ports_affected'],
                            'pattern_matched': pattern,
                            'raw_line': entry.get('raw_line', '')
                        }
                        offline_analysis['spn_issues'].append(issue)
                        
                        # Update severity counts
                        if pattern_info['severity'] in offline_analysis['severity_summary']:
                            offline_analysis['severity_summary'][pattern_info['severity']] += 1
                        break
            
            # Check for specific event IDs mentioned in the logs
            for event_id, event_info in {**self.critical_offline_events, **self.authentication_certificate_events, 
                                        **self.service_driver_events, **self.communication_agent_events, 
                                        **self.configuration_policy_events}.items():
                if str(event_id) in message:
                    event_tracking[event_id] = event_tracking.get(event_id, 0) + 1
                    offline_analysis['event_correlation'].append({
                        'event_id': event_id,
                        'description': event_info['description'],
                        'severity': event_info['severity'],
                        'timestamp': timestamp,
                        'message': entry.get('message', ''),
                        'count': event_tracking[event_id]
                    })
            
            # Resource constraint detection
            if any(keyword in message for keyword in ['disk space', 'memory', 'resource', 'insufficient']):
                offline_analysis['resource_issues'].append({
                    'type': 'resource_constraint',
                    'severity': 'high',
                    'message': entry.get('message', ''),
                    'timestamp': timestamp,
                    'log_level': log_level,
                    'raw_line': entry.get('raw_line', '')
                })
                offline_analysis['severity_summary']['high'] += 1
        
        # Perform comprehensive root cause analysis
        offline_analysis['root_cause_analysis'] = self._perform_enhanced_root_cause_analysis(offline_analysis)
        
        return offline_analysis
    
    def _analyze_event_timeline(self, timeline_events: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze event timeline for patterns and correlations"""
        timeline_analysis = {
            'event_sequence': [],
            'critical_periods': [],
            'recurring_patterns': [],
            'correlation_insights': []
        }
        
        # Sort events by timestamp
        sorted_events = sorted(timeline_events, key=lambda x: x.get('timestamp', ''))
        
        # Identify critical periods (clusters of high-priority events)
        critical_window = []
        for event in sorted_events:
            if event.get('priority', 5) <= 2:  # High priority events
                critical_window.append(event)
            else:
                if len(critical_window) >= 3:  # Found a critical period
                    timeline_analysis['critical_periods'].append({
                        'start_time': critical_window[0].get('timestamp'),
                        'end_time': critical_window[-1].get('timestamp'),
                        'event_count': len(critical_window),
                        'events': critical_window
                    })
                critical_window = []
        
        return timeline_analysis
    
    def _analyze_communication_flows(self, offline_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze communication flow patterns"""
        flow_analysis = {
            'failed_flows': [],
            'affected_ports': set(),
            'communication_health': {}
        }
        
        # Analyze network issues for communication flow impact
        for issue in offline_analysis.get('network_issues', []):
            flow_analysis['affected_ports'].update(issue.get('ports_affected', []))
            
            flow_type = issue.get('communication_direction', 'unknown')
            if flow_type not in flow_analysis['communication_health']:
                flow_analysis['communication_health'][flow_type] = {
                    'issues': 0,
                    'severity_distribution': {'critical': 0, 'high': 0, 'medium': 0, 'low': 0}
                }
            
            flow_analysis['communication_health'][flow_type]['issues'] += 1
            severity = issue.get('severity', 'low')
            if severity in flow_analysis['communication_health'][flow_type]['severity_distribution']:
                flow_analysis['communication_health'][flow_type]['severity_distribution'][severity] += 1
        
        # Convert set to list for JSON serialization
        flow_analysis['affected_ports'] = list(flow_analysis['affected_ports'])
        
        return flow_analysis
    
    def _perform_enhanced_root_cause_analysis(self, offline_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Perform comprehensive root cause analysis based on detected issues
        """
        root_causes = []
        
        # Critical issue priority: Network -> Authentication -> Service -> SPN -> Resources
        total_issues = (len(offline_analysis.get('network_issues', [])) +
                       len(offline_analysis.get('service_issues', [])) +
                       len(offline_analysis.get('authentication_issues', [])) +
                       len(offline_analysis.get('spn_issues', [])) +
                       len(offline_analysis.get('resource_issues', [])))
        
        if total_issues == 0:
            root_causes.append({
                'type': 'information',
                'severity': 'low',
                'title': 'No Critical Offline Indicators Found',
                'description': 'No specific offline patterns detected in the log entries analyzed.',
                'recommendations': [
                    'Verify DS Manager connectivity manually',
                    'Check system-level network configuration',
                    'Review Windows Event Logs for system-level issues',
                    'Validate DS Agent service is running'
                ]
            })
            return root_causes
        
        # Primary Network Communication Issues
        network_issues = offline_analysis.get('network_issues', [])
        if network_issues:
            critical_network = [i for i in network_issues if i.get('severity') == 'critical']
            high_network = [i for i in network_issues if i.get('severity') == 'high']
            
            if critical_network:
                heartbeat_failures = [i for i in critical_network if 'heartbeat' in i.get('category', '')]
                connection_failures = [i for i in critical_network if 'connectivity' in i.get('category', '')]
                
                if heartbeat_failures:
                    root_causes.append({
                        'type': 'critical_network',
                        'severity': 'critical',
                        'title': 'Critical Heartbeat Communication Failure',
                        'description': f'Detected {len(heartbeat_failures)} critical heartbeat failures. DS Agent cannot maintain connection with DS Manager.',
                        'affected_ports': list(set(port for issue in heartbeat_failures for port in issue.get('ports_affected', []))),
                        'recommendations': self._get_heartbeat_recommendations(),
                        'diagnostic_commands': self._get_network_diagnostic_commands(),
                        'evidence': [issue.get('message', '') for issue in heartbeat_failures[:3]]
                    })
                
                if connection_failures:
                    root_causes.append({
                        'type': 'network_connectivity',
                        'severity': 'critical',
                        'title': 'Network Connectivity Failure',
                        'description': f'Detected {len(connection_failures)} critical network connection issues.',
                        'affected_ports': list(set(port for issue in connection_failures for port in issue.get('ports_affected', []))),
                        'recommendations': self._get_connectivity_recommendations(),
                        'diagnostic_commands': self._get_network_diagnostic_commands(),
                        'evidence': [issue.get('message', '') for issue in connection_failures[:3]]
                    })
            
            if high_network:
                root_causes.append({
                    'type': 'network_configuration',
                    'severity': 'high',
                    'title': 'Network Configuration Issues',
                    'description': f'Detected {len(high_network)} high-priority network configuration problems.',
                    'recommendations': self._get_network_config_recommendations(),
                    'evidence': [issue.get('message', '') for issue in high_network[:3]]
                })
        
        # Authentication and Certificate Issues
        auth_issues = offline_analysis.get('authentication_issues', [])
        if auth_issues:
            critical_auth = [i for i in auth_issues if i.get('severity') == 'critical']
            
            if critical_auth:
                root_causes.append({
                    'type': 'authentication_failure',
                    'severity': 'critical',
                    'title': 'Authentication/Certificate Failure',
                    'description': f'Detected {len(critical_auth)} critical authentication failures. DS Agent cannot authenticate with DS Manager.',
                    'recommendations': self._get_authentication_recommendations(),
                    'diagnostic_commands': self._get_certificate_diagnostic_commands(),
                    'evidence': [issue.get('message', '') for issue in critical_auth[:3]]
                })
        
        # Service-Level Issues
        service_issues = offline_analysis.get('service_issues', [])
        if service_issues:
            critical_service = [i for i in service_issues if i.get('severity') == 'critical']
            high_service = [i for i in service_issues if i.get('severity') == 'high']
            
            if critical_service:
                crashes = [i for i in critical_service if 'crash' in i.get('category', '')]
                startup_failures = [i for i in critical_service if 'startup' in i.get('category', '')]
                
                if crashes:
                    root_causes.append({
                        'type': 'service_crash',
                        'severity': 'critical',
                        'title': 'DS Agent Service Crash',
                        'description': f'Detected {len(crashes)} service crashes. DS Agent process terminated unexpectedly.',
                        'recommendations': self._get_service_crash_recommendations(),
                        'diagnostic_commands': self._get_service_diagnostic_commands(),
                        'evidence': [issue.get('message', '') for issue in crashes[:3]]
                    })
                
                if startup_failures:
                    root_causes.append({
                        'type': 'service_startup',
                        'severity': 'critical',
                        'title': 'DS Agent Startup Failure',
                        'description': f'Detected {len(startup_failures)} service startup failures.',
                        'recommendations': self._get_startup_failure_recommendations(),
                        'evidence': [issue.get('message', '') for issue in startup_failures[:3]]
                    })
        
        # Smart Protection Network Issues
        spn_issues = offline_analysis.get('spn_issues', [])
        if spn_issues:
            critical_spn = [i for i in spn_issues if i.get('severity') == 'critical']
            
            if critical_spn:
                root_causes.append({
                    'type': 'smart_protection_network',
                    'severity': 'high',  # SPN issues are important but not always offline-causing
                    'title': 'Smart Protection Network Connectivity Issues',
                    'description': f'Detected {len(critical_spn)} Smart Protection Network connectivity issues.',
                    'affected_endpoints': list(set(endpoint for issue in critical_spn for endpoint in issue.get('endpoints', []))),
                    'recommendations': self._get_spn_recommendations(),
                    'evidence': [issue.get('message', '') for issue in critical_spn[:3]]
                })
        
        # Resource Constraint Issues
        resource_issues = offline_analysis.get('resource_issues', [])
        if resource_issues:
            root_causes.append({
                'type': 'resource_constraints',
                'severity': 'high',
                'title': 'System Resource Constraints',
                'description': f'Detected {len(resource_issues)} resource constraint issues that may impact DS Agent operation.',
                'recommendations': self._get_resource_recommendations(),
                'evidence': [issue.get('message', '') for issue in resource_issues[:3]]
            })
        
        # Event Correlation Analysis
        event_correlations = offline_analysis.get('event_correlation', [])
        if event_correlations:
            critical_events = [e for e in event_correlations if e.get('severity') == 'critical']
            if critical_events:
                root_causes.append({
                    'type': 'event_correlation',
                    'severity': 'high',
                    'title': 'Critical Event Correlation Detected',
                    'description': f'Detected {len(critical_events)} critical events that correlate with offline status.',
                    'event_summary': [f"Event {e['event_id']}: {e['description']}" for e in critical_events[:5]],
                    'recommendations': ['Review Windows Event Logs for additional context', 'Check system stability and recent changes']
                })
        
        # Comprehensive Analysis Summary
        if len(root_causes) > 1:
            root_causes.append({
                'type': 'comprehensive_analysis',
                'severity': 'critical' if any(rc.get('severity') == 'critical' for rc in root_causes) else 'high',
                'title': 'Multiple Contributing Factors Detected',
                'description': f'Analysis identified {len(root_causes)-1} distinct categories of issues contributing to DS Agent offline status.',
                'priority_order': [rc.get('title', '') for rc in sorted(root_causes, key=lambda x: {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}.get(x.get('severity', 'low'), 3))],
                'recommendations': [
                    'Address critical network communication issues first',
                    'Verify authentication and certificate validity',
                    'Ensure DS Agent service is stable and properly configured',
                    'Monitor system resources and performance',
                    'Implement comprehensive logging for future diagnosis'
                ]
            })
        
        return root_causes
    
    def _get_network_diagnostic_commands(self) -> Dict[str, List[str]]:
        """Get platform-specific network diagnostic commands"""
        return {
            'windows': [
                'netstat -an | findstr "4119\\|4120\\|4118"',  # Check port status
                'telnet <ds_manager_ip> 4119',  # Test connectivity
                'nslookup <ds_manager_hostname>',  # DNS resolution
                'ping <ds_manager_ip>',  # Basic connectivity
                'route print',  # Routing table
                'ipconfig /all',  # Network configuration
                'netsh winsock show catalog',  # Winsock status
                'netsh int ip show config'  # IP configuration
            ],
            'linux': [
                'netstat -tuln | grep -E "4119|4120|4118"',
                'telnet <ds_manager_ip> 4119',
                'nslookup <ds_manager_hostname>',
                'ping <ds_manager_ip>',
                'route -n',
                'ifconfig -a',
                'ss -tuln | grep -E "4119|4120|4118"'
            ]
        }
    
    def _get_service_diagnostic_commands(self) -> Dict[str, List[str]]:
        """Get platform-specific service diagnostic commands"""
        return {
            'windows': [
                'sc query "Trend Micro Deep Security Agent"',  # Service status
                'sc qc "Trend Micro Deep Security Agent"',  # Service configuration
                'tasklist | findstr dsa',  # Process status
                'wevtutil qe System /c:50 /f:text /q:"*[System[Provider[@Name=\'Deep Security Agent\']]]"',  # Event logs
                'reg query "HKLM\\SOFTWARE\\TrendMicro\\Deep Security Agent"',  # Registry settings
                'dir "C:\\ProgramData\\Trend Micro\\Deep Security Agent\\dsa_core\\log"',  # Log directory
                'netstat -ano | findstr :4119'  # Port listening status
            ],
            'linux': [
                'systemctl status ds_agent',
                'systemctl is-enabled ds_agent', 
                'ps aux | grep ds_agent',
                'journalctl -u ds_agent -n 50',
                'ls -la /var/opt/ds_agent/log/',
                'netstat -tlnp | grep 4119'
            ]
        }
    
    def _get_certificate_diagnostic_commands(self) -> Dict[str, List[str]]:
        """Get platform-specific certificate diagnostic commands"""
        return {
            'windows': [
                'certlm.msc',  # Certificate manager
                'certutil -store My',  # Personal certificate store
                'certutil -store Root',  # Root certificate store
                'w32tm /query /status',  # Time synchronization
                'reg query "HKLM\\SOFTWARE\\TrendMicro\\Deep Security Agent\\Certificates"',
                'dir "C:\\ProgramData\\Trend Micro\\Deep Security Agent\\certificates" /s'
            ],
            'linux': [
                'openssl x509 -in /var/opt/ds_agent/certificates/agent.crt -text -noout',
                'ls -la /var/opt/ds_agent/certificates/',
                'openssl verify /var/opt/ds_agent/certificates/agent.crt',
                'ntpq -p',  # Time synchronization
                'date',  # Current system time
                'timedatectl status'  # System time status (systemd)
            ]
        }

    def generate_comprehensive_report(self, analysis_results: Dict[str, Any], log_entries: List[Dict[str, Any]]) -> str:
        """
        Generate comprehensive DS Agent offline analysis report
        """
        report_lines = []
        report_lines.append("=" * 80)
        report_lines.append("DEEP SECURITY AGENT OFFLINE ANALYSIS REPORT")
        report_lines.append("=" * 80)
        report_lines.append("")
        
        # Executive Summary
        offline_analysis = analysis_results.get('offline_analysis', {})
        severity_summary = offline_analysis.get('severity_summary', {})
        
        total_issues = sum(severity_summary.values())
        critical_issues = severity_summary.get('critical', 0)
        high_issues = severity_summary.get('high', 0)
        
        report_lines.append("EXECUTIVE SUMMARY")
        report_lines.append("-" * 40)
        report_lines.append(f"Total Issues Detected: {total_issues}")
        report_lines.append(f"Critical Issues: {critical_issues}")
        report_lines.append(f"High Priority Issues: {high_issues}")
        report_lines.append(f"Log Entries Analyzed: {len(log_entries)}")
        report_lines.append("")
        
        # Overall Assessment
        if critical_issues > 0:
            status = "CRITICAL - Immediate Action Required"
            impact = "DS Agent offline status confirmed with critical issues identified"
        elif high_issues > 0:
            status = "HIGH PRIORITY - Attention Required"
            impact = "Significant issues detected that may cause offline status"
        elif total_issues > 0:
            status = "MODERATE - Investigation Recommended"
            impact = "Minor issues detected that could contribute to connectivity problems"
        else:
            status = "NO CRITICAL ISSUES DETECTED"
            impact = "No obvious offline indicators found in analyzed logs"
        
        report_lines.append(f"Overall Status: {status}")
        report_lines.append(f"Impact Assessment: {impact}")
        report_lines.append("")
        
        # Root Cause Analysis
        root_causes = offline_analysis.get('root_cause_analysis', [])
        if root_causes:
            report_lines.append("ROOT CAUSE ANALYSIS")
            report_lines.append("-" * 40)
            
            for i, cause in enumerate(root_causes, 1):
                report_lines.append(f"{i}. {cause.get('title', 'Unknown Issue')} [{cause.get('severity', 'unknown').upper()}]")
                report_lines.append(f"   Description: {cause.get('description', 'No description available')}")
                
                if 'affected_ports' in cause:
                    report_lines.append(f"   Affected Ports: {', '.join(map(str, cause['affected_ports']))}")
                
                if 'evidence' in cause and cause['evidence']:
                    report_lines.append("   Evidence:")
                    for evidence in cause['evidence'][:2]:  # Show first 2 evidence items
                        report_lines.append(f"     - {evidence[:100]}{'...' if len(evidence) > 100 else ''}")
                
                report_lines.append("")
            
        report_lines.append("=" * 80)
        report_lines.append("END OF ANALYSIS REPORT")  
        report_lines.append("=" * 80)
        
        return "\n".join(report_lines)
    
    def _get_heartbeat_recommendations(self) -> List[str]:
        """Get recommendations for heartbeat communication failures"""
        return [
            'Verify DS Manager is accessible on configured ports (4119/4120)',
            'Check network connectivity between DS Agent and DS Manager',
            'Validate firewall rules allow DS Agent communication',
            'Review proxy configuration if using proxy server',
            'Verify DNS resolution for DS Manager hostname',
            'Check for network latency or packet loss issues',
            'Restart DS Agent service to re-establish heartbeat',
            'Review DS Manager server logs for connection attempts'
        ]
    
    def _get_connectivity_recommendations(self) -> List[str]:
        """Get recommendations for general connectivity issues"""
        return [
            'Test network connectivity using telnet to DS Manager ports',
            'Verify routing table for DS Manager subnet access',
            'Check network adapter configuration and IP settings',
            'Validate network security policies and Group Policy settings',
            'Test with different network interface if available',
            'Review network infrastructure between agent and manager',
            'Check for VPN or tunnel configuration issues'
        ]
    
    def _get_network_config_recommendations(self) -> List[str]:
        """Get recommendations for network configuration issues"""
        return [
            'Validate DS Agent configuration file network settings',
            'Check port configuration matches DS Manager setup',
            'Review proxy server configuration and credentials',
            'Verify SSL/TLS certificate configuration',
            'Check DNS server configuration and resolution',
            'Validate network adapter binding and priority',
            'Review Windows networking service status'
        ]
    
    def _get_authentication_recommendations(self) -> List[str]:
        """Get recommendations for authentication failures"""
        return [
            'Verify DS Agent certificate is valid and not expired',
            'Check certificate trust chain and root CA validity',
            'Validate system time synchronization with DS Manager',
            'Review certificate store for corrupted certificates',
            'Re-activate DS Agent if certificate issues persist',
            'Check DS Manager authentication settings',
            'Validate computer account domain membership'
        ]
    
    def _get_service_crash_recommendations(self) -> List[str]:
        """Get recommendations for service crashes"""
        return [
            'Review Windows Event Logs for crash details',
            'Check system memory and disk space availability',
            'Validate DS Agent installation integrity',
            'Review recent system changes or updates',
            'Restart DS Agent service and monitor stability',
            'Check for conflicting security software',
            'Consider DS Agent reinstallation if crashes persist'
        ]
    
    def _get_startup_failure_recommendations(self) -> List[str]:
        """Get recommendations for startup failures"""
        return [
            'Check DS Agent service dependencies are running',
            'Verify DS Agent service account permissions',
            'Review DS Agent configuration file for errors',
            'Check system resources during startup',
            'Validate DS Agent installation files integrity',
            'Review Windows Event Logs for startup errors',
            'Try starting DS Agent service manually'
        ]
    
    def _get_spn_recommendations(self) -> List[str]:
        """Get recommendations for Smart Protection Network issues"""
        return [
            'Verify internet connectivity for Smart Protection',
            'Check firewall rules for Smart Protection endpoints',
            'Review proxy configuration for external connectivity',
            'Validate DNS resolution for Smart Protection servers',
            'Test connectivity to Smart Protection Network URLs',
            'Check Smart Protection Network feature settings',
            'Review Smart Protection cache and update status'
        ]
    
    def _get_resource_recommendations(self) -> List[str]:
        """Get recommendations for resource constraint issues"""
        return [
            'Monitor system memory usage and available RAM',
            'Check disk space on system and DS Agent directories',
            'Review CPU utilization during DS Agent operation',
            'Check for memory leaks in DS Agent process',
            'Validate system performance counters',
            'Consider system resource allocation adjustments',
            'Monitor for competing resource-intensive processes'
        ]
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
                    'severity': 'critical'
                })
            
            if connection_issues:
                root_causes.append({
                    'type': 'connection_failure',
                    'description': 'Agent cannot establish connection to manager',
                    'impact': 'Agent appears offline to manager',
                    'count': len(connection_issues),
                    'severity': 'critical'
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
                    'severity': 'critical'
                })
            
            if startup_failures:
                root_causes.append({
                    'type': 'startup_failure',
                    'description': 'DS Agent service failed to start properly',
                    'impact': 'Agent cannot come online',
                    'count': len(startup_failures),
                    'severity': 'critical'
                })
        
        return root_causes

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
                          len(results['offline_analysis']['service_issues']))
            
            results['summary']['offline_issues'] = total_issues
            results['summary']['critical_issues'] = results['offline_analysis']['severity_summary']['critical']
            
            self._update_progress("Recommendations", "Generating recommendations", 70)
            
            # Generate recommendations
            results['recommendations'] = self._generate_offline_recommendations(results['offline_analysis'])
            
            # Dynamic RAG Integration for DS Agent Offline Analysis - 80% progress
            self._update_progress("Dynamic RAG & AI Intelligence", "Starting Dynamic RAG analysis...", 80)
            if DYNAMIC_RAG_AVAILABLE:
                try:
                    # Read log content for dynamic analysis
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        log_content = f.read()
                    
                    from dynamic_rag_system import apply_dynamic_rag_to_analysis
                    self._update_progress("Dynamic RAG & AI Intelligence", "Processing with Claude AI...", 90)
                    results = apply_dynamic_rag_to_analysis(results, log_content)
                    
                    dynamic_rag = results.get('dynamic_rag_analysis', {})
                    if dynamic_rag and 'error' not in dynamic_rag:
                        print(f"✅ Dynamic RAG Analysis (DS Agent Offline): {dynamic_rag.get('analysis_metadata', {}).get('knowledge_sources_used', 0)} sources")
                        
                        # Add dynamic insights to recommendations
                        if dynamic_rag.get('ai_response'):
                            ai_summary = dynamic_rag['ai_response'][:200] + "..." if len(dynamic_rag['ai_response']) > 200 else dynamic_rag['ai_response']
                            results['recommendations'].append(f'🧠 <strong>AI Offline Analysis</strong>: {ai_summary}')
                            
                except Exception as e:
                    print(f"⚠️ RAG analysis failed: {e}")
            
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
                    "⚠️ DNS resolution issues detected",
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
        
        # General recommendations if no specific issues found
        if not recommendations:
            recommendations.extend([
                "✅ No critical offline issues detected in log analysis",
                "• Monitor agent status in Deep Security Manager",
                "• Check agent last contact time and heartbeat status",
                "• Verify agent policies are applied correctly"
            ])
        
        return recommendations

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
            analysis_results = self.analyze_log_file(log_file)
            
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
                'connectivity_errors': len(analysis_results.get('offline_analysis', {}).get('communication_issues', [])),
                'service_crashes': len([i for i in analysis_results.get('offline_analysis', {}).get('service_issues', []) if 'crash' in i.get('category', '')])
            }
            
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
