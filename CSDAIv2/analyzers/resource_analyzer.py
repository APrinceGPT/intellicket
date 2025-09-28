# -*- coding: utf-8 -*-
"""
ResourceAnalyzer - Resource Analyzer for exclusion recommendations
Extracted from analyzers.py lines 2216-2964 with safety enhancements
"""

from .shared_imports import *
from .base.standardizer import AnalyzerOutputStandardizer

class ResourceAnalyzer(AnalyzerOutputStandardizer):
    """Resource Analyzer for exclusion recommendations with progress tracking"""
    
    def __init__(self, session_manager=None, session_id=None, rag_system=None, ml_analyzer=None):
        """Initialize with optional progress tracking, RAG system, and ML analyzer"""
        self.session_manager = session_manager
        self.session_id = session_id
        self.rag_system = rag_system
        self.ml_analyzer = ml_analyzer
    
    def _safe_parse_count(self, count_value):
        """Safely parse count values, handling non-numeric strings"""
        try:
            if isinstance(count_value, (int, float)):
                return int(count_value)
            count_str = str(count_value).replace(',', '').strip()
            # Handle special cases for partial analysis
            if 'unknown' in count_str.lower() or 'n/a' in count_str.lower():
                return 0
            return int(count_str)
        except (ValueError, TypeError):
            return 0
    
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
                print(f"📊 Resource Analysis Progress - {stage}: {message}")
            except Exception as e:
                print(f"⚠️ Resource Analysis Progress update failed: {e}")
        else:
            # Fallback to console logging
            print(f"📊 Resource Analysis {stage}: {message}")
    
    def extract_processes_from_xml(self, xml_path: str) -> List[str]:
        """Extract process names from RunningProcesses.xml"""
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
        self._update_progress("Initialization", "Starting resource conflict analysis", 5)
        
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
            self._update_progress("Process Filtering", "Filtering Trend Micro processes", 15)
            
            def is_trend_micro(proc_name):
                name = proc_name.lower()
                tm_indicators = [
                    "trend micro", "pccnt", "dsagent", "deep security", "tmcomm", 
                    "tmebc", "amsp", "aegis", "dsa_", "tmansrv", "tmlisten", 
                    "tmpfw", "tmproxy", "ntrtscan", "pccntmon", "tmbmsrv"
                ]
                return any(indicator in name for indicator in tm_indicators)

            # Validate inputs and determine analysis mode
            xml_only = bool(process_list and not busy_processes)
            txt_only = bool(busy_processes and not process_list)
            full_analysis = bool(process_list and busy_processes)
            no_data = not process_list and not busy_processes
            
            if no_data:
                analysis_result['status'] = 'no_files'
                analysis_result['analysis_text'] = "No data provided: Please upload either RunningProcesses.xml, TopNBusyProcess.txt, or both files for resource analysis."
                return analysis_result
            
            # Handle single-file analysis modes with warnings
            if xml_only:
                analysis_result['status'] = 'partial_xml_only'
                analysis_result['analysis_text'] = "⚠️ Partial Analysis (XML Only): Analysis performed using only RunningProcesses.xml. Results may be incomplete without TopNBusyProcess.txt scan data."
                analysis_result['warning'] = "Limited analysis performed with only running processes data. For comprehensive resource conflict detection, please also upload TopNBusyProcess.txt."
                # Perform XML-only analysis
                candidates = self._analyze_xml_only(process_list)
                
            elif txt_only:
                analysis_result['status'] = 'partial_txt_only'
                analysis_result['analysis_text'] = "⚠️ Partial Analysis (TXT Only): Analysis performed using only TopNBusyProcess.txt. Results may be incomplete without RunningProcesses.xml process data."
                analysis_result['warning'] = "Limited analysis performed with only busy process scan data. For comprehensive resource conflict detection, please also upload RunningProcesses.xml."
                # Perform TXT-only analysis
                candidates = self._analyze_txt_only(busy_processes)
                
            elif full_analysis:
                analysis_result['status'] = 'complete'
                analysis_result['analysis_text'] = "✅ Complete Analysis: Full resource conflict analysis performed with both RunningProcesses.xml and TopNBusyProcess.txt."
                # Perform full correlation analysis
                candidates = self._analyze_full_correlation(process_list, busy_processes)
            
            # Set candidates in analysis result
            analysis_result['candidates'] = candidates
            
            # Performance metrics calculation - 50% progress
            self._update_progress("Performance Metrics", "Calculating performance impact", 50)
            total_scan_count = sum(self._safe_parse_count(c.get('count', '0')) for c in candidates)
            analysis_result['performance_metrics'] = {
                'total_scan_count': total_scan_count,
                'high_impact_processes': len([c for c in candidates if self._safe_parse_count(c.get('count', '0')) > 1000]),
                'process_types': list(set(c['process_type'] for c in candidates)),
                'optimization_potential': 'High' if total_scan_count > 5000 else 'Medium' if total_scan_count > 2000 else 'Low'
            }

            # Dynamic RAG-Enhanced Analysis - 85% progress
            self._update_progress("AI Analysis", "Processing with AI intelligence", 85)
            if DYNAMIC_RAG_AVAILABLE:
                try:
                    # Read log content for dynamic analysis
                    process_content = '\n'.join([f"{proc['name']}: {proc.get('count', 'N/A')} scans" for proc in candidates[:20]])
                    
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
                    print(f"⚠️ Dynamic RAG resource analysis failed: {e}")
                    analysis_result['dynamic_rag_analysis'] = {'error': str(e)}

            # Enhanced AI Analysis with Deep Security context
            analysis_text = self._perform_ai_analysis(process_list, busy_processes, candidates, total_scan_count, analysis_result['performance_metrics'])
            analysis_result['analysis_text'] = analysis_text
            
            # Set status based on analysis (preserve partial analysis status)
            if candidates:
                # Keep existing status if it indicates partial analysis mode
                if analysis_result['status'] not in ['partial_xml_only', 'partial_txt_only', 'complete']:
                    analysis_result['status'] = 'candidates_found'
            else:
                analysis_result['status'] = 'optimal'
                
            # Generate structured recommendations - 95% progress
            self._update_progress("Recommendations", "Generating optimization recommendations", 95)
            analysis_result['recommendations'] = self._generate_enhanced_recommendations(
                candidates, analysis_result['performance_metrics'], analysis_result.get('ml_insights'), analysis_result.get('rag_insights')
            )
            
            # Analysis complete - 100% progress
            self._update_progress("Completion", "Resource analysis completed", 100)
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

    def _is_system_critical_process(self, process_name: str) -> bool:
        """
        AI-enhanced filter to identify system-critical processes that should never be excluded.
        Automatically filters out Windows System32 services and critical system processes.
        """
        if not process_name:
            return True
        
        name_lower = process_name.lower().strip()
        
        # Extract just the filename if full path is provided
        base_name = os.path.basename(name_lower)
        
        # Check if process is in system32 directory - CRITICAL: Never exclude these
        if 'system32' in name_lower or 'syswow64' in name_lower:
            return True
        
        # Windows core system processes - NEVER exclude these
        critical_system_processes = {
            'svchost.exe', 'lsass.exe', 'csrss.exe', 'winlogon.exe', 'services.exe',
            'smss.exe', 'wininit.exe', 'dwm.exe', 'explorer.exe', 'ntoskrnl.exe',
            'system', 'registry', 'memory compression', 'secure system', 'system interrupts',
            'idle', 'csrss', 'wininit', 'services', 'lsass', 'winlogon', 'fontdrvhost.exe',
            'dwm.exe', 'sihost.exe', 'taskhostw.exe', 'rundll32.exe', 'conhost.exe',
            'dllhost.exe', 'runtimebroker.exe', 'searchindexer.exe', 'searchui.exe',
            'startmenuexperiencehost.exe', 'shellexperiencehost.exe', 'backgroundtaskhost.exe',
            'audiodg.exe', 'ctfmon.exe', 'wincompose.exe', 'textinputhost.exe',
            'lockapp.exe', 'logonui.exe', 'userinit.exe', 'consent.exe'
        }
        
        if base_name in critical_system_processes:
            return True
        
        # Windows services that should not be excluded
        critical_services = {
            'spoolsv.exe', 'lsm.exe', 'wudfhost.exe', 'taskhost.exe', 'taskeng.exe',
            'msdtc.exe', 'alg.exe', 'bits.exe', 'cryptsvc.exe', 'dhcp.exe',
            'dnscache.exe', 'eventlog.exe', 'netlogon.exe', 'netman.exe',
            'nla.exe', 'pcasvc.exe', 'profsvc.exe', 'schedule.exe', 'seclogon.exe',
            'sens.exe', 'sharedaccess.exe', 'themes.exe', 'trkwks.exe', 'w32time.exe',
            'winmgmt.exe', 'wuauserv.exe', 'xmlprov.exe'
        }
        
        if base_name in critical_services:
            return True
        
        # Windows management and administration tools
        admin_tools = {
            'mmc.exe', 'perfmon.exe', 'resmon.exe', 'taskmgr.exe', 'eventvwr.exe',
            'compmgmt.msc', 'devmgmt.msc', 'diskmgmt.msc', 'fsmgmt.msc',
            'gpedit.msc', 'lusrmgr.msc', 'perfmon.msc', 'rsop.msc', 'secpol.msc',
            'services.msc', 'wmimgmt.msc', 'control.exe', 'msconfig.exe', 'regedit.exe',
            'cmd.exe', 'powershell.exe', 'powershell_ise.exe', 'wbem\\*'
        }
        
        if base_name in admin_tools or any(admin in name_lower for admin in admin_tools):
            return True
        
        # Network and security services
        network_security = {
            'lsaiso.exe', 'csrss.exe', 'smss.exe', 'wininit.exe', 'services.exe',
            'winlogon.exe', 'userinit.exe', 'mpssvc.dll', 'bfe.dll', 'fwpuclnt.dll',
            'icmp.dll', 'iphlpapi.dll', 'netapi32.dll', 'netutils.dll', 'shlwapi.dll',
            'ws2_32.dll', 'wsock32.dll', 'dnsapi.dll', 'winhttp.dll', 'wininet.dll'
        }
        
        if base_name in network_security:
            return True
        
        # Hardware and driver related processes
        hardware_drivers = {
            'audiodg.exe', 'csrss.exe', 'dwm.exe', 'fontdrvhost.exe', 'winlogon.exe',
            'wudfhost.exe', 'igfxpers.exe', 'igfxtray.exe', 'hkcmd.exe', 'igfxsrvc.exe'
        }
        
        if base_name in hardware_drivers:
            return True
        
        # Windows update and maintenance
        update_maintenance = {
            'wuauclt.exe', 'wudfhost.exe', 'trustedinstaller.exe', 'tiworker.exe',
            'sihclient.exe', 'usoclient.exe', 'musnotification.exe', 'musnotificationux.exe'
        }
        
        if base_name in update_maintenance:
            return True
        
        # Check for windows system directories in full path
        system_directories = [
            'c:\\windows\\system32\\',
            'c:\\windows\\syswow64\\',
            'c:\\windows\\winsxs\\',
            'c:\\windows\\servicing\\',
            'c:\\windows\\microsoft.net\\',
            'c:\\windows\\assembly\\',
            'c:\\windows\\globalization\\',
            'c:\\windows\\ime\\',
            'c:\\windows\\inf\\',
            'c:\\windows\\installer\\',
            'c:\\windows\\l2schemas\\',
            'c:\\windows\\livekernelreports\\',
            'c:\\windows\\logs\\',
            'c:\\windows\\panther\\',
            'c:\\windows\\policydefinitions\\',
            'c:\\windows\\resources\\',
            'c:\\windows\\schemas\\',
            'c:\\windows\\security\\',
            'c:\\windows\\serviceprofiles\\',
            'c:\\windows\\servicing\\',
            'c:\\windows\\systemapps\\',
            'c:\\windows\\systemresources\\',
            'c:\\windows\\winsxs\\'
        ]
        
        for sys_dir in system_directories:
            if sys_dir in name_lower:
                return True
        
        # Additional checks for system process patterns
        system_patterns = [
            'microsoft\\windows\\',
            'windows defender',
            'windows security',
            'microsoft corporation',
            'windows.old\\',
            'recovery\\',
            'bootmgr',
            'ntldr',
            'hiberfil',
            'pagefile',
            'swapfile'
        ]
        
        for pattern in system_patterns:
            if pattern in name_lower:
                return True
        
        return False

    def _generate_enhanced_recommendations(self, candidates: List[Dict], performance_metrics: Dict, ml_insights: Dict, rag_insights: Dict) -> List[str]:
        """Generate enhanced recommendations based on all analysis components"""
        recommendations = []
        
        if len(candidates) == 0:
            recommendations.append('<i class="fas fa-check-circle text-success"></i> System Performance: Optimal - No exclusions needed')
            recommendations.append('<i class="fas fa-clock"></i> Scan Efficiency: All processes showing normal resource usage patterns')
            return recommendations
        
        # Performance-based recommendations
        total_scans = sum(self._safe_parse_count(c.get('count', '0')) for c in candidates)
        if total_scans > 5000:
            recommendations.append('<i class="fas fa-exclamation-triangle text-warning"></i> High scan volume detected - immediate performance optimization recommended')
        
        # Process type specific recommendations
        if performance_metrics.get('process_types'):
            dominant_type = max(set(performance_metrics['process_types']), key=performance_metrics['process_types'].count)
            recommendations.append(f'<i class="fas fa-cogs"></i> Focus on {dominant_type} processes for maximum performance impact')
        
        # Implementation guidance
        top_candidates = sorted(candidates, key=lambda x: self._safe_parse_count(x.get('count', '0')), reverse=True)[:3]
        if top_candidates:
            recommendations.append(f'<i class="fas fa-star"></i> Priority exclusion candidates: {", ".join([c["name"] for c in top_candidates])}')
        
        return recommendations

    def _perform_ai_analysis(self, process_list: List[str], busy_processes: List[Dict], candidates: List[Dict], total_scan_count: int, performance_metrics: Dict) -> str:
        """Perform AI analysis with robust error handling"""
        try:
            # Check if OpenAI is available
            if not OPENAI_AVAILABLE:
                return self._generate_fallback_analysis(candidates, performance_metrics)
            
            from config import get_config
            config = get_config()
            
            # Validate API configuration
            if not config.OPENAI_API_KEY:
                return self._generate_fallback_analysis(candidates, performance_metrics)
            
            try:
                # Use basic OpenAI client without httpx dependency
                client = OpenAI(
                    api_key=config.OPENAI_API_KEY,
                    base_url=config.OPENAI_BASE_URL,
                    timeout=120.0  # Increase timeout for ResourceAnalyzer
                )
            except Exception as e:
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
                    prompt += f"• {c['name']} (Scan Count: {c['count']}, Type: {c['process_type']})\n"
                    for k, v in c["details"].items():
                        prompt += f"    {k}: {v}\n"
                prompt += "\nPROVIDE DETAILED ANALYSIS WITH ACTIONABLE RECOMMENDATIONS:\n"
            else:
                prompt += "\nNo high-impact non-Trend Micro processes detected.\n"
                prompt += "PROVIDE ASSESSMENT OF CURRENT PERFORMANCE STATE:\n"

            try:
                response = client.chat.completions.create(
                    model=config.OPENAI_MODEL,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=4000,
                    temperature=0.3,
                    timeout=120  # Extended timeout for resource analysis with large datasets
                )
                
                return response.choices[0].message.content
                
            except Exception as api_error:
                return f"AI analysis temporarily unavailable: {str(api_error)}\n\n{self._generate_fallback_analysis(candidates, performance_metrics)}"
                
        except Exception as e:
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

        total_scans = sum(self._safe_parse_count(c.get('count', '0')) for c in candidates)
        high_impact = [c for c in candidates if self._safe_parse_count(c.get('count', '0')) > 1000]
        
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
        
        for i, candidate in enumerate(sorted(candidates, key=lambda x: self._safe_parse_count(x.get('count', '0')), reverse=True)[:5], 1):
            count = self._safe_parse_count(candidate.get('count', '0'))
            analysis += f"""
#### {i}. {candidate['name']}
- **Scan Count**: {candidate['count']} events
- **Process Type**: {candidate['process_type']}
- **Analysis**: {'High-frequency file access pattern' if count > 1000 else 'Moderate scan activity'}
- **Recommendation**: {'Priority candidate for exclusion' if count > 5000 else 'Consider for exclusion' if count > 1000 else 'Optional exclusion candidate'}
"""

        analysis += f"""

### Performance Recommendations

1. **Immediate Actions**:
   - Review top {min(3, len(high_impact))} processes for exclusion candidates
   - Implement exclusions during maintenance window
   - Monitor performance improvements post-implementation

2. **Implementation Considerations**:
   - Never exclude Trend Micro processes
   - Test exclusions in non-production environments first
   - Implement exclusions gradually and monitor for issues

3. **Implementation Strategy**:
   - Start with highest-impact processes first
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

    def _analyze_xml_only(self, process_list: List[str]) -> List[Dict[str, Any]]:
        """Analyze using only RunningProcesses.xml data"""
        self._update_progress("XML Analysis", "Analyzing running processes for exclusion candidates", 35)
        
        candidates = []
        filtered_count = 0
        
        def is_trend_micro(proc_name):
            name = proc_name.lower()
            tm_indicators = [
                "trend micro", "pccnt", "dsagent", "deep security", "tmcomm", 
                "tmebc", "amsp", "aegis", "dsa_", "tmansrv", "tmlisten", 
                "tmpfw", "tmproxy", "ntrtscan", "pccntmon", "tmbmsrv"
            ]
            return any(indicator in name for indicator in tm_indicators)
        
        # Analyze running processes for potential exclusion candidates
        # Without scan counts, we'll focus on common processes that typically have high impact
        high_impact_process_patterns = [
            'chrome.exe', 'firefox.exe', 'outlook.exe', 'word.exe', 
            'excel.exe', 'powerpoint.exe', 'notepad.exe',
            'code.exe', 'visual studio', 'java.exe', 'python.exe', 'node.exe'
        ]
        
        for proc in process_list:
            name = proc.lower().strip()
            if not name or is_trend_micro(name):
                continue
            
            # AI-Enhanced System Filter: Automatically exclude system-critical processes
            if self._is_system_critical_process(name):
                filtered_count += 1
                continue
                
            # Check if it's a potentially high-impact process
            base_name = os.path.basename(name)
            is_high_impact = any(pattern in base_name.lower() for pattern in high_impact_process_patterns)
            
            if is_high_impact or len(candidates) < 5:  # Include top processes or common high-impact ones
                candidate = {
                    "name": name,
                    "count": "Unknown (XML-only analysis)",
                    "details": {
                        "analysis_mode": "XML-only",
                        "scan_count_available": False,
                        "recommendation_confidence": "Low - requires TXT file for accurate impact assessment",
                        "path": name  # Store full path for frontend
                    },
                    "process_type": self._classify_process_type(name)
                }
                candidates.append(candidate)
        
        # Log filtering results
        if filtered_count > 0:
            print(f"🛡️ AI Filter: Automatically excluded {filtered_count} system-critical processes from analysis")
        
        return candidates[:10]  # Limit to top 10 for XML-only analysis

    def _analyze_txt_only(self, busy_processes: List[Dict]) -> List[Dict[str, Any]]:
        """Analyze using only TopNBusyProcess.txt data"""
        self._update_progress("TXT Analysis", "Analyzing busy processes for exclusion candidates", 35)
        
        candidates = []
        filtered_count = 0
        
        def is_trend_micro(proc_name):
            name = proc_name.lower()
            tm_indicators = [
                "trend micro", "pccnt", "dsagent", "deep security", "tmcomm", 
                "tmebc", "amsp", "aegis", "dsa_", "tmansrv", "tmlisten", 
                "tmpfw", "tmproxy", "ntrtscan", "pccntmon", "tmbmsrv"
            ]
            return any(indicator in name for indicator in tm_indicators)
        
        # Analyze busy processes - we have scan counts but can't verify if they're actually running
        for proc in busy_processes:
            name = proc.get("Name", "").strip().lower()
            if not name or is_trend_micro(name):
                continue
            
            # AI-Enhanced System Filter: Automatically exclude system-critical processes
            if self._is_system_critical_process(name):
                filtered_count += 1
                continue
                
            candidate = {
                "name": name,
                "count": proc.get("Count", "N/A"),
                "details": {
                    **{k: v for k, v in proc.items() if k not in ("Name", "Count")},
                    "analysis_mode": "TXT-only",
                    "running_status_verified": False,
                    "recommendation_confidence": "Medium - requires XML file to verify process is currently running",
                    "path": name  # Store name as path for frontend
                },
                "process_type": self._classify_process_type(name)
            }
            candidates.append(candidate)
        
        # Log filtering results
        if filtered_count > 0:
            print(f"🛡️ AI Filter: Automatically excluded {filtered_count} system-critical processes from busy process analysis")
        
        return candidates

    def _analyze_full_correlation(self, process_list: List[str], busy_processes: List[Dict]) -> List[Dict[str, Any]]:
        """Perform full correlation analysis with both XML and TXT data"""
        self._update_progress("Correlation Analysis", "Correlating running and busy processes", 35)
        
        def is_trend_micro(proc_name):
            name = proc_name.lower()
            tm_indicators = [
                "trend micro", "pccnt", "dsagent", "deep security", "tmcomm", 
                "tmebc", "amsp", "aegis", "dsa_", "tmansrv", "tmlisten", 
                "tmpfw", "tmproxy", "ntrtscan", "pccntmon", "tmbmsrv"
            ]
            return any(indicator in name for indicator in tm_indicators)
        
        # Build running processes set for correlation
        running_set = set()
        for proc in process_list:
            base = os.path.basename(proc).lower()
            running_set.add(base)

        candidates = []
        filtered_count = 0
        
        for proc in busy_processes:
            name = proc.get("Name", "").strip().lower()
            base = os.path.basename(name)
            if not name or is_trend_micro(name):
                continue
                
            # AI-Enhanced System Filter: Automatically exclude system-critical processes
            if self._is_system_critical_process(name):
                filtered_count += 1
                continue
                
            if base in running_set:
                candidate = {
                    "name": name,
                    "count": proc.get("Count", "N/A"),
                    "details": {
                        **{k: v for k, v in proc.items() if k not in ("Name", "Count")},
                        "analysis_mode": "Full correlation",
                        "running_status_verified": True,
                        "recommendation_confidence": "High - both scan count and running status confirmed",
                        "path": name  # Store name as path for frontend
                    },
                    "process_type": self._classify_process_type(name)
                }
                candidates.append(candidate)
        
        # Log filtering results
        if filtered_count > 0:
            print(f"🛡️ AI Filter: Automatically excluded {filtered_count} system-critical processes from correlation analysis")
        
        return candidates

    def analyze(self, file_paths: Union[str, List[str]]) -> Dict[str, Any]:
        """Standardized analysis entry point for resource analysis"""
        try:
            self._update_progress("Initialization", "Starting resource analysis", 1)
            
            # Normalize input to list and validate
            if isinstance(file_paths, str):
                file_paths = [file_paths]
            
            if not file_paths:
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
            
            self._update_progress("File Processing", "Processing XML and TXT files", 20)
            
            # Extract process data
            processes = []
            busy_processes = []
            
            # Process XML files (RunningProcesses.xml)
            for xml_file in xml_files:
                try:
                    processes.extend(self.extract_processes_from_xml(xml_file))
                except Exception as e:
                    print(f"Warning: Failed to process XML file {xml_file}: {e}")
            
            self._update_progress("Data Processing", "Extracting busy process data", 50)
            
            # Process TXT files (TopNBusyProcess.txt)
            for txt_file in txt_files:
                try:
                    busy_processes.extend(self.parse_top_n_busy_process(txt_file))
                except Exception as e:
                    print(f"Warning: Failed to process TXT file {txt_file}: {e}")
            
            self._update_progress("Analysis", "Analyzing resource conflicts", 70)
            
            # Perform resource conflict analysis
            analysis_result = self.analyze_resource_conflicts(processes, busy_processes)
            
            # Apply standardized output format
            standardized_result = self._standardize_analyzer_output(analysis_result, 'resource_analysis')
            
            # Add metadata
            standardized_result['metadata'] = {
                'files_processed': len(file_paths),
                'xml_files': len(xml_files),
                'txt_files': len(txt_files),
                'processes_found': len(processes),
                'busy_processes_found': len(busy_processes),
                'exclusion_candidates': len(analysis_result.get('candidates', []))
            }
            
            self._update_progress("Completion", "Resource analysis completed", 100)
            return standardized_result
            
        except Exception as e:
            error_msg = f"Resource analysis failed: {str(e)}"
            self._update_progress("Error", error_msg, None)
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
