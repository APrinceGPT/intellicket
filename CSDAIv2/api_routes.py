"""
REST API Routes for TrendAI Integration
Provides REST API endpoints for the TrendAI frontend integration
Using the exact same code from CSDAIv2 routes.py for consistent results
"""

import os
import json
import uuid
import re
from datetime import datetime
from flask import request, jsonify, send_file
from werkzeug.utils import secure_filename

# Import existing analyzer components and security
from analyzers import DSAgentLogAnalyzer, AMSPAnalyzer, ConflictAnalyzer, ResourceAnalyzer
from security import SecurityError, validate_file, create_secure_temp_file, cleanup_temp_file

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
    
    @app.route('/upload', methods=['POST'])
    def api_upload():
        """File upload endpoint for TrendAI integration"""
        try:
            # Create new session
            session_id = str(uuid.uuid4())
            print(f"🆔 Created new session: {session_id}")
            
            # Get analysis type
            analysis_type = request.form.get('analysis_type', 'ds_agent')
            print(f"📊 Analysis type: {analysis_type}")
            
            # Process uploaded files
            uploaded_files = []
            temp_files = []
            
            for key in request.files:
                file = request.files[key]
                if file and file.filename:
                    print(f"📁 Processing file: {file.filename}")
                    
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
            print(f"❌ Security Error: {str(e)}")
            # Clean up temp files on error
            for temp_file in temp_files:
                cleanup_temp_file(temp_file)
            return jsonify({'success': False, 'error': f"Security error: {str(e)}"}), 400
        except APIError as e:
            print(f"❌ API Error: {e.message}")
            return jsonify({'success': False, 'error': e.message}), e.status_code
        except Exception as e:
            print(f"❌ Unexpected error: {str(e)}")
            # Clean up temp files on error
            for temp_file in temp_files:
                cleanup_temp_file(temp_file)
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/status/<session_id>', methods=['GET'])
    def api_status(session_id):
        """Get analysis status for a session"""
        try:
            print(f"🔍 Status check for session: {session_id}")
            print(f"📋 Available sessions: {list(api_sessions.keys())}")
            
            if session_id not in api_sessions:
                print(f"❌ Session {session_id} not found")
                return jsonify({'success': False, 'error': 'Session not found'}), 404
            
            session_data = api_sessions[session_id]
            print(f"📊 Current status: {session_data['status']}")
            
            # If analysis hasn't started, start it using CSDAIv2 logic
            if session_data['status'] == 'uploaded':
                print(f"🚀 Starting analysis for session: {session_id}")
                session_data['status'] = 'processing'
                
                # Run analysis using exact CSDAIv2 logic
                try:
                    analysis_type = session_data['analysis_type']
                    uploaded_files = session_data['uploaded_files']
                    configuration = session_data.get('configuration', {})
                    
                    temp_paths = [file_info['temp_path'] for file_info in uploaded_files]
                    
                    # Route to appropriate analyzer (EXACT COPY from CSDAIv2 routes.py)
                    raw_result = None
                    if analysis_type == "ds_logs" or analysis_type == "ds_agent":
                        analyzer = DSAgentLogAnalyzer()
                        if len(temp_paths) == 1:
                            analysis_results = analyzer.analyze_log_file(temp_paths[0])
                            result = format_ds_log_results(analysis_results, False)
                            raw_result = f"DS Agent Log Analysis Results:\n\n{analysis_results.get('summary', 'No summary available')}"
                        else:
                            # Multiple DS log file analysis
                            analysis_results = analyzer.analyze_multiple_log_files(temp_paths)
                            result = format_ds_log_results(analysis_results, True)
                            file_count = len(temp_paths)
                            raw_result = f"Multiple DS Agent Log Analysis Results ({file_count} files):\n\n{analysis_results.get('summary', 'No summary available')}"
                            
                    elif analysis_type == "amsp_logs" or analysis_type == "amsp":
                        analyzer = AMSPAnalyzer()
                        analysis_results = analyzer.analyze_log_file(temp_paths[0])
                        result = format_amsp_results(analysis_results)
                        raw_result = f"AMSP Anti-Malware Log Analysis Results:\n\n{analysis_results.get('summary', 'No summary available')}"
                        
                    elif analysis_type == "av_conflicts" or analysis_type == "conflict":
                        analyzer = ConflictAnalyzer()
                        processes = analyzer.extract_processes_from_xml(temp_paths[0])
                        conflict_analysis = analyzer.analyze_conflicts(processes)
                        result = format_conflict_results(conflict_analysis, len(processes))
                        raw_result = f"Antivirus Conflict Analysis Results:\n\n{conflict_analysis}"
                        
                    elif analysis_type == "resource_analysis" or analysis_type == "resource":
                        if len(temp_paths) < 2:
                            # Try with single file
                            analyzer = ResourceAnalyzer()
                            processes = analyzer.extract_processes_from_xml(temp_paths[0])
                            resource_analysis_data = analyzer.analyze_resource_conflicts(processes, [])
                            result = format_resource_results(resource_analysis_data, len(processes), 0)
                            raw_result = f"Resource Analysis Results (single file):\n\nAnalyzed {len(processes)} processes."
                        else:
                            analyzer = ResourceAnalyzer()
                            
                            # Determine which file is which based on content
                            xml_file = None
                            txt_file = None
                            
                            for path in temp_paths:
                                try:
                                    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                                        first_line = f.readline().strip()
                                        if first_line.startswith('<?xml') or '<' in first_line:
                                            xml_file = path
                                        else:
                                            txt_file = path
                                except Exception:
                                    if path.lower().endswith('.xml'):
                                        xml_file = path
                                    elif path.lower().endswith('.txt'):
                                        txt_file = path
                            
                            if not xml_file or not txt_file:
                                raise SecurityError("Could not identify RunningProcess.xml and TopNBusyProcess.txt files. Please ensure both files are uploaded.")
                            
                            processes = analyzer.extract_processes_from_xml(xml_file)
                            busy_processes = analyzer.parse_top_n_busy_process(txt_file)
                            resource_analysis_data = analyzer.analyze_resource_conflicts(processes, busy_processes)
                            
                            result = format_resource_results(resource_analysis_data, len(processes), len(busy_processes))
                            
                            analysis_text = resource_analysis_data.get('analysis_text', 'No analysis available')
                            candidates = resource_analysis_data.get('candidates', [])
                            
                            raw_result = f"""Resource Analysis Results:

Files Analyzed:
- Running Processes: {len(processes)} processes from RunningProcess.xml
- Busy Processes: {len(busy_processes)} processes from TopNBusyProcess.txt

Exclusion Candidates Found: {len(candidates)}

Analysis:
{analysis_text}

Candidates Summary:
"""
                            for candidate in candidates:
                                raw_result += f"- {candidate.get('name', 'Unknown')}: {candidate.get('count', 'N/A')} scans\n"
                            
                            if resource_analysis_data.get('ml_insights'):
                                raw_result += f"\nML Analysis: Performance Score {resource_analysis_data['ml_insights'].get('performance_score', 'N/A')}%"
                            
                            if resource_analysis_data.get('rag_insights'):
                                raw_result += f"\nKnowledge Sources: {resource_analysis_data['rag_insights'].get('knowledge_sources_used', 'N/A')}"
                    
                    else:
                        raise APIError(f"Unknown analysis type: {analysis_type}")
                    
                    # Update session with results
                    session_data['results'] = result
                    session_data['raw_results'] = raw_result
                    session_data['status'] = 'completed'
                    session_data['analysis_complete'] = True
                    session_data['completed_at'] = datetime.now().isoformat()
                    
                    print(f"✅ Analysis completed for session: {session_id}")
                    
                except Exception as e:
                    print(f"❌ Analysis failed: {str(e)}")
                    session_data['status'] = 'error'
                    session_data['error'] = str(e)
                    session_data['analysis_complete'] = True
                finally:
                    # Clean up temp files
                    for temp_path in temp_paths:
                        cleanup_temp_file(temp_path)
            
            # Always return the current status
            return jsonify({
                'success': True,
                'session_id': session_id,
                'status': session_data['status'],
                'analysis_complete': session_data.get('analysis_complete', False),
                'analysis_type': session_data['analysis_type'],
                'error': session_data.get('error', None)
            })
            
        except Exception as e:
            print(f"❌ Status check error: {str(e)}")
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/results/<session_id>', methods=['GET'])
    def api_results(session_id):
        """Get analysis results for a session"""
        try:
            print(f"📋 Results request for session: {session_id}")
            print(f"📋 Available sessions: {list(api_sessions.keys())}")
            
            if session_id not in api_sessions:
                print(f"❌ Session {session_id} not found for results")
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
            print(f"❌ Results error: {str(e)}")
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
