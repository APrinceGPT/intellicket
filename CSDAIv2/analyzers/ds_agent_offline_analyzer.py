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
        """Initialize Enhanced Deep Security Event IDs (based on Deep Security 20.0 JSON research)"""
        
        # Communication Events - Core DS Agent Network Communication (JSON reference)
        self.communication_events = {
            730: {
                'description': 'Agent offline - Manager cannot communicate with computer',
                'severity': 'critical',
                'root_cause_indicators': ['network_connectivity_failure', 'firewall_blocking', 'service_down'],
                'troubleshooting_ports': [4119, 4120],
                'protocols': ['HTTPS', 'TLS_1.2', 'TLS_1.3'],
                'correlation_events': [742, 4011, 4012]
            },
            731: {
                'description': 'Agent back online - Communication restored with manager',
                'severity': 'resolved',
                'indicates': 'successful_network_restoration',
                'correlation_events': [743, 5000]
            },
            742: {
                'description': 'Communication problem detected - Network issues',
                'severity': 'high',
                'root_cause_indicators': ['network_latency', 'packet_loss', 'dns_resolution_failure'],
                'analysis_focus': 'network_path_diagnostics'
            },
            743: {
                'description': 'Communication problem resolved - Network connectivity restored',
                'severity': 'resolved',
                'indicates': 'network_issue_resolution'
            },
            770: {
                'description': 'Agent heartbeat rejected by manager',
                'severity': 'high',
                'root_cause_indicators': ['certificate_mismatch', 'time_synchronization_drift', 'policy_version_mismatch'],
                'analysis_focus': 'pki_authentication_validation'
            },
            771: {
                'description': 'Contact by unrecognized Deep Security client',
                'severity': 'high',
                'security_implications': 'potential_unauthorized_access_attempt',
                'analysis_focus': 'certificate_chain_validation'
            }
        }
        
        # Authentication Events - PKI and Certificate Management (JSON reference)
        self.authentication_events = {
            930: {
                'description': 'Certificate accepted by Deep Security Manager',
                'severity': 'info',
                'indicates': 'successful_pki_authentication',
                'certificate_validation': 'passed'
            },
            931: {
                'description': 'Certificate deleted from Deep Security Manager',
                'severity': 'warning',
                'indicates': 'certificate_removal_or_expiration',
                'follow_up_required': 'certificate_renewal_process'
            },
            734: {
                'description': 'Time synchronization issue - Certificate validation affected',
                'severity': 'high',
                'root_cause_indicators': ['ntp_server_failure', 'system_clock_drift', 'timezone_mismatch'],
                'impact': 'certificate_validation_failures',
                'resolution': 'time_synchronization_procedures'
            }
        }
        
        # Service Events - DS Agent and AMSP Platform (JSON reference)  
        self.service_events = {
            5000: {
                'description': 'Deep Security Agent started successfully',
                'severity': 'info',
                'indicates': 'service_initialization_success',
                'dependencies': ['amsp_platform', 'network_services', 'certificate_store']
            },
            5003: {
                'description': 'Deep Security Agent stopped',
                'severity': 'high',
                'root_cause_indicators': ['service_crash', 'insufficient_resources', 'dependency_failure'],
                'impact': 'protection_module_offline',
                'analysis_focus': 'service_dependency_chain'
            },
            1008: {
                'description': 'Kernel version unsupported by Deep Security Agent',
                'severity': 'critical',
                'platform_compatibility': 'kernel_driver_incompatibility',
                'resolution': 'agent_version_upgrade_or_kernel_downgrade'
            },
            1112: {
                'description': 'Deep Security drivers cannot be installed - kernel incompatibility',
                'severity': 'critical',
                'impact': 'complete_protection_failure',
                'analysis_focus': 'platform_compatibility_validation'
            }
        }
        
        # Communication Specific Events - Heartbeat and Manager Contact (JSON reference)
        self.communication_specific_events = {
            4011: {
                'description': 'Deep Security Agent failure to contact manager',
                'severity': 'critical',
                'root_cause_indicators': ['dns_resolution_failure', 'firewall_blocking_4119', 'manager_service_down'],
                'diagnostic_ports': [4119, 4120, 4122, 443],
                'troubleshooting_focus': 'network_connectivity_validation'
            },
            4012: {
                'description': 'Deep Security Agent heartbeat failed',
                'severity': 'critical',
                'heartbeat_protocol': 'https_port_4119_4120',
                'frequency_default': '600_seconds_10_minutes',
                'root_cause_indicators': ['network_timeout', 'certificate_expiration', 'manager_overload'],
                'correlation_analysis': 'heartbeat_pattern_timing'
            },
            4002: {
                'description': 'Deep Security command session initiated',
                'severity': 'info',
                'indicates': 'successful_manager_agent_communication',
                'protocol': 'https_encrypted_session'
            },
            4003: {
                'description': 'Deep Security configuration session initiated',
                'severity': 'info',
                'indicates': 'policy_synchronization_start',
                'data_transmitted': 'security_policy_updates'
            }
        }
        
        # Network and Protocol Specific Mappings (JSON reference)
        self.network_protocol_mapping = {
            'port_4119': {
                'protocol': 'HTTPS',
                'purpose': 'Primary agent to manager communication',
                'direction': 'Outbound from DS Agent',
                'authentication': 'SSL/TLS mutual authentication with PKI certificates',
                'related_events': [4011, 4012, 730]
            },
            'port_4120': {
                'protocol': 'HTTPS',
                'purpose': 'Manager to agent heartbeat and policy distribution',
                'direction': 'Inbound to DS Agent', 
                'authentication': 'SSL/TLS mutual authentication',
                'related_events': [770, 4003, 742]
            },
            'port_4122': {
                'protocol': 'HTTPS',
                'purpose': 'Deep Security Relay server communication',
                'direction': 'Bidirectional',
                'benefits': 'Reduces bandwidth to external Trend Micro servers'
            },
            'port_443': {
                'protocol': 'HTTPS',
                'purpose': 'Smart Protection Network and Cloud Services',
                'endpoints': ['*.icrc.trendmicro.com', 'ds20*.icrc.trendmicro.com'],
                'services': ['file_reputation', 'threat_intelligence', 'smart_scan']
            }
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
        """Focused DS Agent Offline Analyzer - Heartbeat & Network Communication Analysis Only"""
        self._update_progress("Heartbeat Analysis", f"Starting heartbeat and network analysis of {os.path.basename(file_path)}", 20)
        
        results = {
            'summary': {
                'file_path': file_path,
                'analysis_type': 'heartbeat_network_communication',
                'total_lines': 0,
                'parsed_lines': 0
            },
            'communication_analysis': {},
            'ai_root_cause_analysis': {},
            'troubleshooting_recommendations': []
        }
        
        try:
            self._update_progress("Log Processing", "Reading DS Agent log for heartbeat analysis", 30)
            
            # Read log content for focused analysis
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                log_content = f.read()
                log_lines = log_content.split('\n')
                results['summary']['total_lines'] = len(log_lines)
                results['summary']['parsed_lines'] = len([line for line in log_lines if line.strip()])
            
            self._update_progress("Communication Analysis", "Analyzing heartbeat and network patterns", 50)
            
            # FOCUSED ANALYSIS: Three-card structure (Key Findings, Root Cause, Troubleshooting)
            focused_analysis = self._analyze_focused_communication(log_content)
            
            # Update results with the three-card structure
            results.update(focused_analysis)
            
            # Legacy compatibility - map to old structure names
            results['communication_analysis'] = focused_analysis.get('key_findings_card', {})
            results['ai_root_cause_analysis'] = focused_analysis.get('root_cause_analysis_card', {})
            results['troubleshooting_recommendations'] = focused_analysis.get('troubleshooting_recommendations_card', {})
            
            # Dynamic RAG Integration for Enhanced Troubleshooting (Optional)
            print(f"🔍 Debug: DYNAMIC_RAG_AVAILABLE = {DYNAMIC_RAG_AVAILABLE}")
            if DYNAMIC_RAG_AVAILABLE:
                try:
                    from dynamic_rag_system import apply_dynamic_rag_to_analysis
                    self._update_progress("AI Knowledge Enhancement", "Enhancing with Deep Security knowledge base...", 90)
                    results = apply_dynamic_rag_to_analysis(results, log_content)
                    
                    dynamic_rag = results.get('dynamic_rag_analysis', {})
                    if dynamic_rag and 'error' not in dynamic_rag:
                        print(f"✅ Dynamic RAG Enhancement: {dynamic_rag.get('analysis_metadata', {}).get('knowledge_sources_used', 0)} knowledge sources")
                        
                except Exception as e:
                    print(f"⚠️ RAG enhancement failed: {e}")

            # ML Analysis for Pattern Recognition (Optional)
            if self.ml_analyzer:
                try:
                    ml_insights = self.ml_analyzer.analyze_heartbeat_patterns(results)
                    results['ai_root_cause_analysis']['ml_confidence'] = ml_insights.get('confidence_score', 0)
                    print(f"✅ ML Pattern Analysis: Confidence {ml_insights.get('confidence_score', 0):.2f}")
                except Exception as e:
                    print(f"⚠️ ML analysis failed: {e}")
            
            self._update_progress("Complete", "Focused heartbeat and network analysis completed", 100)
            
        except Exception as e:
            error_msg = f"Failed to analyze DS Agent log: {str(e)}"
            print(f"❌ {error_msg}")
            results['error'] = error_msg
        
        # Debug: Print focused analysis results
        print("🔍 Debug: Focused DS Agent Offline Analysis Complete")
        print(f"Communication Analysis: {'✅ Available' if 'communication_analysis' in results else '❌ Missing'}")
        print(f"AI Root Cause: {'✅ Available' if 'ai_root_cause_analysis' in results and 'error' not in results['ai_root_cause_analysis'] else '❌ Missing'}")
        print(f"Troubleshooting Guide: {'✅ Available' if 'troubleshooting_recommendations' in results and len(results['troubleshooting_recommendations']) > 0 else '❌ Missing'}")
        print(f"RAG Enhancement: {'✅ Available' if 'dynamic_rag_analysis' in results and 'error' not in results['dynamic_rag_analysis'] else '❌ Optional'}")
        
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

    def _analyze_focused_communication(self, log_content: str) -> Dict[str, Any]:
        """
        FOCUSED ANALYSIS: DS Agent Offline Root Cause Analysis
        
        Provides three structured cards:
        1. Key Findings Card - Critical diagnostic information
        2. Root Cause Analysis Card - AI-powered correlation and diagnosis
        3. Troubleshooting Recommendations Card - Step-by-step resolution guide
        """
        from datetime import datetime, timedelta
        import re
        
        # Initialize the three-card structure
        analysis = {
            'key_findings_card': {
                'last_successful_heartbeat': {
                    'timestamp': None,
                    'time_ago': None,
                    'status': 'Not found in logs'
                },
                'communication_method': {
                    'primary_method': 'Unknown',
                    'detected_method': 'Not determined',
                    'ports_detected': [],
                    'protocols_found': []
                },
                'proxy_server_analysis': {
                    'proxy_detected': False,
                    'proxy_details': [],
                    'proxy_issues': []
                },
                'handshake_failures': {
                    'failures_detected': False,
                    'failure_count': 0,
                    'failure_details': []
                },
                'certificate_issues': {
                    'cert_problems_found': False,
                    'cert_issues_count': 0,
                    'cert_problem_details': []
                },
                'network_communication_failures': {
                    'network_failures_found': False,
                    'failure_count': 0,
                    'network_failure_details': []
                },
                'port_failures': {
                    'port_issues_found': False,
                    'failed_ports': [],
                    'listening_failures': [],
                    'receiving_failures': []
                }
            },
            'root_cause_analysis_card': {
                'primary_root_cause': 'Analysis in progress...',
                'contributing_factors': [],
                'severity_assessment': 'Unknown',
                'offline_duration_impact': 'Unknown',
                'correlation_analysis': [],
                'ai_confidence_score': 0
            },
            'troubleshooting_recommendations_card': {
                'immediate_actions': [],
                'diagnostic_steps': [],
                'long_term_solutions': [],
                'monitoring_recommendations': [],
                'escalation_criteria': []
            }
        }
        
        lines = log_content.split('\n')
        current_time = datetime.now()
        
        # CARD 1: ENHANCED KEY FINDINGS ANALYSIS (Deep Security 20.0 Architecture)
        
        # Enhanced Deep Security Event Detection
        ds_events_detected = self._detect_deep_security_events(log_content)
        
        # 1. Find last successful heartbeat (Enhanced with DS 20.0 specifications)
        heartbeat_patterns = [
            r'heartbeat.*success|heartbeat.*sent|heartbeat.*ok',
            r'communication.*restored|back.*online|event.*id.*731',
            r'agent.*online|connection.*established',
            r'event.*id.*731.*back.*online.*communication.*restored',
            r'heartbeat.*manager.*successful|manager.*heartbeat.*ok',
            r'port.*4120.*heartbeat.*success|4120.*communication.*ok',
            r'manager.*reachable|manager.*contact.*successful',
            # Enhanced DS 20.0 heartbeat patterns
            r'agent.*heartbeat.*response.*received|manager.*heartbeat.*response',
            r'port.*4119.*4120.*communication.*success',
            r'ssl.*tls.*handshake.*completed.*successfully',
            r'pki.*certificate.*authentication.*success'
        ]
        
        for line in reversed(lines):  # Start from the end
            for pattern in heartbeat_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    # Extract timestamp from log line
                    timestamp_patterns = [
                        r'(\d{4}-\d{2}-\d{2}[T\s]\d{2}:\d{2}:\d{2})',
                        r'(\d{2}/\d{2}/\d{4}\s\d{2}:\d{2}:\d{2})',
                        r'(\w{3}\s\d{1,2}\s\d{2}:\d{2}:\d{2})'
                    ]
                    
                    for ts_pattern in timestamp_patterns:
                        timestamp_match = re.search(ts_pattern, line)
                        if timestamp_match:
                            try:
                                ts_str = timestamp_match.group(1).replace('T', ' ')
                                # Try different timestamp formats
                                for fmt in ['%Y-%m-%d %H:%M:%S', '%m/%d/%Y %H:%M:%S', '%b %d %H:%M:%S']:
                                    try:
                                        heartbeat_time = datetime.strptime(ts_str, fmt)
                                        if fmt == '%b %d %H:%M:%S':
                                            heartbeat_time = heartbeat_time.replace(year=current_time.year)
                                        
                                        time_diff = current_time - heartbeat_time
                                        analysis['key_findings_card']['last_successful_heartbeat'] = {
                                            'timestamp': ts_str,
                                            'time_ago': f"{time_diff.days} days, {time_diff.seconds//3600} hours, {(time_diff.seconds//60)%60} minutes ago",
                                            'status': 'Found in logs'
                                        }
                                        break
                                    except:
                                        continue
                                break
                            except:
                                continue
            if analysis['key_findings_card']['last_successful_heartbeat']['status'] == 'Found in logs':
                break
        
        # 2. Enhanced Deep Security Network Protocol Analysis (DS 20.0 Architecture)
        ds_network_analysis = self._analyze_ds_network_protocols(log_content)
        analysis['key_findings_card']['communication_method'].update(ds_network_analysis)
        
        # 3. Detect proxy server (Enhanced with DS 20.0 proxy support)
        proxy_patterns = [
            r'proxy.*server|proxy.*host|proxy.*authentication',
            r'http.*proxy|https.*proxy|socks.*proxy|proxy.*config',
            r'proxy.*connect|proxy.*failed|proxy.*error',
            r'proxy.*user|proxy.*password|proxy.*ntlm',
            r'kerberos.*proxy|basic.*authentication.*proxy',
            r'http.*407.*proxy.*authentication.*required',
            r'automatic.*proxy.*detection|per.*agent.*proxy.*settings',
            r'policy.*based.*proxy.*configuration'
        ]
        
        for line in lines:
            for pattern in proxy_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    analysis['key_findings_card']['proxy_server_analysis']['proxy_detected'] = True
                    
                    # Extract proxy details
                    proxy_match = re.search(r'proxy[:\s]*([\w\.-]+)[:\s]*(\d+)?', line, re.IGNORECASE)
                    if proxy_match:
                        proxy_detail = {
                            'host': proxy_match.group(1),
                            'port': proxy_match.group(2) if proxy_match.group(2) else 'unknown',
                            'line': line.strip()[:100] + '...' if len(line.strip()) > 100 else line.strip()
                        }
                        if proxy_detail not in analysis['key_findings_card']['proxy_server_analysis']['proxy_details']:
                            analysis['key_findings_card']['proxy_server_analysis']['proxy_details'].append(proxy_detail)
                    
                    # Check for proxy issues
                    if any(issue in line.lower() for issue in ['failed', 'error', 'timeout', 'denied', 'blocked']):
                        issue_desc = f"Proxy issue detected: {line.strip()[:100]}{'...' if len(line.strip()) > 100 else ''}"
                        if issue_desc not in analysis['key_findings_card']['proxy_server_analysis']['proxy_issues']:
                            analysis['key_findings_card']['proxy_server_analysis']['proxy_issues'].append(issue_desc)
        
        # 4. Detect handshake failures (Enhanced with DS 20.0 TLS/SSL specifications)
        handshake_patterns = [
            r'handshake.*failed|ssl.*handshake.*error|tls.*handshake.*failed',
            r'handshake.*timeout|handshake.*rejected',
            r'ssl.*error|tls.*error|certificate.*handshake',
            r'tls.*1\.2.*handshake.*failed|tls.*1\.3.*handshake.*error',
            r'aes.*encryption.*handshake.*failed',
            r'mutual.*authentication.*handshake.*failed',
            r'pki.*certificate.*handshake.*error',
            r'deep.*security.*manager.*handshake.*failed'
        ]
        
        for line in lines:
            for pattern in handshake_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    analysis['key_findings_card']['handshake_failures']['failures_detected'] = True
                    analysis['key_findings_card']['handshake_failures']['failure_count'] += 1
                    failure_detail = f"{self._extract_timestamp(line) or 'Unknown time'}: {line.strip()[:100]}{'...' if len(line.strip()) > 100 else ''}"
                    if failure_detail not in analysis['key_findings_card']['handshake_failures']['failure_details']:
                        analysis['key_findings_card']['handshake_failures']['failure_details'].append(failure_detail)
        
        # 5. Detect certificate issues (Enhanced with DS 20.0 PKI specifications)
        cert_patterns = [
            r'certificate.*expired|certificate.*invalid|certificate.*error',
            r'certificate.*not.*trusted|certificate.*validation.*failed',
            r'cert.*expired|cert.*invalid|cert.*error',
            r'event.*id.*930.*certificate.*accepted|event.*id.*931.*certificate.*deleted',
            r'pki.*certificate.*authentication.*failed',
            r'certificate.*chain.*verification.*failed',
            r'certificate.*revocation.*checking.*failed',
            r'root.*ca.*certificate.*invalid',
            r'agent.*identity.*certificate.*error',
            r'manager.*server.*certificate.*invalid',
            r'time.*synchronization.*certificate.*validation.*failed'
        ]
        
        for line in lines:
            for pattern in cert_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    analysis['key_findings_card']['certificate_issues']['cert_problems_found'] = True
                    analysis['key_findings_card']['certificate_issues']['cert_issues_count'] += 1
                    cert_detail = f"{self._extract_timestamp(line) or 'Unknown time'}: {line.strip()[:100]}{'...' if len(line.strip()) > 100 else ''}"
                    if cert_detail not in analysis['key_findings_card']['certificate_issues']['cert_problem_details']:
                        analysis['key_findings_card']['certificate_issues']['cert_problem_details'].append(cert_detail)
        
        # 6. Detect network communication failures (Enhanced with DS 20.0 event IDs)
        network_failure_patterns = [
            r'connection.*failed|network.*error|network.*timeout',
            r'cannot.*connect|connection.*refused|network.*unreachable',
            r'timeout.*connecting|connection.*timeout|host.*unreachable',
            r'event.*id.*4011.*failure.*to.*contact.*manager',
            r'event.*id.*4012.*heartbeat.*failed',
            r'event.*id.*730.*offline.*manager.*cannot.*communicate',
            r'event.*id.*742.*communication.*problem.*detected',
            r'event.*id.*770.*agent.*heartbeat.*rejected',
            r'event.*id.*771.*contact.*by.*unrecognized.*client',
            r'deep.*security.*manager.*unreachable',
            r'dns.*resolution.*failure.*deep.*security',
            r'firewall.*blocking.*deep.*security.*communication'
        ]
        
        for line in lines:
            for pattern in network_failure_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    analysis['key_findings_card']['network_communication_failures']['network_failures_found'] = True
                    analysis['key_findings_card']['network_communication_failures']['failure_count'] += 1
                    network_detail = f"{self._extract_timestamp(line) or 'Unknown time'}: {line.strip()[:100]}{'...' if len(line.strip()) > 100 else ''}"
                    if network_detail not in analysis['key_findings_card']['network_communication_failures']['network_failure_details']:
                        analysis['key_findings_card']['network_communication_failures']['network_failure_details'].append(network_detail)
        
        # 7. Detect port failures (Enhanced with DS 20.0 communication ports)
        port_failure_patterns = [
            r'port.*\d+.*failed|port.*\d+.*blocked|port.*\d+.*refused',
            r'listening.*failed|receiving.*failed|bind.*failed',
            r'cannot.*listen.*port|failed.*bind.*port',
            r'port.*4119.*blocked.*agent.*to.*manager',
            r'port.*4120.*blocked.*manager.*to.*agent',
            r'port.*4122.*blocked.*relay.*server',
            r'port.*443.*blocked.*smart.*protection.*network',
            r'firewall.*blocking.*port.*4119|firewall.*blocking.*port.*4120',
            r'deep.*security.*port.*accessibility.*failed'
        ]
        
        for line in lines:
            for pattern in port_failure_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    analysis['key_findings_card']['port_failures']['port_issues_found'] = True
                    
                    # Extract port number
                    port_match = re.search(r'port[:\s]*(\d+)', line, re.IGNORECASE)
                    if port_match:
                        port_num = port_match.group(1)
                        if port_num not in analysis['key_findings_card']['port_failures']['failed_ports']:
                            analysis['key_findings_card']['port_failures']['failed_ports'].append(port_num)
                    
                    # Categorize failure type
                    if 'listening' in line.lower() or 'bind' in line.lower():
                        listening_detail = f"{self._extract_timestamp(line) or 'Unknown time'}: {line.strip()[:100]}{'...' if len(line.strip()) > 100 else ''}"
                        if listening_detail not in analysis['key_findings_card']['port_failures']['listening_failures']:
                            analysis['key_findings_card']['port_failures']['listening_failures'].append(listening_detail)
                    elif 'receiving' in line.lower() or 'blocked' in line.lower():
                        receiving_detail = f"{self._extract_timestamp(line) or 'Unknown time'}: {line.strip()[:100]}{'...' if len(line.strip()) > 100 else ''}"
                        if receiving_detail not in analysis['key_findings_card']['port_failures']['receiving_failures']:
                            analysis['key_findings_card']['port_failures']['receiving_failures'].append(receiving_detail)
        
        # CARD 2: ROOT CAUSE ANALYSIS (AI-Powered)
        self._populate_root_cause_analysis_card(analysis, log_content)
        
        # CARD 3: TROUBLESHOOTING RECOMMENDATIONS (Step-by-step guidance)
        self._populate_troubleshooting_recommendations_card(analysis)
        
        # ENHANCED ANALYSIS: Apply Deep Security event intelligence
        self._enhance_analysis_with_ds_events(analysis, ds_events_detected)
        
        return analysis
    
    def _detect_deep_security_events(self, log_content: str) -> Dict[str, Any]:
        """Detect specific Deep Security events based on JSON specifications"""
        detected_events = {
            'communication_events': [],
            'authentication_events': [],
            'service_events': [],
            'communication_specific_events': [],
            'critical_patterns': [],
            'event_timeline': []
        }
        
        lines = log_content.split('\n')
        
        # Combine all event mappings for comprehensive detection
        all_events = {
            **self.communication_events,
            **self.authentication_events, 
            **self.service_events,
            **self.communication_specific_events
        }
        
        for i, line in enumerate(lines):
            line_lower = line.lower()
            
            # Event ID detection
            event_id_pattern = r'event\s*id[:\s]*(\d+)|id[:\s]*(\d+)'
            event_match = re.search(event_id_pattern, line_lower)
            
            if event_match:
                event_id = int(event_match.group(1) or event_match.group(2))
                
                if event_id in all_events:
                    event_info = all_events[event_id].copy()
                    event_info.update({
                        'event_id': event_id,
                        'line_number': i + 1,
                        'log_content': line.strip(),
                        'timestamp': self._extract_timestamp_from_line(line)
                    })
                    
                    # Categorize event
                    if event_id in self.communication_events:
                        detected_events['communication_events'].append(event_info)
                    elif event_id in self.authentication_events:
                        detected_events['authentication_events'].append(event_info)
                    elif event_id in self.service_events:
                        detected_events['service_events'].append(event_info)
                    elif event_id in self.communication_specific_events:
                        detected_events['communication_specific_events'].append(event_info)
                    
                    detected_events['event_timeline'].append(event_info)
            
            # Pattern-based detection for additional intelligence
            critical_patterns = {
                'dns_resolution_failure': r'dns.*resolution.*fail|nslookup.*fail|hostname.*resolution.*error',
                'firewall_blocking': r'connection.*timeout|port.*blocked|firewall.*block',
                'certificate_expiration': r'certificate.*expir|cert.*expir|ssl.*certificate.*invalid',
                'time_synchronization': r'time.*sync.*fail|clock.*drift|time.*difference',
                'proxy_authentication': r'proxy.*auth.*fail|407.*proxy.*auth|proxy.*credential',
                'manager_unreachable': r'manager.*unreachable|cannot.*contact.*manager|manager.*timeout',
                'service_crash': r'service.*crash|process.*terminated|unexpected.*exit',
                'insufficient_resources': r'insufficient.*memory|disk.*space.*low|resource.*exhausted',
                'network_connectivity': r'network.*unreachable|connection.*refused|network.*timeout',
                'ssl_handshake_failure': r'ssl.*handshake.*fail|tls.*handshake.*fail|certificate.*validation.*fail'
            }
            
            for pattern_name, pattern in critical_patterns.items():
                if re.search(pattern, line_lower):
                    detected_events['critical_patterns'].append({
                        'pattern_type': pattern_name,
                        'line_number': i + 1,
                        'content': line.strip(),
                        'severity': self._get_pattern_severity(pattern_name)
                    })
        
        # Sort timeline by line number
        detected_events['event_timeline'].sort(key=lambda x: x['line_number'])
        
        return detected_events
    
    def _extract_timestamp_from_line(self, line: str) -> str:
        """Extract timestamp from log line"""
        timestamp_patterns = [
            r'(\d{4}-\d{2}-\d{2}[T\s]\d{2}:\d{2}:\d{2})',
            r'(\d{2}/\d{2}/\d{4}\s\d{2}:\d{2}:\d{2})',
            r'(\w{3}\s\d{1,2}\s\d{2}:\d{2}:\d{2})'
        ]
        
        for pattern in timestamp_patterns:
            match = re.search(pattern, line)
            if match:
                return match.group(1)
        return 'Unknown'
    
    def _get_pattern_severity(self, pattern_name: str) -> str:
        """Get severity level for detected patterns"""
        severity_mapping = {
            'dns_resolution_failure': 'high',
            'firewall_blocking': 'high', 
            'certificate_expiration': 'critical',
            'time_synchronization': 'high',
            'proxy_authentication': 'medium',
            'manager_unreachable': 'critical',
            'service_crash': 'critical',
            'insufficient_resources': 'high',
            'network_connectivity': 'high',
            'ssl_handshake_failure': 'high'
        }
        return severity_mapping.get(pattern_name, 'medium')
    
    def _enhance_analysis_with_ds_events(self, analysis: Dict[str, Any], ds_events: Dict[str, Any]):
        """Enhance key findings analysis with Deep Security event intelligence"""
        
        # Enhance communication failures detection
        comm_events = ds_events['communication_events']
        if any(event['event_id'] in [730, 742, 4011, 4012] for event in comm_events):
            analysis['key_findings_card']['network_communication_failures']['network_failures_found'] = True
            analysis['key_findings_card']['network_communication_failures']['failure_count'] = len([
                e for e in comm_events if e['event_id'] in [730, 742, 4011, 4012]
            ])
            analysis['key_findings_card']['network_communication_failures']['network_failure_details'] = [
                f"Event ID {event['event_id']}: {event['description']} (Line {event['line_number']})"
                for event in comm_events if event['event_id'] in [730, 742, 4011, 4012]
            ]
        
        # Enhance certificate issues detection
        auth_events = ds_events['authentication_events']
        if any(event['event_id'] in [931, 734] for event in auth_events):
            analysis['key_findings_card']['certificate_issues']['cert_problems_found'] = True
            analysis['key_findings_card']['certificate_issues']['cert_issues_count'] = len([
                e for e in auth_events if e['event_id'] in [931, 734]
            ])
            analysis['key_findings_card']['certificate_issues']['cert_problem_details'] = [
                f"Event ID {event['event_id']}: {event['description']} (Line {event['line_number']})"
                for event in auth_events if event['event_id'] in [931, 734]
            ]
        
        # Enhance handshake failures detection with critical patterns
        ssl_failures = [p for p in ds_events['critical_patterns'] if p['pattern_type'] == 'ssl_handshake_failure']
        if ssl_failures:
            analysis['key_findings_card']['handshake_failures']['failures_detected'] = True
            analysis['key_findings_card']['handshake_failures']['failure_count'] = len(ssl_failures)
            analysis['key_findings_card']['handshake_failures']['failure_details'] = [
                f"SSL/TLS handshake failure detected (Line {failure['line_number']}): {failure['content'][:100]}..."
                for failure in ssl_failures
            ]
        
        # Enhance port failures detection
        port_issues = [p for p in ds_events['critical_patterns'] if p['pattern_type'] in ['firewall_blocking', 'network_connectivity']]
        if port_issues:
            analysis['key_findings_card']['port_failures']['port_issues_found'] = True
            # Determine affected ports based on Deep Security architecture
            affected_ports = ['4119', '4120', '4122', '443']  # Core DS ports
            analysis['key_findings_card']['port_failures']['failed_ports'] = affected_ports
            analysis['key_findings_card']['port_failures']['listening_failures'] = [
                f"Port connectivity issue detected (Line {issue['line_number']})"
                for issue in port_issues
            ]
        
        # Enhance proxy analysis
        proxy_issues = [p for p in ds_events['critical_patterns'] if p['pattern_type'] == 'proxy_authentication']
        if proxy_issues:
            analysis['key_findings_card']['proxy_server_analysis']['proxy_detected'] = True
            analysis['key_findings_card']['proxy_server_analysis']['proxy_issues'] = [
                f"Proxy authentication issue (Line {issue['line_number']}): {issue['content'][:100]}..."
                for issue in proxy_issues
            ]
    
    def _analyze_ds_network_protocols(self, log_content: str) -> Dict[str, Any]:
        """Comprehensive Deep Security Network Protocol Analysis (JSON specifications)"""
        network_analysis = {
            'primary_method': 'Communication method not clearly detected from logs',
            'detected_method': 'Not determined',
            'ports_detected': [],
            'protocols_found': [],
            'communication_flows': [],
            'network_architecture': 'Unknown',
            'tls_version_detected': [],
            'certificate_validation': 'Not detected',
            'bandwidth_indicators': [],
            'cloud_service_endpoints': []
        }
        
        lines = log_content.split('\n')
        
        # Enhanced Deep Security Port Analysis (JSON reference)
        ds_port_mapping = {
            '4119': {
                'description': 'Agent-to-Manager Primary Communication (Outbound)',
                'protocol': 'HTTPS',
                'purpose': 'Primary agent to manager communication', 
                'direction': 'Outbound from DS Agent',
                'authentication': 'SSL/TLS mutual authentication with PKI certificates',
                'data_types': ['agent_heartbeat', 'security_events', 'system_status', 'audit_logs'],
                'frequency': 'Configurable, default 10 minutes'
            },
            '4120': {
                'description': 'Manager-to-Agent Heartbeat & Policy Distribution (Inbound)',
                'protocol': 'HTTPS',
                'purpose': 'Manager to agent heartbeat and policy distribution',
                'direction': 'Inbound to DS Agent',
                'authentication': 'SSL/TLS mutual authentication with PKI certificates',
                'data_types': ['security_policy_updates', 'configuration_changes', 'management_commands'],
                'trigger': 'Policy changes or scheduled updates'
            },
            '4122': {
                'description': 'Deep Security Relay Server Communication',
                'protocol': 'HTTPS', 
                'purpose': 'Deep Security Relay server communication',
                'direction': 'Bidirectional',
                'authentication': 'SSL/TLS mutual authentication',
                'benefits': 'Reduces bandwidth to external Trend Micro servers',
                'data_types': ['security_pattern_distribution', 'policy_relay', 'update_packages']
            },
            '443': {
                'description': 'Smart Protection Network & Cloud Services',
                'protocol': 'HTTPS',
                'purpose': 'Smart Protection Network and Cloud Services',
                'endpoints': ['*.icrc.trendmicro.com', 'ds20*.icrc.trendmicro.com', 'deepsec20-*.gfrbridge.trendmicro.com'],
                'services': ['file_reputation', 'threat_intelligence', 'smart_scan', 'predictive_ml'],
                'cloud_integration': 'Cloud One Workload Security'
            }
        }
        
        # Detect ports and protocols with enhanced context
        for line in lines:
            line_lower = line.lower()
            
            # Port detection with Deep Security context
            for port, port_info in ds_port_mapping.items():
                port_patterns = [
                    rf'port[:\s]*{port}',
                    rf':{port}[/\s]',
                    rf'port.*{port}',
                    rf'{port}.*port'
                ]
                
                for pattern in port_patterns:
                    if re.search(pattern, line_lower):
                        # Check if already detected
                        if not any(p['port'] == port for p in network_analysis['ports_detected']):
                            port_entry = port_info.copy()
                            port_entry['port'] = port
                            port_entry['detected_in_line'] = line.strip()
                            network_analysis['ports_detected'].append(port_entry)
                            
                            # Add communication flow
                            network_analysis['communication_flows'].append({
                                'port': port,
                                'direction': port_info['direction'],
                                'purpose': port_info['purpose'],
                                'protocol': port_info['protocol']
                            })
                        break
            
            # Enhanced Protocol Detection
            protocol_patterns = {
                'HTTPS': r'https|ssl.*3|tls.*1\.[2-3]',
                'TLS_1.2': r'tls.*1\.2|tlsv1\.2',
                'TLS_1.3': r'tls.*1\.3|tlsv1\.3',
                'SSL': r'ssl[^v]|ssl.*3',
                'TCP': r'tcp[^/]',
                'HTTP': r'http[^s]'
            }
            
            for protocol, pattern in protocol_patterns.items():
                if re.search(pattern, line_lower) and protocol not in network_analysis['protocols_found']:
                    network_analysis['protocols_found'].append(protocol)
                    
                    # Detect TLS versions specifically
                    if protocol in ['TLS_1.2', 'TLS_1.3']:
                        network_analysis['tls_version_detected'].append(protocol)
            
            # Certificate validation detection
            cert_validation_patterns = [
                r'certificate.*valid|cert.*valid|ssl.*certificate.*ok',
                r'pki.*authentication.*success|mutual.*auth.*success',
                r'certificate.*chain.*valid|cert.*chain.*ok'
            ]
            
            for pattern in cert_validation_patterns:
                if re.search(pattern, line_lower):
                    network_analysis['certificate_validation'] = 'Certificate validation detected'
                    break
            
            # Cloud service endpoint detection
            cloud_endpoints = [
                r'\*\.icrc\.trendmicro\.com',
                r'ds20.*\.icrc\.trendmicro\.com',
                r'deepsec20-.*\.gfrbridge\.trendmicro\.com',
                r'\*\.workload\.trendmicro\.com',
                r'\*\.xdr\.trendmicro\.com',
                r'ds20-.*-.*\.trx\.trendmicro\.com'
            ]
            
            for endpoint_pattern in cloud_endpoints:
                if re.search(endpoint_pattern, line_lower):
                    if endpoint_pattern not in network_analysis['cloud_service_endpoints']:
                        network_analysis['cloud_service_endpoints'].append(endpoint_pattern)
            
            # Communication method detection
            comm_method_patterns = {
                'Agent Initiated Communication (AIC)': r'aic.*mode|agent.*initiated.*communication',
                'Manager Initiated Communication (MIC)': r'mic.*mode|manager.*initiated.*communication', 
                'Bi-directional Communication': r'bidirectional.*mode|bi.*directional.*communication'
            }
            
            for method, pattern in comm_method_patterns.items():
                if re.search(pattern, line_lower):
                    network_analysis['detected_method'] = method
                    break
            
            # Bandwidth and performance indicators
            bandwidth_patterns = [
                r'bandwidth.*(\d+).*kbps|(\d+).*kbps.*bandwidth',
                r'network.*latency.*(\d+).*ms',
                r'packet.*loss.*(\d+).*%',
                r'throughput.*(\d+).*mbps'
            ]
            
            for pattern in bandwidth_patterns:
                match = re.search(pattern, line_lower)
                if match:
                    network_analysis['bandwidth_indicators'].append(line.strip())
        
        # Determine primary communication method based on detected ports
        detected_ports = [p['port'] for p in network_analysis['ports_detected']]
        
        if '4120' in detected_ports:
            network_analysis['primary_method'] = 'Manager-to-Agent Heartbeat (Port 4120/HTTPS)'
            network_analysis['network_architecture'] = 'Manager Initiated Communication'
        elif '4119' in detected_ports:
            network_analysis['primary_method'] = 'Agent-to-Manager Communication (Port 4119/HTTPS)'
            network_analysis['network_architecture'] = 'Agent Initiated Communication'
        elif '4122' in detected_ports:
            network_analysis['primary_method'] = 'Relay Server Communication (Port 4122/HTTPS)'
            network_analysis['network_architecture'] = 'Relay Server Architecture'
        elif '443' in detected_ports:
            network_analysis['primary_method'] = 'Smart Protection Network (Port 443/HTTPS)'
            network_analysis['network_architecture'] = 'Cloud-Enhanced Protection'
        
        # Determine overall network architecture
        if len(detected_ports) > 2:
            network_analysis['network_architecture'] = 'Hybrid Deep Security Architecture'
        elif any(endpoint in str(network_analysis['cloud_service_endpoints']) for endpoint in ['workload.trendmicro.com', 'xdr.trendmicro.com']):
            network_analysis['network_architecture'] = 'Cloud One Workload Security / Vision One XDR'
        
        return network_analysis
    
    def _analyze_pki_certificate_issues(self, log_content: str, cert_issues: Dict[str, Any]) -> Dict[str, Any]:
        """Comprehensive PKI Certificate Analysis for Deep Security (JSON specifications)"""
        pki_analysis = {
            'certificate_validation_status': 'Unknown',
            'time_synchronization_status': 'Unknown',
            'certificate_chain_status': 'Unknown',
            'certificate_expiration_status': 'Unknown',
            'root_ca_validation': 'Unknown',
            'contributing_factors': [],
            'specific_issues': [],
            'resolution_complexity': 'Unknown',
            'security_impact': 'Unknown'
        }
        
        lines = log_content.split('\n')
        
        # Deep Security PKI Certificate Patterns (JSON reference)
        certificate_patterns = {
            'certificate_expiration': {
                'patterns': [
                    r'certificate.*expir|cert.*expir|certificate.*invalid.*date',
                    r'ssl.*certificate.*expir|tls.*certificate.*expir',
                    r'certificate.*not.*valid.*time|cert.*validity.*period',
                    r'certificate.*expired.*on|cert.*expiration.*date'
                ],
                'severity': 'critical',
                'root_cause': 'Certificate expiration preventing authentication',
                'resolution': 'Certificate renewal required'
            },
            'time_synchronization_issues': {
                'patterns': [
                    r'time.*sync.*fail|clock.*drift|time.*difference.*exceed',
                    r'system.*time.*incorrect|ntp.*sync.*fail|time.*server.*unreachable',
                    r'certificate.*validation.*fail.*time|time.*skew.*detected',
                    r'event.*id.*734.*time.*synchronization'
                ],
                'severity': 'high',
                'root_cause': 'Time synchronization drift affecting certificate validation',
                'resolution': 'NTP synchronization and time zone verification'
            },
            'certificate_chain_validation': {
                'patterns': [
                    r'certificate.*chain.*invalid|cert.*chain.*fail|chain.*validation.*error',
                    r'intermediate.*certificate.*missing|ca.*certificate.*not.*found',
                    r'certificate.*authority.*invalid|root.*ca.*not.*trusted',
                    r'certificate.*path.*validation.*fail'
                ],
                'severity': 'high',
                'root_cause': 'Certificate chain validation failure',
                'resolution': 'Certificate chain reconstruction or CA trust establishment'
            },
            'certificate_revocation': {
                'patterns': [
                    r'certificate.*revok|cert.*revok|crl.*check.*fail',
                    r'ocsp.*validation.*fail|certificate.*status.*invalid',
                    r'revocation.*check.*timeout|crl.*download.*fail'
                ],
                'severity': 'high',
                'root_cause': 'Certificate revocation status validation failure',
                'resolution': 'Certificate replacement or CRL/OCSP configuration'
            },
            'mutual_authentication_failure': {
                'patterns': [
                    r'mutual.*auth.*fail|client.*certificate.*required|authentication.*handshake.*fail',
                    r'certificate.*not.*present|client.*cert.*missing|ssl.*mutual.*auth.*error'
                ],
                'severity': 'critical',
                'root_cause': 'Mutual SSL/TLS authentication failure',
                'resolution': 'Client certificate installation and configuration'
            },
            'certificate_mismatch': {
                'patterns': [
                    r'certificate.*mismatch|hostname.*verification.*fail|certificate.*name.*invalid',
                    r'subject.*alternative.*name.*mismatch|cn.*mismatch|certificate.*hostname.*error'
                ],
                'severity': 'medium',
                'root_cause': 'Certificate subject/hostname mismatch',
                'resolution': 'Certificate re-issuance with correct subject names'
            }
        }
        
        # Analyze certificate issues in log content
        detected_issues = []
        for issue_type, issue_info in certificate_patterns.items():
            for pattern in issue_info['patterns']:
                matches = []
                for i, line in enumerate(lines):
                    if re.search(pattern, line, re.IGNORECASE):
                        matches.append({
                            'line_number': i + 1,
                            'content': line.strip(),
                            'pattern_type': issue_type
                        })
                
                if matches:
                    detected_issues.append({
                        'issue_type': issue_type,
                        'severity': issue_info['severity'],
                        'root_cause': issue_info['root_cause'],
                        'resolution': issue_info['resolution'],
                        'occurrences': len(matches),
                        'sample_lines': matches[:3]  # Top 3 matches
                    })
        
        # Analyze specific PKI infrastructure components
        if detected_issues:
            # Determine primary certificate issue
            critical_issues = [issue for issue in detected_issues if issue['severity'] == 'critical']
            high_issues = [issue for issue in detected_issues if issue['severity'] == 'high']
            
            if critical_issues:
                primary_issue = critical_issues[0]
                pki_analysis['resolution_complexity'] = 'High - Critical certificate infrastructure issue'
                pki_analysis['security_impact'] = 'Critical - Authentication system compromised'
            elif high_issues:
                primary_issue = high_issues[0]
                pki_analysis['resolution_complexity'] = 'Medium - Certificate configuration issue'
                pki_analysis['security_impact'] = 'High - Authentication reliability affected'
            else:
                primary_issue = detected_issues[0]
                pki_analysis['resolution_complexity'] = 'Low - Minor certificate issue'
                pki_analysis['security_impact'] = 'Medium - Potential authentication issues'
        
        # Certificate validation status analysis
        cert_validation_patterns = [
            r'certificate.*valid|cert.*valid|certificate.*ok|pki.*auth.*success',
            r'ssl.*certificate.*accepted|tls.*certificate.*verified|certificate.*chain.*valid'
        ]
        
        cert_validation_detected = False
        for pattern in cert_validation_patterns:
            if any(re.search(pattern, line, re.IGNORECASE) for line in lines):
                cert_validation_detected = True
                break
        
        if cert_validation_detected:
            pki_analysis['certificate_validation_status'] = 'Certificate validation successful detected'
        elif detected_issues:
            pki_analysis['certificate_validation_status'] = 'Certificate validation failures detected'
        else:
            pki_analysis['certificate_validation_status'] = 'No certificate validation events detected'
        
        # Time synchronization analysis
        time_sync_patterns = [
            r'ntp.*sync.*success|time.*sync.*ok|clock.*synchronized',
            r'system.*time.*correct|time.*server.*reachable'
        ]
        
        time_sync_success = any(
            re.search(pattern, line, re.IGNORECASE) 
            for pattern in time_sync_patterns 
            for line in lines
        )
        
        if time_sync_success:
            pki_analysis['time_synchronization_status'] = 'Time synchronization successful'
        elif any(issue['issue_type'] == 'time_synchronization_issues' for issue in detected_issues):
            pki_analysis['time_synchronization_status'] = 'Time synchronization failures detected'
        else:
            pki_analysis['time_synchronization_status'] = 'Time synchronization status unknown'
        
        # Generate contributing factors for root cause analysis
        pki_analysis['contributing_factors'] = []
        
        for issue in detected_issues:
            if issue['severity'] == 'critical':
                pki_analysis['contributing_factors'].append(f"PKI {issue['root_cause']} (critical impact)")
            elif issue['severity'] == 'high':
                pki_analysis['contributing_factors'].append(f"PKI {issue['root_cause']} (high impact)")
            else:
                pki_analysis['contributing_factors'].append(f"PKI {issue['root_cause']} (medium impact)")
        
        # Store specific issues for detailed analysis
        pki_analysis['specific_issues'] = detected_issues
        
        return pki_analysis
    
    def _populate_root_cause_analysis_card(self, analysis: Dict[str, Any], log_content: str):
        """Populate the AI-powered root cause analysis card"""
        import re
        
        key_findings = analysis['key_findings_card']
        root_cause_card = analysis['root_cause_analysis_card']
        
        # Analyze issues and correlation
        issues_detected = []
        contributing_factors = []
        
        # Check each key finding
        if key_findings['last_successful_heartbeat']['status'] == 'Not found in logs':
            issues_detected.append("No successful heartbeat communication detected")
            contributing_factors.append("Agent-Manager heartbeat failure (critical)")
        
        if key_findings['network_communication_failures']['network_failures_found']:
            issues_detected.append(f"Network failures detected ({key_findings['network_communication_failures']['failure_count']} events)")
            contributing_factors.append("Network infrastructure issues (high impact)")
        
        if key_findings['certificate_issues']['cert_problems_found']:
            # Enhanced PKI Certificate Analysis
            pki_analysis = self._analyze_pki_certificate_issues(log_content, key_findings['certificate_issues'])
            issues_detected.append(f"PKI Certificate issues detected ({key_findings['certificate_issues']['cert_issues_count']} events)")
            contributing_factors.extend(pki_analysis['contributing_factors'])
        
        if key_findings['handshake_failures']['failures_detected']:
            issues_detected.append(f"SSL/TLS handshake failures ({key_findings['handshake_failures']['failure_count']} events)")
            contributing_factors.append("Cryptographic communication issues (high impact)")
        
        if key_findings['port_failures']['port_issues_found']:
            issues_detected.append(f"Port accessibility issues on ports: {', '.join(key_findings['port_failures']['failed_ports'])}")
            contributing_factors.append("Firewall or service binding problems (medium impact)")
        
        if key_findings['proxy_server_analysis']['proxy_detected']:
            if key_findings['proxy_server_analysis']['proxy_issues']:
                issues_detected.append("Proxy server configuration issues detected")
                contributing_factors.append("Proxy authentication or connectivity problems (medium impact)")
            else:
                contributing_factors.append("Proxy server present but functioning normally (low impact)")
        
        # Enhanced AMSP Platform Dependencies Analysis
        amsp_analysis = self._analyze_amsp_platform_dependencies(log_content)
        if amsp_analysis['platform_integration_issues']:
            for issue in amsp_analysis['platform_integration_issues']:
                issues_detected.append(f"AMSP Platform Issue: {issue['description']}")
                impact_level = "high impact" if issue['severity'] == 'high' else "medium impact"
                contributing_factors.append(f"{issue['issue_type']} ({impact_level})")
        
        # Add AMSP service status to analysis
        amsp_service_issues = []
        for service_name, status in amsp_analysis['amsp_service_status'].items():
            if not status['service_running'] and status['service_detected']:
                amsp_service_issues.append(f"{service_name} not running")
            if status['dependency_issues']:
                amsp_service_issues.append(f"{service_name} dependency issues")
            if status['error_patterns']:
                amsp_service_issues.append(f"{service_name} error patterns detected")
        
        if amsp_service_issues:
            issues_detected.append(f"AMSP Service Issues: {', '.join(amsp_service_issues)}")
            contributing_factors.append("Deep Security service integration problems (high impact)")
        
        # Enhanced Proxy Configuration Intelligence Analysis
        proxy_intelligence = self._analyze_proxy_configuration_intelligence(log_content)
        
        # Analyze proxy issues and add to root cause analysis
        if proxy_intelligence['authentication_analysis']['http_407_errors_detected']:
            issues_detected.append(f"HTTP 407 Proxy Authentication Errors ({proxy_intelligence['authentication_analysis']['authentication_failures']} events)")
            contributing_factors.append("Proxy authentication failure preventing network access (high impact)")
        
        # Add proxy connection errors
        proxy_errors = proxy_intelligence['proxy_errors']
        if proxy_errors['connection_errors']['error_count'] > 0:
            issues_detected.append(f"Proxy Connection Failures ({proxy_errors['connection_errors']['error_count']} events)")
            contributing_factors.append("Proxy server connectivity issues (high impact)")
        
        if proxy_errors['configuration_errors']['error_count'] > 0:
            issues_detected.append(f"Proxy Configuration Errors ({proxy_errors['configuration_errors']['error_count']} events)")
            contributing_factors.append("Proxy configuration problems (medium impact)")
        
        if proxy_errors['ssl_tls_errors']['error_count'] > 0:
            issues_detected.append(f"Proxy SSL/TLS Errors ({proxy_errors['ssl_tls_errors']['error_count']} events)")
            contributing_factors.append("Proxy SSL tunnel failures (high impact)")
        
        # Add proxy intelligence recommendations to analysis
        if proxy_intelligence['troubleshooting_recommendations']:
            high_priority_proxy_issues = [rec for rec in proxy_intelligence['troubleshooting_recommendations'] if rec['priority'] == 'high']
            if high_priority_proxy_issues:
                issues_detected.append(f"Critical Proxy Issues: {len(high_priority_proxy_issues)} high-priority configuration problems")
                contributing_factors.append("Critical proxy configuration requiring immediate attention (high impact)")
        
        # Determine primary root cause using AI correlation
        if "No successful heartbeat" in str(issues_detected) and "Network failures" in str(issues_detected):
            root_cause_card['primary_root_cause'] = "Complete communication breakdown between DS Agent and Manager due to network infrastructure failure"
            root_cause_card['severity_assessment'] = "Critical - Agent completely offline"
            root_cause_card['ai_confidence_score'] = 95
        elif "Certificate problems" in str(issues_detected) and "handshake failures" in str(issues_detected):
            root_cause_card['primary_root_cause'] = "PKI certificate authentication failure preventing secure communication"
            root_cause_card['severity_assessment'] = "High - Authentication system compromised"
            root_cause_card['ai_confidence_score'] = 88
        elif "Network failures" in str(issues_detected):
            root_cause_card['primary_root_cause'] = "Network connectivity issues preventing DS Agent communication"
            root_cause_card['severity_assessment'] = "High - Network infrastructure problems"
            root_cause_card['ai_confidence_score'] = 82
        elif "No successful heartbeat" in str(issues_detected):
            root_cause_card['primary_root_cause'] = "DS Agent heartbeat communication failure - Agent may be offline"
            root_cause_card['severity_assessment'] = "Critical - Agent status unknown"
            root_cause_card['ai_confidence_score'] = 75
        elif "AMSP Platform Issue" in str(issues_detected) and "AMSP Service Issues" in str(issues_detected):
            root_cause_card['primary_root_cause'] = "AMSP platform integration failure - Deep Security service dependencies compromised"
            root_cause_card['severity_assessment'] = "Critical - Core platform services failed"
            root_cause_card['ai_confidence_score'] = 90
        elif "AMSP Service Issues" in str(issues_detected):
            root_cause_card['primary_root_cause'] = "Deep Security service integration problems - AMSP platform service issues"
            root_cause_card['severity_assessment'] = "High - Service dependency problems"
            root_cause_card['ai_confidence_score'] = 85
        elif "AMSP Platform Issue" in str(issues_detected):
            root_cause_card['primary_root_cause'] = "AMSP platform initialization or module loading issues"
            root_cause_card['severity_assessment'] = "High - Platform integration problems"
            root_cause_card['ai_confidence_score'] = 80
        elif "HTTP 407 Proxy Authentication" in str(issues_detected):
            root_cause_card['primary_root_cause'] = "Proxy authentication failure - HTTP 407 errors preventing network access"
            root_cause_card['severity_assessment'] = "High - Proxy authentication system failure"
            root_cause_card['ai_confidence_score'] = 87
        elif "Proxy Connection Failures" in str(issues_detected) and "Critical Proxy Issues" in str(issues_detected):
            root_cause_card['primary_root_cause'] = "Complete proxy infrastructure failure - Multiple proxy configuration and connectivity issues"
            root_cause_card['severity_assessment'] = "Critical - Proxy system completely non-functional"
            root_cause_card['ai_confidence_score'] = 92
        elif "Proxy Connection Failures" in str(issues_detected):
            root_cause_card['primary_root_cause'] = "Proxy server connectivity failure preventing network communication"
            root_cause_card['severity_assessment'] = "High - Proxy infrastructure problems"
            root_cause_card['ai_confidence_score'] = 84
        elif "Proxy SSL/TLS Errors" in str(issues_detected):
            root_cause_card['primary_root_cause'] = "Proxy SSL/TLS tunnel failures - Encrypted communication through proxy compromised"
            root_cause_card['severity_assessment'] = "High - Proxy security tunnel problems"
            root_cause_card['ai_confidence_score'] = 83
        elif "Proxy Configuration Errors" in str(issues_detected) or "Critical Proxy Issues" in str(issues_detected):
            root_cause_card['primary_root_cause'] = "Proxy configuration problems - Invalid proxy settings preventing network access"
            root_cause_card['severity_assessment'] = "Medium - Proxy configuration issues"
            root_cause_card['ai_confidence_score'] = 78
        elif "Port accessibility" in str(issues_detected):
            root_cause_card['primary_root_cause'] = "Port accessibility issues - Firewall or service configuration problems"
            root_cause_card['severity_assessment'] = "Medium - Configuration issues"
            root_cause_card['ai_confidence_score'] = 70
        else:
            root_cause_card['primary_root_cause'] = "Communication patterns appear normal - Review logs for intermittent issues"
            root_cause_card['severity_assessment'] = "Low - Monitoring recommended"
            root_cause_card['ai_confidence_score'] = 60
        
        # Calculate offline duration impact
        heartbeat_info = key_findings['last_successful_heartbeat']
        if heartbeat_info['time_ago'] and 'days' in heartbeat_info['time_ago']:
            days_match = re.search(r'(\d+) days', heartbeat_info['time_ago'])
            if days_match and int(days_match.group(1)) > 1:
                root_cause_card['offline_duration_impact'] = f"Extended offline period ({heartbeat_info['time_ago']}) - High security risk"
            else:
                root_cause_card['offline_duration_impact'] = f"Recent offline event ({heartbeat_info['time_ago']}) - Moderate impact"
        else:
            root_cause_card['offline_duration_impact'] = "Cannot determine offline duration from available logs"
        
        # Set correlation analysis
        root_cause_card['contributing_factors'] = contributing_factors
        root_cause_card['issues_detected'] = issues_detected
        root_cause_card['root_causes'] = issues_detected  # For backward compatibility
        root_cause_card['correlation_analysis'] = [
            f"Total issues detected: {len(issues_detected)}",
            f"Primary communication method: {key_findings['communication_method']['detected_method']}",
            f"Protocols in use: {', '.join(key_findings['communication_method']['protocols_found']) if key_findings['communication_method']['protocols_found'] else 'None detected'}",
            f"Proxy configuration: {'Present' if key_findings['proxy_server_analysis']['proxy_detected'] else 'Not detected'}"
        ]
    
    def _populate_troubleshooting_recommendations_card(self, analysis: Dict[str, Any]):
        """Trend Micro Deep Security Technical Support - Direct Troubleshooting Instructions"""
        key_findings = analysis['key_findings_card'] 
        root_cause_card = analysis['root_cause_analysis_card']
        recommendations_card = analysis['troubleshooting_recommendations_card']
        
        # Get AI analysis results
        ai_confidence = root_cause_card.get('ai_confidence_score', 0)
        primary_root_cause = root_cause_card.get('primary_root_cause', '')
        severity = root_cause_card.get('severity_assessment', 'Unknown')
        
        # Count actual issues detected
        issues_detected = 0
        critical_issues = []
        
        if key_findings['last_successful_heartbeat']['status'] == 'Not found in logs':
            issues_detected += 1
            critical_issues.append('heartbeat_failure')
            
        if key_findings['network_communication_failures']['network_failures_found']:
            issues_detected += 1
            critical_issues.append('network_failures')
            
        if key_findings['certificate_issues']['cert_problems_found']:
            issues_detected += 1
            critical_issues.append('certificate_issues')
            
        if key_findings['handshake_failures']['failures_detected']:
            issues_detected += 1
            critical_issues.append('handshake_failures')
            
        if key_findings['port_failures']['port_issues_found']:
            issues_detected += 1
            critical_issues.append('port_failures')
            
        if key_findings['proxy_server_analysis']['proxy_detected'] and key_findings['proxy_server_analysis']['proxy_issues']:
            issues_detected += 1
            critical_issues.append('proxy_issues')
        
        # Generate direct technical support instructions
        if issues_detected == 0 or ai_confidence < 70:
            # No significant issues - minimal guidance
            troubleshooting_steps = [
                "✅ Analysis complete: No critical DS Agent communication issues detected",
                "The logs indicate normal DS Agent operation with successful heartbeat communications",
                "",
                "If you're experiencing DS Agent offline issues:",
                "• Verify logs were collected during the actual problem occurrence",
                "• Check DS Manager console for real-time agent status",
                "• Enable DS Agent debug logging: 'dsa_control --debug' and reproduce the issue"
            ]
            
        else:
            # Critical issues detected - provide direct Trend Micro technical support instructions
            troubleshooting_steps = []
            
            # Add severity and confidence header
            if 'Critical' in severity:
                troubleshooting_steps.append(f"🚨 CRITICAL DS AGENT ISSUE DETECTED")
            elif 'High' in severity:
                troubleshooting_steps.append(f"⚠️ HIGH PRIORITY DS AGENT ISSUE") 
            else:
                troubleshooting_steps.append(f"📋 DS AGENT COMMUNICATION ISSUE")
                
            troubleshooting_steps.extend([
                f"Root Cause: {primary_root_cause}",
                f"AI Confidence: {ai_confidence}%",
                "",
                "TREND MICRO TECHNICAL SUPPORT INSTRUCTIONS:"
            ])
            
            # Provide direct, issue-specific instructions
            if 'heartbeat_failure' in critical_issues:
                troubleshooting_steps.extend([
                    "",
                    "🔧 DS Agent Service Issue:",
                    "1. Check DS Agent service: Get-Service 'Trend Micro Deep Security Agent'",
                    "2. If stopped, restart: Restart-Service 'Trend Micro Deep Security Agent'",
                    "3. Verify DS Manager connectivity: Test-NetConnection <DS_Manager_IP> -Port 4119"
                ])
            
            if 'network_failures' in critical_issues:
                troubleshooting_steps.extend([
                    "",
                    "🌐 Network Connectivity Issue:",
                    "1. Test DNS resolution: nslookup <DS_Manager_FQDN>",
                    "2. Verify network connectivity: ping <DS_Manager_IP>",
                    "3. Check DS communication ports: telnet <DS_Manager_IP> 4119",
                    "4. Verify firewall rules allow DS Agent traffic (ports 4119, 4120, 4122, 443)"
                ])
            
            if 'certificate_issues' in critical_issues:
                troubleshooting_steps.extend([
                    "",
                    "🔐 Certificate Authentication Issue:",
                    "1. Verify system time is synchronized with DS Manager",
                    "2. Check DS Manager Event Log for certificate errors (Event IDs 930, 931)",
                    "3. Reset DS Agent certificate: dsa_control --reset-certificate",
                    "4. Re-activate agent: dsa_control --activate dsm://<DS_Manager>:4119/"
                ])
            
            if 'handshake_failures' in critical_issues:
                troubleshooting_steps.extend([
                    "",
                    "🤝 SSL/TLS Handshake Issue:",
                    "1. Check DS Manager certificate validity and trust chain",
                    "2. Verify SSL cipher compatibility between Agent and Manager",
                    "3. Review DS Agent SSL settings in registry or configuration files",
                    "4. Test SSL connection: openssl s_client -connect <DS_Manager>:4119"
                ])
            
            if 'port_failures' in critical_issues:
                failed_ports = key_findings['port_failures'].get('failed_ports', [])
                troubleshooting_steps.extend([
                    "",
                    f"🚪 Port Access Issue (Ports: {', '.join(failed_ports)}):",
                    "1. Verify DS Manager is listening on required ports",
                    "2. Check local Windows Firewall: Get-NetFirewallRule | Where DisplayName -like '*Deep Security*'",
                    "3. Test port connectivity from agent machine: telnet <DS_Manager_IP> <port>",
                    "4. Review network firewall rules for DS communication ports"
                ])
            
            if 'proxy_issues' in critical_issues:
                troubleshooting_steps.extend([
                    "",
                    "🔄 Proxy Server Issue:",
                    "1. Verify proxy settings in DS Agent configuration",
                    "2. Test proxy connectivity: curl --proxy <proxy_host:port> https://<DS_Manager>:4119",
                    "3. Check proxy authentication credentials",
                    "4. Ensure proxy supports HTTPS tunneling for DS Agent communication"
                ])
            
            # Add final resolution steps
            troubleshooting_steps.extend([
                "",
                "📋 VERIFICATION STEPS:",
                "1. After changes, restart DS Agent service",
                "2. Monitor DS Manager console for agent status changes",
                "3. Check DS Agent logs for successful heartbeat communications",
                "4. Verify protection status: dsa_control --status",
                "",
                "📞 If issue persists after following these steps:",
                "Contact Trend Micro Technical Support with this analysis report"
            ])
        
        # Store simplified troubleshooting steps
        recommendations_card['troubleshooting_steps'] = troubleshooting_steps
    
    def _analyze_amsp_platform_dependencies(self, log_content: str) -> Dict[str, Any]:
        """
        Analyze AMSP (Anti-Malware Solution Platform) dependencies and service correlation
        Based on JSON specifications for Deep Security component integration
        
        Args:
            log_content (str): The DS Agent log content
            
        Returns:
            Dict[str, Any]: AMSP platform dependency analysis
        """
        amsp_analysis = {
            'analysis_timestamp': datetime.now().isoformat(),
            'amsp_service_status': {},
            'dependency_chain_analysis': {},
            'service_correlation': {},
            'platform_integration_issues': [],
            'recommendation_priority': 'medium'
        }
        
        # AMSP Service Detection Patterns (from JSON specifications)
        amsp_service_patterns = {
            'ds_agent_service': {
                'patterns': [
                    r'ds_agent\.exe|dsa\.exe',
                    r'trend.*micro.*ds.*agent',
                    r'deep.*security.*agent.*service'
                ],
                'status_indicators': [
                    r'service.*started|service.*running',
                    r'service.*stopped|service.*failed',
                    r'service.*initialization.*complete|service.*ready'
                ]
            },
            'dsa_core_service': {
                'patterns': [
                    r'dsa_core\.exe|dsa\.core',
                    r'deep.*security.*core.*service',
                    r'trend.*micro.*core.*process'
                ],
                'dependency_check': [
                    r'core.*service.*dependency|dependency.*core.*service',
                    r'failed.*load.*core.*module|core.*module.*not.*found'
                ]
            },
            'amsp_platform_service': {
                'patterns': [
                    r'amsp.*platform|anti.*malware.*solution.*platform',
                    r'trend.*micro.*solution.*platform',
                    r'amenableselfprotection|tmsp.*service'
                ],
                'failure_indicators': [
                    r'amsp.*initialization.*failed|amsp.*service.*crashed',
                    r'failed.*install.*upgrade.*amsp|amsp.*not.*responding',
                    r'amsp.*func.*not.*support|amenableselfprotection.*failed'
                ]
            }
        }
        
        # Analyze service status for each component
        for service_name, service_config in amsp_service_patterns.items():
            service_status = {
                'service_detected': False,
                'service_running': False,
                'dependency_issues': [],
                'error_patterns': [],
                'last_activity': None
            }
            
            # Check for service presence
            for pattern in service_config['patterns']:
                service_matches = re.findall(pattern, log_content, re.IGNORECASE | re.MULTILINE)
                if service_matches:
                    service_status['service_detected'] = True
                    service_status['detection_count'] = len(service_matches)
                    break
            
            # Check service status indicators
            if 'status_indicators' in service_config:
                for status_pattern in service_config['status_indicators']:
                    status_matches = re.findall(status_pattern, log_content, re.IGNORECASE | re.MULTILINE)
                    if status_matches:
                        if 'started' in status_pattern or 'running' in status_pattern or 'ready' in status_pattern:
                            service_status['service_running'] = True
                        service_status['status_events'] = len(status_matches)
            
            # Check for dependency issues
            if 'dependency_check' in service_config:
                for dep_pattern in service_config['dependency_check']:
                    dep_matches = re.findall(dep_pattern, log_content, re.IGNORECASE | re.MULTILINE)
                    if dep_matches:
                        service_status['dependency_issues'].extend(dep_matches)
            
            # Check for failure indicators
            if 'failure_indicators' in service_config:
                for failure_pattern in service_config['failure_indicators']:
                    failure_matches = re.findall(failure_pattern, log_content, re.IGNORECASE | re.MULTILINE)
                    if failure_matches:
                        service_status['error_patterns'].extend(failure_matches)
            
            amsp_analysis['amsp_service_status'][service_name] = service_status
        
        # Service Dependency Chain Analysis
        dependency_chain = {
            'primary_dependencies': {
                'ds_agent_to_dsa_core': self._check_service_dependency(
                    log_content, 'ds_agent', 'dsa_core'
                ),
                'dsa_core_to_amsp_platform': self._check_service_dependency(
                    log_content, 'dsa_core', 'amsp_platform'
                ),
                'amsp_to_network_services': self._check_service_dependency(
                    log_content, 'amsp_platform', 'network_services'
                )
            },
            'circular_dependency_check': self._detect_circular_dependencies(log_content),
            'missing_dependencies': []
        }
        
        # Check for missing critical dependencies
        critical_dependencies = ['network_services', 'certificate_store', 'wmi_service', 'event_log_service']
        for dependency in critical_dependencies:
            if not self._check_dependency_availability(log_content, dependency):
                dependency_chain['missing_dependencies'].append(dependency)
        
        amsp_analysis['dependency_chain_analysis'] = dependency_chain
        
        # Service Correlation Analysis - Events happening together
        correlation_patterns = {
            'amsp_ds_agent_correlation': self._analyze_service_correlation(
                log_content, 'amsp', 'ds_agent'
            ),
            'network_amsp_correlation': self._analyze_service_correlation(
                log_content, 'network', 'amsp'
            ),
            'certificate_amsp_correlation': self._analyze_service_correlation(
                log_content, 'certificate', 'amsp'
            )
        }
        
        amsp_analysis['service_correlation'] = correlation_patterns
        
        # Platform Integration Issues Detection
        integration_issues = []
        
        # Check for AMSP initialization failures
        amsp_init_failures = re.findall(
            r'amsp.*initialization.*failed|failed.*initialize.*amsp|amsp.*startup.*error',
            log_content, re.IGNORECASE | re.MULTILINE
        )
        if amsp_init_failures:
            integration_issues.append({
                'issue_type': 'amsp_initialization_failure',
                'severity': 'high',
                'description': f'AMSP platform initialization failures detected ({len(amsp_init_failures)} events)',
                'recommendation': 'Check AMSP service dependencies and system requirements'
            })
        
        # Check for module loading issues
        module_load_failures = re.findall(
            r'failed.*load.*module|module.*not.*found|dll.*load.*failed',
            log_content, re.IGNORECASE | re.MULTILINE
        )
        if module_load_failures:
            integration_issues.append({
                'issue_type': 'module_loading_failure',
                'severity': 'medium',
                'description': f'Module loading issues detected ({len(module_load_failures)} events)',
                'recommendation': 'Verify Deep Security installation integrity and file permissions'
            })
        
        # Check for service communication failures
        service_comm_failures = re.findall(
            r'service.*communication.*failed|failed.*communicate.*service|ipc.*failure',
            log_content, re.IGNORECASE | re.MULTILINE
        )
        if service_comm_failures:
            integration_issues.append({
                'issue_type': 'service_communication_failure',
                'severity': 'high',
                'description': f'Inter-service communication failures ({len(service_comm_failures)} events)',
                'recommendation': 'Check service permissions and IPC configuration'
            })
        
        amsp_analysis['platform_integration_issues'] = integration_issues
        
        # Determine recommendation priority
        if len(integration_issues) > 0:
            high_severity_issues = [issue for issue in integration_issues if issue['severity'] == 'high']
            if high_severity_issues:
                amsp_analysis['recommendation_priority'] = 'critical'
            else:
                amsp_analysis['recommendation_priority'] = 'high'
        
        return amsp_analysis
    
    def _check_service_dependency(self, log_content: str, source_service: str, target_service: str) -> Dict[str, Any]:
        """Check dependency relationship between two services"""
        dependency_info = {
            'dependency_exists': False,
            'dependency_healthy': False,
            'failure_events': 0,
            'last_interaction': None
        }
        
        # Look for dependency-related log entries
        dependency_pattern = rf'{source_service}.*{target_service}|{target_service}.*{source_service}'
        dependency_matches = re.findall(dependency_pattern, log_content, re.IGNORECASE | re.MULTILINE)
        
        if dependency_matches:
            dependency_info['dependency_exists'] = True
            dependency_info['interaction_count'] = len(dependency_matches)
            
            # Check for failure patterns in dependency
            failure_pattern = rf'{source_service}.*{target_service}.*failed|{target_service}.*{source_service}.*error'
            failure_matches = re.findall(failure_pattern, log_content, re.IGNORECASE | re.MULTILINE)
            dependency_info['failure_events'] = len(failure_matches)
            dependency_info['dependency_healthy'] = len(failure_matches) == 0
        
        return dependency_info
    
    def _detect_circular_dependencies(self, log_content: str) -> Dict[str, Any]:
        """Detect circular dependency patterns that could cause service issues"""
        circular_check = {
            'circular_dependencies_detected': False,
            'potential_cycles': [],
            'recommendation': 'No circular dependencies detected'
        }
        
        # Look for circular dependency indicators
        circular_patterns = [
            r'circular.*dependency|dependency.*loop|recursive.*dependency',
            r'service.*waiting.*for.*service.*waiting',
            r'deadlock.*detected|mutual.*dependency.*failure'
        ]
        
        for pattern in circular_patterns:
            matches = re.findall(pattern, log_content, re.IGNORECASE | re.MULTILINE)
            if matches:
                circular_check['circular_dependencies_detected'] = True
                circular_check['potential_cycles'].extend(matches)
                circular_check['recommendation'] = 'Review service startup order and dependency configuration'
        
        return circular_check
    
    def _check_dependency_availability(self, log_content: str, dependency_name: str) -> bool:
        """Check if a critical dependency is available"""
        dependency_patterns = {
            'network_services': [r'network.*service.*running|network.*interface.*up', r'dns.*resolution.*successful'],
            'certificate_store': [r'certificate.*store.*available|cert.*store.*accessible'],
            'wmi_service': [r'wmi.*service.*running|wmi.*query.*successful'],
            'event_log_service': [r'event.*log.*service.*running|event.*logging.*enabled']
        }
        
        if dependency_name in dependency_patterns:
            for pattern in dependency_patterns[dependency_name]:
                if re.search(pattern, log_content, re.IGNORECASE | re.MULTILINE):
                    return True
        
        return False
    
    def _analyze_service_correlation(self, log_content: str, service1: str, service2: str) -> Dict[str, Any]:
        """Analyze correlation between two services based on log timestamps and events"""
        correlation_info = {
            'correlation_detected': False,
            'correlation_strength': 'none',
            'event_timing_analysis': {},
            'related_events_count': 0
        }
        
        # Look for events involving both services within close time proximity
        service1_events = re.findall(rf'.*{service1}.*', log_content, re.IGNORECASE | re.MULTILINE)
        service2_events = re.findall(rf'.*{service2}.*', log_content, re.IGNORECASE | re.MULTILINE)
        
        if service1_events and service2_events:
            correlation_info['correlation_detected'] = True
            correlation_info['service1_events'] = len(service1_events)
            correlation_info['service2_events'] = len(service2_events)
            
            # Simple correlation strength based on event frequency
            total_events = len(service1_events) + len(service2_events)
            if total_events > 20:
                correlation_info['correlation_strength'] = 'high'
            elif total_events > 10:
                correlation_info['correlation_strength'] = 'medium'
            else:
                correlation_info['correlation_strength'] = 'low'
            
            correlation_info['related_events_count'] = total_events
        
        return correlation_info

    def _analyze_proxy_configuration_intelligence(self, log_content: str) -> Dict[str, Any]:
        """
        Enhanced proxy configuration intelligence analysis
        Based on JSON specifications for HTTP 407 errors, authentication methods, and corporate proxy patterns
        
        Args:
            log_content (str): The DS Agent log content
            
        Returns:
            Dict[str, Any]: Advanced proxy configuration analysis
        """
        proxy_intelligence = {
            'analysis_timestamp': datetime.now().isoformat(),
            'proxy_detection': {},
            'authentication_analysis': {},
            'proxy_errors': {},
            'corporate_proxy_patterns': {},
            'bypass_configuration': {},
            'troubleshooting_recommendations': []
        }
        
        # Enhanced Proxy Detection Patterns (from JSON specifications)
        proxy_detection_patterns = {
            'http_proxy_patterns': [
                r'http[s]?://.*proxy.*:\d+|proxy.*server.*http[s]?',
                r'http.*proxy.*host|http.*proxy.*port',
                r'environment.*http_proxy|system.*http.*proxy'
            ],
            'socks_proxy_patterns': [
                r'socks[45]?://.*:\d+|socks.*proxy.*server',
                r'socks.*proxy.*host|socks.*proxy.*port'
            ],
            'automatic_proxy_patterns': [
                r'wpad.*proxy.*auto.*config|pac.*file.*proxy',
                r'automatic.*proxy.*detection|dhcp.*proxy.*discovery',
                r'internet.*explorer.*proxy.*settings'
            ],
            'policy_based_proxy_patterns': [
                r'group.*policy.*proxy|domain.*policy.*proxy',
                r'registry.*proxy.*settings|policy.*based.*proxy'
            ]
        }
        
        # Analyze proxy detection
        proxy_detection = {
            'proxy_types_detected': [],
            'proxy_servers_found': [],
            'detection_confidence': 'none'
        }
        
        for proxy_type, patterns in proxy_detection_patterns.items():
            for pattern in patterns:
                matches = re.findall(pattern, log_content, re.IGNORECASE | re.MULTILINE)
                if matches:
                    proxy_detection['proxy_types_detected'].append(proxy_type)
                    
                    # Extract proxy server details
                    server_pattern = r'((?:\d{1,3}\.){3}\d{1,3}|[\w\.-]+):\d+'
                    server_matches = re.findall(server_pattern, str(matches), re.IGNORECASE)
                    proxy_detection['proxy_servers_found'].extend(server_matches)
        
        # Determine detection confidence
        if len(proxy_detection['proxy_types_detected']) > 2:
            proxy_detection['detection_confidence'] = 'high'
        elif len(proxy_detection['proxy_types_detected']) > 0:
            proxy_detection['detection_confidence'] = 'medium'
        
        proxy_intelligence['proxy_detection'] = proxy_detection
        
        # HTTP 407 Proxy Authentication Analysis
        http_407_patterns = [
            r'http.*407.*proxy.*authentication.*required',
            r'proxy.*authentication.*failed.*407',
            r'authentication.*required.*proxy.*server',
            r'407.*unauthorized.*proxy.*authentication'
        ]
        
        authentication_analysis = {
            'http_407_errors_detected': False,
            'authentication_failures': 0,
            'authentication_methods': [],
            'credential_issues': []
        }
        
        for pattern in http_407_patterns:
            matches = re.findall(pattern, log_content, re.IGNORECASE | re.MULTILINE)
            if matches:
                authentication_analysis['http_407_errors_detected'] = True
                authentication_analysis['authentication_failures'] += len(matches)
        
        # Authentication Method Detection
        auth_method_patterns = {
            'ntlm_authentication': [
                r'ntlm.*authentication|ntlm.*proxy|proxy.*ntlm',
                r'windows.*integrated.*authentication|negotiate.*ntlm'
            ],
            'kerberos_authentication': [
                r'kerberos.*authentication|kerberos.*proxy',
                r'spnego.*kerberos|negotiate.*kerberos'
            ],
            'basic_authentication': [
                r'basic.*authentication|basic.*proxy',
                r'username.*password.*proxy|credentials.*basic'
            ],
            'digest_authentication': [
                r'digest.*authentication|digest.*proxy',
                r'md5.*digest.*authentication'
            ]
        }
        
        for auth_method, patterns in auth_method_patterns.items():
            for pattern in patterns:
                matches = re.findall(pattern, log_content, re.IGNORECASE | re.MULTILINE)
                if matches:
                    authentication_analysis['authentication_methods'].append(auth_method)
        
        # Credential Issues Detection
        credential_issue_patterns = [
            r'invalid.*proxy.*credentials|proxy.*credentials.*failed',
            r'authentication.*timeout|proxy.*authentication.*expired',
            r'user.*account.*locked|domain.*authentication.*failed'
        ]
        
        for pattern in credential_issue_patterns:
            matches = re.findall(pattern, log_content, re.IGNORECASE | re.MULTILINE)
            if matches:
                authentication_analysis['credential_issues'].extend(matches)
        
        proxy_intelligence['authentication_analysis'] = authentication_analysis
        
        # Proxy Error Analysis
        proxy_error_patterns = {
            'connection_errors': [
                r'proxy.*connection.*failed|failed.*connect.*proxy',
                r'proxy.*server.*unreachable|proxy.*timeout',
                r'proxy.*connection.*refused|proxy.*server.*down'
            ],
            'configuration_errors': [
                r'proxy.*configuration.*error|invalid.*proxy.*settings',
                r'proxy.*port.*invalid|proxy.*host.*invalid',
                r'malformed.*proxy.*url|proxy.*address.*error'
            ],
            'ssl_tls_errors': [
                r'proxy.*ssl.*error|proxy.*tls.*error',
                r'proxy.*certificate.*error|proxy.*handshake.*failed',
                r'tunnel.*through.*proxy.*failed'
            ]
        }
        
        proxy_errors = {}
        for error_type, patterns in proxy_error_patterns.items():
            error_count = 0
            error_details = []
            for pattern in patterns:
                matches = re.findall(pattern, log_content, re.IGNORECASE | re.MULTILINE)
                if matches:
                    error_count += len(matches)
                    error_details.extend(matches)
            
            proxy_errors[error_type] = {
                'error_count': error_count,
                'error_details': error_details[:5]  # Limit to first 5 errors
            }
        
        proxy_intelligence['proxy_errors'] = proxy_errors
        
        # Corporate Proxy Pattern Analysis
        corporate_patterns = {
            'domain_integration': [
                r'domain.*proxy.*authentication|corporate.*proxy.*server',
                r'active.*directory.*proxy|domain.*controller.*proxy'
            ],
            'proxy_pac_files': [
                r'pac.*file.*proxy|proxy.*auto.*config',
                r'wpad.*configuration|automatic.*proxy.*script'
            ],
            'enterprise_features': [
                r'proxy.*bypass.*list|proxy.*exception.*list',
                r'per.*application.*proxy|application.*specific.*proxy'
            ]
        }
        
        corporate_proxy_patterns = {}
        for pattern_type, patterns in corporate_patterns.items():
            pattern_detected = False
            pattern_details = []
            for pattern in patterns:
                matches = re.findall(pattern, log_content, re.IGNORECASE | re.MULTILINE)
                if matches:
                    pattern_detected = True
                    pattern_details.extend(matches)
            
            corporate_proxy_patterns[pattern_type] = {
                'detected': pattern_detected,
                'details': pattern_details[:3]  # Limit details
            }
        
        proxy_intelligence['corporate_proxy_patterns'] = corporate_proxy_patterns
        
        # Proxy Bypass Configuration Analysis
        bypass_patterns = [
            r'proxy.*bypass.*list|bypass.*proxy.*for',
            r'no.*proxy.*for|proxy.*exception',
            r'direct.*connection.*for|bypass.*proxy.*server'
        ]
        
        bypass_analysis = {
            'bypass_configured': False,
            'bypass_rules': [],
            'local_bypass_detected': False
        }
        
        for pattern in bypass_patterns:
            matches = re.findall(pattern, log_content, re.IGNORECASE | re.MULTILINE)
            if matches:
                bypass_analysis['bypass_configured'] = True
                bypass_analysis['bypass_rules'].extend(matches)
        
        # Check for local/localhost bypass
        local_bypass_patterns = [
            r'bypass.*localhost|bypass.*127\.0\.0\.1',
            r'local.*direct.*connection|localhost.*no.*proxy'
        ]
        
        for pattern in local_bypass_patterns:
            if re.search(pattern, log_content, re.IGNORECASE | re.MULTILINE):
                bypass_analysis['local_bypass_detected'] = True
        
        proxy_intelligence['bypass_configuration'] = bypass_analysis
        
        # Generate Troubleshooting Recommendations
        recommendations = []
        
        if authentication_analysis['http_407_errors_detected']:
            recommendations.append({
                'priority': 'high',
                'category': 'authentication',
                'recommendation': 'Configure proxy authentication credentials',
                'details': 'HTTP 407 errors indicate proxy authentication failure. Verify username/password or enable integrated authentication.'
            })
        
        if proxy_errors['connection_errors']['error_count'] > 0:
            recommendations.append({
                'priority': 'high',
                'category': 'connectivity',
                'recommendation': 'Verify proxy server connectivity',
                'details': 'Proxy connection failures detected. Check proxy server availability and network connectivity.'
            })
        
        if proxy_errors['configuration_errors']['error_count'] > 0:
            recommendations.append({
                'priority': 'medium',
                'category': 'configuration',
                'recommendation': 'Review proxy configuration settings',
                'details': 'Configuration errors detected. Verify proxy server address, port, and URL format.'
            })
        
        if proxy_errors['ssl_tls_errors']['error_count'] > 0:
            recommendations.append({
                'priority': 'high',
                'category': 'security',
                'recommendation': 'Fix SSL/TLS proxy tunnel issues',
                'details': 'SSL/TLS errors through proxy detected. Check proxy SSL configuration and certificate trust.'
            })
        
        if not bypass_analysis['bypass_configured'] and corporate_proxy_patterns['domain_integration']['detected']:
            recommendations.append({
                'priority': 'medium',
                'category': 'optimization',
                'recommendation': 'Configure proxy bypass for internal resources',
                'details': 'Corporate proxy detected without bypass configuration. Consider adding bypass rules for internal servers.'
            })
        
        proxy_intelligence['troubleshooting_recommendations'] = recommendations
        
        return proxy_intelligence

    def _ai_analyze_heartbeat_communication(self, log_content: str, communication_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """AI-powered root cause analysis for heartbeat and network communication issues"""
        
        root_cause_analysis = {
            'root_causes': [],
            'confidence_score': 0.0,
            'ai_insights': [],
            'correlation_analysis': {}
        }
        
        # Analyze patterns and correlations
        issues_found = []
        
        # Heartbeat issues
        if communication_analysis['last_successful_heartbeat']['status'] != 'found':
            issues_found.append('No successful heartbeat detected')
            root_cause_analysis['root_causes'].append({
                'category': 'Heartbeat Communication',
                'issue': 'Agent-Manager heartbeat communication failure',
                'severity': 'critical',
                'confidence': 0.9,
                'explanation': 'No successful heartbeat communication detected in logs, indicating complete communication failure between DS Agent and Manager'
            })
        
        # Communication method issues
        if communication_analysis['communication_method']['primary_method'] == 'unknown':
            issues_found.append('Unknown communication method')
            root_cause_analysis['root_causes'].append({
                'category': 'Communication Protocol',
                'issue': 'Unable to determine communication method',
                'severity': 'high',
                'confidence': 0.8,
                'explanation': 'Could not identify the primary communication protocol, suggesting fundamental connectivity issues'
            })
        
        # Certificate issues (Enhanced with DS 20.0 PKI specifications)
        if communication_analysis['certificate_issues']['found']:
            issues_found.append(f"DS PKI Certificate problems ({communication_analysis['certificate_issues']['count']} events)")
            root_cause_analysis['root_causes'].append({
                'category': 'Deep Security PKI Certificate Authentication',
                'issue': 'PKI mutual authentication failures between DS Agent and Manager',
                'severity': 'high',
                'confidence': 0.9,
                'explanation': f"Found {communication_analysis['certificate_issues']['count']} certificate-related issues. Deep Security uses PKI certificates for mutual authentication with certificate chain verification and revocation checking. Monitor Event IDs 930/931 for certificate status."
            })
        
        # Handshake failures
        if communication_analysis['handshake_failures']['found']:
            issues_found.append(f"SSL/TLS handshake failures ({communication_analysis['handshake_failures']['count']} events)")
            root_cause_analysis['root_causes'].append({
                'category': 'SSL/TLS Handshake',
                'issue': 'SSL/TLS handshake failures',
                'severity': 'high',
                'confidence': 0.9,
                'explanation': f"Detected {communication_analysis['handshake_failures']['count']} handshake failures indicating certificate or protocol issues"
            })
        
        # Network communication failures (Enhanced with DS 20.0 event correlation)
        if communication_analysis['network_communication_failures']['found']:
            issues_found.append(f"DS Network failures ({communication_analysis['network_communication_failures']['count']} events)")
            root_cause_analysis['root_causes'].append({
                'category': 'Deep Security Network Communication',
                'issue': 'DS Agent-Manager network communication failures',
                'severity': 'critical',
                'confidence': 0.95,
                'explanation': f"Found {communication_analysis['network_communication_failures']['count']} network communication failures. Critical Deep Security Event IDs detected: 730 (Agent offline), 742 (Communication problem), 4011 (Failure to contact manager), 4012 (Heartbeat failed). Requires immediate network infrastructure investigation."
            })
        
        # Port failures
        if communication_analysis['port_failures']['found']:
            failed_ports = ', '.join(communication_analysis['port_failures']['failed_ports'])
            issues_found.append(f"Port failures on {failed_ports}")
            root_cause_analysis['root_causes'].append({
                'category': 'Port Accessibility',
                'issue': 'Port binding or accessibility failures',
                'severity': 'high',
                'confidence': 0.8,
                'explanation': f"Port failures detected on {failed_ports}, indicating firewall or service binding issues"
            })
        
        # Proxy issues
        if communication_analysis['proxy_server_detected']['found']:
            root_cause_analysis['ai_insights'].append({
                'type': 'proxy_analysis',
                'insight': f"Proxy server detected ({communication_analysis['proxy_server_detected']['proxy_type']})",
                'impact': 'Proxy configuration may be affecting DS Agent communication'
            })
        
        # Calculate overall confidence score
        if root_cause_analysis['root_causes']:
            avg_confidence = sum(rc['confidence'] for rc in root_cause_analysis['root_causes']) / len(root_cause_analysis['root_causes'])
            root_cause_analysis['confidence_score'] = avg_confidence
        
        # AI correlation analysis
        root_cause_analysis['correlation_analysis'] = {
            'primary_failure_mode': self._determine_primary_failure_mode(communication_analysis),
            'secondary_issues': issues_found,
            'recommended_investigation_order': self._get_investigation_priority(root_cause_analysis['root_causes'])
        }
        
        return root_cause_analysis
    
    def _generate_focused_troubleshooting(self, communication_analysis: Dict[str, Any], ai_root_cause: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate step-by-step troubleshooting recommendations focused on heartbeat and network issues"""
        
        troubleshooting_steps = []
        
        # Step 1: Heartbeat Communication Check (Enhanced with DS 20.0 specifications)
        if communication_analysis['last_successful_heartbeat']['status'] != 'found':
            troubleshooting_steps.append({
                'step_number': 1,
                'category': 'Deep Security Heartbeat Verification',
                'title': 'Verify DS Agent-Manager Heartbeat Communication (Default 10-minute interval)',
                'priority': 'critical',
                'actions': [
                    'Windows: Test-NetConnection -ComputerName <DSM_hostname> -Port 4120',
                    'Linux: telnet <DSM_hostname> 4120 (Manager-to-Agent heartbeat)',
                    'Verify DS Agent service: Windows: Get-Service ds_agent | Linux: systemctl status ds_agent',
                    'Check DNS resolution: nslookup <DSM_hostname>',
                    'Validate Manager address in DS Agent configuration',
                    'Monitor for Event ID 731 (back online) vs Event ID 730 (offline)',
                    'Verify heartbeat frequency setting (default 600 seconds)'
                ],
                'validation': 'Monitor logs for Event ID 731 (Agent back online) and successful heartbeat messages'
            })
        
        # Step 2: Certificate and Authentication (Enhanced with DS 20.0 PKI specifications)
        if communication_analysis['certificate_issues']['found'] or communication_analysis['handshake_failures']['found']:
            troubleshooting_steps.append({
                'step_number': 2,
                'category': 'Deep Security PKI Certificate Authentication',
                'title': 'Resolve Certificate and TLS 1.2/1.3 Handshake Issues',
                'priority': 'high',
                'actions': [
                    'Verify NTP time synchronization (critical for certificate validation)',
                    'Check for Event ID 930 (Certificate accepted) vs Event ID 931 (Certificate deleted)',
                    'Validate agent identity certificates and manager server certificates',
                    'Verify certificate chain and root CA certificate accessibility',
                    'Test TLS 1.2/1.3 with AES encryption handshake manually',
                    'Check certificate revocation status and validation process',
                    'Windows: Use certlm.msc for certificate store management',
                    'Monitor for Event ID 734 (Time synchronization issues affecting certificates)'
                ],
                'validation': 'Confirm Event ID 930 (Certificate accepted) and successful TLS handshake completion'
            })
        
        # Step 3: Network Communication (Enhanced with DS 20.0 communication architecture)
        if communication_analysis['network_communication_failures']['found']:
            troubleshooting_steps.append({
                'step_number': 3,
                'category': 'Deep Security Network Communication',
                'title': 'Diagnose DS Agent Network Communication Failures',
                'priority': 'critical',
                'actions': [
                    'Test port 4119 (Agent-to-Manager HTTPS communication outbound)',
                    'Test port 4120 (Manager-to-Agent HTTPS heartbeat inbound)',
                    'Test port 4122 (Relay server communication if applicable)',
                    'Test port 443 (Smart Protection Network and Cloud One connectivity)',
                    'Verify DNS resolution for *.trendmicro.com domains',
                    'Check firewall rules for Deep Security communication ports',
                    'Monitor for Event ID 4011 (Failure to contact manager)',
                    'Monitor for Event ID 742/743 (Communication problem detected/resolved)',
                    'Validate minimum bandwidth: 64kbps per agent, recommended 128kbps'
                ],
                'validation': 'Confirm Event ID 743 (Communication problem resolved) and successful port connectivity'
            })
        
        # Step 4: Port and Service Issues
        if communication_analysis['port_failures']['found']:
            troubleshooting_steps.append({
                'step_number': 4,
                'category': 'Port and Service Diagnostics',
                'title': 'Resolve Port Binding and Service Issues',
                'priority': 'high',
                'actions': [
                    f"Check if ports {', '.join(communication_analysis['port_failures']['failed_ports'])} are available",
                    'Verify DS Agent service has proper permissions to bind ports',
                    'Check for conflicting services using the same ports',
                    'Review system firewall and security software configurations',
                    'Restart DS Agent service with elevated privileges if needed'
                ],
                'validation': 'Confirm ports are successfully bound and accessible'
            })
        
        # Step 5: Proxy Configuration (Enhanced with DS 20.0 proxy support)
        if communication_analysis['proxy_server_detected']['found']:
            troubleshooting_steps.append({
                'step_number': 5,
                'category': 'Deep Security Proxy Configuration',
                'title': f"Configure {communication_analysis['proxy_server_detected']['proxy_type']} for DS Agent",
                'priority': 'medium',
                'actions': [
                    'Verify supported proxy types: HTTP, HTTPS, SOCKS proxy servers',
                    'Test authentication methods: Basic, NTLM, Kerberos authentication',
                    'Configure per-agent proxy settings or policy-based proxy configuration',
                    'Test automatic proxy detection if enabled',
                    'Verify proxy server can handle HTTPS traffic to Manager (ports 4119/4120)',
                    'Check proxy server logs for Deep Security communication attempts',
                    'Consider proxy bypass for internal Deep Security Manager communications',
                    'Monitor for HTTP 407 (Proxy Authentication Required) errors'
                ],
                'validation': 'Verify DS Agent can communicate through proxy to Deep Security Manager without HTTP 407 errors'
            })
        
        # Add general health check if no specific issues found
        if not troubleshooting_steps:
            troubleshooting_steps.append({
                'step_number': 1,
                'category': 'Health Verification',
                'title': 'Verify DS Agent Communication Health',
                'priority': 'informational',
                'actions': [
                    'Confirm regular heartbeat communications are occurring',
                    'Monitor communication method and protocol usage',
                    'Verify all required ports are functioning correctly',
                    'Check for any proxy server configurations',
                    'Validate certificate health and expiration dates'
                ],
                'validation': 'All communication patterns appear healthy'
            })
        
        return troubleshooting_steps
    
    def _extract_timestamp(self, log_line: str) -> str:
        """Extract timestamp from log line"""
        import re
        timestamp_patterns = [
            r'(\d{4}-\d{2}-\d{2}[T\s]\d{2}:\d{2}:\d{2})',
            r'(\d{2}/\d{2}/\d{4}\s\d{2}:\d{2}:\d{2})',
            r'(\w{3}\s+\d{1,2}\s+\d{2}:\d{2}:\d{2})'
        ]
        
        for pattern in timestamp_patterns:
            match = re.search(pattern, log_line)
            if match:
                return match.group(1)
        return 'unknown'
    
    def _determine_primary_failure_mode(self, communication_analysis: Dict[str, Any]) -> str:
        """Determine the primary failure mode based on analysis"""
        if communication_analysis['network_communication_failures']['found']:
            return 'Network Infrastructure Failure'
        elif communication_analysis['certificate_issues']['found']:
            return 'Certificate Authentication Failure'
        elif communication_analysis['handshake_failures']['found']:
            return 'SSL/TLS Communication Failure'
        elif communication_analysis['port_failures']['found']:
            return 'Port Accessibility Failure'
        elif communication_analysis['last_successful_heartbeat']['status'] != 'found':
            return 'Heartbeat Communication Failure'
        else:
            return 'Unknown Communication Issue'
    
    def _get_investigation_priority(self, root_causes: List[Dict[str, Any]]) -> List[str]:
        """Get prioritized investigation order"""
        priority_order = []
        
        # Sort by confidence and severity
        sorted_causes = sorted(root_causes, key=lambda x: (x['confidence'], 1 if x['severity'] == 'critical' else 0), reverse=True)
        
        for cause in sorted_causes:
            priority_order.append(f"{cause['category']}: {cause['issue']}")
        
        return priority_order
