# -*- coding: utf-8 -*-
"""
AMSPAnalyzer - AMSP Anti-Malware Log Analyzer
Extracted from analyzers.py lines 1031-1824 with safety enhancements
"""

from .shared_imports import *
from .base.standardizer import AnalyzerOutputStandardizer

class AMSPAnalyzer(AnalyzerOutputStandardizer):
    """AMSP Anti-Malware Log Analyzer with progress tracking"""
    
    def __init__(self, session_manager=None, session_id=None, rag_system=None, ml_analyzer=None):
        """Initialize with optional progress tracking, RAG system, and ML analyzer"""
        self.session_manager = session_manager
        self.session_id = session_id
        self.rag_system = rag_system
        self.ml_analyzer = ml_analyzer
        
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
                print(f"⚠️ AMSP Progress update failed: {e}")
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
                'total_lines': analysis_results.get('summary', {}).get('total_lines', 0),
                'errors_found': len(analysis_results.get('errors', [])),
                'warnings_found': len(analysis_results.get('warnings', [])),
                'pattern_failures': len([e for e in analysis_results.get('errors', []) if 'pattern' in e.get('message', '').lower()]),
                'bpf_failures': len([e for e in analysis_results.get('errors', []) if 'bpf' in e.get('message', '').lower()]),
                'trendx_failures': len([e for e in analysis_results.get('errors', []) if 'trendx' in e.get('message', '').lower()])
            }
            
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
