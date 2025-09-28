# -*- coding: utf-8 -*-
"""
ConflictAnalyzer - AntiVirus Conflict Analyzer
Extracted from analyzers.py lines 1825-2215 with safety enhancements
"""

from .shared_imports import *
from .base.standardizer import AnalyzerOutputStandardizer

class ConflictAnalyzer(AnalyzerOutputStandardizer):
    """AntiVirus Conflict Analyzer"""
    
    def __init__(self, session_manager=None, session_id=None, rag_system=None, ml_analyzer=None):
        """Initialize with optional progress tracking, RAG system, and ML analyzer"""
        self.session_manager = session_manager
        self.session_id = session_id
        self.rag_system = rag_system
        self.ml_analyzer = ml_analyzer
    
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

    def filter_antivirus_processes(self, process_list: List[str]) -> List[str]:
        """Enhanced pre-filter with hybrid detection to catch unknown Anti-Virus software"""
        # Known Anti-Virus process patterns and keywords (EXPANDED)
        av_patterns = [
            # Norton/Symantec
            'norton', 'symantec', 'nrt', 'nav', 'nis', 'navapsvc', 'ccsvchst', 'ccapp',
            # McAfee
            'mcafee', 'mcshield', 'mcagent', 'mctray', 'mcods', 'mcsacore', 'mfeann', 'mfevtps',
            # Kaspersky
            'kaspersky', 'kavfs', 'avp', 'klnagent', 'kavtray', 'klelamx86', 'ksdeui', 'kavsvc',
            # Avast
            'avast', 'avastui', 'avastsvc', 'avastantivirus', 'avastbrowser',
            # AVG
            'avg', 'avgui', 'avgidsagent', 'avgwdsvc', 'avgtray',
            # Bitdefender
            'bitdefender', 'bdagent', 'bdservicehost', 'bdwtxag', 'updatesrv',
            # ESET
            'eset', 'egui', 'ekrn', 'eamonm', 'ecmd', 'esetonlineinstaller',
            # Sophos
            'sophos', 'savservice', 'savadminservice', 'swi_service', 'swc_service',
            # Trend Micro (other products)
            'trendmicro', 'tmproxy', 'tmpfw', 'tmccsf', 'pccntmon', 'titanium',
            # Windows Defender
            'defender', 'msmpeng', 'mssense', 'windefend', 'antimalware', 'msascuil',
            # Avira
            'avira', 'avgnt', 'avshadow', 'sched', 'avguard',
            # F-Secure
            'fsecure', 'fsgk32', 'fssm32', 'fswebfilter', 'fsav32',
            # Comodo
            'comodo', 'cfp', 'cmdagent', 'cistray', 'cavtray',
            # Malwarebytes
            'malwarebytes', 'mbam', 'mbamservice', 'mbamtray', 'mbae',
            # Webroot
            'webroot', 'wrsa', 'wrskynet', 'wrcleaner',
            # EXPANDED: Lesser-known AV vendors
            'quickheal', 'gdata', 'immunet', 'vipre', 'drweb', 'qihoo360', 'k7antivirus',
            'spybot', 'superantispyware', 'arcabit', 'zillya', 'bullguard', 'adaware',
            'panda', 'emsisoft', 'zemana', 'hitmanpro', 'iobit', 'baidu', 'rising',
            # General AV terms (EXPANDED)
            'antivirus', 'antiviruses', 'antimalware', 'virusscanner', 'realtime protection',
            'scan', 'scanner', 'guard', 'shield', 'protect', 'security', 'firewall',
            'virus', 'malware', 'threat', 'detection', 'quarantine', 'realtime'
        ]
        
        # HYBRID DETECTION STRATEGY
        av_processes = []
        suspicious_processes = []  # For secondary analysis
        
        # EDR/Advanced Security Exclusion Patterns (NOT traditional AV)
        edr_exclusion_patterns = [
            # CrowdStrike Falcon
            'csfalcon', 'crowdstrike', 'csagent', 'falcon',
            # Guardicore by Akamai
            'guardicore', 'akamai', 'guardian',
            # Other major EDR vendors
            'carbonblack', 'carbon black', 'cb', 'sentinelone', 'sentinel', 
            'cybereason', 'cortex', 'xdr', 'palo alto', 'cylance',
            'tanium', 'endgame', 'fireeye', 'mandiant', 'mcafee mvision',
            # Generic EDR terms
            'edr', 'endpoint detection', 'threat hunting', 'incident response'
        ]
        
        for process in process_list:
            process_lower = process.lower()
            
            # FIRST: Check if it's an EDR solution (exclude immediately)
            is_edr = any(edr_pattern in process_lower for edr_pattern in edr_exclusion_patterns)
            if is_edr:
                continue  # Skip EDR processes entirely
            
            # Primary detection: Known AV patterns
            is_av_related = any(pattern in process_lower for pattern in av_patterns)
            
            # Secondary detection: Common AV executable patterns
            if not is_av_related:
                # Enhanced AV executable suffixes and patterns
                av_suffixes = [
                    'guard.exe', 'scan.exe', 'tray.exe', 'service.exe', 'agent.exe', 'ui.exe',
                    'monitor.exe', 'engine.exe', 'core.exe', 'updater.exe', 'manager.exe'
                ]
                is_av_related = any(process_lower.endswith(suffix) for suffix in av_suffixes)
            
            # Tertiary detection: Suspicious process naming patterns
            if not is_av_related:
                # Patterns that might indicate AV software
                suspicious_patterns = [
                    # Common AV naming conventions
                    r'.*av.*\.exe$', r'.*virus.*\.exe$', r'.*security.*\.exe$',
                    r'.*protect.*\.exe$', r'.*safe.*\.exe$', r'.*clean.*\.exe$',
                    # Service/daemon patterns
                    r'.*svc\.exe$', r'.*srv\.exe$', r'.*daemon\.exe$',
                    # Process names with numbers (common in AV)
                    r'.*\d+.*\.exe$'
                ]
                
                import re
                for pattern in suspicious_patterns:
                    if re.match(pattern, process_lower):
                        suspicious_processes.append(process)
                        break
            
            # Include if AV-related or system security process
            if is_av_related or any(term in process_lower for term in ['security', 'protection', 'antimalware']):
                av_processes.append(process)
        
        # Always include some key system processes for context
        system_security_processes = [proc for proc in process_list 
                                   if any(term in proc.lower() for term in ['winlogon', 'csrss', 'services', 'svchost'])]
        
        # ENHANCED: Include suspicious processes for AI analysis (with limit)
        suspicious_sample = suspicious_processes[:10]  # Limit to prevent overload
        
        # Combine all categories (avoid duplicates)
        filtered_processes = list(set(av_processes + system_security_processes[:5] + suspicious_sample))
        
        return filtered_processes

    def analyze_conflicts(self, process_list: List[str]) -> str:
        """Analyze for AV conflicts with performance optimization and pre-filtering"""
        try:
            if not process_list:
                return "No processes found to analyze"
            
            # Pre-filter to focus on Anti-Virus processes only
            av_focused_processes = self.filter_antivirus_processes(process_list)
            
            if not av_focused_processes:
                return "No Anti-Virus related processes detected - Deep Security installation should proceed safely"
            
            # PERFORMANCE OPTIMIZATION: Aggressive process limiting
            original_count = len(av_focused_processes)
            if len(av_focused_processes) > 15:  # Further reduced for speed
                # Prioritize known AV processes first
                known_av_terms = ['norton', 'mcafee', 'kaspersky', 'avast', 'avg', 'bitdefender', 'eset', 'sophos', 'avira', 'defender']
                priority_processes = [p for p in av_focused_processes if any(term in p.lower() for term in known_av_terms)]
                other_processes = [p for p in av_focused_processes if not any(term in p.lower() for term in known_av_terms)]
                
                # Take top priority processes + some others
                av_focused_processes = priority_processes[:10] + other_processes[:5]
                print(f"⚡ Performance mode: analyzing {len(av_focused_processes)}/{original_count} processes")
            
            return self._perform_ai_analysis(av_focused_processes, len(process_list))
            
        except Exception as e:
            return f"Unexpected error analyzing conflicts: {str(e)}"
            
    def _perform_ai_analysis(self, av_focused_processes: List[str], original_count: int) -> str:
        """Perform optimized AI analysis with timeout handling"""
        try:
            # Check if OpenAI is available
            if not OPENAI_AVAILABLE:
                return "OpenAI library not available for analysis"
            
            from config import get_config
            config = get_config()
            
            # Validate API configuration
            if not config.OPENAI_API_KEY:
                return "OpenAI API key not configured"
            
            try:
                # PERFORMANCE OPTIMIZATION: Increased timeout and optimized client settings
                client = OpenAI(
                    api_key=config.OPENAI_API_KEY,
                    base_url=config.OPENAI_BASE_URL,
                    timeout=60.0  # Increased from 30 to 60 seconds
                )
            except Exception as e:
                return f"Failed to initialize OpenAI client: {str(e)}"
                
            # PERFORMANCE OPTIMIZATION: Streamlined prompt for faster processing
            prompt = (
                "You are an Anti-Virus Conflict Detection Expert for Trend Micro Deep Security.\n\n"
                
                "TASK: Analyze processes and identify ONLY Anti-Virus software conflicts.\n\n"
                
                "DETECTION CRITERIA:\n"
                "✅ INCLUDE: Norton, McAfee, Kaspersky, Avast, AVG, Bitdefender, ESET, Sophos, Avira, F-Secure, Comodo, Malwarebytes, Windows Defender, Quick Heal, G Data, Dr.Web, Immunet, VIPRE, K7, and other legitimate AV vendors\n"
                "❌ EXCLUDE: EDR solutions (CrowdStrike Falcon, Guardicore/Akamai, Carbon Black, SentinelOne, Cybereason, Cortex XDR), Firewalls, VPN, backup tools, virtualization software\n\n"
                
                "STREAMLINED ANALYSIS:\n"
                "1. Quickly identify known AV processes\n"
                "2. Check suspicious processes for AV characteristics\n"
                "3. Report conflicts only if real Anti-Virus software found\n\n"
                
                "OUTPUT FORMAT:\n"
                "Start with: 'CONFLICTS DETECTED' or 'NO CONFLICTS DETECTED'\n\n"
                "For each AV product found:\n"
                "### [AV Product] - [Vendor]\n"
                "**Main Process:** [process.exe]\n"
                "**Risk Level:** [High/Medium/Low]\n"
                "**Deep Security Impact:** [Brief impact description]\n\n"
                
                f"ANALYZE THESE {len(av_focused_processes)} PROCESSES:\n{chr(10).join(av_focused_processes)}\n\n"
                f"Focus on efficiency - identify real AV conflicts quickly."
            )
            
            try:
                # PERFORMANCE OPTIMIZATION: Reduced token limit and increased temperature for faster processing
                response = client.chat.completions.create(
                    model=config.OPENAI_MODEL,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=2000,  # Reduced from 4000 to 2000 for faster processing
                    temperature=0.5,  # Increased from 0.3 to 0.5 for faster, less overthinking
                    timeout=60  # Increased timeout to 60 seconds
                )
                
                text = response.choices[0].message.content
                
            except Exception as api_error:
                # FALLBACK: If AI fails, provide basic analysis
                return self._fallback_analysis(av_focused_processes)
            
            conflicts = self.parse_conflict_response(text)
            
            # Return just the raw AI response text, not HTML formatted
            return text
            
        except Exception as e:
            return self._fallback_analysis(av_focused_processes)
            
    def _fallback_analysis(self, av_focused_processes: List[str]) -> str:
        """Fallback analysis when AI times out - basic pattern matching with EDR exclusion"""
        known_av_patterns = {
            'norton': 'Norton/Symantec',
            'mcafee': 'McAfee',
            'kaspersky': 'Kaspersky', 
            'avast': 'Avast',
            'avg': 'AVG',
            'bitdefender': 'Bitdefender',
            'eset': 'ESET',
            'sophos': 'Sophos',
            'defender': 'Windows Defender',
            'quickheal': 'Quick Heal',
            'gdata': 'G Data',
            'immunet': 'Immunet'
        }
        
        # EDR exclusion patterns
        edr_patterns = ['csfalcon', 'crowdstrike', 'guardicore', 'akamai', 'carbonblack', 'sentinel']
        
        detected_avs = []
        for process in av_focused_processes:
            process_lower = process.lower()
            
            # Skip if it's an EDR solution
            if any(edr in process_lower for edr in edr_patterns):
                continue
                
            for pattern, vendor in known_av_patterns.items():
                if pattern in process_lower:
                    detected_avs.append(f"{vendor} ({process})")
                    break
        
        if detected_avs:
            result = "CONFLICTS DETECTED\n\n"
            result += "⚠️ AI Analysis timed out - using basic detection:\n\n"
            for i, av in enumerate(detected_avs, 1):
                result += f"### {av}\n"
                result += "**Risk Level:** Medium\n" 
                result += "**Deep Security Impact:** Potential conflict - manual review recommended\n\n"
            return result
        else:
            return "NO CONFLICTS DETECTED\n\n✅ Basic analysis found no obvious Anti-Virus conflicts"

    def parse_conflict_response(self, response_text: str) -> List[Dict[str, str]]:
        """Parse AI response to extract Anti-Virus conflict information with parent/sub-process details"""
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
        
        # Enhanced parsing for Anti-Virus specific format with process hierarchy
        in_policy_section = False
        in_resolution_section = False
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Look for AV software headers: ### [AV Product Name] - [Vendor]
            if line.startswith("###") and ("-" in line or any(av_indicator in line.lower() for av_indicator in ["antivirus", "security", "defender", "norton", "mcafee", "kaspersky", "avast", "avg", "bitdefender", "eset", "sophos", "avira", "f-secure", "comodo", "malwarebytes"])):
                if current_conflict:
                    conflicts.append(current_conflict)
                
                # Extract AV product name and vendor
                software_info = line.replace("###", "").strip()
                
                current_conflict = {
                    'name': software_info,
                    'description': '',
                    'av_main_process': '',
                    'av_parent_process': '',
                    'av_sub_processes': '',
                    'vendor_research': '',  # NEW: Track vendor research findings
                    'conflict_assessment': '',
                    'installation_risk': '',
                    'policy_exclusions': [],
                    'resolution_steps': []
                }
                in_policy_section = False
                in_resolution_section = False
                
            # Parse AV-specific process information
            elif line.startswith("**AV Main Process:**"):
                current_conflict['av_main_process'] = line.replace("**AV Main Process:**", "").strip()
            elif line.startswith("**AV Parent Process:**"):
                current_conflict['av_parent_process'] = line.replace("**AV Parent Process:**", "").strip()
            elif line.startswith("**AV Sub-Processes:**"):
                current_conflict['av_sub_processes'] = line.replace("**AV Sub-Processes:**", "").strip()
            elif line.startswith("**Vendor Research:**"):
                current_conflict['vendor_research'] = line.replace("**Vendor Research:**", "").strip()
            elif line.startswith("**Conflict Assessment:**"):
                current_conflict['conflict_assessment'] = line.replace("**Conflict Assessment:**", "").strip()
            elif line.startswith("**Installation Risk:**"):
                current_conflict['installation_risk'] = line.replace("**Installation Risk:**", "").strip()
                
            # Parse existing fields
            elif line.startswith("**Process Found:**"):
                # For backward compatibility, map to av_main_process if not set
                if not current_conflict.get('av_main_process'):
                    current_conflict['av_main_process'] = line.replace("**Process Found:**", "").strip()
            elif line.startswith("**Deep Security Policy Exclusions Required:**"):
                in_policy_section = True
                in_resolution_section = False
            elif line.startswith("**Resolution Steps:**"):
                in_resolution_section = True
                in_policy_section = False
            elif line.startswith(('-', '*', '•')) and current_conflict:
                detail = line.lstrip('- *•').strip()
                if in_policy_section:
                    current_conflict['policy_exclusions'].append(detail)
                elif in_resolution_section:
                    current_conflict['resolution_steps'].append(detail)
                else:
                    # General description
                    if current_conflict.get('description'):
                        current_conflict['description'] += f" {detail}"
                    else:
                        current_conflict['description'] = detail
            elif line and current_conflict and not line.startswith("**"):
                # Add to general description if not in specific sections
                if not in_policy_section and not in_resolution_section:
                    if current_conflict.get('description'):
                        current_conflict['description'] += f" {line}"
                    else:
                        current_conflict['description'] = line
        
        # Add final conflict if exists
        if current_conflict:
            conflicts.append(current_conflict)
        
        return conflicts

    def format_conflict_results(self, analysis_text: str, conflicts: List[Dict], status: str) -> str:
        """Format conflict analysis results"""
        
        if status == "error":
            status_color = "#dc3545"
            status_text = "ANALYSIS ERROR"
            status_icon = "⚠️"
        elif conflicts:  # Only check conflicts list, not text content
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
                        </div>
                    </div>
                </div>
            </div>
        </div>
        """
        
        if conflicts:
            html += """
            <div class="row mb-4">
                <div class="col-12">
                    <div class="card">
                        <div class="card-header">
                            <i class="fa-solid fa-virus-slash text-danger"></i> 
                            Anti-Virus Conflicts Detected - Deep Security Installation Assessment
                        </div>
                        <div class="card-body">
            """
            
            for i, conflict in enumerate(conflicts, 1):
                name = conflict.get('name', 'Unknown Anti-Virus Software')
                av_main_process = conflict.get('av_main_process', conflict.get('process_found', 'Not detected'))
                av_parent_process = conflict.get('av_parent_process', 'Not specified')
                av_sub_processes = conflict.get('av_sub_processes', 'Not specified')
                conflict_assessment = conflict.get('conflict_assessment', 'Anti-virus conflict assessment not available')
                installation_risk = conflict.get('installation_risk', 'Unknown')
                policy_exclusions = conflict.get('policy_exclusions', [])
                resolution_steps = conflict.get('resolution_steps', [])
                description = conflict.get('description', 'Anti-virus software detected that may conflict with Deep Security')
                
                # Determine risk color based on installation risk
                risk_color = "warning"
                risk_bg = "#fff3cd"
                if "high" in installation_risk.lower():
                    risk_color = "danger"
                    risk_bg = "#f8d7da"
                elif "low" in installation_risk.lower():
                    risk_color = "success"
                    risk_bg = "#d1f2eb"
                
                html += f"""
                <div class="mb-4 p-4" style="border: 2px solid #dee2e6; border-radius: 12px; background-color: {risk_bg};">
                    <h5 class="text-{risk_color} mb-3">
                        <i class="fa-solid fa-shield-virus"></i> 
                        {i}. {name}
                    </h5>
                    
                    <!-- Anti-Virus Process Hierarchy -->
                    <div class="row mb-3">
                        <div class="col-md-6">
                            <div class="card border-primary">
                                <div class="card-header bg-primary text-white">
                                    <i class="fa-solid fa-cogs"></i> AV Process Hierarchy
                                </div>
                                <div class="card-body">"""
                
                if av_main_process and av_main_process != 'Not detected':
                    html += f"""
                                    <div class="mb-2">
                                        <strong class="text-primary">Main Process:</strong>
                                        <br><code class="bg-dark text-light p-1 rounded">{av_main_process}</code>
                                    </div>"""
                
                if av_parent_process and av_parent_process != 'Not specified':
                    html += f"""
                                    <div class="mb-2">
                                        <strong class="text-info">Parent Process:</strong>
                                        <br><code class="bg-dark text-light p-1 rounded">{av_parent_process}</code>
                                    </div>"""
                
                if av_sub_processes and av_sub_processes != 'Not specified':
                    html += f"""
                                    <div class="mb-2">
                                        <strong class="text-secondary">Sub-Processes:</strong>
                                        <br><code class="bg-dark text-light p-1 rounded">{av_sub_processes}</code>
                                    </div>"""
                
                html += """
                                </div>
                            </div>
                        </div>
                        <div class="col-md-6">
                            <div class="card border-warning">
                                <div class="card-header bg-warning text-dark">
                                    <i class="fa-solid fa-exclamation-triangle"></i> Deep Security Risk Assessment
                                </div>
                                <div class="card-body">"""
                
                html += f"""
                                    <div class="mb-2">
                                        <strong>Installation Risk:</strong>
                                        <span class="badge bg-{risk_color} ms-2">{installation_risk}</span>
                                    </div>
                                    <div class="mb-2">
                                        <strong>Conflict Details:</strong>
                                        <p class="mt-1 text-muted small">{conflict_assessment}</p>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <div class="mb-3">
                        <strong>Analysis:</strong> {description}
                    </div>
                """
                
                if policy_exclusions:
                    html += """
                    <div class="mb-3">
                        <h6 class="text-primary">
                            <i class="fa-solid fa-cog"></i> Required Policy Exclusions:
                        </h6>
                        <div class="alert alert-info">
                    """
                    for exclusion in policy_exclusions:
                        html += f'<div class="mb-1"><code>{exclusion}</code></div>'
                    html += """
                        </div>
                    </div>
                    """
                
                if resolution_steps:
                    html += """
                    <div class="mb-3">
                        <h6 class="text-success">
                            <i class="fa-solid fa-list-check"></i> Resolution Steps:
                        </h6>
                        <ol class="mb-0">
                    """
                    for step in resolution_steps:
                        html += f'<li class="mb-2">{step}</li>'
                    html += """
                        </ol>
                    </div>
                    """
                
                html += """
                </div>
                """
            
            html += """
                        <div class="mt-4 p-3" style="background-color: #d1ecf1; border-radius: 8px;">
                            <h6 class="text-info mb-2">
                                <i class="fa-solid fa-lightbulb"></i> Quick Access to Deep Security Manager:
                            </h6>
                            <p class="mb-1"><strong>Web Console:</strong> https://[DSM-Server]:4119</p>
                            <p class="mb-1"><strong>Policy Path:</strong> Policies → [Your Policy] → Anti-Malware → Exclusions</p>
                            <p class="mb-0"><strong>Apply Changes:</strong> Don't forget to apply the policy after adding exclusions</p>
                        </div>
                        </div>
                    </div>
                </div>
            </div>
            """
        
        return html

    def analyze(self, file_paths: Union[str, List[str]], file_mapping: Dict[str, str] = None) -> Dict[str, Any]:
        """Standardized analysis entry point for conflict analysis
        
        Args:
            file_paths: List of file paths to analyze
            file_mapping: Optional mapping of temp_path -> original_filename for uploaded files
        """
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
                # Check original filename if mapping available
                original_name = file_mapping.get(file_path, '') if file_mapping else ''
                
                # Check both actual path and original filename
                if (file_path.lower().endswith('.xml') and 'runningprocess' in file_path.lower()) or \
                   (original_name.lower().endswith('.xml') and 'runningprocess' in original_name.lower()):
                    xml_file = file_path
                    break
            
            if not xml_file:
                available_files = []
                for file_path in file_paths:
                    original_name = file_mapping.get(file_path, '') if file_mapping else ''
                    if original_name:
                        available_files.append(f"{original_name} (temp: {os.path.basename(file_path)})")
                    else:
                        available_files.append(os.path.basename(file_path))
                
                return {
                    'analysis_type': 'conflict',
                    'status': 'error',
                    'summary': 'No RunningProcesses.xml file found',
                    'details': [
                        'Conflict analysis requires RunningProcesses.xml file',
                        f'Available files: {", ".join(available_files)}'
                    ],
                    'recommendations': ['Please provide the RunningProcesses.xml file from the diagnostic package'],
                    'severity': 'medium',
                    'error': True,
                    'metadata': {
                        'files_processed': len(file_paths),
                        'error_type': 'missing_xml_file',
                        'available_files': available_files
                    }
                }
            
            self._update_progress("XML Processing", "Extracting process information", 30)
            processes = self.extract_processes_from_xml(xml_file)
            
            self._update_progress("Conflict Analysis", "Analyzing for AV conflicts", 70)
            analysis_html = self.analyze_conflicts(processes)
            
            # Parse conflicts from AI response to get structured data
            conflicts_list = self.parse_conflict_response(analysis_html)
            
            self._update_progress("Standardization", "Converting to standardized format", 90)
            
            # Determine conflict status based on AI response content AND parsed conflicts
            conflicts_detected = (
                "CONFLICTS DETECTED" in analysis_html and 
                "NO CONFLICTS DETECTED" not in analysis_html
            ) or len(conflicts_list) > 0
            
            severity = 'high' if conflicts_detected else 'low'
            
            # Extract key insights from analysis
            details = []
            recommendations = []
            
            if conflicts_detected:
                details.append(f"Potential antivirus conflicts detected - {len(conflicts_list)} conflicts found")
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
            
            # Apply standardized output format with enhanced metadata
            standardized_result = self._standardize_analyzer_output({
                'conflicts_detected': conflicts_detected,
                'conflicts_list': conflicts_list,
                'processes_analyzed': len(processes),
                'analysis_html': analysis_html
            }, 'conflict')
            
            # Override with specific conflict analysis details
            standardized_result.update({
                'summary': f"Conflict analysis completed - {'Conflicts detected' if conflicts_detected else 'No conflicts found'}",
                'details': details,
                'recommendations': recommendations,
                'severity': severity,
                'formatted_output': analysis_html,
                'metadata': {
                    'files_processed': len(file_paths),
                    'xml_file': os.path.basename(xml_file),
                    'processes_analyzed': len(processes),
                    'conflicts_detected': conflicts_detected,
                    'conflicts_count': len(conflicts_list),
                    'conflicts_list': conflicts_list
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
                print(f"📊 Conflict Progress - {stage}: {message}")
            except Exception as e:
                print(f"⚠️ Conflict Progress update failed: {e}")
        else:
            # Fallback to console logging
            print(f"🔄 ConflictAnalyzer: {stage} - {message}")
            if percentage is not None:
                print(f"📊 Progress: {percentage}%")
