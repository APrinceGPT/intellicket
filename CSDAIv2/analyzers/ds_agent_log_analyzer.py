# -*- coding: utf-8 -*-
"""
DSAgentLogAnalyzer - Deep Security Agent Log Analyzer with Dynamic RAG integration
Extracted from analyzers.py lines 303-1030 with safety enhancements
"""

from .shared_imports import *
from .base.standardizer import AnalyzerOutputStandardizer
from datetime import datetime

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
                print(f"📊 DS Agent Progress - {stage}: {message}")
            except Exception as e:
                print(f"⚠️ DS Agent Progress update failed: {e}")
        else:
            # Fallback to console logging
            print(f"📊 DS Agent {stage}: {message}")

    def _convert_numpy_types(self, obj):
        """
        Recursively convert NumPy types to native Python types for JSON serialization
        """
        try:
            import numpy as np
        except ImportError:
            return obj  # No NumPy available, return as-is
        
        if isinstance(obj, dict):
            return {k: self._convert_numpy_types(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._convert_numpy_types(item) for item in obj]
        elif isinstance(obj, tuple):
            return tuple(self._convert_numpy_types(item) for item in obj)
        elif isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif hasattr(obj, 'dtype'):  # Other NumPy types
            if np.issubdtype(obj.dtype, np.integer):
                return int(obj)
            elif np.issubdtype(obj.dtype, np.floating):
                return float(obj)
            else:
                return str(obj)
        else:
            return obj

    def _clean_html_from_recommendations(self, recommendations: list) -> list:
        """
        Clean HTML tags from recommendations for structured output
        Maintains the semantic meaning while removing presentation markup
        """
        import re
        
        cleaned_recommendations = []
        
        for rec in recommendations:
            if isinstance(rec, str):
                # Remove HTML tags but preserve the content
                # Pattern to match HTML tags like <i class="...">content</i>
                cleaned = re.sub(r'<i[^>]*class="[^"]*fa-[^"]*"[^>]*></i>\s*', '', rec)
                cleaned = re.sub(r'<i[^>]*class="[^"]*fa-[^"]*"[^>]*>', '', cleaned)
                cleaned = re.sub(r'<[^>]+>', '', cleaned)  # Remove any remaining HTML tags
                cleaned = cleaned.strip()
                
                # Convert icon patterns to text equivalents
                if 'search' in rec.lower() or 'fa-search' in rec:
                    cleaned = f"🔍 {cleaned}"
                elif 'exclamation' in rec.lower() or 'triangle-exclamation' in rec or 'circle-exclamation' in rec:
                    cleaned = f"⚠️ {cleaned}"
                elif 'check-circle' in rec or 'success' in rec:
                    cleaned = f"✅ {cleaned}"
                elif 'wrench' in rec or 'fa-wrench' in rec:
                    cleaned = f"🔧 {cleaned}"
                elif 'folder' in rec or 'fa-folder' in rec:
                    cleaned = f"📁 {cleaned}"
                
                if cleaned:  # Only add non-empty recommendations
                    cleaned_recommendations.append(cleaned)
            else:
                cleaned_recommendations.append(rec)
        
        return cleaned_recommendations

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
        
        # NEW: Module Status Patterns for enhanced analysis
        self.module_status_patterns = {
            'relay': re.compile(r'features relay on=(\w+)', re.IGNORECASE),
            'anti_malware': re.compile(r'features am on=(\w+)', re.IGNORECASE),
            'web_reputation': re.compile(r'features wrs on=(\w+)', re.IGNORECASE),
            'device_control': re.compile(r'features dc on=(\w+)', re.IGNORECASE),
            'sensor': re.compile(r'features sensor on=(\w+)', re.IGNORECASE),
            'application_control': re.compile(r'features ac on=(\w+)', re.IGNORECASE),
            'integrity_monitoring': re.compile(r'features im on=(\w+)', re.IGNORECASE),
            'log_inspection': re.compile(r'features li on=(\w+)', re.IGNORECASE),
            'firewall': re.compile(r'features fw on=(\w+)', re.IGNORECASE),
            'intrusion_prevention': re.compile(r'features dpi on=(\w+)', re.IGNORECASE),
            'cloud_control': re.compile(r'features cctrl on=(\w+)', re.IGNORECASE),
            'sap': re.compile(r'features sap on=(\w+)', re.IGNORECASE),
            'icap': re.compile(r'features icap on=(\w+)', re.IGNORECASE),
            # Additional patterns for DPI/Firewall logs
            'dpi_engine': re.compile(r'DPI.*enabled', re.IGNORECASE),
            'firewall_engine': re.compile(r'Firewall.*enabled', re.IGNORECASE)
        }
        
        # NEW: Configuration Patterns for DS Agent settings
        self.configuration_patterns = {
            'manager_url': re.compile(r"manager is at '([^']+)'", re.IGNORECASE),
            'agent_initiated': re.compile(r'agentInitiated=(\w+)', re.IGNORECASE),
            'azure_status': re.compile(r'AzureStatus=(\w+)', re.IGNORECASE),
            'secure_boot': re.compile(r'Secure Boot enabled: (\w+)', re.IGNORECASE),
            'fips_available': re.compile(r'DSA FIPS available = (\d+)', re.IGNORECASE),
            'proxy_settings': re.compile(r'Auto:(\d+) \| PACUrl:([^|]*) \| StaticProxy: ([^|]*) \| Bypass: ([^|]*)', re.IGNORECASE),
            'bios_uuid': re.compile(r"bios-uuid:'([^']+)' -> '([^']+)'", re.IGNORECASE),
            'platform_check': re.compile(r'platformcheck_disable=(\d+)', re.IGNORECASE),
            'ssl_settings': re.compile(r'security_policy_ssl_enable[^=]*=(\d+)', re.IGNORECASE)
        }

        self.component_patterns = {
            'anti_malware': [r'antimalware', r'amsp', r'aegis', r'adc'],
            'intrusion_prevention': [r'dpi', r'ips', r'fwdpi'],
            'firewall': [r'firewall', r'fw', r'fwdpi'],
            'integrity_monitoring': [r'integrity', r'fim'],
            'log_inspection': [r'loginspection', r'li'],
            'device_control': [r'device control', r'dc'],
            'web_reputation': [r'web reputation', r'wr'],
            'application_control': [r'application control', r'ac'],
            'connection_handler': [r'connectionhandler', r'heartbeat'],
            'agent_core': [r'dsa', r'agent', r'core'],
            'logdata': [r'logdata', r'logscan'],
            'network_security': [r'network', r'netsec', r'packet']
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
        """Categorize log entry severity with ML enhancement"""
        if not log_entry.get('parsed'):
            return 'unknown'
        
        message = log_entry['message'].lower()
        component = log_entry.get('component', '').lower()
        
        # Use ML-enhanced severity classification if available
        if hasattr(self, 'ml_analyzer') and self.ml_analyzer:
            try:
                ml_severity = self._get_ml_severity_classification(log_entry)
                if ml_severity:
                    return ml_severity
            except Exception as e:
                print(f"⚠️ ML severity classification failed: {e}")
        
        # Fallback to pattern-based classification
        # Enhanced critical patterns
        critical_indicators = [
            r'(critical|CRITICAL|fatal|FATAL|crash|CRASH)',
            r'unable to open file', r'file not available', r'connection failed',
            r'authentication failed', r'permission denied', r'access denied',
            r'certificate error', r'ssl error', r'network error',
            r'scan engine.*crash', r'service.*stop', r'agent.*disconnect'
        ]
        
        # Component-specific severity analysis
        if component in ['amsp', 'am', 'antimalware']:
            critical_indicators.extend([r'scan.*fail', r'engine.*error', r'malware.*detect.*fail'])
        elif component in ['fw', 'firewall', 'dpi']:
            critical_indicators.extend([r'block.*fail', r'rule.*error', r'traffic.*drop'])
        
        for pattern in critical_indicators:
            if re.search(pattern, message, re.IGNORECASE):
                return 'critical'
        
        # Enhanced warning patterns with context
        warning_indicators = [
            r'(warning|WARNING)', r'failed', r'timeout', r'retry',
            r'deprecated', r'not supported', r'metrics failed',
            r'connection.*slow', r'memory.*high', r'cpu.*high'
        ]
        
        for pattern in warning_indicators:
            if re.search(pattern, message, re.IGNORECASE):
                return 'warning'
        
        # Info patterns
        for pattern in self.error_patterns['info']:
            if re.search(pattern, message, re.IGNORECASE):
                return 'info'
        
        return 'normal'
    
    def _get_ml_severity_classification(self, log_entry: Dict[str, Any]) -> str:
        """Use ML model to classify severity based on context and patterns"""
        try:
            if not ML_AVAILABLE:
                return None
                
            # Create feature vector for ML classification
            features = {
                'message_length': len(log_entry.get('message', '')),
                'has_error_keywords': len([kw for kw in ['error', 'fail', 'timeout'] 
                                          if kw in log_entry.get('message', '').lower()]),
                'component_criticality': self._get_component_criticality(log_entry.get('component', '')),
                'hour_of_day': self._extract_hour_from_timestamp(log_entry.get('timestamp', '')),
                'contains_numbers': len(re.findall(r'\d+', log_entry.get('message', ''))),
                'message_entropy': self._calculate_message_entropy(log_entry.get('message', ''))
            }
            
            # Simple ML-based classification (can be enhanced with trained model)
            severity_score = 0
            
            # Component criticality factor
            severity_score += features['component_criticality'] * 0.3
            
            # Error keyword density
            severity_score += min(features['has_error_keywords'] / 3, 1) * 0.4
            
            # Message complexity/entropy
            severity_score += min(features['message_entropy'] / 4, 1) * 0.2
            
            # Time-based factors (issues during business hours are more critical)
            hour = features['hour_of_day']
            if 9 <= hour <= 17:  # Business hours
                severity_score += 0.1
            
            # Classify based on score
            if severity_score >= 0.8:
                return 'critical'
            elif severity_score >= 0.6:
                return 'warning'
            elif severity_score >= 0.3:
                return 'info'
            else:
                return 'normal'
                
        except Exception as e:
            print(f"⚠️ ML severity classification error: {e}")
            return None
    
    def _get_component_criticality(self, component: str) -> float:
        """Get criticality score for DS Agent component"""
        criticality_map = {
            'amsp': 0.9, 'antimalware': 0.9, 'am': 0.9,
            'firewall': 0.8, 'fw': 0.8, 'dpi': 0.8,
            'agent': 0.7, 'dsa': 0.7, 'core': 0.7,
            'heartbeat': 0.6, 'connectionhandler': 0.6,
            'logdata': 0.4, 'metrics': 0.3
        }
        return criticality_map.get(component.lower(), 0.5)
    
    def _extract_hour_from_timestamp(self, timestamp: str) -> int:
        """Extract hour from timestamp string"""
        try:
            import datetime
            # Parse timestamp format: 2024-08-12 10:00:00.123
            dt = datetime.datetime.strptime(timestamp[:19], '%Y-%m-%d %H:%M:%S')
            return dt.hour
        except:
            return 12  # Default to noon
    
    def _calculate_message_entropy(self, message: str) -> float:
        """Calculate entropy of message (complexity indicator)"""
        try:
            import math
            from collections import Counter
            
            if not message:
                return 0
                
            # Calculate character frequency
            counter = Counter(message.lower())
            length = len(message)
            
            # Calculate entropy
            entropy = 0
            for count in counter.values():
                prob = count / length
                entropy -= prob * math.log2(prob)
                
            return entropy
        except:
            return 2.0  # Default moderate entropy
    
    def _calculate_component_health_scores(self, analysis: Dict[str, Any], log_entries: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate ML-based health scores for each DS component"""
        try:
            component_health = {}
            component_analysis = analysis.get('component_analysis', {})
            
            for component, stats in component_analysis.items():
                # Base health calculation
                total_entries = stats.get('total_entries', 1)
                errors = stats.get('errors', 0)
                warnings = stats.get('warnings', 0)
                
                # Calculate base score (100 - error/warning penalty)
                error_penalty = min((errors / total_entries) * 50, 40)  # Max 40% penalty for errors
                warning_penalty = min((warnings / total_entries) * 25, 20)  # Max 20% penalty for warnings
                base_score = max(100 - error_penalty - warning_penalty, 0)
                
                # ML Enhancement: Pattern analysis
                component_patterns = self._analyze_component_patterns(component, log_entries)
                pattern_modifier = self._calculate_pattern_health_modifier(component_patterns)
                
                # Time-based analysis
                time_modifier = self._calculate_time_based_health_modifier(component, log_entries)
                
                # Final health score
                final_score = max(min(base_score + pattern_modifier + time_modifier, 100), 0)
                
                # Health status classification
                if final_score >= 90:
                    status = "excellent"
                    status_icon = "🟢"
                elif final_score >= 75:
                    status = "good"
                    status_icon = "🟡"
                elif final_score >= 60:
                    status = "fair"
                    status_icon = "🟠"
                else:
                    status = "poor"
                    status_icon = "🔴"
                
                component_health[component] = {
                    'health_score': round(final_score, 1),
                    'status': status,
                    'status_icon': status_icon,
                    'total_entries': total_entries,
                    'error_count': errors,
                    'warning_count': warnings,
                    'patterns': component_patterns,
                    'recommendations': self._generate_component_health_recommendations(component, final_score, component_patterns)
                }
            
            return {
                'individual_scores': component_health,
                'overall_health': self._calculate_overall_system_health(component_health),
                'health_trend': self._analyze_health_trends(log_entries),
                'analysis_timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"⚠️ Component health scoring failed: {e}")
            return {}
    
    def _analyze_component_patterns(self, component: str, log_entries: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze patterns specific to each component"""
        patterns = {
            'startup_success': 0,
            'connection_issues': 0,
            'performance_issues': 0,
            'recovery_success': 0,
            'configuration_changes': 0
        }
        
        component_entries = [entry for entry in log_entries 
                           if entry.get('component', '').lower() == component.lower()]
        
        for entry in component_entries:
            message = entry.get('message', '').lower()
            
            # Pattern detection
            if any(word in message for word in ['start', 'load', 'init', 'activate']):
                patterns['startup_success'] += 1
            elif any(word in message for word in ['timeout', 'connection', 'fail']):
                patterns['connection_issues'] += 1
            elif any(word in message for word in ['slow', 'memory', 'cpu', 'performance']):
                patterns['performance_issues'] += 1
            elif any(word in message for word in ['recover', 'reconnect', 'success']):
                patterns['recovery_success'] += 1
            elif any(word in message for word in ['config', 'setting', 'update']):
                patterns['configuration_changes'] += 1
        
        return patterns
    
    def _calculate_pattern_health_modifier(self, patterns: Dict[str, Any]) -> float:
        """Calculate health modifier based on detected patterns"""
        modifier = 0
        
        # Positive patterns
        modifier += patterns.get('startup_success', 0) * 0.5
        modifier += patterns.get('recovery_success', 0) * 1.0
        
        # Negative patterns
        modifier -= patterns.get('connection_issues', 0) * 1.5
        modifier -= patterns.get('performance_issues', 0) * 1.0
        
        return max(min(modifier, 10), -20)  # Cap between -20 and +10
    
    def _calculate_time_based_health_modifier(self, component: str, log_entries: List[Dict[str, Any]]) -> float:
        """Calculate health modifier based on time patterns"""
        try:
            from datetime import datetime, timedelta
            
            recent_entries = []
            now = datetime.now()
            
            for entry in log_entries:
                try:
                    timestamp_str = entry.get('timestamp', '')
                    if timestamp_str:
                        entry_time = datetime.strptime(timestamp_str[:19], '%Y-%m-%d %H:%M:%S')
                        if (now - entry_time).total_seconds() < 3600:  # Last hour
                            recent_entries.append(entry)
                except:
                    continue
            
            if not recent_entries:
                return 0
            
            # Recent activity analysis
            recent_errors = sum(1 for entry in recent_entries 
                              if 'error' in entry.get('message', '').lower())
            
            if recent_errors > len(recent_entries) * 0.3:  # >30% recent errors
                return -5
            elif recent_errors == 0:  # No recent errors
                return 2
            else:
                return 0
                
        except Exception as e:
            print(f"⚠️ Time-based health analysis failed: {e}")
            return 0
    
    def _generate_component_health_recommendations(self, component: str, health_score: float, patterns: Dict[str, Any]) -> List[str]:
        """Generate health-specific recommendations for components"""
        recommendations = []
        
        if health_score < 60:
            recommendations.append(f"🚨 {component} requires immediate attention")
            
            if patterns.get('connection_issues', 0) > 3:
                recommendations.append("🔗 Multiple connection issues detected - check network connectivity")
            
            if patterns.get('performance_issues', 0) > 2:
                recommendations.append("⚡ Performance issues detected - monitor system resources")
        
        elif health_score < 75:
            recommendations.append(f"⚠️ {component} shows signs of degradation")
            recommendations.append("📊 Consider scheduled maintenance during next maintenance window")
        
        else:
            recommendations.append(f"✅ {component} operating within normal parameters")
        
        # Component-specific recommendations
        if component.lower() in ['amsp', 'antimalware', 'anti malware']:
            if patterns.get('startup_success', 0) == 0:
                recommendations.append("🛡️ Anti-malware engine may need restart")
        elif component.lower() in ['firewall', 'fw']:
            if patterns.get('configuration_changes', 0) > 5:
                recommendations.append("🔥 Frequent firewall rule changes detected")
        
        return recommendations
    
    def _calculate_overall_system_health(self, component_health: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate overall system health from component scores"""
        if not component_health:
            return {'score': 0, 'status': 'unknown'}
        
        scores = [comp['health_score'] for comp in component_health.values()]
        overall_score = sum(scores) / len(scores)
        
        # Weight critical components more heavily
        critical_components = ['Agent Core', 'Anti Malware', 'Firewall']
        critical_scores = [comp['health_score'] for name, comp in component_health.items() 
                         if name in critical_components]
        
        if critical_scores:
            weighted_score = (overall_score * 0.6) + (sum(critical_scores) / len(critical_scores) * 0.4)
        else:
            weighted_score = overall_score
        
        if weighted_score >= 85:
            status = "healthy"
            status_icon = "🟢"
        elif weighted_score >= 70:
            status = "stable"
            status_icon = "🟡"
        elif weighted_score >= 50:
            status = "degraded"
            status_icon = "🟠"
        else:
            status = "critical"
            status_icon = "🔴"
        
        return {
            'score': round(weighted_score, 1),
            'status': status,
            'status_icon': status_icon,
            'component_count': len(component_health)
        }
    
    def _analyze_health_trends(self, log_entries: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze health trends over time"""
        try:
            from datetime import datetime, timedelta
            
            if len(log_entries) < 10:
                return {'trend': 'insufficient_data', 'direction': 'stable'}
            
            # Split entries into time periods
            sorted_entries = sorted(log_entries, key=lambda x: x.get('timestamp', ''))
            
            first_half = sorted_entries[:len(sorted_entries)//2]
            second_half = sorted_entries[len(sorted_entries)//2:]
            
            # Calculate error rates for each half
            first_half_errors = sum(1 for entry in first_half 
                                  if 'error' in entry.get('message', '').lower())
            second_half_errors = sum(1 for entry in second_half 
                                   if 'error' in entry.get('message', '').lower())
            
            first_rate = first_half_errors / len(first_half) if first_half else 0
            second_rate = second_half_errors / len(second_half) if second_half else 0
            
            # Determine trend
            if second_rate > first_rate * 1.2:  # >20% increase
                trend = 'degrading'
                direction = '📉'
            elif second_rate < first_rate * 0.8:  # >20% decrease
                trend = 'improving'
                direction = '📈'
            else:
                trend = 'stable'
                direction = '➡️'
            
            return {
                'trend': trend,
                'direction': direction,
                'first_period_error_rate': round(first_rate * 100, 1),
                'second_period_error_rate': round(second_rate * 100, 1)
            }
            
        except Exception as e:
            print(f"⚠️ Health trend analysis failed: {e}")
            return {'trend': 'unknown', 'direction': '❓'}
    
    def _analyze_smart_log_patterns(self, log_entries: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Use ML clustering to identify smart log patterns and anomalies"""
        try:
            if not log_entries or len(log_entries) < 5:
                return {'status': 'insufficient_data', 'patterns': [], 'anomalies': []}
            
            pattern_analysis = {
                'message_clusters': [],
                'anomalous_patterns': [],
                'recurring_sequences': [],
                'temporal_patterns': {},
                'component_interaction_patterns': {},
                'similarity_groups': [],
                'anomaly_score': 0.0,
                'pattern_insights': []
            }
            
            # Extract feature vectors for clustering
            feature_vectors, message_features = self._extract_pattern_features(log_entries)
            
            if len(feature_vectors) < 3:
                return pattern_analysis
            
            # Perform ML clustering on log patterns
            clusters, cluster_labels = self._perform_smart_clustering(feature_vectors)
            
            # Analyze clusters for patterns
            pattern_analysis['message_clusters'] = self._analyze_message_clusters(
                log_entries, clusters, cluster_labels, message_features
            )
            
            # Detect anomalous patterns
            pattern_analysis['anomalous_patterns'] = self._detect_anomalous_patterns(
                log_entries, cluster_labels, clusters
            )
            
            # Find recurring sequences
            pattern_analysis['recurring_sequences'] = self._find_recurring_sequences(log_entries)
            
            # Analyze temporal patterns
            pattern_analysis['temporal_patterns'] = self._analyze_temporal_patterns(log_entries)
            
            # Component interaction analysis
            pattern_analysis['component_interaction_patterns'] = self._analyze_component_interactions(log_entries)
            
            # Generate pattern insights
            pattern_analysis['pattern_insights'] = self._generate_pattern_insights(pattern_analysis)
            
            # Calculate overall anomaly score
            pattern_analysis['anomaly_score'] = self._calculate_pattern_anomaly_score(pattern_analysis)
            
            return pattern_analysis
            
        except Exception as e:
            print(f"⚠️ Smart pattern analysis failed: {e}")
            return {'status': 'error', 'error': str(e), 'patterns': [], 'anomalies': []}
    
    def _extract_pattern_features(self, log_entries: List[Dict[str, Any]]) -> tuple:
        """Extract numerical features for ML clustering from log entries"""
        try:
            import re
            from collections import Counter
            
            feature_vectors = []
            message_features = []
            
            for entry in log_entries:
                message = entry.get('message', '').lower()
                component = entry.get('component', '').lower()
                timestamp = entry.get('timestamp', '')
                
                # Extract numerical features
                features = {
                    'message_length': len(message),
                    'word_count': len(message.split()),
                    'number_count': len(re.findall(r'\d+', message)),
                    'special_char_count': len(re.findall(r'[^a-zA-Z0-9\s]', message)),
                    'uppercase_ratio': sum(1 for c in message if c.isupper()) / max(len(message), 1),
                    'has_error_keyword': 1 if any(kw in message for kw in ['error', 'fail', 'timeout']) else 0,
                    'has_warning_keyword': 1 if any(kw in message for kw in ['warning', 'warn']) else 0,
                    'has_success_keyword': 1 if any(kw in message for kw in ['success', 'start', 'load', 'connect']) else 0,
                    'component_criticality': self._get_component_criticality(component),
                    'hour_of_day': self._extract_hour_from_timestamp(timestamp),
                    'message_entropy': self._calculate_message_entropy(message),
                    'has_ip_address': 1 if re.search(r'\d+\.\d+\.\d+\.\d+', message) else 0,
                    'has_file_path': 1 if re.search(r'[a-zA-Z]:\\\\|/', message) else 0,
                    'thread_id_present': 1 if 'thread' in message.lower() else 0
                }
                
                # Create feature vector
                feature_vector = [
                    features['message_length'],
                    features['word_count'],
                    features['number_count'],
                    features['special_char_count'],
                    features['uppercase_ratio'],
                    features['has_error_keyword'],
                    features['has_warning_keyword'],
                    features['has_success_keyword'],
                    features['component_criticality'],
                    features['hour_of_day'],
                    features['message_entropy'],
                    features['has_ip_address'],
                    features['has_file_path'],
                    features['thread_id_present']
                ]
                
                feature_vectors.append(feature_vector)
                message_features.append({
                    'message': message,
                    'component': component,
                    'features': features,
                    'original_entry': entry
                })
            
            return feature_vectors, message_features
            
        except Exception as e:
            print(f"⚠️ Feature extraction failed: {e}")
            return [], []
    
    def _perform_smart_clustering(self, feature_vectors: List[List[float]]) -> tuple:
        """Perform ML clustering on feature vectors"""
        try:
            if not ML_AVAILABLE or len(feature_vectors) < 3:
                # Simple rule-based clustering fallback
                return self._simple_clustering_fallback(feature_vectors)
            
            from sklearn.cluster import KMeans
            from sklearn.preprocessing import StandardScaler
            import numpy as np
            
            # Normalize features
            scaler = StandardScaler()
            normalized_features = scaler.fit_transform(feature_vectors)
            
            # Determine optimal number of clusters (between 2 and min(8, n_samples//2))
            n_samples = len(feature_vectors)
            max_clusters = min(8, max(2, n_samples // 2))
            
            # Use K-means clustering
            n_clusters = min(max_clusters, 5)  # Default to 5 clusters max
            kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
            cluster_labels = kmeans.fit_predict(normalized_features)
            
            # Group features by cluster
            clusters = {}
            for i, label in enumerate(cluster_labels):
                if label not in clusters:
                    clusters[label] = []
                clusters[label].append(i)
            
            return clusters, cluster_labels
            
        except Exception as e:
            print(f"⚠️ ML clustering failed: {e}")
            return self._simple_clustering_fallback(feature_vectors)
    
    def _simple_clustering_fallback(self, feature_vectors: List[List[float]]) -> tuple:
        """Simple rule-based clustering when ML is not available"""
        clusters = {0: [], 1: [], 2: []}  # Error, Warning, Normal clusters
        cluster_labels = []
        
        for i, features in enumerate(feature_vectors):
            # Simple classification based on error/warning keywords
            if features[5] == 1:  # has_error_keyword
                clusters[0].append(i)
                cluster_labels.append(0)
            elif features[6] == 1:  # has_warning_keyword
                clusters[1].append(i)
                cluster_labels.append(1)
            else:
                clusters[2].append(i)
                cluster_labels.append(2)
        
        return clusters, cluster_labels
    
    def _analyze_message_clusters(self, log_entries: List[Dict[str, Any]], clusters: Dict, 
                                cluster_labels: List[int], message_features: List[Dict]) -> List[Dict[str, Any]]:
        """Analyze clusters to identify common patterns"""
        cluster_analysis = []
        
        for cluster_id, entry_indices in clusters.items():
            if not entry_indices:
                continue
                
            cluster_messages = [message_features[i] for i in entry_indices]
            
            # Find common patterns in this cluster
            common_words = self._find_common_words(cluster_messages)
            common_components = self._find_common_components(cluster_messages)
            
            # Calculate cluster characteristics
            avg_criticality = sum(msg['features']['component_criticality'] for msg in cluster_messages) / len(cluster_messages)
            error_ratio = sum(msg['features']['has_error_keyword'] for msg in cluster_messages) / len(cluster_messages)
            
            cluster_info = {
                'cluster_id': cluster_id,
                'size': len(entry_indices),
                'common_words': common_words[:5],  # Top 5 common words
                'dominant_components': common_components[:3],  # Top 3 components
                'avg_criticality': round(avg_criticality, 2),
                'error_ratio': round(error_ratio, 2),
                'sample_messages': [msg['message'][:100] for msg in cluster_messages[:3]],
                'pattern_type': self._classify_cluster_pattern(avg_criticality, error_ratio),
                'insights': self._generate_cluster_insights(cluster_messages, common_words, common_components)
            }
            
            cluster_analysis.append(cluster_info)
        
        return cluster_analysis
    
    def _detect_anomalous_patterns(self, log_entries: List[Dict[str, Any]], 
                                 cluster_labels: List[int], clusters: Dict) -> List[Dict[str, Any]]:
        """Detect anomalous patterns that don't fit normal clusters"""
        anomalies = []
        
        # Find small clusters (potential anomalies)
        total_entries = len(log_entries)
        
        for cluster_id, entry_indices in clusters.items():
            cluster_size = len(entry_indices)
            
            # Consider clusters with <5% of total entries as potentially anomalous
            if cluster_size < max(2, total_entries * 0.05):
                for idx in entry_indices:
                    if idx < len(log_entries):
                        entry = log_entries[idx]
                        anomaly = {
                            'entry_index': idx,
                            'message': entry.get('message', ''),
                            'component': entry.get('component', ''),
                            'timestamp': entry.get('timestamp', ''),
                            'anomaly_reason': f'Rare pattern (cluster size: {cluster_size})',
                            'cluster_id': cluster_id,
                            'anomaly_score': 1.0 - (cluster_size / total_entries)
                        }
                        anomalies.append(anomaly)
        
        # Sort by anomaly score (highest first)
        anomalies.sort(key=lambda x: x['anomaly_score'], reverse=True)
        
        return anomalies[:10]  # Return top 10 anomalies
    
    def _find_recurring_sequences(self, log_entries: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Find recurring sequences of log patterns"""
        sequences = []
        
        if len(log_entries) < 6:
            return sequences
        
        try:
            # Look for sequences of 2-3 consecutive entries that repeat
            for seq_length in [2, 3]:
                sequence_counts = {}
                
                for i in range(len(log_entries) - seq_length + 1):
                    # Create sequence signature
                    sequence = []
                    for j in range(seq_length):
                        entry = log_entries[i + j]
                        signature = f"{entry.get('component', '')}:{entry.get('message', '')[:50]}"
                        sequence.append(signature)
                    
                    seq_key = " -> ".join(sequence)
                    sequence_counts[seq_key] = sequence_counts.get(seq_key, 0) + 1
                
                # Find sequences that occur multiple times
                for seq_key, count in sequence_counts.items():
                    if count >= 2:  # Occurs at least twice
                        sequences.append({
                            'sequence': seq_key,
                            'length': seq_length,
                            'occurrences': count,
                            'frequency': round(count / len(log_entries), 3)
                        })
            
            # Sort by frequency
            sequences.sort(key=lambda x: x['occurrences'], reverse=True)
            return sequences[:5]  # Return top 5 recurring sequences
            
        except Exception as e:
            print(f"⚠️ Sequence analysis failed: {e}")
            return []
    
    def _analyze_temporal_patterns(self, log_entries: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze temporal patterns in log entries"""
        try:
            hourly_distribution = {}
            component_timing = {}
            
            for entry in log_entries:
                hour = self._extract_hour_from_timestamp(entry.get('timestamp', ''))
                component = entry.get('component', 'unknown')
                
                # Hourly distribution
                hourly_distribution[hour] = hourly_distribution.get(hour, 0) + 1
                
                # Component timing patterns
                if component not in component_timing:
                    component_timing[component] = {}
                component_timing[component][hour] = component_timing[component].get(hour, 0) + 1
            
            # Find peak hours
            peak_hour = max(hourly_distribution.items(), key=lambda x: x[1])[0] if hourly_distribution else 12
            
            return {
                'hourly_distribution': hourly_distribution,
                'peak_hour': peak_hour,
                'component_timing': component_timing,
                'total_unique_hours': len(hourly_distribution)
            }
            
        except Exception as e:
            print(f"⚠️ Temporal analysis failed: {e}")
            return {}
    
    def _analyze_component_interactions(self, log_entries: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze interactions between different components"""
        try:
            component_sequences = []
            component_counts = {}
            
            # Track component transitions
            for i in range(len(log_entries) - 1):
                current_comp = log_entries[i].get('component', 'unknown')
                next_comp = log_entries[i + 1].get('component', 'unknown')
                
                component_counts[current_comp] = component_counts.get(current_comp, 0) + 1
                
                if current_comp != next_comp:
                    transition = f"{current_comp} -> {next_comp}"
                    component_sequences.append(transition)
            
            # Count transition frequencies
            transition_counts = {}
            for transition in component_sequences:
                transition_counts[transition] = transition_counts.get(transition, 0) + 1
            
            # Find most common transitions
            common_transitions = sorted(transition_counts.items(), key=lambda x: x[1], reverse=True)[:5]
            
            return {
                'component_counts': component_counts,
                'common_transitions': common_transitions,
                'total_transitions': len(component_sequences),
                'unique_components': len(component_counts)
            }
            
        except Exception as e:
            print(f"⚠️ Component interaction analysis failed: {e}")
            return {}
    
    def _find_common_words(self, cluster_messages: List[Dict]) -> List[str]:
        """Find common words in cluster messages"""
        from collections import Counter
        
        all_words = []
        for msg in cluster_messages:
            words = msg['message'].split()
            # Filter out very common words
            filtered_words = [w for w in words if len(w) > 3 and w not in ['the', 'and', 'for', 'with', 'from']]
            all_words.extend(filtered_words)
        
        word_counts = Counter(all_words)
        return [word for word, count in word_counts.most_common(10) if count > 1]
    
    def _find_common_components(self, cluster_messages: List[Dict]) -> List[str]:
        """Find common components in cluster messages"""
        from collections import Counter
        
        components = [msg['component'] for msg in cluster_messages]
        component_counts = Counter(components)
        return [comp for comp, count in component_counts.most_common(5)]
    
    def _classify_cluster_pattern(self, avg_criticality: float, error_ratio: float) -> str:
        """Classify the type of pattern in a cluster"""
        if error_ratio > 0.7:
            return "Error Pattern"
        elif error_ratio > 0.3:
            return "Mixed Issues Pattern"
        elif avg_criticality > 0.8:
            return "Critical Component Pattern"
        else:
            return "Normal Operations Pattern"
    
    def _generate_cluster_insights(self, cluster_messages: List[Dict], 
                                 common_words: List[str], common_components: List[str]) -> List[str]:
        """Generate insights for a cluster"""
        insights = []
        
        if len(cluster_messages) > len(set(msg['message'] for msg in cluster_messages)) * 0.5:
            insights.append("High message similarity - potential recurring issue")
        
        if common_words:
            insights.append(f"Common keywords: {', '.join(common_words[:3])}")
        
        if len(common_components) == 1:
            insights.append(f"Component-specific pattern: {common_components[0]}")
        
        error_count = sum(msg['features']['has_error_keyword'] for msg in cluster_messages)
        if error_count > len(cluster_messages) * 0.5:
            insights.append("Error-dominated cluster - requires attention")
        
        return insights
    
    def _generate_pattern_insights(self, pattern_analysis: Dict[str, Any]) -> List[str]:
        """Generate high-level insights from pattern analysis"""
        insights = []
        
        clusters = pattern_analysis.get('message_clusters', [])
        anomalies = pattern_analysis.get('anomalous_patterns', [])
        sequences = pattern_analysis.get('recurring_sequences', [])
        
        if len(clusters) > 5:
            insights.append(f"📊 {len(clusters)} distinct log patterns identified - diverse system activity")
        elif len(clusters) <= 2:
            insights.append("📊 Limited pattern diversity - system behavior appears consistent")
        
        if len(anomalies) > 0:
            insights.append(f"🔍 {len(anomalies)} anomalous patterns detected - investigate unusual activity")
        
        if len(sequences) > 0:
            insights.append(f"🔄 {len(sequences)} recurring sequences found - potential automated processes")
        
        # Error cluster analysis
        error_clusters = [c for c in clusters if c.get('error_ratio', 0) > 0.5]
        if error_clusters:
            insights.append(f"⚠️ {len(error_clusters)} error-dominated patterns identified")
        
        return insights
    
    def _calculate_pattern_anomaly_score(self, pattern_analysis: Dict[str, Any]) -> float:
        """Calculate overall anomaly score based on pattern analysis"""
        try:
            score = 0.0
            
            # Anomalous patterns contribute to score
            anomalies = pattern_analysis.get('anomalous_patterns', [])
            if anomalies:
                score += min(len(anomalies) * 0.1, 0.5)
            
            # High number of small clusters indicates irregularity
            clusters = pattern_analysis.get('message_clusters', [])
            small_clusters = [c for c in clusters if c.get('size', 0) < 3]
            if len(small_clusters) > len(clusters) * 0.5:
                score += 0.3
            
            # Few recurring sequences might indicate inconsistent behavior
            sequences = pattern_analysis.get('recurring_sequences', [])
            if len(sequences) == 0 and len(clusters) > 3:
                score += 0.2
            
            return min(score, 1.0)
            
        except Exception as e:
            print(f"⚠️ Anomaly score calculation failed: {e}")
            return 0.0

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
        """Check if log entry matches known issues with AI enhancement"""
        if not log_entry.get('parsed'):
            return None
        
        message = log_entry['message']
        
        # Check static known issues first
        for issue_key, issue_info in self.known_issues.items():
            if issue_key.lower() in message.lower():
                return {
                    'issue_type': issue_key,
                    'severity': issue_info['severity'],
                    'description': issue_info['description'],
                    'resolution': issue_info['resolution'],
                    'impact': issue_info['impact'],
                    'confidence': 0.9,  # High confidence for known patterns
                    'source': 'static_database'
                }
        
        # AI-Enhanced Issue Detection for unknown patterns
        if hasattr(self, 'ml_analyzer') and self.ml_analyzer:
            try:
                ai_issue_analysis = self._analyze_unknown_issue_with_ai(log_entry)
                if ai_issue_analysis:
                    return ai_issue_analysis
            except Exception as e:
                print(f"⚠️ AI issue analysis failed: {e}")
        
        return None
    
    def _analyze_unknown_issue_with_ai(self, log_entry: Dict[str, Any]) -> Dict[str, Any]:
        """Use AI to analyze unknown issues and generate insights"""
        try:
            if not DYNAMIC_RAG_AVAILABLE:
                return None
                
            from dynamic_rag_system import DynamicRAGSystem
            
            # Create AI prompt for issue analysis
            issue_prompt = f"""
            Analyze this Deep Security Agent log entry for potential issues:
            
            Timestamp: {log_entry.get('timestamp', 'Unknown')}
            Component: {log_entry.get('component', 'Unknown')}
            Message: {log_entry.get('message', '')}
            Location: {log_entry.get('location', 'Unknown')}
            
            Provide analysis in this format:
            - Issue Type: [Brief identifier]
            - Severity: [critical/high/medium/low] 
            - Description: [Technical explanation]
            - Resolution: [Specific troubleshooting steps]
            - Impact: [Business/operational impact]
            - Confidence: [0.0-1.0 confidence score]
            
            Focus on actionable technical guidance for support staff.
            """
            
            # Use RAG system for intelligent analysis
            rag_system = DynamicRAGSystem()
            
            # Create context for RAG analysis
            rag_results = rag_system.process_log_with_dynamic_rag(issue_prompt)
            ai_response = rag_results.get('ai_response', '')
            
            if ai_response:
                # Parse AI response into structured format
                parsed_analysis = self._parse_ai_issue_response(ai_response)
                if parsed_analysis:
                    parsed_analysis['source'] = 'ai_analysis'
                    return parsed_analysis
                    
        except Exception as e:
            print(f"⚠️ AI issue analysis error: {e}")
            
        return None
    
    def _parse_ai_issue_response(self, ai_response: str) -> Dict[str, Any]:
        """Parse AI response into structured issue analysis"""
        try:
            import re
            
            # Extract key information using regex patterns
            issue_type_match = re.search(r'Issue Type:\s*(.+)', ai_response, re.IGNORECASE)
            severity_match = re.search(r'Severity:\s*(critical|high|medium|low)', ai_response, re.IGNORECASE)
            description_match = re.search(r'Description:\s*(.+?)(?=Resolution:|Impact:|$)', ai_response, re.IGNORECASE | re.DOTALL)
            resolution_match = re.search(r'Resolution:\s*(.+?)(?=Impact:|Confidence:|$)', ai_response, re.IGNORECASE | re.DOTALL)
            impact_match = re.search(r'Impact:\s*(.+?)(?=Confidence:|$)', ai_response, re.IGNORECASE | re.DOTALL)
            confidence_match = re.search(r'Confidence:\s*([0-9.]+)', ai_response, re.IGNORECASE)
            
            if issue_type_match and severity_match:
                return {
                    'issue_type': issue_type_match.group(1).strip(),
                    'severity': severity_match.group(1).lower(),
                    'description': description_match.group(1).strip() if description_match else 'AI-generated analysis',
                    'resolution': resolution_match.group(1).strip() if resolution_match else 'Contact support for guidance',
                    'impact': impact_match.group(1).strip() if impact_match else 'Unknown impact',
                    'confidence': float(confidence_match.group(1)) if confidence_match else 0.7,
                    'ai_enhanced': True
                }
        except Exception as e:
            print(f"⚠️ AI response parsing error: {e}")
            
        return None

    def extract_module_status(self, log_content: str) -> Dict[str, Any]:
        """Extract DS Agent module status information"""
        module_status = {}
        enabled_modules = []
        disabled_modules = []
        
        for module_name, pattern in self.module_status_patterns.items():
            matches = pattern.findall(log_content)
            if matches:
                # Get the most recent status for each module
                latest_status = matches[-1].lower()
                module_status[module_name] = latest_status == 'true'
                
                if latest_status == 'true':
                    enabled_modules.append(module_name.replace('_', ' ').title())
                else:
                    disabled_modules.append(module_name.replace('_', ' ').title())
        
        return {
            'module_status': module_status,
            'enabled_modules': enabled_modules,
            'disabled_modules': disabled_modules,
            'total_modules': len(module_status)
        }

    def extract_configuration(self, log_content: str) -> Dict[str, Any]:
        """Extract DS Agent configuration settings"""
        configuration = {}
        
        for config_name, pattern in self.configuration_patterns.items():
            matches = pattern.findall(log_content)
            if matches:
                if config_name == 'proxy_settings':
                    # Special handling for proxy settings tuple
                    latest_match = matches[-1]
                    configuration[config_name] = {
                        'auto': latest_match[0],
                        'pac_url': latest_match[1] if latest_match[1] != '(null)' else None,
                        'static_proxy': latest_match[2] if latest_match[2] != '(null)' else None,
                        'bypass': latest_match[3] if latest_match[3] != '(null)' else None
                    }
                elif config_name == 'bios_uuid':
                    # Special handling for BIOS UUID change
                    latest_match = matches[-1]
                    configuration[config_name] = {
                        'old': latest_match[0],
                        'new': latest_match[1]
                    }
                else:
                    # Standard single value extraction
                    configuration[config_name] = matches[-1]
        
        return configuration

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
            'ml_insights': None,
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
                
                # Enhanced file type detection for DPI/Firewall logs
                if first_line and '[fwdpi/' in first_line.lower():
                    print(f"⚠️  Detected DPI/Firewall log content - this may contain mixed DS Agent and DPI data")
                    print(f"🔍 First line: {first_line[:200]}")
                
                # Progress: 15% - Extracting log entries
                self._update_progress('File Parsing & Initial Analysis', 'Extracting log entries and timestamps...', 15)
                
                for line_num, line in enumerate(f, 1):
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
                        progress = min(15 + (line_num / 50000) * 10, 25)  # 15% to 25% for up to 50k lines
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
            
            # NEW: Extract module status and configuration information
            self._update_progress('Module Status & Configuration', 'Extracting module status and configuration...', 60)
            
            # Read full log content for pattern extraction
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                full_log_content = f.read()
            
            # Extract module status information
            module_status_info = self.extract_module_status(full_log_content)
            results['module_status'] = module_status_info
            
            # Extract configuration information
            configuration_info = self.extract_configuration(full_log_content)
            results['configuration'] = configuration_info
            
            # Connection Health Analysis for Cloud One Workload Security  
            all_log_entries = []
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                for line_num, line in enumerate(f, 1):
                    log_entry = self.parse_log_entry(line.strip())
                    if log_entry['parsed']:
                        log_entry['line'] = line_num
                        all_log_entries.append(log_entry)
            
            # NEW: Component Health Scoring with ML
            component_health_scores = self._calculate_component_health_scores(results, all_log_entries)
            results['component_health'] = component_health_scores
            
            # Merge health scores into component analysis for enhanced display
            if component_health_scores and 'individual_scores' in component_health_scores:
                for component, health_data in component_health_scores['individual_scores'].items():
                    if component in results['component_analysis']:
                        results['component_analysis'][component]['health_score'] = health_data['health_score']
                        results['component_analysis'][component]['status'] = health_data['status']
                        results['component_analysis'][component]['status_icon'] = health_data['status_icon']
            
            # NEW: Smart Log Pattern Recognition with ML Clustering
            pattern_analysis = self._analyze_smart_log_patterns(all_log_entries)
            results['pattern_analysis'] = pattern_analysis
            
            # NEW: Cross-Component Relationship Analysis
            cross_component_relations = self._analyze_cross_component_relations(results, all_log_entries)
            results['cross_component_relations'] = cross_component_relations
            
            # NEW: Enhanced Analysis Details Generation  
            analysis_details = self._generate_enhanced_analysis_details(results, all_log_entries)
            results['analysis_details'] = analysis_details
            
            self._update_progress('Module Status & Configuration', 'Module status and configuration extracted', 65)
            
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
    
    def _analyze_cross_component_relations(self, results: Dict[str, Any], log_entries: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze cross-component relationships and dependencies from log patterns
        """
        try:
            cross_relations = {
                'component_interactions': {},
                'dependency_chains': [],
                'error_propagation': [],
                'communication_patterns': [],
                'relationship_summary': {}
            }
            
            component_interactions = {}
            component_timeline = {}
            
            # Analyze log entries for cross-component patterns
            for entry in log_entries:
                component = self.identify_component(entry)
                timestamp = entry.get('timestamp', '')
                message = entry.get('message', '')
                
                # Track component timeline
                if component not in component_timeline:
                    component_timeline[component] = []
                component_timeline[component].append({
                    'timestamp': timestamp,
                    'message': message,
                    'severity': self.categorize_severity(entry)
                })
                
                # Detect cross-component communication patterns
                if 'connecting to' in message.lower() or 'communicating with' in message.lower():
                    cross_relations['communication_patterns'].append({
                        'source': component,
                        'message': message,
                        'timestamp': timestamp,
                        'type': 'communication'
                    })
                
                # Detect dependency chains
                if 'depends on' in message.lower() or 'waiting for' in message.lower():
                    cross_relations['dependency_chains'].append({
                        'dependent': component,
                        'dependency': message,
                        'timestamp': timestamp
                    })
            
            # Analyze error propagation patterns
            error_components = []
            for component, events in component_timeline.items():
                error_events = [e for e in events if e['severity'] in ['critical', 'error']]
                if error_events:
                    error_components.append({
                        'component': component,
                        'error_count': len(error_events),
                        'first_error': error_events[0]['timestamp'] if error_events else None,
                        'last_error': error_events[-1]['timestamp'] if error_events else None
                    })
            
            # Sort by error timing to detect propagation
            error_components.sort(key=lambda x: x['first_error'] or '')
            cross_relations['error_propagation'] = error_components
            
            # Generate relationship summary
            total_components = len(component_timeline)
            communicating_components = len(cross_relations['communication_patterns'])
            dependent_components = len(cross_relations['dependency_chains'])
            
            cross_relations['relationship_summary'] = {
                'total_components': total_components,
                'communicating_components': communicating_components,
                'dependent_components': dependent_components,
                'error_affected_components': len(error_components),
                'complexity_score': min(100, (communicating_components + dependent_components) * 10)
            }
            
            return cross_relations
            
        except Exception as e:
            print(f"⚠️ Cross-component analysis failed: {e}")
            return {
                'component_interactions': {},
                'dependency_chains': [],
                'error_propagation': [],
                'communication_patterns': [],
                'relationship_summary': {'error': str(e)}
            }
    
    def _generate_enhanced_analysis_details(self, results: Dict[str, Any], log_entries: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate enhanced analysis details with technical insights
        """
        try:
            summary = results.get('summary', {})
            component_analysis = results.get('component_analysis', {})
            cross_relations = results.get('cross_component_relations', {})
            
            analysis_details = {
                'summary_statistics': self._format_summary_statistics(summary),
                'issue_analysis': self._format_issue_analysis(results),
                'component_details': self._format_component_details(component_analysis),
                'cross_component_analysis': self._format_cross_component_analysis(cross_relations),
                'ai_analysis': self._format_ai_analysis_details(results),
                'troubleshooting': self._format_troubleshooting_guidance(results)
            }
            
            return analysis_details
            
        except Exception as e:
            print(f"⚠️ Enhanced analysis details generation failed: {e}")
            return {
                'summary_statistics': 'Analysis details could not be generated',
                'error': str(e)
            }
    
    def _format_summary_statistics(self, summary: Dict[str, Any]) -> str:
        """Format summary statistics into detailed analysis text"""
        total_lines = summary.get('total_lines', 0)
        parsed_lines = summary.get('parsed_lines', 0)
        parsing_rate = (parsed_lines / total_lines * 100) if total_lines > 0 else 0
        
        return f"""
        <strong>File Processing Analysis:</strong><br>
        • Total log entries processed: {total_lines:,}<br>
        • Successfully parsed entries: {parsed_lines:,}<br>
        • Parsing efficiency: {parsing_rate:.1f}%<br>
        • Time span: {summary.get('timespan', {}).get('start', 'Unknown')} to {summary.get('timespan', {}).get('end', 'Unknown')}<br>
        
        <strong>Issue Distribution:</strong><br>
        • Critical issues requiring immediate attention: {summary.get('critical_count', 0)}<br>
        • Error conditions detected: {summary.get('error_count', 0)}<br>
        • Warning conditions logged: {summary.get('warning_count', 0)}<br>
        """
    
    def _format_issue_analysis(self, results: Dict[str, Any]) -> str:
        """Format detailed issue analysis"""
        errors = results.get('errors', [])
        critical_issues = results.get('critical_issues', [])
        known_issues = results.get('known_issues', [])
        
        analysis = f"<strong>Critical Issue Analysis:</strong><br>"
        if critical_issues:
            analysis += f"• {len(critical_issues)} critical issues detected requiring immediate investigation<br>"
        else:
            analysis += "• No critical issues detected - system appears stable<br>"
        
        analysis += f"<strong>Error Pattern Analysis:</strong><br>"
        if errors:
            analysis += f"• {len(errors)} error conditions logged<br>"
            # Group errors by component
            error_by_component = {}
            for error in errors[:10]:  # Analyze top 10 errors
                comp = error.get('component', 'Unknown')
                if comp not in error_by_component:
                    error_by_component[comp] = 0
                error_by_component[comp] += 1
            
            for comp, count in error_by_component.items():
                analysis += f"• {comp}: {count} errors<br>"
        else:
            analysis += "• No significant error patterns detected<br>"
        
        analysis += f"<strong>Known Issue Recognition:</strong><br>"
        if known_issues:
            analysis += f"• {len(known_issues)} recognized patterns matched against knowledge base<br>"
        else:
            analysis += "• No known issue patterns detected<br>"
        
        return analysis
    
    def _format_component_details(self, component_analysis: Dict[str, Any]) -> str:
        """Format component analysis details"""
        if not component_analysis:
            return "No component analysis data available"
        
        details = "<strong>Component Health Assessment:</strong><br>"
        for component, stats in component_analysis.items():
            total = stats.get('total_entries', 0)
            errors = stats.get('errors', 0)
            warnings = stats.get('warnings', 0)
            
            health_score = max(0, 100 - (errors * 10) - (warnings * 2))
            health_status = "Excellent" if health_score >= 90 else "Good" if health_score >= 70 else "Fair" if health_score >= 50 else "Poor"
            
            details += f"• <strong>{component}</strong>: {total} entries, {errors} errors, {warnings} warnings (Health: {health_status} - {health_score}/100)<br>"
        
        return details
    
    def _format_cross_component_analysis(self, cross_relations: Dict[str, Any]) -> str:
        """Format cross-component relationship analysis"""
        if not cross_relations or not cross_relations.get('relationship_summary'):
            return "Cross-component analysis not available"
        
        summary = cross_relations['relationship_summary']
        details = f"<strong>Cross-Component Relationship Analysis:</strong><br>"
        details += f"• Total components identified: {summary.get('total_components', 0)}<br>"
        details += f"• Inter-component communications detected: {summary.get('communicating_components', 0)}<br>"
        details += f"• Component dependencies identified: {summary.get('dependent_components', 0)}<br>"
        details += f"• Components affected by errors: {summary.get('error_affected_components', 0)}<br>"
        details += f"• System complexity score: {summary.get('complexity_score', 0)}/100<br>"
        
        # Add communication patterns
        comm_patterns = cross_relations.get('communication_patterns', [])
        if comm_patterns:
            details += f"<br><strong>Communication Patterns Detected:</strong><br>"
            for pattern in comm_patterns[:3]:  # Show top 3
                details += f"• {pattern.get('source', 'Unknown')}: {pattern.get('message', '')[:100]}...<br>"
        
        return details
    
    def _format_ai_analysis_details(self, results: Dict[str, Any]) -> str:
        """Format AI analysis insights"""
        ml_insights = results.get('ml_insights')
        rag_insights = results.get('rag_insights') or results.get('dynamic_rag_analysis')
        
        analysis = "<strong>AI-Enhanced Analysis:</strong><br>"
        
        if ml_insights:
            analysis += "• Machine Learning pattern recognition applied<br>"
            analysis += "• Anomaly detection algorithms processed log data<br>"
        
        if rag_insights and not rag_insights.get('error'):
            sources_used = rag_insights.get('analysis_metadata', {}).get('knowledge_sources_used', 0)
            analysis += f"• Dynamic RAG system consulted {sources_used} knowledge sources<br>"
            if rag_insights.get('ai_response'):
                ai_summary = rag_insights['ai_response'][:200] + "..." if len(rag_insights['ai_response']) > 200 else rag_insights['ai_response']
                analysis += f"• AI Expert Analysis: {ai_summary}<br>"
        
        if not ml_insights and not rag_insights:
            analysis += "• Standard pattern matching and rule-based analysis applied<br>"
        
        return analysis
    
    def _format_troubleshooting_guidance(self, results: Dict[str, Any]) -> str:
        """Generate troubleshooting guidance based on analysis"""
        critical_count = results.get('summary', {}).get('critical_count', 0)
        error_count = results.get('summary', {}).get('error_count', 0)
        
        guidance = "<strong>Troubleshooting Guidance:</strong><br>"
        
        if critical_count > 0:
            guidance += "• <span style='color: #dc3545;'>IMMEDIATE ACTION REQUIRED</span>: Critical issues detected<br>"
            guidance += "• Review critical issues section for specific remediation steps<br>"
            guidance += "• Consider engaging vendor support for critical system components<br>"
        elif error_count > 10:
            guidance += "• <span style='color: #fd7e14;'>ATTENTION NEEDED</span>: Multiple errors detected<br>"
            guidance += "• Review error patterns to identify root causes<br>"
            guidance += "• Consider preventive maintenance scheduling<br>"
        else:
            guidance += "• <span style='color: #198754;'>SYSTEM STABLE</span>: No immediate actions required<br>"
            guidance += "• Continue regular monitoring and maintenance<br>"
            guidance += "• Review recommendations for optimization opportunities<br>"
        
        return guidance

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
            'connection_health': None,
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
            
            # Generate consolidated recommendations
            consolidated_results['recommendations'] = self.generate_recommendations(consolidated_results)
            
            # NEW: Add Predictive Analysis for proactive troubleshooting
            if len(all_log_entries) > 10:  # Need sufficient data for predictions
                predictive_insights = self._generate_predictive_insights(all_log_entries)
                if predictive_insights:
                    consolidated_results['predictive_analysis'] = predictive_insights
                    # Add predictive recommendations
                    for insight in predictive_insights.get('warnings', []):
                        consolidated_results['recommendations'].append(f'🔮 <strong>Predictive Alert</strong>: {insight}')
            
            # Add multi-file specific recommendations
            if len(file_paths) > 1:
                consolidated_results["recommendations"].insert(0, f'<i class="fa-solid fa-folder me-2"></i>Analyzed {len(file_paths)} log files covering {consolidated_results["summary"]["total_lines"]:,} total log entries')
                
                if consolidated_results['summary']['critical_count'] > 0:
                    consolidated_results["recommendations"].append(f'<i class="fa-solid fa-circle-exclamation me-2"></i>{consolidated_results["summary"]["critical_count"]} critical issues found across all files - prioritize by timestamp')
            
            # ML Enhancement for Dynamic RAG (Consolidated Analysis)
            if ML_AVAILABLE and len(all_log_entries) > 0:
                try:
                    # Combine log content from all files for ML analysis
                    combined_content = "\n".join([f"{entry.get('timestamp', '')} {entry.get('message', '')}" for entry in all_log_entries])
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
                            print(f"⚠  Could not read {file_path} for RAG: {e}")
                    
                    consolidated_results = apply_dynamic_rag_to_analysis(consolidated_results, combined_log_content)
                    
                    dynamic_rag = consolidated_results.get('dynamic_rag_analysis', {})
                    if dynamic_rag and 'error' not in dynamic_rag:
                        print(f"✅ Consolidated Dynamic RAG Analysis: {dynamic_rag.get('analysis_metadata', {}).get('knowledge_sources_used', 0)} sources")
                        
                        # Add dynamic insights to recommendations
                        if dynamic_rag.get('ai_response'):
                            ai_summary = dynamic_rag['ai_response'][:200] + "..." if len(dynamic_rag['ai_response']) > 200 else dynamic_rag['ai_response']
                            consolidated_results['recommendations'].append(f'🧠 <strong>Multi-file AI Analysis</strong>: {ai_summary}')
                    
                except Exception as e:
                    print(f"⚠  Consolidated Dynamic RAG analysis failed: {e}")
                    consolidated_results['dynamic_rag_analysis'] = {'error': str(e)}
            
            print(f"✅ Multiple file analysis completed: {len(file_paths)} files, {consolidated_results['summary']['total_lines']:,} total lines")
            
        except Exception as e:
            raise SecurityError(f"Error analyzing multiple log files: {str(e)}")
        
        # Standardize return structure for frontend compatibility
        return consolidated_results

    def generate_recommendations(self, analysis: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on analysis with AI enhancement"""
        recommendations = []
        
        # Add resolution effectiveness summary at the top
        resolution_summary = self._generate_resolution_summary(analysis)
        if resolution_summary.get('total_issues', 0) > 0:
            high_conf = resolution_summary['high_confidence_resolutions']
            med_conf = resolution_summary['medium_confidence_resolutions']
            low_conf = resolution_summary['low_confidence_resolutions']
            
            summary_text = f"📊 Resolution Confidence Summary: {high_conf} high-confidence, {med_conf} medium-confidence, {low_conf} low-confidence resolutions"
            recommendations.append(summary_text)
            
            # Add automation candidates
            automation_candidates = resolution_summary.get('automation_candidates', [])
            if automation_candidates:
                recommendations.append(f"🤖 Automation Opportunities: {', '.join(automation_candidates[:3])}")
            
            # Add improvement suggestions
            improvements = resolution_summary.get('improvement_suggestions', [])
            recommendations.extend(improvements[:3])  # Limit to top 3 suggestions
        
        # Critical issues - immediate attention
        if analysis['summary']['critical_count'] > 0:
            recommendations.append('<i class="fa-solid fa-circle-exclamation me-2"></i>Critical issues detected - immediate attention required')
            
            # Add AI-powered specific recommendations for critical issues
            if DYNAMIC_RAG_AVAILABLE:
                try:
                    critical_recs = self._get_ai_recommendations_for_critical_issues(analysis)
                    recommendations.extend(critical_recs)
                except Exception as e:
                    print(f"⚠️ AI critical recommendations failed: {e}")
        
        # High error count analysis
        if analysis['summary']['error_count'] > 10:
            recommendations.append('<i class="fa-solid fa-triangle-exclamation me-2"></i>High number of errors detected - review agent configuration')
            
            # Add specific configuration guidance
            config_info = analysis.get('configuration', {})
            if config_info:
                if config_info.get('manager_url'):
                    recommendations.append(f'🔗 Manager Connection: {config_info["manager_url"]} - verify connectivity')
                if config_info.get('proxy_settings'):
                    proxy = config_info['proxy_settings']
                    if proxy.get('static_proxy'):
                        recommendations.append(f'🌐 Proxy Configuration: {proxy["static_proxy"]} - verify proxy accessibility')
        
        # Warning threshold analysis
        if analysis['summary']['warning_count'] > 50:
            recommendations.append('<i class="fa-solid fa-triangle-exclamation me-2"></i>Many warnings detected - consider reviewing agent policies')
        
        # Component-specific analysis with enhanced guidance
        for component, stats in analysis['component_analysis'].items():
            if stats['errors'] > 5:
                component_rec = self._get_component_specific_recommendation(component, stats)
                recommendations.append(component_rec)
        
        # Component Health Scoring insights
        component_health = analysis.get('component_health', {})
        if component_health:
            overall_health = component_health.get('overall_health', {})
            if overall_health.get('score', 0) < 70:
                recommendations.append(f'📊 System Health Score: {overall_health.get("score", 0)}% {overall_health.get("status_icon", "⚠️")} - {overall_health.get("status", "degraded")}')
            
            # Add specific component health alerts
            individual_scores = component_health.get('individual_scores', {})
            for comp_name, comp_data in individual_scores.items():
                if comp_data.get('health_score', 100) < 60:
                    recommendations.append(f'🔴 {comp_name} Health Critical: {comp_data.get("health_score", 0)}% - {", ".join(comp_data.get("recommendations", []))}')
        
        # Known issues analysis with enhanced resolution steps
        issue_counts = {}
        for issue in analysis['known_issues']:
            issue_type = issue['issue_type']
            issue_counts[issue_type] = issue_counts.get(issue_type, 0) + 1
        
        for issue_type, count in issue_counts.items():
            if count > 10:
                issue_info = self.known_issues.get(issue_type, {})
                enhanced_resolution = self._enhance_resolution_with_context(issue_type, issue_info, analysis)
                
                # Add automated resolution scoring
                resolution_score = self._calculate_resolution_effectiveness_score(issue_type, count, analysis)
                score_indicator = "🎯" if resolution_score > 0.8 else "⚠️" if resolution_score > 0.5 else "❌"
                
                recommendations.append(f'<i class="fa-solid fa-search"></i> Recurring issue "{issue_type}" ({count} occurrences): {enhanced_resolution} {score_indicator} (Resolution confidence: {resolution_score:.1%})')
        
        # Module status recommendations
        module_status = analysis.get('module_status', {})
        if module_status:
            disabled_modules = module_status.get('disabled_modules', [])
            if disabled_modules:
                recommendations.append(f'📋 Disabled Modules Detected: {", ".join(disabled_modules)} - verify if intentional')
        
        # Add AI-powered environmental recommendations
        if DYNAMIC_RAG_AVAILABLE:
            try:
                env_recs = self._get_environment_specific_recommendations(analysis)
                recommendations.extend(env_recs)
            except Exception as e:
                print(f"⚠️ Environmental recommendations failed: {e}")
        
        # Smart Pattern Analysis insights
        pattern_analysis = analysis.get('pattern_analysis', {})
        if pattern_analysis and pattern_analysis.get('pattern_insights'):
            recommendations.append('🧠 <strong>Pattern Analysis Insights</strong>:')
            for insight in pattern_analysis['pattern_insights'][:3]:
                recommendations.append(f'   {insight}')
        
        # Anomaly detection recommendations
        if pattern_analysis.get('anomalous_patterns'):
            anomaly_count = len(pattern_analysis['anomalous_patterns'])
            if anomaly_count > 0:
                recommendations.append(f'🔍 <strong>Anomaly Alert</strong>: {anomaly_count} unusual patterns detected - investigate for potential security incidents')
        
        # Default positive message
        if not recommendations:
            recommendations.append('<i class="fa-solid fa-check-circle text-success"></i> No critical issues detected - agent appears to be functioning normally')
        
        return recommendations
    
    def _get_component_specific_recommendation(self, component: str, stats: Dict[str, Any]) -> str:
        """Generate component-specific troubleshooting recommendations"""
        base_rec = f'<i class="fa-solid fa-wrench me-2"></i>{component}: High error count ({stats["errors"]} errors)'
        
        # Component-specific guidance
        specific_guidance = {
            'Anti Malware': 'Check scan engine updates and pattern file versions',
            'Firewall': 'Review firewall rules and network connectivity',
            'Intrusion Prevention': 'Verify DPI engine status and rule updates',
            'Agent Core': 'Check agent-manager communication and certificates',
            'Connectionhandler': 'Verify network connectivity and DNS resolution',
            'Heartbeat': 'Check manager connectivity and proxy settings'
        }
        
        guidance = specific_guidance.get(component, 'check component configuration')
        return f'{base_rec} - {guidance}'
    
    def _enhance_resolution_with_context(self, issue_type: str, issue_info: Dict[str, Any], analysis: Dict[str, Any]) -> str:
        """Enhance resolution steps with contextual information"""
        base_resolution = issue_info.get('resolution', 'Review configuration')
        
        # Add context from analysis
        if issue_type == 'AMSP_FUNC_NOT_SUPPORT':
            module_status = analysis.get('module_status', {})
            if 'device_control' in module_status.get('disabled_modules', []):
                return f"{base_resolution} ✅ Device Control is disabled - this warning is expected"
            else:
                return f"{base_resolution} ⚠️ Device Control status unclear - verify module configuration"
        
        return base_resolution
    
    def _get_ai_recommendations_for_critical_issues(self, analysis: Dict[str, Any]) -> List[str]:
        """Get AI-powered recommendations for critical issues"""
        try:
            if not DYNAMIC_RAG_AVAILABLE:
                return []
                
            from dynamic_rag_system import DynamicRAGSystem
            
            critical_issues = analysis.get('critical_issues', [])
            if not critical_issues:
                return []
            
            # Create focused prompt for critical issues
            critical_summary = "\n".join([f"- {issue['component']}: {issue['message']}" 
                                        for issue in critical_issues[:5]])  # Limit to top 5
            
            prompt = f"""
            Analyze these CRITICAL Deep Security Agent issues and provide specific troubleshooting steps:
            
            {critical_summary}
            
            Provide numbered troubleshooting steps for technical support staff.
            Focus on immediate resolution actions.
            """
            
            rag_system = DynamicRAGSystem()
            
            # Create context for RAG analysis
            rag_results = rag_system.process_log_with_dynamic_rag(prompt)
            ai_response = rag_results.get('ai_response', '')
            
            if ai_response:
                # Extract actionable steps from AI response
                steps = []
                lines = ai_response.split('\n')
                for line in lines:
                    if re.match(r'^\d+\.', line.strip()) or line.strip().startswith('-'):
                        cleaned_step = re.sub(r'^\d+\.\s*|\-\s*', '', line.strip())
                        if len(cleaned_step) > 10:  # Filter out very short lines
                            steps.append(f'🎯 {cleaned_step}')
                
                return steps[:3]  # Return top 3 actionable steps
                
        except Exception as e:
            print(f"⚠️ AI critical recommendations error: {e}")
            
        return []
    
    def _get_environment_specific_recommendations(self, analysis: Dict[str, Any]) -> List[str]:
        """Get environment-specific recommendations based on configuration"""
        recommendations = []
        
        try:
            config = analysis.get('configuration', {})
            
            # Azure-specific recommendations
            if config.get('azure_status') == 'true':
                recommendations.append('☁️ Azure Environment Detected - ensure VM extensions are properly configured')
            
            # Proxy environment recommendations
            proxy_settings = config.get('proxy_settings', {})
            if proxy_settings and proxy_settings.get('static_proxy'):
                recommendations.append('🌐 Proxy Environment - verify proxy authentication and Deep Security Manager accessibility')
            
            # FIPS environment
            if config.get('fips_available') == '1':
                recommendations.append('🔒 FIPS Environment - ensure all certificates and communications are FIPS-compliant')
            
            # Manager URL analysis
            manager_url = config.get('manager_url', '')
            if manager_url:
                if 'cloud' in manager_url.lower():
                    recommendations.append('☁️ Cloud One Environment - verify internet connectivity and DNS resolution')
                elif 'local' in manager_url.lower() or re.match(r'^\d+\.\d+\.\d+\.\d+', manager_url):
                    recommendations.append('🏢 On-Premise Environment - verify local network connectivity and certificate trust')
            
        except Exception as e:
            print(f"⚠️ Environment recommendations error: {e}")
        
        # Interactive troubleshooting guide integration
        try:
            interactive_guide = self._generate_interactive_troubleshooting_guide(analysis)
            if interactive_guide.get('recommended_path'):
                recommendations.append("🎯 Recommended Troubleshooting Path:")
                for step in interactive_guide['recommended_path'][:3]:  # Show first 3 steps
                    recommendations.append(f"  {step}")
            
            # Add follow-up questions for deeper investigation
            follow_up_questions = interactive_guide.get('follow_up_questions', [])
            if follow_up_questions:
                recommendations.append("❓ For deeper investigation, consider:")
                for question in follow_up_questions[:2]:  # Limit to 2 questions
                    recommendations.append(f"  • {question}")
                    
            # Add success validation steps
            validation_steps = interactive_guide.get('validation_steps', [])
            if validation_steps:
                recommendations.append("✅ Validation Steps:")
                for validation in validation_steps[:2]:
                    recommendations.append(f"  • {validation}")
                    
        except Exception as e:
            print(f"⚠️ Interactive troubleshooting guide error: {e}")
        
        return recommendations
    
    def _generate_predictive_insights(self, log_entries: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate predictive insights from log entry patterns"""
        try:
            predictive_analysis = {
                'warnings': [],
                'trends': {},
                'risk_score': 0.0,
                'recommendations': []
            }
            
            if not log_entries:
                return predictive_analysis
            
            # Analyze error frequency trends
            error_timeline = {}
            connection_issues = 0
            memory_warnings = 0
            component_failures = {}
            
            for entry in log_entries[-100:]:  # Last 100 entries for trend analysis
                timestamp = entry.get('timestamp', '')
                message = entry.get('message', '').lower()
                component = entry.get('component', 'unknown')
                
                # Track error frequency by hour
                hour = self._extract_hour_from_timestamp(timestamp)
                if hour not in error_timeline:
                    error_timeline[hour] = 0
                
                if any(keyword in message for keyword in ['error', 'fail', 'timeout']):
                    error_timeline[hour] += 1
                
                # Track specific issue patterns
                if 'connection' in message and ('timeout' in message or 'fail' in message):
                    connection_issues += 1
                
                if 'memory' in message and 'high' in message:
                    memory_warnings += 1
                
                if 'error' in message:
                    if component not in component_failures:
                        component_failures[component] = 0
                    component_failures[component] += 1
            
            # Generate predictive warnings
            total_entries = len(log_entries[-100:])
            
            # Connection degradation prediction
            if connection_issues > total_entries * 0.1:  # More than 10% connection issues
                predictive_analysis['warnings'].append(
                    f"Connection degradation detected ({connection_issues} issues). "
                    "Potential service interruption risk. Check network connectivity and firewall rules."
                )
                predictive_analysis['risk_score'] += 0.3
            
            # Memory pressure prediction
            if memory_warnings > 3:
                predictive_analysis['warnings'].append(
                    f"Memory pressure indicators detected ({memory_warnings} warnings). "
                    "Consider monitoring system resources and planning maintenance."
                )
                predictive_analysis['risk_score'] += 0.2
            
            # Component failure prediction
            for component, failures in component_failures.items():
                if failures > total_entries * 0.15:  # Component with >15% error rate
                    predictive_analysis['warnings'].append(
                        f"Component '{component}' showing instability ({failures} errors). "
                        "Recommend component restart or configuration review."
                    )
                    predictive_analysis['risk_score'] += 0.25
            
            # Error clustering analysis
            if error_timeline:
                peak_hours = [hour for hour, count in error_timeline.items() if count > 3]
                if peak_hours:
                    predictive_analysis['trends']['peak_error_hours'] = peak_hours
                    predictive_analysis['warnings'].append(
                        f"Error clustering detected during hours: {', '.join(map(str, peak_hours))}. "
                        "Consider scheduled maintenance during low-activity periods."
                    )
            
            # Overall risk assessment
            if predictive_analysis['risk_score'] >= 0.7:
                predictive_analysis['recommendations'].append(
                    "🚨 High risk of service degradation - immediate intervention recommended"
                )
            elif predictive_analysis['risk_score'] >= 0.4:
                predictive_analysis['recommendations'].append(
                    "⚠️ Moderate risk indicators - schedule preventive maintenance"
                )
            else:
                predictive_analysis['recommendations'].append(
                    "✅ System appears stable - continue monitoring"
                )
            
            return predictive_analysis
            
        except Exception as e:
            print(f"⚠️ Predictive analysis failed: {e}")
            return {'warnings': [], 'trends': {}, 'risk_score': 0.0, 'recommendations': []}

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
            
            # NEW: Generate structured JSON data instead of HTML
            self._update_progress("Output Formatting", "Generating structured output data", 98)
            
            # Store raw analysis data for frontend processing
            standardized_result['raw_data'] = analysis_results
            
            # Clean recommendations from HTML for structured output
            clean_recommendations = self._clean_html_from_recommendations(analysis_results.get('recommendations', []))
            
            standardized_result['structured_data'] = {
                'summary_statistics': analysis_results.get('summary', {}),
                'module_status': analysis_results.get('module_status', {}),
                'configuration': analysis_results.get('configuration', {}),
                'issues_found': {
                    'critical_issues': analysis_results.get('critical_issues', []),
                    'errors': analysis_results.get('errors', []),
                    'warnings': analysis_results.get('warnings', []),
                    'known_issues': analysis_results.get('known_issues', [])
                },
                'recommendations': clean_recommendations,
                'component_analysis': analysis_results.get('component_analysis', {}),
                'ml_insights': analysis_results.get('ml_insights', {}),
                'rag_insights': analysis_results.get('rag_insights', {}),
                'is_multiple_files': is_multiple,
                'file_paths': file_paths
            }
            
            # Generate legacy HTML only if specifically requested (backward compatibility)
            try:
                from routes import format_ds_log_results
                formatted_html = format_ds_log_results(analysis_results, is_multiple)
                standardized_result['legacy_html'] = formatted_html
            except Exception as e:
                print(f"⚠️ Legacy HTML generation failed: {e}")
                standardized_result['legacy_html'] = None
            
            # CRITICAL FIX: Convert NumPy types to native Python types for JSON serialization
            standardized_result = self._convert_numpy_types(standardized_result)
            
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

    def _calculate_resolution_effectiveness_score(self, issue_type, occurrence_count, analysis):
        """
        Calculate automated resolution effectiveness score for known issues.
        
        Args:
            issue_type (str): Type of issue being analyzed
            occurrence_count (int): Number of times issue appears in logs
            analysis (dict): Complete analysis results
            
        Returns:
            float: Resolution effectiveness score (0.0 to 1.0)
        """
        try:
            base_score = 0.8  # Default confidence for known issues
            
            # Factor 1: Issue frequency impact (more frequent = lower confidence)
            frequency_penalty = min(occurrence_count / 100, 0.3)  # Max 30% penalty
            
            # Factor 2: Severity assessment impact
            severity_boost = 0.0
            if hasattr(analysis, 'get') and analysis.get('severity_levels'):
                severity_levels = analysis['severity_levels']
                critical_count = severity_levels.get('critical', 0)
                high_count = severity_levels.get('high', 0)
                
                if critical_count == 0 and high_count <= 2:
                    severity_boost = 0.1  # Boost for manageable severity profile
                elif critical_count > 5:
                    severity_boost = -0.2  # Penalty for critical issues
            
            # Factor 3: Known issue complexity scoring
            complexity_factor = 0.0
            known_issue_info = self.known_issues.get(issue_type, {})
            resolution_steps = known_issue_info.get('resolution_steps', [])
            
            if len(resolution_steps) <= 3:
                complexity_factor = 0.1  # Simple resolution = higher confidence
            elif len(resolution_steps) > 8:
                complexity_factor = -0.1  # Complex resolution = lower confidence
            
            # Factor 4: Component health correlation
            health_penalty = 0.0
            if hasattr(analysis, 'get') and analysis.get('component_health_scores'):
                avg_health = sum(analysis['component_health_scores'].values()) / len(analysis['component_health_scores'])
                if avg_health < 0.5:
                    health_penalty = 0.2  # Penalty for poor overall health
            
            # Factor 5: Historical pattern recognition
            pattern_bonus = 0.0
            if hasattr(analysis, 'get') and analysis.get('pattern_analysis'):
                pattern_insights = analysis['pattern_analysis']
                if pattern_insights.get('anomalous_patterns', 0) < 2:
                    pattern_bonus = 0.1  # Bonus for predictable patterns
            
            # Calculate final score
            final_score = base_score - frequency_penalty + severity_boost + complexity_factor - health_penalty + pattern_bonus
            
            # Ensure score stays within bounds
            return max(0.0, min(1.0, final_score))
            
        except Exception as e:
            # Fallback to default score if calculation fails
            return 0.6

    def _track_resolution_feedback(self, issue_type, success_rate=None):
        """
        Track resolution feedback for continuous improvement.
        
        Args:
            issue_type (str): Type of issue resolved
            success_rate (float, optional): Success rate if available
        """
        try:
            # This would integrate with a feedback system in production
            # For now, we'll simulate tracking logic
            feedback_data = {
                'issue_type': issue_type,
                'timestamp': datetime.now().isoformat(),
                'success_rate': success_rate or 0.8,
                'confidence_level': 'medium'
            }
            
            # In production, this would save to database or analytics system
            # print(f"Resolution feedback tracked: {feedback_data}")
            
        except Exception as e:
            pass  # Silently fail for tracking to not impact main analysis

    def _suggest_resolution_improvements(self, analysis):
        """
        Suggest improvements to resolution approaches based on analysis.
        
        Args:
            analysis (dict): Complete analysis results
            
        Returns:
            list: Resolution improvement suggestions
        """
        suggestions = []
        
        try:
            # Analyze recurring issues for improvement opportunities
            issue_counts = {}
            for issue in analysis.get('known_issues', []):
                issue_type = issue['issue_type']
                issue_counts[issue_type] = issue_counts.get(issue_type, 0) + 1
            
            # Suggest automation opportunities
            high_frequency_issues = [issue for issue, count in issue_counts.items() if count > 20]
            if high_frequency_issues:
                suggestions.append(f"🤖 Consider automation for high-frequency issues: {', '.join(high_frequency_issues[:3])}")
            
            # Suggest proactive measures based on patterns
            if analysis.get('pattern_analysis', {}).get('recurring_sequences'):
                suggestions.append("🔄 Implement proactive monitoring for recurring issue sequences")
            
            # Suggest knowledge base updates
            unknown_patterns = analysis.get('pattern_analysis', {}).get('anomalous_patterns', 0)
            if unknown_patterns > 5:
                suggestions.append("📚 Consider expanding knowledge base with new pattern definitions")
            
            # Suggest component-specific improvements
            if analysis.get('component_health_scores'):
                poor_health_components = [comp for comp, score in analysis['component_health_scores'].items() if score < 0.4]
                if poor_health_components:
                    suggestions.append(f"🏥 Focus improvement efforts on: {', '.join(poor_health_components[:2])}")
                    
        except Exception as e:
            suggestions.append("⚠️ Resolution improvement analysis unavailable")
        
        return suggestions

    def _generate_resolution_summary(self, analysis):
        """
        Generate comprehensive resolution summary with effectiveness metrics.
        
        Args:
            analysis (dict): Complete analysis results
            
        Returns:
            dict: Resolution summary with metrics
        """
        try:
            summary = {
                'total_issues': len(analysis.get('known_issues', [])),
                'high_confidence_resolutions': 0,
                'medium_confidence_resolutions': 0,
                'low_confidence_resolutions': 0,
                'automation_candidates': [],
                'improvement_suggestions': []
            }
            
            # Analyze resolution confidence distribution
            issue_counts = {}
            for issue in analysis.get('known_issues', []):
                issue_type = issue['issue_type']
                issue_counts[issue_type] = issue_counts.get(issue_type, 0) + 1
            
            for issue_type, count in issue_counts.items():
                if count > 10:  # Only score significant issues
                    score = self._calculate_resolution_effectiveness_score(issue_type, count, analysis)
                    
                    if score > 0.8:
                        summary['high_confidence_resolutions'] += 1
                    elif score > 0.5:
                        summary['medium_confidence_resolutions'] += 1
                    else:
                        summary['low_confidence_resolutions'] += 1
                    
                    # Track automation candidates
                    if count > 20 and score > 0.7:
                        summary['automation_candidates'].append(issue_type)
            
            # Add improvement suggestions
            summary['improvement_suggestions'] = self._suggest_resolution_improvements(analysis)
            
            return summary
            
        except Exception as e:
            return {
                'total_issues': 0,
                'error': 'Resolution summary generation failed',
                'improvement_suggestions': ['⚠️ Manual review recommended']
            }

    def _generate_interactive_troubleshooting_guide(self, analysis):
        """
        Generate dynamic interactive troubleshooting guide with RAG-powered follow-up questions.
        
        Args:
            analysis (dict): Complete analysis results
            
        Returns:
            dict: Interactive troubleshooting guide with personalized paths
        """
        try:
            guide = {
                'recommended_path': [],
                'follow_up_questions': [],
                'validation_steps': [],
                'personalization_level': 'standard',
                'complexity_score': 0.0
            }
            
            # Determine troubleshooting complexity
            complexity_factors = []
            critical_count = analysis.get('summary', {}).get('critical_count', 0)
            error_count = analysis.get('summary', {}).get('error_count', 0)
            unique_issues = len(set([issue['issue_type'] for issue in analysis.get('known_issues', [])]))
            
            complexity_score = (critical_count * 0.4) + (min(error_count, 50) * 0.01) + (unique_issues * 0.1)
            guide['complexity_score'] = complexity_score
            
            # Generate personalized troubleshooting path
            guide['recommended_path'] = self._create_personalized_troubleshooting_path(analysis, complexity_score)
            
            # Generate intelligent follow-up questions
            guide['follow_up_questions'] = self._generate_intelligent_follow_up_questions(analysis)
            
            # Create success validation steps
            guide['validation_steps'] = self._create_validation_steps(analysis)
            
            # Determine personalization level
            if complexity_score > 5.0:
                guide['personalization_level'] = 'expert'
            elif complexity_score > 2.0:
                guide['personalization_level'] = 'intermediate'
            else:
                guide['personalization_level'] = 'beginner'
            
            return guide
            
        except Exception as e:
            return {
                'recommended_path': ['⚠️ Unable to generate troubleshooting path'],
                'follow_up_questions': [],
                'validation_steps': [],
                'error': f'Guide generation failed: {str(e)}'
            }

    def _create_personalized_troubleshooting_path(self, analysis, complexity_score):
        """Create step-by-step troubleshooting path based on analysis results"""
        path = []
        
        try:
            # Step 1: Priority assessment
            critical_count = analysis.get('summary', {}).get('critical_count', 0)
            if critical_count > 0:
                path.append("1️⃣ Address critical issues immediately - check DS Agent service status and connectivity")
            else:
                path.append("1️⃣ Verify DS Agent basic functionality - check service status and recent heartbeat")
            
            # Step 2: Connection verification
            config = analysis.get('configuration', {})
            manager_url = config.get('manager_url', '')
            if manager_url:
                path.append(f"2️⃣ Verify Deep Security Manager connectivity to {manager_url}")
            else:
                path.append("2️⃣ Check Deep Security Manager configuration and network connectivity")
            
            # Step 3: Component-specific guidance
            component_health = analysis.get('component_health_scores', {})
            if component_health:
                worst_component = min(component_health.items(), key=lambda x: x[1])
                if worst_component[1] < 0.6:
                    path.append(f"3️⃣ Focus on {worst_component[0]} component - health score: {worst_component[1]:.1%}")
                else:
                    path.append("3️⃣ All components healthy - investigate configuration or policy issues")
            
            # Step 4: Pattern-based guidance
            pattern_analysis = analysis.get('pattern_analysis', {})
            if pattern_analysis.get('anomalous_patterns', 0) > 3:
                path.append("4️⃣ Investigate anomalous patterns - review recent policy changes or system updates")
            elif pattern_analysis.get('recurring_sequences'):
                path.append("4️⃣ Address recurring issue sequences - implement proactive monitoring")
            else:
                path.append("4️⃣ Monitor for emerging patterns - establish baseline behavior")
            
            # Step 5: Advanced troubleshooting (for complex cases)
            if complexity_score > 3.0:
                path.append("5️⃣ Advanced diagnostics - collect detailed logs and contact Trend Micro support")
            
        except Exception as e:
            path = ["⚠️ Unable to generate personalized path - proceed with standard troubleshooting"]
        
        return path

    def _generate_intelligent_follow_up_questions(self, analysis):
        """Generate RAG-powered follow-up questions for deeper investigation"""
        questions = []
        
        try:
            # Component-specific questions
            component_health = analysis.get('component_health_scores', {})
            if component_health:
                poor_components = [comp for comp, score in component_health.items() if score < 0.5]
                if poor_components:
                    questions.append(f"Have there been recent changes to {', '.join(poor_components[:2])} configuration?")
            
            # Environment-specific questions
            config = analysis.get('configuration', {})
            if config.get('azure_vm_available') == '1':
                questions.append("Are Azure VM extensions properly configured and up to date?")
            
            proxy_settings = config.get('proxy_settings', {})
            if proxy_settings and proxy_settings.get('static_proxy'):
                questions.append("Has the proxy configuration or authentication changed recently?")
            
            # Pattern-based questions
            pattern_analysis = analysis.get('pattern_analysis', {})
            if pattern_analysis.get('anomalous_patterns', 0) > 5:
                questions.append("Have there been any recent system updates, policy changes, or network modifications?")
            
            # Frequency-based questions
            error_count = analysis.get('summary', {}).get('error_count', 0)
            if error_count > 50:
                questions.append("Is this a recurring issue, and if so, what patterns have you noticed?")
            
            # Known issues questions
            known_issues = analysis.get('known_issues', [])
            frequent_issues = {}
            for issue in known_issues:
                issue_type = issue['issue_type']
                frequent_issues[issue_type] = frequent_issues.get(issue_type, 0) + 1
            
            if frequent_issues:
                most_frequent = max(frequent_issues.items(), key=lambda x: x[1])
                if most_frequent[1] > 10:
                    questions.append(f"For the recurring '{most_frequent[0]}' issue, have previous resolution attempts been tried?")
            
        except Exception as e:
            questions = ["What specific symptoms or behaviors have you observed?"]
        
        return questions

    def _create_validation_steps(self, analysis):
        """Create validation steps to confirm resolution success"""
        steps = []
        
        try:
            # Basic validation
            steps.append("Verify DS Agent service is running and responding to heartbeat checks")
            
            # Component-specific validation
            component_health = analysis.get('component_health_scores', {})
            if component_health:
                poor_components = [comp for comp, score in component_health.items() if score < 0.6]
                if poor_components:
                    steps.append(f"Confirm {', '.join(poor_components[:2])} components are functioning properly")
            
            # Configuration validation
            config = analysis.get('configuration', {})
            if config.get('manager_url'):
                steps.append("Test connectivity to Deep Security Manager and verify policy updates")
            
            # Issue-specific validation
            critical_count = analysis.get('summary', {}).get('critical_count', 0)
            if critical_count > 0:
                steps.append("Monitor logs for 24 hours to ensure critical issues do not recur")
            else:
                steps.append("Monitor system for 1-2 hours to confirm stable operation")
            
            # Pattern validation
            pattern_analysis = analysis.get('pattern_analysis', {})
            if pattern_analysis.get('anomalous_patterns', 0) > 3:
                steps.append("Review system behavior patterns to ensure anomalies are resolved")
            
        except Exception as e:
            steps = ["Monitor DS Agent functionality for stability confirmation"]
        
        return steps
