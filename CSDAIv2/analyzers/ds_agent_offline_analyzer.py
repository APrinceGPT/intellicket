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
    AI-Enhanced Deep Security Agent Offline Communication Analyzer
    
    Advanced AI-powered analysis engine for DS Agent communication issues based on 
    Deep Security 20.0 architecture and comprehensive network communications research.
    
    Core AI Capabilities:
    - Dynamic RAG-powered contextual analysis with Deep Security knowledge base
    - Machine Learning pattern recognition for communication anomalies
    - AI-driven root cause analysis with probabilistic scoring
    - Intelligent troubleshooting recommendations with confidence levels
    
    Communication Analysis Features:
    - Network communication pattern analysis (ports 4119, 4120, 4122, 443)
    - Certificate and PKI authentication failure detection
    - Smart Protection Network connectivity diagnostics
    - Manager-Agent heartbeat and policy synchronization analysis
    - DNS resolution and proxy configuration issue detection
    - Time synchronization and certificate expiration analysis
    - Service dependency and platform-specific failure patterns
    
    Enhanced Diagnostic Capabilities:
    - Event ID correlation with Deep Security 20.0 specifications
    - Multi-platform diagnostic command generation (Windows/Linux)
    - Bandwidth and network requirement validation
    - Firewall and proxy configuration analysis
    - Real-time threat intelligence integration
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
        """Initialize AI-enhanced patterns for DS Agent communication analysis based on Deep Security 20.0 research"""
        
        # AI-Enhanced Network Communication Patterns (Based on comprehensive JSON analysis)
        self.ai_communication_patterns = {
            'heartbeat_communication_failures': {
                'patterns': [
                    r'heartbeat.*failed|heartbeat.*timeout|heartbeat.*error',
                    r'failed.*send.*heartbeat|heartbeat.*not.*sent',
                    r'no.*heartbeat.*response|heartbeat.*response.*timeout', 
                    r'manager.*heartbeat.*failed|heartbeat.*communication.*failed',
                    r'heartbeat.*rejected|heartbeat.*server.*failed',
                    r'agent.*heartbeat.*rejected|contact.*by.*unrecognized.*client',
                    r'event.*id.*770|event.*id.*771|event.*4012'
                ],
                'severity': 'critical',
                'category': 'heartbeat_communication',
                'ports_affected': [4120],
                'communication_direction': 'agent_to_manager',
                'ai_context': 'Heartbeat communication is critical for Deep Security Agent status reporting and policy synchronization',
                'ml_indicators': ['frequency_analysis', 'timing_patterns', 'retry_behavior'],
                'confidence_weight': 0.9
            },
            'manager_connectivity_failures': {
                'patterns': [
                    r'connection.*failed|failed.*connect.*manager',
                    r'cannot.*contact.*manager|manager.*unreachable',
                    r'timeout.*connecting.*manager|connection.*timeout',
                    r'network.*unreachable|host.*unreachable',
                    r'port.*4119.*blocked|port.*4120.*blocked|port.*443.*blocked',
                    r'event.*id.*4011|event.*id.*730|event.*id.*742'
                ],
                'severity': 'critical',
                'category': 'manager_connectivity',
                'ports_affected': [4119, 4120],
                'communication_direction': 'bidirectional',
                'ai_context': 'Primary communication channel between DS Agent and Deep Security Manager',
                'ml_indicators': ['connection_retry_patterns', 'port_accessibility', 'network_latency'],
                'confidence_weight': 0.95
            },
            'certificate_authentication_failures': {
                'patterns': [
                    r'certificate.*expired|certificate.*invalid|certificate.*error',
                    r'ssl.*handshake.*failed|tls.*handshake.*failed',
                    r'authentication.*failed|mutual.*authentication.*failed',
                    r'certificate.*not.*trusted|certificate.*validation.*failed',
                    r'time.*synchronization.*issue|clock.*drift',
                    r'event.*id.*930|event.*id.*931|event.*id.*734'
                ],
                'severity': 'high',
                'category': 'certificate_authentication',
                'ports_affected': [4119, 4120, 443],
                'communication_direction': 'bidirectional',
                'ai_context': 'PKI certificate authentication is essential for secure Deep Security communications',
                'ml_indicators': ['certificate_expiry_patterns', 'time_sync_analysis', 'auth_failure_frequency'],
                'confidence_weight': 0.85
            },
            'smart_protection_network_failures': {
                'patterns': [
                    r'smart.*protection.*network.*failed|spn.*connection.*failed',
                    r'file.*reputation.*service.*failed|threat.*intelligence.*failed',
                    r'cloud.*service.*unavailable|predictive.*ml.*failed',
                    r'icrc\.trendmicro\.com.*failed|gfrbridge\.trendmicro\.com.*failed',
                    r'trx\.trendmicro\.com.*failed|smart.*scan.*service.*failed',
                    r'dns.*resolution.*failed.*trendmicro|proxy.*authentication.*failed'
                ],
                'severity': 'high',
                'category': 'smart_protection_network',
                'ports_affected': [443],
                'communication_direction': 'outbound',
                'ai_context': 'Smart Protection Network provides real-time threat intelligence and cloud-based scanning',
                'ml_indicators': ['cloud_service_availability', 'dns_resolution_patterns', 'proxy_config_analysis'],
                'confidence_weight': 0.8
            },
            'dns_resolution_failures': {
                'patterns': [
                    r'dns.*resolution.*failed|cannot.*resolve.*hostname',
                    r'name.*resolution.*failed|hostname.*not.*found',
                    r'dns.*server.*unreachable|dns.*timeout',
                    r'temporary.*failure.*in.*name.*resolution',
                    r'getaddrinfo.*failed|gethostbyname.*failed'
                ],
                'severity': 'high',
                'category': 'dns_resolution',
                'ports_affected': [53],
                'communication_direction': 'outbound',
                'ai_context': 'DNS resolution is critical for Deep Security Manager and Smart Protection Network connectivity',
                'ml_indicators': ['dns_query_patterns', 'resolution_timing', 'dns_server_accessibility'],
                'confidence_weight': 0.9
            },
            'proxy_configuration_failures': {
                'patterns': [
                    r'proxy.*authentication.*failed|http.*407.*proxy.*authentication',
                    r'proxy.*connection.*failed|proxy.*server.*unreachable',
                    r'proxy.*configuration.*error|invalid.*proxy.*settings',
                    r'ntlm.*authentication.*failed|kerberos.*authentication.*failed',
                    r'socks.*proxy.*failed|https.*proxy.*failed'
                ],
                'severity': 'medium',
                'category': 'proxy_configuration',
                'ports_affected': [8080, 3128, 1080],
                'communication_direction': 'outbound',
                'ai_context': 'Proxy servers are commonly used in enterprise environments for Deep Security communications',
                'ml_indicators': ['proxy_auth_patterns', 'proxy_server_health', 'authentication_method_analysis'],
                'confidence_weight': 0.75
            },
            'service_process_failures': {
                'patterns': [
                    r'ds_agent.*service.*failed|ds_agent.*service.*stopped',
                    r'deep.*security.*agent.*not.*running|dsa_core\.exe.*failed',
                    r'amsp.*platform.*failed|trend.*micro.*solution.*platform.*failed',
                    r'insufficient.*system.*resources|out.*of.*memory',
                    r'event.*id.*5000|event.*id.*5003|event.*id.*1008|event.*id.*1112'
                ],
                'severity': 'critical',
                'category': 'service_process_failures',
                'ports_affected': [],
                'communication_direction': 'local',
                'ai_context': 'Deep Security Agent service is the core component responsible for all security functions',
                'ml_indicators': ['service_restart_patterns', 'resource_utilization', 'dependency_analysis'],
                'confidence_weight': 0.95
            }
        }
        
        # AI-Enhanced Diagnostic Event Mapping (from JSON research)
        self.ai_diagnostic_events = {
            'communication_critical': {
                730: {'desc': 'Agent offline - Manager cannot communicate', 'ai_priority': 1.0, 'troubleshooting': 'network_connectivity_check'},
                742: {'desc': 'Communication problem detected', 'ai_priority': 0.9, 'troubleshooting': 'network_diagnostics'},
                4011: {'desc': 'Failure to contact manager', 'ai_priority': 1.0, 'troubleshooting': 'manager_connectivity_test'},
                4012: {'desc': 'Heartbeat failed', 'ai_priority': 1.0, 'troubleshooting': 'heartbeat_diagnostics'}
            },
            'authentication_issues': {
                770: {'desc': 'Agent heartbeat rejected', 'ai_priority': 0.9, 'troubleshooting': 'certificate_validation'},
                771: {'desc': 'Contact by unrecognized client', 'ai_priority': 0.8, 'troubleshooting': 'certificate_authentication'},
                930: {'desc': 'Certificate accepted', 'ai_priority': 0.3, 'troubleshooting': 'none'},
                931: {'desc': 'Certificate deleted', 'ai_priority': 0.7, 'troubleshooting': 'certificate_renewal'},
                734: {'desc': 'Time synchronization issue', 'ai_priority': 0.8, 'troubleshooting': 'time_sync_check'}
            },
            'service_critical': {
                5000: {'desc': 'Agent started successfully', 'ai_priority': 0.2, 'troubleshooting': 'none'},
                5003: {'desc': 'Agent stopped', 'ai_priority': 1.0, 'troubleshooting': 'service_restart'},
                1008: {'desc': 'Kernel unsupported', 'ai_priority': 1.0, 'troubleshooting': 'platform_compatibility'},
                1112: {'desc': 'Driver installation failed', 'ai_priority': 1.0, 'troubleshooting': 'driver_installation'}
            }
        }
        
        # AI Network Architecture Specifications (from JSON research)
        self.ai_network_architecture = {
            'deep_security_manager_communication': {
                'port_4119': {
                    'protocol': 'HTTPS',
                    'purpose': 'Primary agent to manager communication',
                    'direction': 'outbound_from_agent',
                    'encryption': 'TLS_1.2_1.3_AES',
                    'authentication': 'mutual_pki_certificates',
                    'data_types': ['heartbeat', 'security_events', 'status_reports', 'audit_logs'],
                    'ai_monitoring': 'high_priority'
                },
                'port_4120': {
                    'protocol': 'HTTPS',
                    'purpose': 'Manager to agent heartbeat and policy',
                    'direction': 'inbound_to_agent',
                    'encryption': 'TLS_1.2_1.3_AES',
                    'authentication': 'mutual_pki_certificates',
                    'data_types': ['policy_updates', 'management_commands', 'configuration_changes'],
                    'ai_monitoring': 'high_priority'
                },
                'port_4122': {
                    'protocol': 'HTTPS',
                    'purpose': 'Relay server communication',
                    'direction': 'bidirectional',
                    'encryption': 'TLS_1.2_1.3_AES',
                    'authentication': 'mutual_pki_certificates',
                    'data_types': ['security_patterns', 'policy_relay', 'update_packages'],
                    'ai_monitoring': 'medium_priority'
                }
            },
            'smart_protection_network': {
                'file_reputation_service': {
                    'endpoints': ['*.icrc.trendmicro.com', 'ds20*.icrc.trendmicro.com'],
                    'port': 443,
                    'protocol': 'HTTPS',
                    'purpose': 'real_time_file_reputation_and_threat_intelligence',
                    'ai_monitoring': 'high_priority'
                },
                'predictive_machine_learning': {
                    'endpoints': ['ds20-*-*.trx.trendmicro.com'],
                    'port': 443,
                    'protocol': 'HTTPS',
                    'purpose': 'machine_learning_threat_detection',
                    'ai_monitoring': 'high_priority'
                },
                'gfr_bridge_service': {
                    'endpoints': ['deepsec20-*.gfrbridge.trendmicro.com'],
                    'port': 443,
                    'protocol': 'HTTPS',
                    'purpose': 'global_file_reputation_bridge',
                    'ai_monitoring': 'medium_priority'
                }
            }
        }

        # Legacy patterns for backward compatibility
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
            'communication_issues': [],  # CRITICAL FIX: Add missing communication_issues key
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

    def _ai_analyze_communication_patterns(self, log_content: str) -> Dict[str, Any]:
        """AI-Enhanced communication pattern analysis with Deep Security 20.0 architecture knowledge"""
        ai_communication_analysis = {
            'communication_health_score': 0.0,
            'ai_detected_issues': [],
            'communication_flows': {},
            'network_architecture_analysis': {},
            'ai_confidence_scores': {},
            'intelligent_diagnostics': {}
        }
        
        lines = log_content.split('\n')
        total_confidence = 0.0
        issue_count = 0
        
        # AI-powered pattern matching with confidence scoring
        for pattern_category, pattern_data in self.ai_communication_patterns.items():
            category_issues = []
            category_confidence = 0.0
            
            for pattern in pattern_data['patterns']:
                matches = []
                for i, line in enumerate(lines):
                    if re.search(pattern, line, re.IGNORECASE):
                        matches.append({
                            'line_number': i + 1,
                            'content': line.strip(),
                            'pattern_matched': pattern,
                            'ai_context': pattern_data.get('ai_context', ''),
                            'ml_indicators': pattern_data.get('ml_indicators', [])
                        })
                
                if matches:
                    category_confidence += pattern_data.get('confidence_weight', 0.5)
                    category_issues.extend(matches)
            
            if category_issues:
                ai_communication_analysis['ai_detected_issues'].append({
                    'category': pattern_category,
                    'severity': pattern_data['severity'],
                    'ports_affected': pattern_data['ports_affected'],
                    'communication_direction': pattern_data['communication_direction'],
                    'ai_context': pattern_data.get('ai_context', ''),
                    'ml_indicators': pattern_data.get('ml_indicators', []),
                    'confidence_score': min(category_confidence, 1.0),
                    'issue_count': len(category_issues),
                    'matches': category_issues[:5]  # Limit to top 5 matches for performance
                })
                
                total_confidence += min(category_confidence, 1.0)
                issue_count += 1
        
        # Calculate overall communication health score
        if issue_count > 0:
            ai_communication_analysis['communication_health_score'] = max(0.0, 1.0 - (total_confidence / issue_count))
        else:
            ai_communication_analysis['communication_health_score'] = 1.0
        
        # AI-powered network architecture analysis
        ai_communication_analysis['network_architecture_analysis'] = self._ai_analyze_network_architecture(ai_communication_analysis['ai_detected_issues'])
        
        # Generate intelligent diagnostics
        ai_communication_analysis['intelligent_diagnostics'] = self._ai_generate_intelligent_diagnostics(ai_communication_analysis['ai_detected_issues'])
        
        return ai_communication_analysis

    def _ai_analyze_network_architecture(self, detected_issues: List[Dict[str, Any]]) -> Dict[str, Any]:
        """AI analysis of Deep Security network architecture based on detected issues"""
        architecture_analysis = {
            'affected_communication_flows': [],
            'port_health_analysis': {},
            'service_connectivity_matrix': {},
            'ai_network_recommendations': []
        }
        
        # Analyze affected ports and services
        affected_ports = set()
        for issue in detected_issues:
            affected_ports.update(issue.get('ports_affected', []))
        
        # AI-powered port health analysis
        for port in affected_ports:
            port_analysis = {'port': port, 'health_status': 'unknown', 'services': [], 'ai_recommendations': []}
            
            # Map ports to Deep Security services
            if port == 4119:
                port_analysis.update({
                    'health_status': 'critical' if any(issue['severity'] == 'critical' for issue in detected_issues if port in issue.get('ports_affected', [])) else 'degraded',
                    'services': ['agent_to_manager_communication', 'security_events', 'status_reports'],
                    'ai_recommendations': ['Check manager connectivity', 'Verify firewall rules', 'Test TLS handshake']
                })
            elif port == 4120:
                port_analysis.update({
                    'health_status': 'critical' if any(issue['severity'] == 'critical' for issue in detected_issues if port in issue.get('ports_affected', [])) else 'degraded',
                    'services': ['manager_to_agent_heartbeat', 'policy_distribution'],
                    'ai_recommendations': ['Check heartbeat configuration', 'Verify manager availability', 'Test bidirectional connectivity']
                })
            elif port == 443:
                port_analysis.update({
                    'health_status': 'degraded',
                    'services': ['smart_protection_network', 'cloud_intelligence', 'threat_reputation'],
                    'ai_recommendations': ['Check internet connectivity', 'Verify DNS resolution', 'Test proxy configuration']
                })
            
            architecture_analysis['port_health_analysis'][port] = port_analysis
        
        # Generate AI network recommendations
        if 4119 in affected_ports or 4120 in affected_ports:
            architecture_analysis['ai_network_recommendations'].append({
                'priority': 'critical',
                'category': 'manager_connectivity',
                'recommendation': 'Deep Security Manager connectivity is compromised. Immediate action required.',
                'actions': ['Verify manager server status', 'Check network connectivity', 'Validate firewall rules for ports 4119/4120']
            })
        
        if 443 in affected_ports:
            architecture_analysis['ai_network_recommendations'].append({
                'priority': 'high',
                'category': 'cloud_services',
                'recommendation': 'Smart Protection Network connectivity issues detected. Cloud-based security services may be affected.',
                'actions': ['Check internet connectivity', 'Verify DNS resolution for *.trendmicro.com', 'Test proxy authentication']
            })
        
        return architecture_analysis

    def _ai_generate_intelligent_diagnostics(self, detected_issues: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate AI-powered intelligent diagnostics and troubleshooting recommendations"""
        diagnostics = {
            'priority_issues': [],
            'ai_troubleshooting_steps': [],
            'predictive_analysis': {},
            'automated_commands': {},
            'confidence_analysis': {}
        }
        
        # Sort issues by AI confidence and severity
        priority_issues = sorted(detected_issues, 
                               key=lambda x: (x.get('confidence_score', 0) * (1.0 if x.get('severity') == 'critical' else 0.8)), 
                               reverse=True)
        
        diagnostics['priority_issues'] = priority_issues[:3]  # Top 3 priority issues
        
        # Generate AI troubleshooting steps based on issue categories
        seen_categories = set()
        for issue in priority_issues:
            category = issue['category']
            if category in seen_categories:
                continue
            seen_categories.add(category)
            
            if 'heartbeat' in category:
                diagnostics['ai_troubleshooting_steps'].append({
                    'step': 'Heartbeat Communication Diagnostics',
                    'category': category,
                    'priority': 1,
                    'actions': [
                        'Test network connectivity to Deep Security Manager',
                        'Verify port 4120 accessibility',
                        'Check agent certificate validity',
                        'Review heartbeat interval configuration'
                    ],
                    'expected_resolution_time': '5-15 minutes',
                    'automation_available': True
                })
            elif 'manager_connectivity' in category:
                diagnostics['ai_troubleshooting_steps'].append({
                    'step': 'Manager Connectivity Diagnostics',
                    'category': category,
                    'priority': 1,
                    'actions': [
                        'Test TCP connectivity to manager on port 4119',
                        'Verify DNS resolution of manager hostname',
                        'Check firewall rules for Deep Security ports',
                        'Validate TLS certificate chain'
                    ],
                    'expected_resolution_time': '10-30 minutes',
                    'automation_available': True
                })
            elif 'certificate' in category:
                diagnostics['ai_troubleshooting_steps'].append({
                    'step': 'Certificate Authentication Diagnostics',
                    'category': category,
                    'priority': 2,
                    'actions': [
                        'Check certificate expiration dates',
                        'Verify system time synchronization',
                        'Validate certificate chain',
                        'Test mutual TLS authentication'
                    ],
                    'expected_resolution_time': '15-45 minutes',
                    'automation_available': False
                })
        
        # Generate platform-specific automated commands
        diagnostics['automated_commands'] = {
            'windows': [
                'Test-NetConnection -ComputerName <manager_host> -Port 4119',
                'Get-Service ds_agent | Restart-Service',
                'certlm.msc  # Check certificate store',
                'Get-EventLog -LogName Application -Source "Trend Micro Deep Security Agent" -Newest 50'
            ],
            'linux': [
                'telnet <manager_host> 4119',
                'systemctl restart ds_agent',
                'systemctl status ds_agent',
                'journalctl -u ds_agent -n 50'
            ]
        }
        
        # Confidence analysis
        total_confidence = sum(issue.get('confidence_score', 0) for issue in detected_issues)
        if detected_issues:
            diagnostics['confidence_analysis'] = {
                'overall_confidence': total_confidence / len(detected_issues),
                'high_confidence_issues': len([i for i in detected_issues if i.get('confidence_score', 0) > 0.8]),
                'ai_recommendation_reliability': 'high' if total_confidence / len(detected_issues) > 0.7 else 'medium'
            }
        
        return diagnostics

    def _ai_enhanced_root_cause_analysis(self, ai_communication_analysis: Dict[str, Any], traditional_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """AI-enhanced root cause analysis combining traditional patterns with AI insights"""
        enhanced_root_cause = {
            'ai_primary_causes': [],
            'correlation_analysis': {},
            'predictive_insights': {},
            'resolution_confidence': 0.0,
            'combined_analysis': {}
        }
        
        # Combine AI and traditional analysis
        ai_issues = ai_communication_analysis.get('ai_detected_issues', [])
        traditional_issues = (traditional_analysis.get('network_issues', []) + 
                            traditional_analysis.get('service_issues', []) + 
                            traditional_analysis.get('authentication_issues', []))
        
        # AI correlation analysis
        if ai_issues:
            # Find correlations between different issue categories
            categories = [issue['category'] for issue in ai_issues]
            category_counts = {}
            for category in categories:
                category_counts[category] = category_counts.get(category, 0) + 1
            
            # Primary cause identification based on AI confidence
            primary_cause = max(ai_issues, key=lambda x: x.get('confidence_score', 0))
            enhanced_root_cause['ai_primary_causes'].append({
                'cause': primary_cause['category'],
                'confidence': primary_cause.get('confidence_score', 0),
                'description': primary_cause.get('ai_context', ''),
                'impact_level': primary_cause['severity'],
                'affected_communications': primary_cause['communication_direction']
            })
        
        # Calculate resolution confidence
        if ai_communication_analysis.get('communication_health_score', 0) > 0.7:
            enhanced_root_cause['resolution_confidence'] = 0.9
        elif ai_communication_analysis.get('communication_health_score', 0) > 0.4:
            enhanced_root_cause['resolution_confidence'] = 0.7
        else:
            enhanced_root_cause['resolution_confidence'] = 0.5
        
        return enhanced_root_cause

    def analyze(self, file_paths: Union[str, List[str]]) -> Dict[str, Any]:
        """Standardized analysis entry point for DS Agent offline analysis with ZIP support"""
        import os
        
        try:
            self._update_progress("Initialization", "Starting DS Agent offline analysis", 1)
            
            # Normalize input to handle both string and list
            if isinstance(file_paths, list):
                if not file_paths:
                    raise ValueError("No files provided for DS Agent offline analysis")
                paths_to_analyze = file_paths
            else:
                paths_to_analyze = [file_paths] if file_paths else []
            
            # Validate input
            if not paths_to_analyze:
                raise ValueError("No valid file paths provided")
            
            # Check if any files are ZIP files that need extraction
            extracted_files = []
            log_files_to_analyze = []
            
            print(f"🔍 DEBUG: Analyzing {len(paths_to_analyze)} file(s)")
            for i, file_path in enumerate(paths_to_analyze):
                print(f"🔍 DEBUG: File {i+1}: {file_path}")
                print(f"🔍 DEBUG: File exists: {os.path.exists(file_path)}")
                print(f"🔍 DEBUG: File extension: {os.path.splitext(file_path)[1]}")
                print(f"🔍 DEBUG: Ends with .zip: {file_path.lower().endswith('.zip')}")
                
                if not os.path.exists(file_path):
                    print(f"⚠️ File not found: {file_path}")
                    continue
                
                if file_path.lower().endswith('.zip'):
                    # Extract ZIP file and get DS Agent log files
                    print(f"✅ ZIP file detected: {file_path}")
                    self._update_progress("ZIP Extraction", f"Extracting ZIP file: {os.path.basename(file_path)}", 10)
                    extracted_log_files = self._extract_ds_agent_logs_from_zip(file_path)
                    if extracted_log_files:
                        log_files_to_analyze.extend(extracted_log_files)
                        extracted_files.extend(extracted_log_files)
                        print(f"✅ Extracted {len(extracted_log_files)} DS Agent log files")
                    else:
                        print(f"⚠️ No DS Agent log files found in ZIP: {file_path}")
                else:
                    # Regular log file
                    print(f"📄 Regular file detected: {file_path}")
                    log_files_to_analyze.append(file_path)
            
            if not log_files_to_analyze:
                return {
                    'status': 'error',
                    'error': True,
                    'summary': 'No DS Agent log files found to analyze',
                    'details': ['No .log files or extractable ZIP files with DS Agent logs were found'],
                    'recommendations': [
                        'Ensure you upload DS Agent log files (ds_agent.log, ds_agent-err.log)',
                        'ZIP files should contain DS Agent log files in the root or logs folder',
                        'Check file extensions are .log, .txt, or .zip'
                    ],
                    'metadata': {
                        'files_processed': 0,
                        'analysis_type': 'ds_agent_offline'
                    }
                }
            
            # Perform analysis on all found log files
            self._update_progress("Analysis", "Analyzing DS Agent offline patterns", 20)
            
            if len(log_files_to_analyze) == 1:
                # Single file analysis
                raw_results = self.analyze_log_file(log_files_to_analyze[0])
            else:
                # Multiple files analysis
                raw_results = self.analyze_multiple_log_files(log_files_to_analyze)
            
            # Apply standardized output format
            self._update_progress("Standardization", "Converting to standardized format", 90)
            standardized_result = self._standardize_analyzer_output(raw_results, 'ds_agent_offline')
            
            # Add raw_data field for consistency
            standardized_result['raw_data'] = raw_results or {}
            
            # Add metadata including extraction info
            if raw_results and isinstance(raw_results, dict):
                summary = raw_results.get('summary', {})
                standardized_result['metadata'] = {
                    'files_processed': len(log_files_to_analyze),
                    'file_count': len(log_files_to_analyze),
                    'analysis_type': 'ds_agent_offline',
                    'log_entries_processed': summary.get('parsed_lines', 0),
                    'errors_found': summary.get('offline_issues', 0),
                    'warnings_found': summary.get('offline_issues', 0),
                    'critical_issues': summary.get('critical_issues', 0),
                    'zip_files_extracted': len([f for f in paths_to_analyze if f.lower().endswith('.zip')]),
                    'extracted_files': len(extracted_files)
                }
            else:
                standardized_result['metadata'] = {
                    'files_processed': len(log_files_to_analyze),
                    'file_count': len(log_files_to_analyze),
                    'analysis_type': 'ds_agent_offline',
                    'log_entries_processed': 0,
                    'errors_found': 0,
                    'warnings_found': 0,
                    'critical_issues': 0,
                    'zip_files_extracted': len([f for f in paths_to_analyze if f.lower().endswith('.zip')]),
                    'extracted_files': len(extracted_files)
                }
            
            # Cleanup extracted files
            for temp_file in extracted_files:
                try:
                    if os.path.exists(temp_file):
                        os.remove(temp_file)
                except Exception as e:
                    print(f"⚠️ Could not cleanup temp file {temp_file}: {e}")
            
            self._update_progress("Complete", "DS Agent offline analysis completed", 100)
            return standardized_result
            
        except Exception as e:
            print(f"❌ DS Agent offline analysis failed: {str(e)}")
            return {
                'status': 'error',
                'error': True,
                'summary': f'DS Agent offline analysis failed: {str(e)}',
                'details': [str(e)],
                'recommendations': [
                    'Check that uploaded files are valid DS Agent log files',
                    'Ensure ZIP files contain DS Agent logs (ds_agent.log, ds_agent-err.log)',
                    'Verify file permissions and accessibility'
                ],
                'metadata': {
                    'files_processed': 0,
                    'analysis_type': 'ds_agent_offline'
                }
            }

    def _extract_ds_agent_logs_from_zip(self, zip_path: str) -> List[str]:
        """Extract DS Agent log files from ZIP archive"""
        import zipfile
        import tempfile
        import os
        
        extracted_log_files = []
        
        try:
            # Create temp directory for extraction
            temp_dir = tempfile.mkdtemp(prefix="ds_agent_offline_")
            
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                # Get list of files in ZIP
                zip_contents = zip_ref.namelist()
                
                # DS Agent log file patterns to look for
                ds_agent_patterns = [
                    r'.*ds_agent\.log$',
                    r'.*ds_agent-err\.log$', 
                    r'.*ds_agent-connect\.log$',
                    r'.*ds_agent.*\.log$',
                    r'.*dsa\.log$',
                    r'.*deepsecurity.*\.log$'
                ]
                
                print(f"🔍 Scanning ZIP contents: {len(zip_contents)} files")
                
                for file_name in zip_contents:
                    # Skip directories
                    if file_name.endswith('/'):
                        continue
                    
                    # Check if this looks like a DS Agent log file
                    is_ds_agent_log = False
                    for pattern in ds_agent_patterns:
                        if re.search(pattern, file_name, re.IGNORECASE):
                            is_ds_agent_log = True
                            break
                    
                    if is_ds_agent_log:
                        try:
                            # Extract the file
                            extracted_path = zip_ref.extract(file_name, temp_dir)
                            
                            # Verify it's a readable text file
                            if os.path.exists(extracted_path) and os.path.getsize(extracted_path) > 0:
                                # Quick validation - check if it contains DS Agent content
                                try:
                                    with open(extracted_path, 'r', encoding='utf-8', errors='ignore') as f:
                                        sample_content = f.read(2000).lower()
                                        
                                    # Look for DS Agent indicators
                                    ds_indicators = [
                                        'ds_agent', 'deep security', 'trend micro', 
                                        'dsa.', 'connectionhandler', 'heartbeat',
                                        'manager', 'agent', 'dsacore'
                                    ]
                                    
                                    if any(indicator in sample_content for indicator in ds_indicators):
                                        extracted_log_files.append(extracted_path)
                                        print(f"✅ Extracted DS Agent log: {file_name} -> {extracted_path}")
                                    else:
                                        print(f"⚠️ File doesn't appear to be DS Agent log: {file_name}")
                                        # Clean up non-DS Agent file
                                        os.remove(extracted_path)
                                        
                                except Exception as e:
                                    print(f"⚠️ Could not validate extracted file {file_name}: {e}")
                                    if os.path.exists(extracted_path):
                                        os.remove(extracted_path)
                            else:
                                print(f"⚠️ Extracted file is empty or unreadable: {file_name}")
                                
                        except Exception as e:
                            print(f"⚠️ Could not extract {file_name}: {e}")
                            continue
                
                print(f"🎯 Successfully extracted {len(extracted_log_files)} DS Agent log files")
                
        except zipfile.BadZipFile:
            print(f"❌ Invalid ZIP file: {zip_path}")
        except Exception as e:
            print(f"❌ ZIP extraction failed: {str(e)}")
        
        return extracted_log_files

    def analyze_multiple_log_files(self, file_paths: List[str]) -> Dict[str, Any]:
        """Analyze multiple DS Agent log files and correlate findings"""
        self._update_progress("Multi-File Analysis", "Analyzing multiple DS Agent log files", 30)
        
        combined_results = {
            'summary': {
                'total_files': len(file_paths),
                'processed_files': 0,
                'total_lines': 0,
                'parsed_lines': 0,
                'offline_issues': 0,
                'critical_issues': 0,
                'timespan': {'start': None, 'end': None},
                'file_details': []
            },
            'offline_analysis': {
                'network_issues': [],
                'service_issues': [],
                'communication_issues': [],
                'authentication_issues': [],
                'spn_issues': [],
                'configuration_issues': [],
                'resource_issues': [],
                'event_correlation': [],
                'severity_summary': {'critical': 0, 'high': 0, 'medium': 0, 'low': 0},
                'root_cause_analysis': []
            },
            'recommendations': [],
            'file_specific_results': {},
            'correlation_analysis': {},
            'ml_insights': None,
            'rag_insights': None
        }
        
        all_log_entries = []
        
        # Process each file
        for i, file_path in enumerate(file_paths):
            try:
                self._update_progress("Multi-File Analysis", f"Processing file {i+1}/{len(file_paths)}: {os.path.basename(file_path)}", 30 + (i * 40 // len(file_paths)))
                
                file_result = self.analyze_log_file(file_path)
                combined_results['file_specific_results'][file_path] = file_result
                
                if 'error' not in file_result:
                    # Merge file summary
                    file_summary = file_result.get('summary', {})
                    combined_results['summary']['processed_files'] += 1
                    combined_results['summary']['total_lines'] += file_summary.get('total_lines', 0)
                    combined_results['summary']['parsed_lines'] += file_summary.get('parsed_lines', 0)
                    combined_results['summary']['offline_issues'] += file_summary.get('offline_issues', 0)
                    combined_results['summary']['critical_issues'] += file_summary.get('critical_issues', 0)
                    
                    # Track timespan
                    file_timespan = file_summary.get('timespan', {})
                    if file_timespan.get('start'):
                        if not combined_results['summary']['timespan']['start'] or file_timespan['start'] < combined_results['summary']['timespan']['start']:
                            combined_results['summary']['timespan']['start'] = file_timespan['start']
                    if file_timespan.get('end'):
                        if not combined_results['summary']['timespan']['end'] or file_timespan['end'] > combined_results['summary']['timespan']['end']:
                            combined_results['summary']['timespan']['end'] = file_timespan['end']
                    
                    # Add file details
                    combined_results['summary']['file_details'].append({
                        'file_path': file_path,
                        'file_name': os.path.basename(file_path),
                        'lines_processed': file_summary.get('total_lines', 0),
                        'issues_found': file_summary.get('offline_issues', 0)
                    })
                    
                    # Merge offline analysis results
                    file_offline = file_result.get('offline_analysis', {})
                    for category in ['network_issues', 'service_issues', 'communication_issues', 'authentication_issues', 'spn_issues', 'configuration_issues', 'resource_issues', 'event_correlation']:
                        if category in file_offline:
                            combined_results['offline_analysis'][category].extend(file_offline[category])
                    
                    # Merge severity summary
                    file_severity = file_offline.get('severity_summary', {})
                    for severity in ['critical', 'high', 'medium', 'low']:
                        combined_results['offline_analysis']['severity_summary'][severity] += file_severity.get(severity, 0)
                    
                    # Collect recommendations
                    if 'recommendations' in file_result:
                        combined_results['recommendations'].extend(file_result['recommendations'])
                
            except Exception as e:
                print(f"⚠️ Error processing file {file_path}: {e}")
                combined_results['summary']['file_details'].append({
                    'file_path': file_path,
                    'file_name': os.path.basename(file_path),
                    'error': str(e)
                })
        
        # Perform cross-file correlation analysis
        self._update_progress("Correlation Analysis", "Correlating findings across files", 80)
        combined_results['correlation_analysis'] = self._perform_cross_file_correlation(combined_results['file_specific_results'])
        
        # Generate comprehensive root cause analysis
        combined_results['offline_analysis']['root_cause_analysis'] = self._perform_enhanced_root_cause_analysis(combined_results['offline_analysis'])
        
        # Deduplicate and prioritize recommendations
        combined_results['recommendations'] = list(set(combined_results['recommendations']))
        
        return combined_results

    def _perform_cross_file_correlation(self, file_results: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """Perform correlation analysis across multiple log files"""
        correlation = {
            'timeline_correlation': {},
            'issue_patterns': {},
            'severity_trends': {},
            'common_issues': []
        }
        
        # Collect issues from all files with timestamps
        all_issues_with_time = []
        
        for file_path, results in file_results.items():
            if 'error' in results:
                continue
                
            offline_analysis = results.get('offline_analysis', {})
            
            # Collect all issues with timestamps
            for category in ['network_issues', 'service_issues', 'communication_issues', 'authentication_issues']:
                for issue in offline_analysis.get(category, []):
                    if issue.get('timestamp'):
                        all_issues_with_time.append({
                            'file': file_path,
                            'category': category,
                            'timestamp': issue['timestamp'],
                            'severity': issue.get('severity', 'low'),
                            'type': issue.get('type', 'unknown'),
                            'message': issue.get('message', '')
                        })
        
        # Sort by timestamp for timeline analysis
        all_issues_with_time.sort(key=lambda x: x['timestamp'])
        
        # Find issue patterns
        issue_types = {}
        for issue in all_issues_with_time:
            issue_type = issue['type']
            if issue_type not in issue_types:
                issue_types[issue_type] = []
            issue_types[issue_type].append(issue)
        
        # Identify common issues across files
        for issue_type, issues in issue_types.items():
            if len(issues) > 1:  # Issue appears in multiple places
                correlation['common_issues'].append({
                    'issue_type': issue_type,
                    'occurrence_count': len(issues),
                    'files_affected': len(set(issue['file'] for issue in issues)),
                    'severity_distribution': {
                        'critical': sum(1 for i in issues if i['severity'] == 'critical'),
                        'high': sum(1 for i in issues if i['severity'] == 'high'),
                        'medium': sum(1 for i in issues if i['severity'] == 'medium'),
                        'low': sum(1 for i in issues if i['severity'] == 'low')
                    }
                })
        
        return correlation

    def analyze_log_file(self, file_path: str) -> Dict[str, Any]:
        """Analyze DS Agent log file for offline issues"""
        self._update_progress("File Analysis", f"Starting analysis of {os.path.basename(file_path)}", 40)
        
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
            
            # Generate enhanced recommendations with AI insights
            base_recommendations = self._generate_offline_recommendations(results['offline_analysis'])
            
            # Add AI-enhanced recommendations if available
            ai_recommendations = []
            if 'ai_communication_analysis' in results and not results['ai_communication_analysis'].get('error'):
                ai_recommendations = self._generate_ai_enhanced_recommendations(results['ai_communication_analysis'])
            
            # Combine traditional and AI recommendations
            results['recommendations'] = base_recommendations + ai_recommendations
            
            # AI-Enhanced Communication Analysis - 75% progress
            self._update_progress("AI Communication Analysis", "Performing AI-powered communication pattern analysis...", 75)
            try:
                # Read log content for AI analysis
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    log_content = f.read()
                
                # Perform AI-enhanced communication analysis
                ai_communication_analysis = self._ai_analyze_communication_patterns(log_content)
                results['ai_communication_analysis'] = ai_communication_analysis
                
                # Enhanced root cause analysis combining AI with traditional analysis
                ai_enhanced_root_cause = self._ai_enhanced_root_cause_analysis(ai_communication_analysis, results['offline_analysis'])
                results['ai_enhanced_root_cause'] = ai_enhanced_root_cause
                
                print(f"✅ AI Communication Analysis: Health Score {ai_communication_analysis['communication_health_score']:.2f}, {len(ai_communication_analysis['ai_detected_issues'])} AI-detected issues")
                
            except Exception as e:
                print(f"⚠️ AI Communication analysis failed: {e}")
                results['ai_communication_analysis'] = {'error': str(e)}

            # Dynamic RAG Integration for DS Agent Offline Analysis - 80% progress
            self._update_progress("Dynamic RAG & AI Intelligence", "Starting Dynamic RAG analysis...", 80)
            if DYNAMIC_RAG_AVAILABLE:
                try:
                    # Read log content for dynamic analysis (reuse if already read)
                    if 'log_content' not in locals():
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            log_content = f.read()
                    
                    from dynamic_rag_system import apply_dynamic_rag_to_analysis
                    self._update_progress("Dynamic RAG & AI Intelligence", "Processing with Claude AI...", 85)
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

            # ML Analysis Integration - 90% progress  
            self._update_progress("ML Pattern Analysis", "Applying machine learning insights...", 90)
            if self.ml_analyzer:
                try:
                    ml_insights = self.ml_analyzer.analyze_ds_agent_patterns(results)
                    results['ml_insights'] = ml_insights
                    print(f"✅ ML Analysis: Pattern confidence {ml_insights.get('confidence_score', 0):.2f}")
                except Exception as e:
                    print(f"⚠️ ML analysis failed: {e}")
                    results['ml_insights'] = {'error': str(e)}
            
            self._update_progress("Complete", "DS Agent offline analysis completed", 100)
            
        except Exception as e:
            error_msg = f"Failed to analyze DS Agent log: {str(e)}"
            print(f"❌ {error_msg}")
            results['error'] = error_msg
        
        return results

    def _generate_offline_recommendations(self, offline_analysis: Dict[str, Any]) -> List[str]:
        """Generate AI-enhanced recommendations based on comprehensive offline analysis"""
        recommendations = []
        
        # Communication issue recommendations
        if offline_analysis['communication_issues']:
            heartbeat_issues = [i for i in offline_analysis['communication_issues'] if 'heartbeat' in i['category']]
            connection_issues = [i for i in offline_analysis['communication_issues'] if 'connection' in i['category']]
            dns_issues = [i for i in offline_analysis['communication_issues'] if 'dns' in i['category']]
            
            if heartbeat_issues:
                recommendations.extend([
                    "🔥 CRITICAL: Heartbeat communication failures detected",
                    "• Deep Security Manager connectivity: Test port 4120 accessibility",
                    "• Network diagnostics: telnet <manager_host> 4120",
                    "• Certificate validation: Check agent-manager mutual authentication",
                    "• Time synchronization: Verify system clock accuracy (±5 minutes)",
                    "• Heartbeat interval: Review configuration (default 10 minutes)"
                ])
            
            if connection_issues:
                recommendations.extend([
                    "🔥 CRITICAL: Manager connection failures - Network infrastructure issues",
                    "• Primary communication port 4119: Test TCP connectivity",
                    "• Firewall configuration: Allow Deep Security ports (4119, 4120, 4118, 443)",
                    "• TLS/SSL validation: Check certificate chain and mutual authentication",
                    "• Proxy configuration: Verify authentication (NTLM, Kerberos, Basic)",
                    "• Network path analysis: traceroute to Deep Security Manager"
                ])
            
            if dns_issues:
                recommendations.extend([
                    "⚠️ DNS resolution failures - Name resolution infrastructure",
                    "• DNS server accessibility: Test primary and secondary DNS servers",
                    "• Hostname resolution: nslookup <manager_hostname>",
                    "• DNS cache: Clear local DNS cache (ipconfig /flushdns)",
                    "• Alternative resolution: Consider using IP address temporarily",
                    "• Corporate DNS: Verify internal DNS records for Deep Security Manager"
                ])
        
        # Service issue recommendations
        if offline_analysis['service_issues']:
            service_crashes = [i for i in offline_analysis['service_issues'] if 'crash' in i['category']]
            startup_failures = [i for i in offline_analysis['service_issues'] if 'startup' in i['category']]
            
            if service_crashes:
                recommendations.extend([
                    "🔥 CRITICAL: Deep Security Agent service instability",
                    "• System resources: Monitor memory and CPU utilization",
                    "• Event logs: Check Windows Application/System logs for errors",
                    "• Driver compatibility: Verify kernel version compatibility",
                    "• AMSP platform: Check Trend Micro Solution Platform health",
                    "• Service dependencies: Verify required Windows services running"
                ])
            
            if startup_failures:
                recommendations.extend([
                    "🔥 CRITICAL: Agent service startup failures",
                    "• Service permissions: Run as LocalSystem with proper privileges",
                    "• Driver installation: Check digital signature validation",
                    "• Boot-time loading: Verify service startup type (Automatic)",
                    "• Platform compatibility: Confirm OS and kernel version support",
                    "• Registry integrity: Validate Deep Security registry entries"
                ])
        
        # Smart Protection Network recommendations
        spn_issues = [i for i in offline_analysis.get('communication_issues', []) if 'spn' in i.get('category', '').lower()]
        if spn_issues:
            recommendations.extend([
                "⚠️ Smart Protection Network connectivity issues",
                "• Cloud services: Test connectivity to *.trendmicro.com (port 443)",
                "• File reputation: Verify icrc.trendmicro.com accessibility",
                "• Predictive ML: Check trx.trendmicro.com connectivity",
                "• Proxy authentication: Configure corporate proxy settings",
                "• DNS resolution: Verify external DNS for Trend Micro domains"
            ])
        
        # Certificate and authentication recommendations
        auth_issues = [i for i in offline_analysis.get('communication_issues', []) if 'auth' in i.get('category', '').lower()]
        if auth_issues:
            recommendations.extend([
                "🔒 Certificate and authentication issues",
                "• Certificate expiration: Check agent and manager certificates",
                "• Time synchronization: Ensure accurate system time (NTP)",
                "• PKI validation: Verify certificate chain and root CA",
                "• Mutual authentication: Test TLS handshake between agent and manager",
                "• Certificate store: Check certificate accessibility and permissions"
            ])
        
        # AI-enhanced general recommendations
        if not recommendations:
            recommendations.extend([
                "✅ No critical communication issues detected in Deep Security Agent logs",
                "🔍 Proactive monitoring recommendations:",
                "• Manager connectivity: Regular heartbeat monitoring (every 10 minutes)",
                "• Network health: Monitor bandwidth usage and latency to manager",
                "• Certificate lifecycle: Track certificate expiration dates",
                "• Service health: Monitor DS Agent service uptime and performance",
                "• Policy synchronization: Verify regular policy updates from manager",
                "• Smart Protection Network: Test cloud service connectivity periodically"
            ])
        
        return recommendations
    
    def _generate_ai_enhanced_recommendations(self, ai_analysis: Dict[str, Any]) -> List[str]:
        """Generate AI-powered recommendations based on communication analysis"""
        ai_recommendations = []
        
        if not ai_analysis or ai_analysis.get('error'):
            return ai_recommendations
        
        # AI-detected issues recommendations
        ai_issues = ai_analysis.get('ai_detected_issues', [])
        intelligent_diagnostics = ai_analysis.get('intelligent_diagnostics', {})
        
        # Add AI confidence-based recommendations
        health_score = ai_analysis.get('communication_health_score', 1.0)
        if health_score < 0.3:
            ai_recommendations.append(f"🚨 AI ALERT: Critical communication health detected (Score: {health_score:.2f}/1.0)")
        elif health_score < 0.7:
            ai_recommendations.append(f"⚠️ AI WARNING: Degraded communication health detected (Score: {health_score:.2f}/1.0)")
        else:
            ai_recommendations.append(f"✅ AI ASSESSMENT: Healthy communication patterns (Score: {health_score:.2f}/1.0)")
        
        # Add AI troubleshooting steps
        ai_steps = intelligent_diagnostics.get('ai_troubleshooting_steps', [])
        for step in ai_steps[:3]:  # Top 3 AI recommendations
            ai_recommendations.append(f"🤖 AI RECOMMENDATION: {step.get('step', 'AI-guided troubleshooting')}")
            for action in step.get('actions', [])[:2]:  # Top 2 actions per step
                ai_recommendations.append(f"  └─ {action}")
        
        return ai_recommendations
