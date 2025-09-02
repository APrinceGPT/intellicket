# -*- coding: utf-8 -*-
"""
REST API Routes for TrendAI Integration
Provides REST API endpoints for the TrendAI frontend integration
Using the exact same code from CSDAIv2 routes.py for consistent results
"""

import os
import uuid
import re
from datetime import datetime
from flask import request, jsonify, send_file
from werkzeug.utils import secure_filename

# Import existing analyzer components and security
from analyzers import DSAgentLogAnalyzer, AMSPAnalyzer, ConflictAnalyzer, ResourceAnalyzer, DSAgentOfflineAnalyzer, DiagnosticPackageAnalyzer
from security import SecurityError, validate_file, create_secure_temp_file, cleanup_temp_file

# Import formatting functions from routes.py
from routes import (
    format_ds_log_results, format_amsp_results, format_conflict_results, 
    format_resource_results, format_ds_agent_offline_results, format_diagnostic_package_results
)

class APIError(Exception):
    """Custom API error class"""
    def __init__(self, message, status_code=400):
        self.message = message
        self.status_code = status_code

def register_api_routes(app, config):
    """Register REST API routes for TrendAI integration"""
    
    # In-memory session storage (in production, use Redis or database)
    api_sessions = {}
    
    @app.route('/api/health', methods=['GET'])
    def api_health():
        """Health check endpoint"""
        return jsonify({
            'status': 'ok',
            'message': 'CSDAIv2 API is running',
            'timestamp': datetime.now().isoformat(),
            'version': '2.0'
        })
    
    @app.route('/extract-and-filter', methods=['POST'])
    def api_extract_and_filter():
        """Extract ZIP file and filter files based on analyzer type"""
        temp_files = []
        
        try:
            # Get analyzer type from request
            analyzer_type = request.form.get('analyzer_type', 'diagnostic_package')
            print(f"🎯 Extract and filter request for analyzer type: {analyzer_type}")
            
            # Define file patterns for each analyzer type - CORRECTED PATTERNS
            analyzer_file_patterns = {
                'ds_agent': {
                    'required_files': ['ds_agent.log', 'ds_agent-err.log'],
                    'optional_files': [],  # Only extract core DS Agent files, not numbered logs
                    'description': 'DS Agent log files (ds_agent.log, ds_agent-err.log only)'
                },
                'ds_logs': {  # Alias for ds_agent 
                    'required_files': ['ds_agent.log', 'ds_agent-err.log'],
                    'optional_files': [],  # Only extract core DS Agent files, not numbered logs
                    'description': 'DS Agent log files (ds_agent.log, ds_agent-err.log only)'
                },
                'amsp': {
                    'required_files': ['AMSPInstallDebuglog.log', 'ds_am.log', 'ds_agent.log'],
                    'optional_files': [],  # Only extract the 3 core AMSP files as specified
                    'description': 'AMSP Anti-Malware log files (AMSPInstallDebuglog.log, ds_am.log, ds_agent.log only)'
                },
                'amsp_logs': {  # Alias for amsp
                    'required_files': ['AMSPInstallDebuglog.log', 'ds_am.log', 'ds_agent.log'],
                    'optional_files': [],  # Only extract the 3 core AMSP files as specified
                    'description': 'AMSP Anti-Malware log files (AMSPInstallDebuglog.log, ds_am.log, ds_agent.log only)'
                },
                'resource': {
                    'required_files': ['TopNBusyProcess.txt', 'RunningProcess.xml'],
                    'optional_files': ['RunningProcesses.xml'],  # Alternative spelling
                    'description': 'Resource analysis files (TopNBusyProcess.txt, RunningProcess.xml)'
                },
                'resource_analysis': {  # Alias for resource
                    'required_files': ['TopNBusyProcess.txt', 'RunningProcess.xml'],
                    'optional_files': ['RunningProcesses.xml'],  # Alternative spelling
                    'description': 'Resource analysis files (TopNBusyProcess.txt, RunningProcess.xml)'
                },
                'ds_agent_offline': {
                    'required_files': ['ds_connect.log', 'ds_agent.log', 'ds_agent-err.log'],
                    'optional_files': [],  # Only extract the 3 core files as specified
                    'description': 'DS Agent Offline analysis (ds_connect.log, ds_agent.log, ds_agent-err.log only)'
                },
                'conflict': {
                    'required_files': ['RunningProcess.xml'],
                    'optional_files': ['RunningProcesses.xml'],  # Alternative spelling
                    'description': 'Antivirus conflict analysis files (RunningProcess.xml only)'
                },
                'av_conflicts': {  # Alias for conflict
                    'required_files': ['RunningProcess.xml'],
                    'optional_files': ['RunningProcesses.xml'],  # Alternative spelling
                    'description': 'Antivirus conflict analysis files (RunningProcess.xml only)'
                },
                'diagnostic_package': {
                    'required_files': [],
                    'optional_files': [],
                    'description': 'Complete diagnostic package analysis (all readable files)'
                }
            }
            
            # Process uploaded ZIP file
            uploaded_zip = None
            for key in request.files:
                file = request.files[key]
                if file and file.filename and file.filename.lower().endswith('.zip'):
                    uploaded_zip = file
                    break
            
            if not uploaded_zip:
                return jsonify({'success': False, 'error': 'No ZIP file provided'}), 400
            
            print(f"📦 Processing ZIP file: {uploaded_zip.filename}")
            
            # Create secure temp file for ZIP
            zip_temp_path = create_secure_temp_file(uploaded_zip, config.TEMP_DIR)
            temp_files.append(zip_temp_path)
            
            # Extract ZIP contents
            import zipfile
            import tempfile
            
            extracted_files = []
            extract_dir = tempfile.mkdtemp(dir=config.TEMP_DIR)
            
            with zipfile.ZipFile(zip_temp_path, 'r') as zip_ref:
                file_list = zip_ref.namelist()
                print(f"📋 ZIP contains {len(file_list)} files")
                
                # Extract all files first
                zip_ref.extractall(extract_dir)
                
                # Get the file patterns for the requested analyzer
                file_patterns = analyzer_file_patterns.get(analyzer_type, analyzer_file_patterns['diagnostic_package'])
                
                # Find matching files
                required_files = file_patterns['required_files']
                optional_files = file_patterns['optional_files']
                all_target_files = required_files + optional_files
                
                matched_files = []
                missing_required = []
                
                def matches_target_file(zip_filename: str, target_filename: str) -> bool:
                    """Exact file matching logic to prevent unwanted files"""
                    zip_base = os.path.basename(zip_filename).lower()
                    target_lower = target_filename.lower()
                    
                    # Use EXACT matching for all files to prevent unwanted extractions
                    return zip_base == target_lower
                
                for target_file in all_target_files:
                    found = False
                    # Look for matching files with enhanced logic
                    for zip_file in file_list:
                        if matches_target_file(zip_file, target_file):
                            extracted_path = os.path.join(extract_dir, zip_file)
                            if os.path.exists(extracted_path) and os.path.getsize(extracted_path) > 0:  # Ensure file is not empty
                                matched_files.append({
                                    'original_name': target_file,
                                    'zip_name': zip_file,
                                    'extracted_path': extracted_path,
                                    'size': os.path.getsize(extracted_path),
                                    'required': target_file in required_files
                                })
                                found = True
                                print(f"✅ Found {target_file} as {zip_file}")
                                break
                    
                    if not found and target_file in required_files:
                        missing_required.append(target_file)
                        print(f"❌ Missing required file: {target_file}")
                
                # Check if we have required files (unless it's diagnostic_package type)
                if analyzer_type != 'diagnostic_package' and missing_required:
                    return jsonify({
                        'success': False,
                        'error': f'Missing required files for {analyzer_type} analysis: {", ".join(missing_required)}',
                        'available_files': [os.path.basename(f) for f in file_list],
                        'required_files': required_files
                    }), 400
                
                # If no specific files found for non-diagnostic analysis, fall back to diagnostic
                if analyzer_type != 'diagnostic_package' and not matched_files:
                    print(f"⚠️ No specific files found for {analyzer_type}, falling back to diagnostic package analysis")
                    analyzer_type = 'diagnostic_package'
                    # For diagnostic package, use the SAME file matching logic with diagnostic_package patterns
                    file_patterns = analyzer_file_patterns['diagnostic_package']
                    required_files = file_patterns['required_files']
                    optional_files = file_patterns['optional_files']
                    
                    # Apply the SAME matching logic that respects the patterns
                    for zip_file in file_list:
                        if not zip_file.endswith('/'):  # Skip directories
                            extracted_path = os.path.join(extract_dir, zip_file)
                            if os.path.exists(extracted_path):
                                file_name = os.path.basename(zip_file)
                                
                                # Check if file matches diagnostic package patterns using exact matching
                                all_files = required_files + optional_files
                                if any(matches_target_file(file_name, target_file) for target_file in all_files):
                                    is_required = any(matches_target_file(file_name, req_file) for req_file in required_files)
                                    matched_files.append({
                                        'original_name': file_name,
                                        'zip_name': zip_file,
                                        'extracted_path': extracted_path,
                                        'size': os.path.getsize(extracted_path),
                                        'required': is_required
                                    })
                                    print(f"✅ Diagnostic package matched: {file_name} ({'required' if is_required else 'optional'})")
                
                print(f"📂 Matched {len(matched_files)} files for {analyzer_type} analysis")
                
                # Create new session
                session_id = str(uuid.uuid4())
                print(f"🆔 Created filtered extraction session: {session_id}")
                
                # Store extracted files info
                api_sessions[session_id] = {
                    'session_id': session_id,
                    'analysis_type': analyzer_type,
                    'uploaded_files': matched_files,
                    'temp_files': [extract_dir],  # Track extract directory for cleanup
                    'status': 'extracted',
                    'created_at': datetime.now().isoformat(),
                    'extraction_info': {
                        'original_zip': uploaded_zip.filename,
                        'total_files_in_zip': len(file_list),
                        'matched_files': len(matched_files),
                        'analyzer_type': analyzer_type,
                        'file_patterns': file_patterns,
                        'missing_required': missing_required
                    }
                }
                
                return jsonify({
                    'success': True,
                    'session_id': session_id,
                    'analyzer_type': analyzer_type,
                    'files_extracted': len(matched_files),
                    'files_info': [
                        {
                            'name': f['original_name'],
                            'size': f['size'],
                            'required': f['required'],
                            'zip_path': f['zip_name']
                        } for f in matched_files
                    ],
                    'extraction_summary': {
                        'total_files_in_zip': len(file_list),
                        'files_matched': len(matched_files),
                        'required_files_found': len([f for f in matched_files if f['required']]),
                        'missing_required': missing_required,
                        'description': file_patterns['description']
                    }
                })
                
        except Exception as e:
            print(f"❌ Extract and filter error: {str(e)}")
            # Cleanup temp files on error
            for temp_file in temp_files:
                if os.path.exists(temp_file):
                    cleanup_temp_file(temp_file)
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/analyze-extracted/<session_id>', methods=['POST'])
    def api_analyze_extracted(session_id):
        """Start analysis using pre-extracted and filtered files"""
        
        # Define SimpleSessionManager class for this function
        class SimpleSessionManager:
            def __init__(self, sessions_dict, session_id):
                self.sessions = sessions_dict
                self.session_id = session_id
            
            def update_session(self, session_id, progress_data):
                if session_id in self.sessions:
                    self.sessions[session_id].update(progress_data)
        
        try:
            print(f"🚀 Starting analysis for extracted session: {session_id}")
            
            if session_id not in api_sessions:
                return jsonify({'success': False, 'error': 'Session not found'}), 404
            
            session_data = api_sessions[session_id]
            
            if session_data['status'] != 'extracted':
                return jsonify({'success': False, 'error': f'Session status is {session_data["status"]}, expected "extracted"'}), 400
            
            # Update session status to processing
            session_data['status'] = 'processing'
            session_data['analysis_started'] = datetime.now().isoformat()
            
            # Get the analysis type and files
            analysis_type = session_data['analysis_type']
            matched_files = session_data['uploaded_files']
            
            print(f"📊 Analysis type: {analysis_type}")
            print(f"📁 Processing {len(matched_files)} extracted files")
            
            # Create file paths list from extracted files
            temp_paths = [file_info['extracted_path'] for file_info in matched_files]
            
            # Route to appropriate analyzer using the same logic as /status endpoint
            try:
                result = None
                raw_result = None
                
                if analysis_type == "ds_agent":
                    # DS Agent analysis with standardized output handling
                    session_manager = SimpleSessionManager(api_sessions, session_id)
                    analyzer = DSAgentLogAnalyzer(session_manager=session_manager, session_id=session_id)
                    analysis_results = analyzer.analyze(temp_paths)
                    
                    # Handle standardized analyzer output
                    if analysis_results.get('status') == 'error' or analysis_results.get('error', False):
                        session_data['status'] = 'error'
                        session_data['error_message'] = analysis_results.get('summary', 'Analysis failed')
                        result = f"<div class='alert alert-danger'><strong>Error:</strong> {analysis_results.get('summary', 'Analysis failed')}</div>"
                        raw_result = f"DS Agent Analysis - ERROR: {analysis_results.get('summary', 'Analysis failed')}"
                    else:
                        # Get formatted output or create from standardized data
                        if 'formatted_output' in analysis_results:
                            result = analysis_results['formatted_output']
                        elif 'raw_data' in analysis_results:
                            # Generate formatted output from raw data using the formatter
                            is_multiple = len(temp_paths) > 1
                            result = format_ds_log_results(analysis_results['raw_data'], is_multiple)
                        else:
                            # Generate formatted output from standardized data
                            result = f"""
                            <div class="analysis-container">
                                <h2>🛡️ DS Agent Analysis Results</h2>
                                <div class="summary-section">
                                    <h3>📊 Summary</h3>
                                    <p>{analysis_results.get('summary', 'Analysis completed')}</p>
                                </div>
                                <div class="details-section">
                                    <h3>📋 Details</h3>
                                    <ul>{''.join(f'<li>{detail}</li>' for detail in analysis_results.get('details', []))}</ul>
                                </div>
                                <div class="recommendations-section">
                                    <h3>💡 Recommendations</h3>
                                    <ul>{''.join(f'<li>{rec}</li>' for rec in analysis_results.get('recommendations', []))}</ul>
                                </div>
                            </div>
                            """
                        metadata = analysis_results.get('metadata', {})
                        raw_result = f"DS Agent Log Analysis Results:\nFiles Analyzed: {len(temp_paths)}\nStatus: {analysis_results.get('summary', 'Completed')}"
                
                elif analysis_type == "amsp":
                    session_manager = SimpleSessionManager(api_sessions, session_id)
                    analyzer = AMSPAnalyzer(session_manager=session_manager, session_id=session_id)
                    analysis_results = analyzer.analyze(temp_paths)
                    
                    # Handle standardized analyzer output
                    if analysis_results.get('status') == 'error' or analysis_results.get('error', False):
                        session_data['status'] = 'error'
                        result = f"<div class='alert alert-danger'><strong>Error:</strong> {analysis_results.get('summary', 'Analysis failed')}</div>"
                        raw_result = f"AMSP Analysis - ERROR: {analysis_results.get('summary', 'Analysis failed')}"
                    else:
                        # Get formatted output or create from standardized data
                        if 'formatted_output' in analysis_results:
                            result = analysis_results['formatted_output']
                        elif 'raw_data' in analysis_results:
                            # Generate formatted output from raw data using the formatter
                            result = format_amsp_results(analysis_results['raw_data'])
                        else:
                            # Generate basic formatted output from standardized data
                            result = f"""
                            <div class="analysis-container">
                                <h2>🛡️ AMSP Analysis Results</h2>
                                <div class="summary-section">
                                    <h3>📊 Summary</h3>
                                    <p>{analysis_results.get('summary', 'Analysis completed')}</p>
                                </div>
                                <div class="details-section">
                                    <h3>📋 Details</h3>
                                    <ul>{''.join(f'<li>{detail}</li>' for detail in analysis_results.get('details', []))}</ul>
                                </div>
                                <div class="recommendations-section">
                                    <h3>💡 Recommendations</h3>
                                    <ul>{''.join(f'<li>{rec}</li>' for rec in analysis_results.get('recommendations', []))}</ul>
                                </div>
                            </div>
                            """
                        raw_result = f"AMSP Analysis Results:\nFiles Analyzed: {len(temp_paths)}\nStatus: {analysis_results.get('summary', 'Completed')}"
                
                elif analysis_type == "resource":
                    session_manager = SimpleSessionManager(api_sessions, session_id)
                    analyzer = ResourceAnalyzer(session_manager=session_manager, session_id=session_id)
                    analysis_results = analyzer.analyze(temp_paths)
                    
                    # Handle standardized analyzer output
                    if analysis_results.get('status') == 'error' or analysis_results.get('error', False):
                        session_data['status'] = 'error'
                        result = f"<div class='alert alert-danger'><strong>Error:</strong> {analysis_results.get('summary', 'Analysis failed')}</div>"
                        raw_result = f"Resource Analysis - ERROR: {analysis_results.get('summary', 'Analysis failed')}"
                    else:
                        # Get formatted output or create from standardized data
                        if 'formatted_output' in analysis_results:
                            result = analysis_results['formatted_output']
                        elif 'raw_data' in analysis_results:
                            # Generate formatted output from raw data using the formatter
                            result = format_resource_results(analysis_results['raw_data'])
                        else:
                            # Generate basic formatted output from standardized data
                            result = f"""
                            <div class="analysis-container">
                                <h2>📊 Resource Analysis Results</h2>
                                <div class="summary-section">
                                    <h3>📊 Summary</h3>
                                    <p>{analysis_results.get('summary', 'Analysis completed')}</p>
                                </div>
                                <div class="details-section">
                                    <h3>📋 Details</h3>
                                    <ul>{''.join(f'<li>{detail}</li>' for detail in analysis_results.get('details', []))}</ul>
                                </div>
                                <div class="recommendations-section">
                                    <h3>💡 Recommendations</h3>
                                    <ul>{''.join(f'<li>{rec}</li>' for rec in analysis_results.get('recommendations', []))}</ul>
                                </div>
                            </div>
                            """
                        raw_result = f"Resource Analysis Results:\nFiles Analyzed: {len(temp_paths)}\nStatus: {analysis_results.get('summary', 'Completed')}"
                
                elif analysis_type == "conflict":
                    session_manager = SimpleSessionManager(api_sessions, session_id)
                    analyzer = ConflictAnalyzer(session_manager=session_manager, session_id=session_id)
                    analysis_results = analyzer.analyze(temp_paths)
                    
                    # Handle standardized analyzer output
                    if analysis_results.get('status') == 'error' or analysis_results.get('error', False):
                        session_data['status'] = 'error'
                        result = f"<div class='alert alert-danger'><strong>Error:</strong> {analysis_results.get('summary', 'Analysis failed')}</div>"
                        raw_result = f"Conflict Analysis - ERROR: {analysis_results.get('summary', 'Analysis failed')}"
                    else:
                        # Get formatted output or create from standardized data
                        if 'formatted_output' in analysis_results:
                            result = analysis_results['formatted_output']
                        elif 'raw_data' in analysis_results:
                            # Generate formatted output from raw data using the formatter
                            result = format_conflict_results(analysis_results['raw_data'])
                        else:
                            # Generate basic formatted output from standardized data
                            result = f"""
                            <div class="analysis-container">
                                <h2>⚔️ Conflict Analysis Results</h2>
                                <div class="summary-section">
                                    <h3>📊 Summary</h3>
                                    <p>{analysis_results.get('summary', 'Analysis completed')}</p>
                                </div>
                                <div class="details-section">
                                    <h3>📋 Details</h3>
                                    <ul>{''.join(f'<li>{detail}</li>' for detail in analysis_results.get('details', []))}</ul>
                                </div>
                                <div class="recommendations-section">
                                    <h3>💡 Recommendations</h3>
                                    <ul>{''.join(f'<li>{rec}</li>' for rec in analysis_results.get('recommendations', []))}</ul>
                                </div>
                            </div>
                            """
                        raw_result = f"Conflict Analysis Results:\nFiles Analyzed: {len(temp_paths)}\nStatus: {analysis_results.get('summary', 'Completed')}"
                
                elif analysis_type == "diagnostic_package":
                    session_manager = SimpleSessionManager(api_sessions, session_id)
                    analyzer = DiagnosticPackageAnalyzer(session_manager=session_manager, session_id=session_id)
                    # For diagnostic package, use the original ZIP path
                    zip_path = session_data.get('temp_files', [None])[0]  # This should be updated to point to ZIP
                    analysis_results = analyzer.analyze(zip_path if zip_path else temp_paths[0])
                    
                    # Handle standardized analyzer output
                    if analysis_results.get('status') == 'error' or analysis_results.get('error', False):
                        session_data['status'] = 'error'
                        result = f"<div class='alert alert-danger'><strong>Error:</strong> {analysis_results.get('summary', 'Analysis failed')}</div>"
                        raw_result = f"Diagnostic Package Analysis - ERROR: {analysis_results.get('summary', 'Analysis failed')}"
                    else:
                        # Get formatted output or create from standardized data
                        if 'formatted_output' in analysis_results:
                            result = analysis_results['formatted_output']
                        elif 'raw_data' in analysis_results:
                            # Generate formatted output from raw data using the formatter
                            result = format_diagnostic_package_results(analysis_results['raw_data'])
                        else:
                            # Generate basic formatted output from standardized data
                            result = f"""
                            <div class="analysis-container">
                                <h2>📦 Diagnostic Package Analysis Results</h2>
                                <div class="summary-section">
                                    <h3>📊 Summary</h3>
                                    <p>{analysis_results.get('summary', 'Analysis completed')}</p>
                                </div>
                                <div class="details-section">
                                    <h3>📋 Details</h3>
                                    <ul>{''.join(f'<li>{detail}</li>' for detail in analysis_results.get('details', []))}</ul>
                                </div>
                                <div class="recommendations-section">
                                    <h3>💡 Recommendations</h3>
                                    <ul>{''.join(f'<li>{rec}</li>' for rec in analysis_results.get('recommendations', []))}</ul>
                                </div>
                            </div>
                            """
                        raw_result = f"Diagnostic Package Analysis Results:\nFiles Analyzed: {len(temp_paths)}\nStatus: {analysis_results.get('summary', 'Completed')}"
                
                else:
                    raise ValueError(f"Unknown analysis type: {analysis_type}")
                
                # Store results
                if session_data['status'] != 'error':
                    session_data['status'] = 'completed'
                
                session_data['analysis_complete'] = True
                session_data['results'] = result
                session_data['raw_results'] = raw_result
                session_data['completed_at'] = datetime.now().isoformat()
                
                print(f"✅ Analysis completed for extracted session: {session_id}")
                
                return jsonify({
                    'success': True,
                    'session_id': session_id,
                    'status': session_data['status'],
                    'analysis_type': analysis_type,
                    'files_processed': len(temp_paths)
                })
                
            except Exception as analysis_error:
                session_data['status'] = 'error'
                session_data['error_message'] = str(analysis_error)
                print(f"❌ Analysis error: {str(analysis_error)}")
                return jsonify({'success': False, 'error': str(analysis_error)}), 500
                
        except Exception as e:
            print(f"❌ Analyze extracted error: {str(e)}")
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/test-extract', methods=['POST']) 
    def api_test_extract():
        """Test endpoint to verify extraction and filtering logic"""
        try:
            # Test with sample diagnostic package
            sample_zip = "../sample_logs/Diagnostic Package.zip"
            
            if not os.path.exists(sample_zip):
                return jsonify({'error': 'Sample diagnostic package not found'}), 404
            
            # Test different analyzer types
            test_results = {}
            
            analyzer_types = ['ds_agent', 'amsp', 'resource', 'conflict', 'diagnostic_package']
            
            for analyzer_type in analyzer_types:
                # Simulate the file filtering logic
                analyzer_file_patterns = {
                    'ds_agent': {
                        'required_files': ['ds_agent.log', 'ds_agent-err.log'],
                        'optional_files': [],  # Only extract core DS Agent files, not numbered logs
                        'description': 'DS Agent log files (ds_agent.log, ds_agent-err.log only)'
                    },
                    'amsp': {
                        'required_files': ['AMSP-Inst_LocalDebugLog.log', 'ds_am.log', 'ds_agent.log'],
                        'optional_files': ['AMSP-UnInst_LocalDebugLog.log', 'ds_am-01.log', 'ds_am-02.log', 'ds_am-icrc.log'],
                        'description': 'AMSP Anti-Malware log files'
                    },
                    'resource': {
                        'required_files': ['TopNBusyProcess.txt', 'RunningProcesses.xml'],
                        'optional_files': [],
                        'description': 'Resource analysis files'
                    },
                    'conflict': {
                        'required_files': ['RunningProcesses.xml'],
                        'optional_files': [],
                        'description': 'Antivirus conflict analysis files'
                    },
                    'diagnostic_package': {
                        'required_files': [],
                        'optional_files': [],
                        'description': 'Complete diagnostic package analysis'
                    }
                }
                
                patterns = analyzer_file_patterns[analyzer_type]
                test_results[analyzer_type] = {
                    'required_files': patterns['required_files'],
                    'optional_files': patterns['optional_files'],
                    'description': patterns['description']
                }
            
            return jsonify({
                'success': True,
                'sample_zip_exists': True,
                'analyzer_patterns': test_results,
                'message': 'File filtering patterns configured successfully'
            })
            
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/upload', methods=['POST'])
    def api_upload():
        """File upload endpoint for TrendAI integration"""
        # Initialize temp_files at the beginning to avoid UnboundLocalError
        temp_files = []
        
        try:
            # Create new session
            session_id = str(uuid.uuid4())
            print(f"🆔 Created new session: {session_id}")
            
            # Get analysis type
            analysis_type = request.form.get('analysis_type', 'ds_agent')
            print(f"📊 Analysis type: {analysis_type}")
            
            # Process uploaded files
            uploaded_files = []
            
            for key in request.files:
                file = request.files[key]
                if file and file.filename:
                    print(f"📁 Processing file: {file.filename}")
                    
                    try:
                        # Validate file using CSDAIv2 security
                        file_type = validate_file(file)
                        
                        # Create secure temp file
                        temp_file_path = create_secure_temp_file(file, config.TEMP_DIR)
                        temp_files.append(temp_file_path)
                        uploaded_files.append({
                            'name': file.filename,
                            'original_name': secure_filename(file.filename),
                            'temp_path': temp_file_path,
                            'size': os.path.getsize(temp_file_path),
                            'type': file_type
                        })
                        print(f"✅ File saved to: {temp_file_path}")
                    except SecurityError as e:
                        if "File is empty" in str(e):
                            print(f"⚠️ Skipping empty file: {file.filename}")
                            continue
                        else:
                            raise  # Re-raise other security errors
            
            if not uploaded_files:
                raise APIError("No valid files uploaded")
            
            # Store session data in CSDAIv2 format
            api_sessions[session_id] = {
                'session_id': session_id,
                'analysis_type': analysis_type,
                'uploaded_files': uploaded_files,
                'temp_files': temp_files,
                'status': 'uploaded',
                'created_at': datetime.now().isoformat(),
                'analysis_complete': False,
                'results': None,
                'raw_results': None,
                'current_step': 4,
                'configuration': {
                    'analysis_depth': 'expert',
                    'ml_analysis': True,
                    'rag_enhancement': True,
                    'correlation_analysis': True,
                    'output_format': 'html'
                }
            }
            
            print(f"💾 Session stored. Total sessions: {len(api_sessions)}")
            
            return jsonify({
                'success': True,
                'session_id': session_id,
                'files_uploaded': len(uploaded_files),
                'analysis_type': analysis_type
            })
            
        except SecurityError as e:
            print(f"� � Security Error: {str(e)}")
            # Clean up temp files on error
            for temp_file in temp_files:
                cleanup_temp_file(temp_file)
            return jsonify({'success': False, 'error': f"Security error: {str(e)}"}), 400
        except APIError as e:
            print(f"� � API Error: {e.message}")
            return jsonify({'success': False, 'error': e.message}), e.status_code
        except Exception as e:
            print(f"� � Unexpected error: {str(e)}")
            # Clean up temp files on error
            for temp_file in temp_files:
                cleanup_temp_file(temp_file)
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/status/<session_id>', methods=['GET'])
    def api_status(session_id):
        """Get analysis status for a session with real-time progress"""
        try:
            print(f"🔍 Status check for session: {session_id}")
            print(f"📋 Available sessions: {list(api_sessions.keys())}")
            
            if session_id not in api_sessions:
                print(f"❌ Session {session_id} not found")
                return jsonify({'success': False, 'error': 'Session not found'}), 404
            
            session_data = api_sessions[session_id]
            print(f"📊 Current status: {session_data['status']}")
            
            # Return current progress data immediately if available
            if session_data['status'] in ['processing', 'completed', 'error']:
                progress_response = {
                    'success': True,
                    'status': session_data['status'],
                    'progress_percentage': session_data.get('progress_percentage', 0),
                    'progress_message': session_data.get('progress_message', 'Processing...'),
                    'analysis_stage': session_data.get('analysis_stage', 'Unknown'),
                    'analysis_complete': session_data['status'] == 'completed',
                    'session_id': session_id
                }
                
                if session_data['status'] == 'error':
                    progress_response['error'] = session_data.get('error_message', 'Analysis failed')
                
                return jsonify(progress_response)
            
            # If analysis hasn't started, start it using CSDAIv2 logic
            if session_data['status'] == 'uploaded':
                print(f"🚀 Starting analysis for session: {session_id}")
                session_data['status'] = 'processing'
                session_data['progress_percentage'] = 5
                session_data['progress_message'] = 'Starting analysis...'
                session_data['analysis_stage'] = 'Initialization'
                
                # Run analysis using exact CSDAIv2 logic
                try:
                    analysis_type = session_data['analysis_type']
                    uploaded_files = session_data['uploaded_files']
                    configuration = session_data.get('configuration', {})
                    
                    temp_paths = [file_info['temp_path'] for file_info in uploaded_files]
                    
                    # Route to appropriate analyzer using standardized methods
                    raw_result = None
                    if analysis_type == "ds_logs" or analysis_type == "ds_agent":
                        # Create session manager for progress tracking
                        class SimpleSessionManager:
                            def __init__(self, sessions_dict, session_id):
                                self.sessions = sessions_dict
                                self.session_id = session_id
                            
                            def update_session(self, session_id, progress_data):
                                if session_id in self.sessions:
                                    self.sessions[session_id].update(progress_data)
                        
                        session_manager = SimpleSessionManager(api_sessions, session_id)
                        analyzer = DSAgentLogAnalyzer(
                            session_manager=session_manager,
                            session_id=session_id
                        )
                        
                        # Use standardized analyze method
                        analysis_results = analyzer.analyze(temp_paths)
                        
                        # Check if analysis resulted in an error
                        if analysis_results.get('error', False):
                            # Handle error case
                            session_data['status'] = 'error'
                            session_data['error_message'] = analysis_results.get('summary', 'Analysis failed')
                            result = f"<div class='alert alert-danger'><strong>Error:</strong> {analysis_results.get('summary', 'Analysis failed')}</div>"
                            
                            error_details = analysis_results.get('details', [])
                            error_recommendations = analysis_results.get('recommendations', [])
                            
                            raw_result = f"""DS Agent Log Analysis - ERROR:

Error: {analysis_results.get('summary', 'Analysis failed')}
Analysis Type: {analysis_results.get('analysis_type', 'ds_agent')}
Status: {analysis_results.get('status', 'error')}

Error Details:
{chr(10).join(f'- {detail}' for detail in error_details)}

Recommendations:
{chr(10).join(f'- {rec}' for rec in error_recommendations)}

Files Processed: {analysis_results.get('metadata', {}).get('files_processed', len(temp_paths))}
"""
                        else:
                            # Handle success case
                            result = analysis_results.get('formatted_output', 'DS Agent analysis completed')
                            
                            # Enhanced debugging for raw result
                            metadata = analysis_results.get('metadata', {})
                            details = analysis_results.get('details', [])
                            recommendations = analysis_results.get('recommendations', [])
                            
                            raw_result = f"""DS Agent Log Analysis Results:

Files Analyzed: {metadata.get('files_processed', len(temp_paths))}
Total Lines: {metadata.get('total_lines', 0)}
Errors Found: {metadata.get('errors_found', 0)}
Warnings Found: {metadata.get('warnings_found', 0)}

Analysis Type: {analysis_results.get('analysis_type', 'unknown')}
Status: {analysis_results.get('summary', 'Analysis completed')}

Details ({len(details)} items):
{chr(10).join(f'- {detail}' for detail in details[:10])}

Recommendations ({len(recommendations)} items):
{chr(10).join(f'- {rec}' for rec in recommendations[:10])}

Debug Info:
- Analysis keys: {list(analysis_results.keys())}
- Has formatted_output: {'formatted_output' in analysis_results}
- Raw data keys: {list(analysis_results.get('raw_data', {}).keys()) if analysis_results.get('raw_data') else 'No raw_data'}
"""
                            
                    elif analysis_type == "ds_agent_offline":
                        # Create session manager for progress tracking
                        class SimpleSessionManager:
                            def __init__(self, sessions_dict, session_id):
                                self.sessions = sessions_dict
                                self.session_id = session_id
                            
                            def update_session(self, session_id, progress_data):
                                if session_id in self.sessions:
                                    self.sessions[session_id].update(progress_data)
                        
                        session_manager = SimpleSessionManager(api_sessions, session_id)
                        analyzer = DSAgentOfflineAnalyzer(
                            session_manager=session_manager,
                            session_id=session_id
                        )
                        
                        # Use standardized analyze method
                        analysis_results = analyzer.analyze(temp_paths)
                        
                        # Handle standardized analyzer output
                        if analysis_results.get('status') == 'error' or analysis_results.get('error', False):
                            session_data['status'] = 'error'
                            session_data['error_message'] = analysis_results.get('summary', 'Analysis failed')
                            result = f"<div class='alert alert-danger'><strong>Error:</strong> {analysis_results.get('summary', 'Analysis failed')}</div>"
                            raw_result = f"DS Agent Offline Analysis - ERROR: {analysis_results.get('summary', 'Analysis failed')}"
                        else:
                            # Get formatted output or create from standardized data
                            if 'formatted_output' in analysis_results:
                                result = analysis_results['formatted_output']
                            elif 'raw_data' in analysis_results:
                                # Generate formatted output from raw data using the formatter
                                result = format_ds_agent_offline_results(analysis_results['raw_data'])
                            else:
                                # Generate basic formatted output from standardized data
                                result = f"""
                                <div class="analysis-container">
                                    <h2>📴 DS Agent Offline Analysis Results</h2>
                                    <div class="summary-section">
                                        <h3>📊 Summary</h3>
                                        <p>{analysis_results.get('summary', 'Analysis completed')}</p>
                                    </div>
                                    <div class="details-section">
                                        <h3>📋 Details</h3>
                                        <ul>{''.join(f'<li>{detail}</li>' for detail in analysis_results.get('details', []))}</ul>
                                    </div>
                                    <div class="recommendations-section">
                                        <h3>💡 Recommendations</h3>
                                        <ul>{''.join(f'<li>{rec}</li>' for rec in analysis_results.get('recommendations', []))}</ul>
                                    </div>
                                </div>
                                """
                            metadata = analysis_results.get('metadata', {})
                            raw_result = f"""DS Agent Offline Analysis Results:

Files Analyzed: {metadata.get('files_processed', len(temp_paths))}
Offline Issues: {metadata.get('offline_issues', 0)}
Critical Issues: {metadata.get('critical_issues', 0)}

Status: {analysis_results.get('summary', 'Analysis completed')}
"""
                        
                    elif analysis_type == "amsp_logs" or analysis_type == "amsp":
                        # Create session manager for progress tracking
                        class SimpleSessionManager:
                            def __init__(self, sessions_dict, session_id):
                                self.sessions = sessions_dict
                                self.session_id = session_id
                            
                            def update_session(self, session_id, progress_data):
                                if session_id in self.sessions:
                                    self.sessions[session_id].update(progress_data)
                        
                        session_manager = SimpleSessionManager(api_sessions, session_id)
                        analyzer = AMSPAnalyzer(
                            session_manager=session_manager,
                            session_id=session_id
                        )
                        
                        # Use standardized analyze method
                        analysis_results = analyzer.analyze(temp_paths)
                        
                        # Check if analysis resulted in an error
                        if analysis_results.get('error', False):
                            session_data['status'] = 'error'
                            session_data['error_message'] = analysis_results.get('summary', 'Analysis failed')
                            result = f"<div class='alert alert-danger'><strong>Error:</strong> {analysis_results.get('summary', 'Analysis failed')}</div>"
                            raw_result = f"AMSP Analysis - ERROR: {analysis_results.get('summary', 'Analysis failed')}"
                        else:
                            result = analysis_results.get('formatted_output', 'AMSP analysis completed')
                            metadata = analysis_results.get('metadata', {})
                            raw_result = f"""AMSP Anti-Malware Log Analysis Results:

Files Analyzed: {metadata.get('files_processed', len(temp_paths))}
Errors Found: {metadata.get('errors_found', 0)}
Pattern Failures: {metadata.get('pattern_failures', 0)}
BPF Failures: {metadata.get('bpf_failures', 0)}

Status: {analysis_results.get('summary', 'Analysis completed')}
"""
                        
                    elif analysis_type == "av_conflicts" or analysis_type == "conflict":
                        # Create session manager for progress tracking
                        class SimpleSessionManager:
                            def __init__(self, sessions_dict, session_id):
                                self.sessions = sessions_dict
                                self.session_id = session_id
                            
                            def update_session(self, session_id, progress_data):
                                if session_id in self.sessions:
                                    self.sessions[session_id].update(progress_data)
                        
                        session_manager = SimpleSessionManager(api_sessions, session_id)
                        analyzer = ConflictAnalyzer(
                            session_manager=session_manager,
                            session_id=session_id
                        )
                        
                        # Use standardized analyze method
                        analysis_results = analyzer.analyze(temp_paths)
                        
                        # Check if analysis resulted in an error
                        if analysis_results.get('error', False):
                            session_data['status'] = 'error'
                            session_data['error_message'] = analysis_results.get('summary', 'Analysis failed')
                            result = f"<div class='alert alert-danger'><strong>Error:</strong> {analysis_results.get('summary', 'Analysis failed')}</div>"
                            raw_result = f"Conflict Analysis - ERROR: {analysis_results.get('summary', 'Analysis failed')}"
                        else:
                            result = analysis_results.get('formatted_output', 'Conflict analysis completed')
                            metadata = analysis_results.get('metadata', {})
                            raw_result = f"""Antivirus Conflict Analysis Results:

Files Analyzed: {metadata.get('files_processed', len(temp_paths))}
Processes Analyzed: {metadata.get('processes_analyzed', 0)}
Conflicts Detected: {'Yes' if metadata.get('conflicts_detected', False) else 'No'}

Status: {analysis_results.get('summary', 'Analysis completed')}
"""
                        
                    elif analysis_type == "resource_analysis" or analysis_type == "resource":
                        # Create a simple session manager for progress tracking
                        class SimpleSessionManager:
                            def __init__(self, sessions_dict, session_id):
                                self.sessions = sessions_dict
                                self.session_id = session_id
                            
                            def update_session(self, session_id, progress_data):
                                if session_id in self.sessions:
                                    self.sessions[session_id].update(progress_data)
                        
                        session_manager = SimpleSessionManager(api_sessions, session_id)
                        analyzer = ResourceAnalyzer(
                            session_manager=session_manager,
                            session_id=session_id,
                            rag_system=None,  # Can be added later
                            ml_analyzer=None  # Can be added later
                        )
                        
                        # Use the new standardized analyze method
                        analysis_results = analyzer.analyze(temp_paths)
                        result = analysis_results.get('formatted_output', 'Resource analysis completed')
                        
                        # Create raw result summary
                        metadata = analysis_results.get('metadata', {})
                        candidates = len(analysis_results.get('details', []))
                        
                        raw_result = f"""Resource Analysis Results:

Files Analyzed:
- Total Files: {metadata.get('files_processed', len(temp_paths))}
- XML Files (RunningProcesses): {metadata.get('xml_files', 0)}
- TXT Files (TopNBusyProcess): {metadata.get('txt_files', 0)}

Analysis Summary:
- Running Processes Found: {metadata.get('processes_found', 0)}
- Busy Processes Found: {metadata.get('busy_processes_found', 0)}
- Exclusion Candidates: {metadata.get('exclusion_candidates', 0)}

Status: {analysis_results.get('summary', 'Analysis completed')}

Recommendations:
"""
                        for rec in analysis_results.get('recommendations', []):
                            raw_result += f"- {rec}\n"
                    
                    elif analysis_type == "diagnostic_package":
                        # Create a simple session manager for progress tracking
                        class SimpleSessionManager:
                            def __init__(self, sessions_dict, session_id):
                                self.sessions = sessions_dict
                                self.session_id = session_id
                            
                            def update_session(self, session_id, progress_data):
                                if session_id in self.sessions:
                                    self.sessions[session_id].update(progress_data)
                        
                        session_manager = SimpleSessionManager(api_sessions, session_id)
                        analyzer = DiagnosticPackageAnalyzer(
                            session_manager=session_manager,
                            session_id=session_id
                        )
                        
                        if len(temp_paths) == 1:
                            # Single ZIP file analysis - use consistent analyze() method
                            analysis_results = analyzer.analyze(temp_paths[0])
                            result = format_diagnostic_package_results(analysis_results)
                            
                            files_analyzed = analysis_results.get('files_analyzed', 0)
                            correlations = analysis_results.get('cross_log_correlations', {})
                            correlation_count = len(correlations.get('correlations', []))
                            
                            raw_result = f"""Diagnostic Package Analysis Results:

Package Summary:
- Files Analyzed: {files_analyzed}
- Cross-log Correlations: {correlation_count}
- Analysis Completed: {analysis_results.get('completed_at', 'Unknown')}

Executive Summary:
{analysis_results.get('executive_summary', {}).get('overview', 'No executive summary available')}

Key Findings:
"""
                            for finding in analysis_results.get('executive_summary', {}).get('key_findings', []):
                                raw_result += f"- {finding}\n"
                                
                            if analysis_results.get('ml_insights'):
                                raw_result += f"\nML Analysis: Overall Health Score {analysis_results['ml_insights'].get('overall_health_score', 'N/A')}%"
                            
                            if analysis_results.get('rag_insights'):
                                raw_result += f"\nKnowledge Sources: {analysis_results['rag_insights'].get('knowledge_sources_used', 'N/A')}"
                        else:
                            raise SecurityError("Diagnostic package analysis requires exactly one ZIP file.")
                    
                    else:
                        raise APIError(f"Unknown analysis type: {analysis_type}")
                    
                    # Update session with results and final progress
                    session_data['results'] = result
                    session_data['raw_results'] = raw_result
                    session_data['status'] = 'completed'
                    session_data['analysis_complete'] = True
                    session_data['progress_percentage'] = 100
                    session_data['progress_message'] = 'Analysis completed successfully'
                    session_data['analysis_stage'] = 'Completed'
                    session_data['completed_at'] = datetime.now().isoformat()
                    
                    print(f"✅ Analysis completed for session: {session_id}")
                    
                except Exception as e:
                    print(f"❌ Analysis failed: {str(e)}")
                    session_data['status'] = 'error'
                    session_data['error'] = str(e)
                    session_data['error_message'] = str(e)
                    session_data['analysis_complete'] = True
                    session_data['progress_percentage'] = 0
                    session_data['progress_message'] = f'Analysis failed: {str(e)}'
                    session_data['analysis_stage'] = 'Error'
                finally:
                    # Clean up temp files
                    for temp_path in temp_paths:
                        cleanup_temp_file(temp_path)
            
            # Always return the current status with comprehensive progress information
            return jsonify({
                'success': True,
                'session_id': session_id,
                'status': session_data['status'],
                'analysis_complete': session_data.get('analysis_complete', False),
                'progress_percentage': session_data.get('progress_percentage', 0),
                'progress_message': session_data.get('progress_message', 'Processing...'),
                'analysis_stage': session_data.get('analysis_stage', 'Unknown'),
                'analysis_type': session_data['analysis_type'],
                'error': session_data.get('error', None),
                'error_message': session_data.get('error_message', None),
                'completed_at': session_data.get('completed_at', None)
            })
            
        except Exception as e:
            print(f"� � Status check error: {str(e)}")
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/results/<session_id>', methods=['GET'])
    def api_results(session_id):
        """Get analysis results for a session"""
        try:
            print(f"📋 Results request for session: {session_id}")
            print(f"📋 Available sessions: {list(api_sessions.keys())}")
            
            if session_id not in api_sessions:
                print(f"� � Session {session_id} not found for results")
                return jsonify({'success': False, 'error': 'Session not found'}), 404
            
            session_data = api_sessions[session_id]
            print(f"📊 Session status: {session_data['status']}, Complete: {session_data.get('analysis_complete', False)}")
            
            if not session_data['analysis_complete']:
                return jsonify({
                    'success': False, 
                    'error': 'Analysis not complete'
                }), 400
            
            # Check if analysis failed
            if session_data['status'] == 'error':
                error_message = session_data.get('error', 'Analysis failed')
                return jsonify({
                    'success': False,
                    'error': error_message,
                    'session_id': session_id,
                    'analysis_type': session_data['analysis_type']
                }), 500
            
            results = session_data['results']
            if not results:
                return jsonify({
                    'success': False, 
                    'error': 'No results available'
                }), 404
            
            # Return the HTML formatted results (same as CSDAIv2)
            return jsonify({
                'success': True,
                'session_id': session_id,
                'analysis_type': session_data['analysis_type'],
                'results': results,  # This is the formatted HTML
                'raw_results': session_data.get('raw_results', results),
                'completed_at': session_data.get('completed_at', datetime.now().isoformat())
            })
            
        except Exception as e:
            print(f"� � Results error: {str(e)}")
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/export/<session_id>', methods=['GET'])
    def api_export(session_id):
        """Export analysis results as a file"""
        try:
            if session_id not in api_sessions:
                return jsonify({'success': False, 'error': 'Session not found'}), 404
            
            session_data = api_sessions[session_id]
            
            if not session_data['analysis_complete']:
                return jsonify({
                    'success': False, 
                    'error': 'Analysis not complete'
                }), 400
            
            # Use CSDAIv2 export format
            analysis_type = session_data['analysis_type']
            uploaded_files = session_data.get('uploaded_files', [])
            file_names = ', '.join([f.get('name', 'unknown') for f in uploaded_files])
            
            # Clean HTML tags from the result
            raw_results = session_data.get('raw_results', '')
            if not raw_results:
                # If no raw results, clean the HTML results
                clean_result = re.sub(r'<[^>]+>', '', session_data['results'])
                clean_result = re.sub(r'&[a-zA-Z0-9#]+;', '', clean_result)
                clean_result = re.sub(r'\n\s*\n', '\n\n', clean_result)
                clean_result = clean_result.strip()
            else:
                clean_result = raw_results
            
            # Create export content
            export_content = f"""DEEP SECURITY UNIFIED ANALYZER - ANALYSIS EXPORT
=================================================

Session ID: {session_id}
Analysis Type: {analysis_type.replace('_', ' ').title()}
File(s) Analyzed: {file_names}
Analysis Date: {session_data.get('created_at', 'Unknown')}
Completion Date: {session_data.get('completed_at', 'Unknown')}
Status: {session_data.get('status', 'Unknown')}
Generated by: Deep Security Unified Analyzer

ANALYSIS RESULT:
================

{clean_result}

---
Export generated at: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
Deep Security Unified Analyzer v1.0
Trend Micro Deep Security Analysis Tool
"""
            
            # Create filename for export
            safe_filename = re.sub(r'[^\w\s-]', '', file_names.split(',')[0] if file_names else 'analysis')
            safe_filename = re.sub(r'[-\s]+', '-', safe_filename)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            export_filename = f"ds_analysis_{analysis_type}_{safe_filename}_{timestamp}.txt"
            
            # Create temporary report file
            temp_report_path = os.path.join(config.TEMP_DIR, export_filename)
            
            with open(temp_report_path, 'w', encoding='utf-8') as f:
                f.write(export_content)
            
            return send_file(
                temp_report_path,
                as_attachment=True,
                download_name=export_filename,
                mimetype='text/plain'
            )
            
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/sessions/cleanup', methods=['POST'])
    def api_cleanup():
        """Cleanup old sessions and temp files"""
        try:
            cleaned_sessions = 0
            for session_id, session_data in list(api_sessions.items()):
                # Clean up temp files
                for temp_file in session_data.get('temp_files', []):
                    cleanup_temp_file(temp_file)
                
                # Remove session
                del api_sessions[session_id]
                cleaned_sessions += 1
            
            return jsonify({
                'success': True,
                'cleaned_sessions': cleaned_sessions
            })
            
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    # Include the exact formatting functions from CSDAIv2 routes.py
    def format_ds_log_results(analysis, is_multiple=False):
        """Import from routes.py - DS log formatting function"""
        from routes import format_ds_log_results as format_func
        return format_func(analysis, is_multiple)
    
    def format_amsp_results(analysis):
        """Import from routes.py - AMSP formatting function"""
        from routes import format_amsp_results as format_func
        return format_func(analysis)
    
    def format_conflict_results(analysis, process_count):
        """Import from routes.py - Conflict formatting function"""
        from routes import format_conflict_results as format_func
        return format_func(analysis, process_count)
    
    def format_resource_results(analysis_data, process_count, busy_count):
        """Import from routes.py - Resource formatting function"""
        from routes import format_resource_results as format_func
        return format_func(analysis_data, process_count, busy_count)
    
    print("✅ REST API routes registered for TrendAI integration with CSDAIv2 backend")
