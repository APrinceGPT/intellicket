# -*- coding: utf-8 -*-
"""
DiagnosticPackageAnalyzer - Comprehensive analysis of diagnostic packages with multi-log correlation
Extracted from analyzers.py lines 3725-4626 with safety enhancements
"""

from .shared_imports import *
from .base.standardizer import AnalyzerOutputStandardizer

class DiagnosticPackageAnalyzer(AnalyzerOutputStandardizer):
    """Deep Security Diagnostic Package Analyzer - Comprehensive analysis of diagnostic packages with multi-log correlation"""
    
    def __init__(self, session_manager=None, session_id=None, rag_system=None, ml_analyzer=None):
        """Initialize the Diagnostic Package Analyzer with enhanced ML/RAG support"""
        self.session_manager = session_manager
        self.session_id = session_id
        self.rag_system = rag_system
        self.ml_analyzer = ml_analyzer
        
        # Initialize analyzers for different log types with safe imports
        self._initialize_sub_analyzers()
        
        # Package analysis patterns
        self._initialize_package_patterns()

    def _initialize_sub_analyzers(self):
        """Initialize sub-analyzers with safe imports to prevent circular dependencies"""
        try:
            # Import from modular system first, fallback to legacy if needed
            from .ds_agent_log_analyzer import DSAgentLogAnalyzer
            self.ds_analyzer = DSAgentLogAnalyzer(self.session_manager, self.session_id, self.rag_system, self.ml_analyzer)
        except ImportError:
            # Fallback during transition period
            try:
                from analyzers_original import DSAgentLogAnalyzer
                self.ds_analyzer = DSAgentLogAnalyzer(self.session_manager, self.session_id, self.rag_system, self.ml_analyzer)
            except ImportError:
                print("⚠️ DSAgentLogAnalyzer not available for DiagnosticPackageAnalyzer")
                self.ds_analyzer = None
        
        try:
            from .amsp_analyzer import AMSPAnalyzer
            self.amsp_analyzer = AMSPAnalyzer(self.session_manager, self.session_id)
        except ImportError:
            try:
                from analyzers_original import AMSPAnalyzer
                self.amsp_analyzer = AMSPAnalyzer(self.session_manager, self.session_id)
            except ImportError:
                print("⚠️ AMSPAnalyzer not available for DiagnosticPackageAnalyzer")
                self.amsp_analyzer = None
        
        try:
            from .conflict_analyzer import ConflictAnalyzer
            self.conflict_analyzer = ConflictAnalyzer()
        except ImportError:
            try:
                from analyzers_original import ConflictAnalyzer
                self.conflict_analyzer = ConflictAnalyzer()
            except ImportError:
                print("⚠️ ConflictAnalyzer not available for DiagnosticPackageAnalyzer")
                self.conflict_analyzer = None
        
        try:
            from .resource_analyzer import ResourceAnalyzer
            self.resource_analyzer = ResourceAnalyzer(self.session_manager, self.session_id, self.rag_system, self.ml_analyzer)
        except ImportError:
            try:
                from analyzers_original import ResourceAnalyzer
                self.resource_analyzer = ResourceAnalyzer(self.session_manager, self.session_id, self.rag_system, self.ml_analyzer)
            except ImportError:
                print("⚠️ ResourceAnalyzer not available for DiagnosticPackageAnalyzer")
                self.resource_analyzer = None
        
        try:
            from .ds_agent_offline_analyzer import DSAgentOfflineAnalyzer
            self.offline_analyzer = DSAgentOfflineAnalyzer(self.rag_system, self.ml_analyzer, self.session_manager, self.session_id)
        except ImportError:
            try:
                from analyzers_original import DSAgentOfflineAnalyzer
                self.offline_analyzer = DSAgentOfflineAnalyzer(self.rag_system, self.ml_analyzer, self.session_manager, self.session_id)
            except ImportError:
                print("⚠️ DSAgentOfflineAnalyzer not available for DiagnosticPackageAnalyzer")
                self.offline_analyzer = None

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

    def analyze(self, file_paths: Union[str, List[str]]) -> Dict[str, Any]:
        """Standardized analysis entry point for diagnostic packages"""
        import os
        
        try:
            self._update_progress("Initialization", "Starting diagnostic package analysis", 1)
            
            # Normalize input to handle both string and list
            if isinstance(file_paths, list):
                if not file_paths:
                    raise ValueError("No diagnostic package files provided")
                zip_path = file_paths[0]  # Take first file for diagnostic package
            else:
                zip_path = file_paths
            
            # Validate input
            if not zip_path or not os.path.exists(zip_path):
                raise ValueError(f"Invalid zip file path: {zip_path}")
            
            # Perform comprehensive analysis
            self._update_progress("Analysis", "Performing comprehensive diagnostic package analysis", 20)
            raw_results = self.analyze_diagnostic_package(zip_path)
            
            # Apply standardized output format
            self._update_progress("Standardization", "Converting to standardized format", 90)
            standardized_result = self._standardize_analyzer_output(raw_results, 'diagnostic_package')
            
            # Add raw_data field for consistency
            standardized_result['raw_data'] = raw_results or {}
            
            # Add metadata
            if raw_results and isinstance(raw_results, dict):
                summary = raw_results.get('summary', {})
                standardized_result['metadata'] = {
                    'files_processed': summary.get('files_analyzed', 0),
                    'file_count': summary.get('files_analyzed', 0),
                    'analysis_type': 'diagnostic_package',
                    'log_entries_processed': summary.get('total_entries', 0),
                    'errors_found': len(raw_results.get('critical_issues', [])),
                    'warnings_found': len(raw_results.get('warnings', [])),
                    'critical_issues': len(raw_results.get('critical_issues', []))
                }
            else:
                standardized_result['metadata'] = {
                    'files_processed': 0,
                    'file_count': 0,
                    'analysis_type': 'diagnostic_package',
                    'log_entries_processed': 0,
                    'errors_found': 0,
                    'warnings_found': 0,
                    'critical_issues': 0
                }
            
            # Generate formatted output
            self._update_progress("Output Formatting", "Generating formatted HTML output", 98)
            from routes import format_diagnostic_package_results
            formatted_html = format_diagnostic_package_results(raw_results)
            standardized_result['formatted_output'] = formatted_html
            
            self._update_progress("Completion", "Diagnostic package analysis completed", 100)
            return standardized_result
            
        except Exception as e:
            error_msg = f"Diagnostic package analysis failed: {str(e)}"
            self._update_progress("Error", error_msg, None)
            return {
                'analysis_type': 'diagnostic_package',
                'status': 'error',
                'summary': error_msg,
                'details': [error_msg],
                'recommendations': ['Please ensure valid diagnostic package file is provided'],
                'severity': 'high',
                'error': True,
                'metadata': {
                    'files_processed': 0,
                    'error_type': 'analysis_failure'
                }
            }

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
            if extracted_files['ds_agent_logs'] and self.ds_analyzer:
                ds_files = [f['file_path'] for f in extracted_files['ds_agent_logs']]
                if len(ds_files) == 1:
                    comprehensive_results['individual_analyses']['ds_agent'] = self.ds_analyzer.analyze_log_file(ds_files[0])
                else:
                    comprehensive_results['individual_analyses']['ds_agent'] = self.ds_analyzer.analyze_multiple_log_files(ds_files)
            
            self._update_progress("Individual Analysis", "Analyzing AMSP logs", 40)
            
            # AMSP Log Analysis
            if extracted_files['amsp_logs'] and self.amsp_analyzer:
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
            running_process_files = [f for f in extracted_files['system_info'] if 'RunningProcesses.xml' in f['file_name']]
            busy_process_files = [f for f in extracted_files['system_info'] if 'TopNBusyProcess.txt' in f['file_name']]
            
            if running_process_files:
                # AV Conflict Analysis
                if self.conflict_analyzer:
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
                if busy_process_files and self.resource_analyzer:
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
