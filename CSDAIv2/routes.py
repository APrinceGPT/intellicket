"""

Flask Routes Module

Contains all Flask routes and handler functions for the Deep Security Unified Analyzer.

"""

import os

import re

import json

from datetime import datetime

from typing import List, Dict, Any

from io import BytesIO

from flask import request, render_template_string, abort, session, Response, jsonify, redirect, url_for



# Import security and configuration

import sys

sys.path.append('../shared')



from security import (

    SecurityError, 

    validate_file, 

    create_secure_temp_file, 

    cleanup_temp_file,

    validate_host_access

)

from config import get_config

from ui_components import session_manager, wizard, guidance

from wizard_templates import (

    WIZARD_STEP_1_TEMPLATE, 

    WIZARD_STEP_2_TEMPLATE, 

    WIZARD_STEP_3_TEMPLATE, 

    WIZARD_STEP_4_TEMPLATE, 

    WIZARD_STEP_5_TEMPLATE,

    SESSIONS_TEMPLATE,

    SESSION_DETAIL_TEMPLATE

)



# Import analyzer classes

from analyzers import DSAgentLogAnalyzer, AMSPAnalyzer, ConflictAnalyzer, ResourceAnalyzer



# Load configuration

config = get_config()



# Declare OpenAI variables  

OPENAI_AVAILABLE = False

client = None



def initialize_openai():

    """Initialize OpenAI client when needed"""

    global OPENAI_AVAILABLE, client

    try:

        from openai import OpenAI

        import httpx

        

        # Create custom httpx client

        custom_http_client = httpx.Client(timeout=30.0, follow_redirects=True)

        

        # Initialize OpenAI client

        client = OpenAI(

            api_key=config.OPENAI_API_KEY,

            base_url=config.OPENAI_BASE_URL,

            http_client=custom_http_client

        )

        OPENAI_AVAILABLE = True

        return True

    except ImportError:

        OPENAI_AVAILABLE = False

        client = None

        return False



def register_routes(app):

    """Register all routes with the Flask app"""

    

    @app.route("/", methods=["GET"])

    def index():

        """Main landing page with wizard initialization"""

        if not validate_host_access(request.host, config.ALLOWED_HOSTS):

            abort(403)

        

        analysis_session_id = session.get('analysis_session_id')

        if not analysis_session_id:

            analysis_session_id = session_manager.create_session()

            session['analysis_session_id'] = analysis_session_id

        

        session_data = session_manager.get_session(analysis_session_id)

        current_step = session_data.get('current_step', 1) if session_data else 1

        

        return redirect(url_for('wizard_step', step=current_step))



    @app.route("/wizard/<int:step>", methods=["GET", "POST"])

    def wizard_step(step):

        """Handle wizard steps"""

        if not validate_host_access(request.host, config.ALLOWED_HOSTS):

            abort(403)

        

        analysis_session_id = session.get('analysis_session_id')

        if not analysis_session_id:

            return redirect(url_for('index'))

        

        session_data = session_manager.get_session(analysis_session_id)

        if not session_data:

            return redirect(url_for('index'))

        

        if not wizard.can_proceed_to_step(analysis_session_id, step):

            current_step = session_data.get('current_step', 1)

            return redirect(url_for('wizard_step', step=current_step))

        

        if request.method == "POST":

            return handle_wizard_post(step, analysis_session_id)

        else:

            # Special handling for step 4: show progress bar immediately and start analysis in background

            if step == 4 and session_data.get('status') == 'initialized':

                # Update status to processing immediately

                session_manager.update_session(analysis_session_id, {

                    'status': 'processing',

                    'current_step': 4

                })

                # Start analysis in background (non-blocking)

                import threading

                analysis_thread = threading.Thread(target=run_analysis_background, args=(analysis_session_id,))

                analysis_thread.daemon = True

                analysis_thread.start()

                # Return step 4 template immediately

                return render_wizard_step(step, session_manager.get_session(analysis_session_id))

            return render_wizard_step(step, session_data)



    @app.route("/sessions")

    def view_sessions():

        """View analysis history/sessions"""

        user_sessions = session_manager.get_user_sessions('anonymous')

        sessions_content = render_template_string(SESSIONS_TEMPLATE, sessions=user_sessions)

        return render_template_string(get_html_template(), content=sessions_content)



    @app.route("/session/<session_id>")

    def view_session(session_id):

        """View specific session details"""

        session_data = session_manager.get_session(session_id)

        if not session_data:

            abort(404)

        

        session_detail_content = render_template_string(SESSION_DETAIL_TEMPLATE, session_data=session_data)

        return render_template_string(get_html_template(), content=session_detail_content)



    @app.route("/api/session/status/<session_id>")

    def session_status(session_id):

        """API endpoint to get session status"""

        session_data = session_manager.get_session(session_id)

        if not session_data:

            return jsonify({'error': 'Session not found'}), 404

        

        return jsonify({
            'session_id': session_id,
            'status': session_data.get('status', 'unknown'),
            'current_step': session_data.get('current_step', 1),
            'progress_percentage': session_data.get('progress_percentage', wizard.get_progress_percentage(session_data.get('current_step', 1))),
            'analysis_stage': session_data.get('analysis_stage', 'Unknown'),
            'progress_message': session_data.get('progress_message', 'Processing...')
        })

    @app.route('/api/cleanup/cache', methods=['POST'])
    def cleanup_cache():
        """Clean up cache and temporary files for fresh analysis"""
        try:
            # Clean up user sessions
            cleaned_sessions = session_manager.cleanup_all_sessions('anonymous')
            
            # Clear Flask session data
            session.clear()
            
            # Clean up any remaining temporary files
            import os
            import glob
            from config import get_config
            config = get_config()
            
            temp_files_cleaned = 0
            try:
                temp_pattern = os.path.join(config.TEMP_DIR, '*')
                temp_files = glob.glob(temp_pattern)
                for temp_file in temp_files:
                    try:
                        if os.path.isfile(temp_file):
                            os.remove(temp_file)
                            temp_files_cleaned += 1
                    except Exception:
                        pass  # Continue cleanup even if one file fails
            except Exception:
                pass  # Continue even if temp directory cleanup fails
            
            return jsonify({
                'success': True,
                'message': 'Cache cleaned successfully',
                'sessions_cleaned': cleaned_sessions,
                'temp_files_cleaned': temp_files_cleaned
            })
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': f'Cache cleanup failed: {str(e)}'
            }), 500



    @app.route("/test")

    def test_template():

        """Test route to check template rendering"""

        test_content = "<h1>Test Content</h1><p>This is a test to check template rendering.</p>"

        return render_template_string(get_html_template(), content=test_content)



    @app.route("/debug-html")

    def debug_html():

        """Debug route to see raw HTML"""

        test_content = "<h1>Debug Content</h1><p>Checking for duplicate headers.</p>"

        html_output = render_template_string(get_html_template(), content=test_content)

        # Return as plain text so we can see the raw HTML

        from flask import Response

        return Response(html_output, mimetype='text/plain')



    @app.route("/unified", methods=["GET", "POST"])

    def unified_analyzer():

        """Legacy route for backward compatibility"""

        return redirect(url_for('index'))



    @app.route('/download/<session_id>')

    def download_session(session_id):

        """Download analysis results for a specific session"""

        session_data = session_manager.get_session(session_id)

        if not session_data:

            abort(404, description="Session not found")

        

        if not session_data.get('results'):

            abort(404, description="No analysis results available for this session")

        

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

        analysis_type = session_data.get('analysis_type', 'unknown')

        uploaded_files = session_data.get('uploaded_files', [])

        file_names = ', '.join([f.get('name', 'unknown') for f in uploaded_files])

        

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

        

        return Response(

            export_content,

            mimetype='text/plain',

            headers={

                'Content-Disposition': f'attachment; filename={export_filename}'

            }

        )



    @app.route('/export')

    def export_analysis():

        """Export the last analysis result as a text file."""

        try:

            # Get current session ID
            session_id = session.get('session_id')
            if not session_id:
                abort(404, description="No active session found")
            
            # Get analysis data from session manager
            session_data = session_manager.get_session(session_id)
            if not session_data or 'results' not in session_data:
                abort(404, description="No analysis result available for export")
            
            # Create analysis data in the expected format
            analysis_data = {
                'type': session_data.get('analysis_type', 'unknown'),
                'result': session_data.get('raw_results', session_data.get('results', '')),
                'timestamp': session_data.get('completed_at', datetime.now().isoformat()),
                'filename': ', '.join([f['name'] for f in session_data.get('uploaded_files', [])])
            }

            

            # Clean HTML tags from the result

            clean_result = re.sub(r'<[^>]+>', '', analysis_data['result'])

            clean_result = re.sub(r'&[a-zA-Z0-9#]+;', '', clean_result)

            clean_result = re.sub(r'\n\s*\n', '\n\n', clean_result)

            clean_result = clean_result.strip()

            

            # Create export content

            export_content = f"""DEEP SECURITY UNIFIED ANALYZER - ANALYSIS EXPORT

=================================================



Analysis Type: {analysis_data['type'].replace('_', ' ').title()}

File(s) Analyzed: {analysis_data['filename']}

Analysis Date: {analysis_data['timestamp']}

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

            safe_filename = re.sub(r'[^\w\s-]', '', analysis_data['filename'].split(',')[0])

            safe_filename = re.sub(r'[-\s]+', '-', safe_filename)

            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

            export_filename = f"ds_analysis_{analysis_data['type']}_{safe_filename}_{timestamp}.txt"

            

            return Response(

                export_content,

                mimetype='text/plain',

                headers={

                    'Content-Disposition': f'attachment; filename={export_filename}'

                }

            )

            

        except Exception as e:

            abort(500, description=f"Export failed: {str(e)}")





def handle_wizard_post(step, analysis_session_id):

    """Handle POST requests for wizard steps"""

    session_data = session_manager.get_session(analysis_session_id)

    

    if step == 1:

        analysis_type = request.form.get('analysis_type')

        if analysis_type:

            session_manager.update_session(analysis_session_id, {

                'analysis_type': analysis_type,

                'current_step': 2

            })

            return redirect(url_for('wizard_step', step=2))

        else:

            return render_wizard_step(1, session_data, error="Please select an analysis type")

    

    elif step == 2:

        return handle_file_upload(analysis_session_id)

    

    elif step == 3:

        return handle_configuration(analysis_session_id)

    

    elif step == 4:

        return start_analysis(analysis_session_id)

    

    return redirect(url_for('wizard_step', step=step))





def handle_file_upload(analysis_session_id):

    """Handle file upload in wizard step 2"""

    session_data = session_manager.get_session(analysis_session_id)

    temp_paths = []

    

    try:

        files = request.files.getlist("files")

        valid_files = [f for f in files if f.filename]

        

        if not valid_files:

            return render_wizard_step(2, session_data, error="No files provided for upload")

        

        if len(valid_files) > 10:

            return render_wizard_step(2, session_data, error="Maximum 10 files allowed for upload")

        

        file_info = []

        for file in valid_files:

            file_type = validate_file(file)

            temp_path = create_secure_temp_file(file, config.TEMP_DIR)

            temp_paths.append(temp_path)

            file_info.append({

                'name': file.filename,

                'size': file.content_length,

                'type': file_type,

                'temp_path': temp_path

            })

        

        session_manager.update_session(analysis_session_id, {

            'uploaded_files': file_info,

            'current_step': 3

        })

        

        return redirect(url_for('wizard_step', step=3))

        

    except SecurityError as e:

        for temp_path in temp_paths:

            cleanup_temp_file(temp_path)

        return render_wizard_step(2, session_data, error=f"Security error: {str(e)}")

    except Exception as e:

        for temp_path in temp_paths:

            cleanup_temp_file(temp_path)

        return render_wizard_step(2, session_data, error=f"Upload error: {str(e)}")





def handle_configuration(analysis_session_id):

    """Handle analysis configuration in wizard step 3"""

    session_data = session_manager.get_session(analysis_session_id)

    

    configuration = {

        'analysis_depth': 'expert',  # Always use expert level analysis

        'ml_analysis': 'ml_analysis' in request.form,

        'rag_enhancement': 'rag_enhancement' in request.form,

        'correlation_analysis': 'correlation_analysis' in request.form,

        'output_format': 'html'  # Always use HTML format

    }

    

    session_manager.update_session(analysis_session_id, {

        'configuration': configuration,

        'current_step': 4

    })

    

    return redirect(url_for('wizard_step', step=4))





def start_analysis(analysis_session_id):

    """Start the analysis process"""

    session_data = session_manager.get_session(analysis_session_id)

    

    try:

        session_manager.update_session(analysis_session_id, {

            'status': 'processing',

            'current_step': 4

        })

        

        analysis_type = session_data['analysis_type']

        uploaded_files = session_data['uploaded_files']

        configuration = session_data.get('configuration', {})

        

        temp_paths = [file_info['temp_path'] for file_info in uploaded_files]

        

        # Route to appropriate analyzer

        raw_result = None

        if analysis_type == "ds_logs":

            analyzer = DSAgentLogAnalyzer(session_manager=session_manager, session_id=analysis_session_id)

            if len(temp_paths) == 1:

                analysis_results = analyzer.analyze_log_file(temp_paths[0])

                result = format_ds_log_results(analysis_results, False)

                raw_result = f"DS Agent Log Analysis Results:\n\n{analysis_results.get('summary', 'No summary available')}"

            else:

                # Multiple DS log file analysis

                analysis_results = analyzer.analyze_multiple_log_files(temp_paths)

                result = format_ds_log_results(analysis_results, True)  # True indicates multiple files

                file_count = len(temp_paths)

                raw_result = f"Multiple DS Agent Log Analysis Results ({file_count} files):\n\n{analysis_results.get('summary', 'No summary available')}"

                

        elif analysis_type == "amsp_logs":

            analyzer = AMSPAnalyzer(session_manager=session_manager, session_id=analysis_session_id)

            analysis_results = analyzer.analyze_log_file(temp_paths[0])

            result = format_amsp_results(analysis_results)

            raw_result = f"AMSP Anti-Malware Log Analysis Results:\n\n{analysis_results.get('summary', 'No summary available')}"

            

        elif analysis_type == "av_conflicts":

            analyzer = ConflictAnalyzer()

            processes = analyzer.extract_processes_from_xml(temp_paths[0])

            conflict_analysis = analyzer.analyze_conflicts(processes)

            result = format_conflict_results(conflict_analysis, len(processes))

            raw_result = f"Antivirus Conflict Analysis Results:\n\n{conflict_analysis}"

            

        elif analysis_type == "resource_analysis":

            if len(temp_paths) < 2:

                raise SecurityError("Resource analysis requires both RunningProcess.xml and TopNBusyProcess.txt files")

            

            analyzer = ResourceAnalyzer(session_manager=session_manager, session_id=analysis_session_id)
            
            # Determine which file is which based on content
            xml_file = None
            txt_file = None
            
            for path in temp_paths:
                try:
                    # Check if it's XML by trying to read the first few lines
                    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                        first_line = f.readline().strip()
                        if first_line.startswith('<?xml') or '<' in first_line:
                            xml_file = path
                        else:
                            txt_file = path
                except Exception:
                    # If we can't determine, use file extension as fallback
                    if path.lower().endswith('.xml'):
                        xml_file = path
                    elif path.lower().endswith('.txt'):
                        txt_file = path
            
            if not xml_file or not txt_file:
                raise SecurityError("Could not identify RunningProcess.xml and TopNBusyProcess.txt files. Please ensure both files are uploaded.")
            
            processes = analyzer.extract_processes_from_xml(xml_file)
            busy_processes = analyzer.parse_top_n_busy_process(txt_file)
            resource_analysis_data = analyzer.analyze_resource_conflicts(processes, busy_processes)
            
            # Format results using the new enhanced formatter
            result = format_resource_results(resource_analysis_data, len(processes), len(busy_processes))
            
            # Create raw result for export
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

        

        # Stage 4: Report Generation
        session_manager.update_session(analysis_session_id, {
            'analysis_stage': 'Report Generation',
            'progress_message': 'Compiling analysis results...',
            'progress_percentage': 80,
            'status': 'processing'
        })
        
        session_manager.update_session(analysis_session_id, {
            'analysis_stage': 'Report Generation',
            'progress_message': 'Generating HTML report...',
            'progress_percentage': 85,
            'status': 'processing'
        })
        
        session_manager.update_session(analysis_session_id, {
            'analysis_stage': 'Report Generation',
            'progress_message': 'Formatting recommendations...',
            'progress_percentage': 90,
            'status': 'processing'
        })
        
        session_manager.update_session(analysis_session_id, {
            'analysis_stage': 'Report Generation',
            'progress_message': 'Finalizing security assessments...',
            'progress_percentage': 95,
            'status': 'processing'
        })
        
        # Update session with results

        session_manager.update_session(analysis_session_id, {

            'results': result,

            'raw_results': raw_result,

            'status': 'completed',

            'current_step': 5,

            'completed_at': datetime.now().isoformat()

        })

        

        # Store in Flask session for export functionality

        session['last_analysis'] = {

            'type': analysis_type,

            'result': raw_result,

            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),

            'filename': ', '.join([f['name'] for f in uploaded_files])

        }

        

        # Render step 4 (processing) and let frontend handle redirect

        return render_wizard_step(4, session_manager.get_session(analysis_session_id))

        

    except Exception as e:

        session_manager.update_session(analysis_session_id, {

            'status': 'error',

            'error_message': str(e)

        })

        return render_wizard_step(4, session_data, error=f"Analysis error: {str(e)}")

    finally:

        for temp_path in temp_paths:

            cleanup_temp_file(temp_path)





def run_analysis_background(analysis_session_id):

    """Run analysis in background thread - non-blocking"""

    session_data = session_manager.get_session(analysis_session_id)

    temp_paths = []

    

    try:

        analysis_type = session_data['analysis_type']

        uploaded_files = session_data['uploaded_files']

        configuration = session_data.get('configuration', {})

        

        temp_paths = [file_info['temp_path'] for file_info in uploaded_files]

        

        # Route to appropriate analyzer

        raw_result = None

        if analysis_type == "ds_logs":

            analyzer = DSAgentLogAnalyzer(session_manager=session_manager, session_id=analysis_session_id)

            if len(temp_paths) == 1:

                analysis_results = analyzer.analyze_log_file(temp_paths[0])

                result = format_ds_log_results(analysis_results, False)

                raw_result = f"DS Agent Log Analysis Results:\n\n{analysis_results.get('summary', 'No summary available')}"

            else:

                # Multiple DS log file analysis

                analysis_results = analyzer.analyze_multiple_log_files(temp_paths)

                result = format_ds_log_results(analysis_results, True)  # True indicates multiple files

                file_count = len(temp_paths)

                raw_result = f"Multiple DS Agent Log Analysis Results ({file_count} files):\n\n{analysis_results.get('summary', 'No summary available')}"

                

        elif analysis_type == "amsp_logs":

            analyzer = AMSPAnalyzer(session_manager=session_manager, session_id=analysis_session_id)

            analysis_results = analyzer.analyze_log_file(temp_paths[0])

            result = format_amsp_results(analysis_results)

            raw_result = f"AMSP Anti-Malware Log Analysis Results:\n\n{analysis_results.get('summary', 'No summary available')}"

            

        elif analysis_type == "av_conflicts":

            analyzer = ConflictAnalyzer()

            processes = analyzer.extract_processes_from_xml(temp_paths[0])

            conflict_analysis = analyzer.analyze_conflicts(processes)

            result = format_conflict_results(conflict_analysis, len(processes))

            raw_result = f"Antivirus Conflict Analysis Results:\n\n{conflict_analysis}"

            

        elif analysis_type == "resource_analysis":

            if len(temp_paths) < 2:

                raise SecurityError("Resource analysis requires both RunningProcess.xml and TopNBusyProcess.txt files")

            

            analyzer = ResourceAnalyzer(session_manager=session_manager, session_id=analysis_session_id)
            
            # Determine which file is which based on content
            xml_file = None
            txt_file = None
            
            for path in temp_paths:
                try:
                    # Check if it's XML by trying to read the first few lines
                    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                        first_line = f.readline().strip()
                        if first_line.startswith('<?xml') or '<' in first_line:
                            xml_file = path
                        else:
                            txt_file = path
                except Exception:
                    # If we can't determine, use file extension as fallback
                    if path.lower().endswith('.xml'):
                        xml_file = path
                    elif path.lower().endswith('.txt'):
                        txt_file = path
            
            if not xml_file or not txt_file:
                raise SecurityError("Could not identify RunningProcess.xml and TopNBusyProcess.txt files. Please ensure both files are uploaded.")
            
            processes = analyzer.extract_processes_from_xml(xml_file)
            busy_processes = analyzer.parse_top_n_busy_process(txt_file)
            resource_analysis_data = analyzer.analyze_resource_conflicts(processes, busy_processes)
            
            # Format results using the new enhanced formatter
            result = format_resource_results(resource_analysis_data, len(processes), len(busy_processes))
            
            # Create raw result for export
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

        

        # Stage 4: Report Generation
        session_manager.update_session(analysis_session_id, {
            'analysis_stage': 'Report Generation',
            'progress_message': 'Compiling analysis results...',
            'progress_percentage': 80,
            'status': 'processing'
        })
        
        session_manager.update_session(analysis_session_id, {
            'analysis_stage': 'Report Generation',
            'progress_message': 'Generating HTML report...',
            'progress_percentage': 85,
            'status': 'processing'
        })
        
        session_manager.update_session(analysis_session_id, {
            'analysis_stage': 'Report Generation',
            'progress_message': 'Formatting recommendations...',
            'progress_percentage': 90,
            'status': 'processing'
        })
        
        session_manager.update_session(analysis_session_id, {
            'analysis_stage': 'Report Generation',
            'progress_message': 'Finalizing security assessments...',
            'progress_percentage': 95,
            'status': 'processing'
        })
        
        # Update session with results

        session_manager.update_session(analysis_session_id, {

            'results': result,

            'raw_results': raw_result,

            'status': 'completed',

            'current_step': 5,

            'completed_at': datetime.now().isoformat()

        })

        
        # Note: Flask session access removed from background thread
        # Export functionality will be handled when user accesses results
        

        print(f"✅ Background analysis completed for session {analysis_session_id}")

        

    except Exception as e:

        print(f"❌ Background analysis failed for session {analysis_session_id}: {str(e)}")

        session_manager.update_session(analysis_session_id, {

            'status': 'error',

            'error_message': str(e)

        })

    finally:

        # Clean up temp files

        for temp_path in temp_paths:

            cleanup_temp_file(temp_path)





def render_wizard_step(step, session_data, error=None):

    """Render the appropriate wizard step template"""

    step_info = wizard.get_step_info(step)

    progress_percentage = wizard.get_progress_percentage(step)

    

    analysis_type = session_data.get('analysis_type')

    analysis_guidance = guidance.get_analysis_guidance(analysis_type) if analysis_type else {}

    

    template_data = {

        'current_step': step,

        'step_info': step_info,

        'progress_percentage': progress_percentage,

        'session_data': session_data,

        'analysis_guidance': analysis_guidance,

        'error': error,

        'guidance': guidance,

        'wizard_steps': wizard.STEPS

    }

    

    # Get the appropriate wizard content template

    if step == 1:

        wizard_content = render_template_string(WIZARD_STEP_1_TEMPLATE, **template_data)

    elif step == 2:

        wizard_content = render_template_string(WIZARD_STEP_2_TEMPLATE, **template_data)

    elif step == 3:

        wizard_content = render_template_string(WIZARD_STEP_3_TEMPLATE, **template_data)

    elif step == 4:

        wizard_content = render_template_string(WIZARD_STEP_4_TEMPLATE, **template_data)

    elif step == 5:

        wizard_content = render_template_string(WIZARD_STEP_5_TEMPLATE, **template_data)

    else:

        return redirect(url_for('index'))

    

    return render_template_string(get_html_template(), content=wizard_content)





def format_ds_log_results(analysis: Dict[str, Any], is_multiple: bool = False) -> str:

    """Format DS log analysis results as HTML with full AI, ML, and RAG analysis"""

    summary = analysis['summary']

    

    if summary['critical_count'] > 0:

        status_color = "#dc3545"

        status_text = "CRITICAL ISSUES DETECTED"

        status_icon = '<i class="fas fa-exclamation-circle text-danger"></i>'

    elif summary['error_count'] > 10:

        status_color = "#fd7e14"

        status_text = "MULTIPLE ERRORS DETECTED"

        status_icon = '<i class="fa-solid fa-exclamation-triangle"></i>'

    elif summary['warning_count'] > 20:

        status_color = "#ffc107"

        status_text = "WARNINGS DETECTED"

        status_icon = '<i class="fa-solid fa-exclamation-triangle"></i>'

    else:

        status_color = "#198754"

        status_text = "HEALTHY"

        status_icon = '<i class="fa-solid fa-check-circle text-success"></i>'

    

    html = f"""

    <div class="mb-4 font-consistent">

        <h4 style="color: {status_color}; font-family: Inter, "Segoe UI", Roboto, sans-serif !important;">{status_icon} DS Agent Log Analysis - Status: {status_text}</h4>

        {'<p style="font-family: Inter, Segoe UI, Roboto, sans-serif !important;"><i class="fas fa-layer-group"></i> <strong>Multiple File Analysis:</strong> ' + str(summary.get('file_count', 1)) + ' files analyzed</p>' if is_multiple else ''}

    </div>

    

    <div class="row mb-4 font-consistent" id="summary-stats-section">
            <div class="col-md-6">
            <div class="card font-consistent">

                <div class="card-header font-consistent" style=\"font-family: 'Inter', 'Segoe UI', 'Roboto', sans-serif !important;\"><i class="fas fa-chart-bar"></i> Summary Statistics</div>

                <div class="card-body font-consistent" style=\"font-family: 'Inter', 'Segoe UI', 'Roboto', sans-serif !important;\">

                    <p style=\"font-family: 'Inter', 'Segoe UI', 'Roboto', sans-serif !important;\"><strong>Total Lines:</strong> {summary['total_lines']:,}</p>

                    <p style=\"font-family: 'Inter', 'Segoe UI', 'Roboto', sans-serif !important;\"><strong>Parsed Lines:</strong> {summary['parsed_lines']:,}</p>

                    <p style=\"font-family: 'Inter', 'Segoe UI', 'Roboto', sans-serif !important;\"><strong>Critical Issues:</strong> <span style="color: #dc3545;">{summary['critical_count']}</span></p>

                    <p style=\"font-family: 'Inter', 'Segoe UI', 'Roboto', sans-serif !important;\"><strong>Errors:</strong> <span style="color: #fd7e14;">{summary['error_count']}</span></p>

                    <p style=\"font-family: 'Inter', 'Segoe UI', 'Roboto', sans-serif !important;\"><strong>Warnings:</strong> <span style="color: #ffc107;">{summary['warning_count']}</span></p>

                    <p style=\"font-family: 'Inter', 'Segoe UI', 'Roboto', sans-serif !important;\"><strong>Time Range:</strong> {summary['timespan']['start'] or 'N/A'} to {summary['timespan']['end'] or 'N/A'}</p>

                    {'<p style="font-family: Inter, Segoe UI, Roboto, sans-serif !important;"><strong>Files Analyzed:</strong> ' + str(summary.get('file_count', 1)) + '</p>' if is_multiple else ''}

                </div>

            </div>

        </div>

        <div class="col-md-6">
            <div class="card font-consistent" id="recommendations-section">

                <div class="card-header font-consistent" style=\"font-family: 'Inter', 'Segoe UI', 'Roboto', sans-serif !important;\"><i class="fa-solid fa-bullseye me-2"></i>Key Recommendations</div>

                <div class="card-body font-consistent" style=\"font-family: 'Inter', 'Segoe UI', 'Roboto', sans-serif !important;\">

                    <ul class="list-unstyled" style=\"font-family: 'Inter', 'Segoe UI', 'Roboto', sans-serif !important;\">

    """

    for rec in analysis['recommendations']:

        html += f'<li class="mb-2" style="font-family: Inter, \'Segoe UI\', Roboto, sans-serif !important;">{rec}</li>'

    

    html += """

                    </ul>

                </div>

            </div>

        </div>

    </div>

    """

    # Component Analysis Section

    if analysis.get('component_analysis'):

        html += """

        <div class="row mb-4 font-consistent" id="component-analysis-section">

            <div class="col-12">
            <div class="card font-consistent">
            <div class="card-header font-consistent" style=\"font-family: 'Inter', 'Segoe UI', 'Roboto', sans-serif !important;\"><i class="fas fa-wrench"></i> Component Analysis</div>

                    <div class='card-body font-consistent' style=\"font-family: 'Inter', 'Segoe UI', 'Roboto', sans-serif !important;\">

                        <div class="table-responsive">

                            <table class="table table-striped font-consistent" style=\"font-family: 'Inter', 'Segoe UI', 'Roboto', sans-serif !important;\">

                                <thead>

                                    <tr style=\"font-family: 'Inter', 'Segoe UI', 'Roboto', sans-serif !important;\">

                                        <th style=\"font-family: 'Inter', 'Segoe UI', 'Roboto', sans-serif !important;\">Component</th>

                                        <th style=\"font-family: 'Inter', 'Segoe UI', 'Roboto', sans-serif !important;\">Total Entries</th>

                                        <th style=\"font-family: 'Inter', 'Segoe UI', 'Roboto', sans-serif !important;\">Errors</th>

                                        <th style=\"font-family: 'Inter', 'Segoe UI', 'Roboto', sans-serif !important;\">Warnings</th>

                                        <th style=\"font-family: 'Inter', 'Segoe UI', 'Roboto', sans-serif !important;\">Health Status</th>

                                    </tr>

                                </thead>

                                <tbody style=\"font-family: 'Inter', 'Segoe UI', 'Roboto', sans-serif !important;\">

        """

        for component, stats in analysis['component_analysis'].items():

            if stats['errors'] > 0:

                health_status = f'<span class="text-danger"><i class="fa-solid fa-exclamation-triangle me-2"></i>{stats["errors"]} errors</span>'

            elif stats['warnings'] > 0:

                health_status = f'<span class="text-warning"><i class="fa-solid fa-exclamation-triangle me-2"></i>{stats["warnings"]} warnings</span>'

            else:

                health_status = '<span class="text-success"><i class="fa-solid fa-check-circle me-2 text-success"></i>Healthy</span>'

                

            html += f"""

                                    <tr style=\"font-family: 'Inter', 'Segoe UI', 'Roboto', sans-serif !important;\">

                                        <td style=\"font-family: 'Inter', 'Segoe UI', 'Roboto', sans-serif !important;\"><strong>{component}</strong></td>

                                        <td style=\"font-family: 'Inter', 'Segoe UI', 'Roboto', sans-serif !important;\">{stats['total_entries']}</td>

                                        <td style=\"font-family: 'Inter', 'Segoe UI', 'Roboto', sans-serif !important;\">{stats['errors']}</td>

                                        <td style=\"font-family: 'Inter', 'Segoe UI', 'Roboto', sans-serif !important;\">{stats['warnings']}</td>

                                        <td style=\"font-family: 'Inter', 'Segoe UI', 'Roboto', sans-serif !important;\">{health_status}</td>

                                    </tr>

            """

        html += """

                                </tbody>

                            </table>

                        </div>

                    </div>

                </div>

            </div>

        </div>

        """

    # ML Analysis Section

    if analysis.get('ml_insights'):

        ml_insights = analysis['ml_insights']

        html += f"""

        <div class="row mb-4" id="ml-analysis-section">

            <div class="col-12">
            <div class="card border-info">
            <div class="card-header bg-info text-white"><i class="fas fa-wrench"></i>  Machine Learning Analysis</div>

                    <div class="card-body">

        """

        if ml_insights.get('overview'):

            ml_overview = ml_insights['overview']

            html += f"""

                        <div class="row mb-3">
            <div class="col-md-4">

                                <strong>Entries Analyzed:</strong> {ml_overview.get('total_entries', 0)}<br>

                                <strong>ML Features:</strong> {len(ml_overview.get('ml_features_used', []))}

                            </div>

                            <div class="col-md-4">

                                <strong>Anomalies Detected:</strong> 

                                <span class="badge bg-warning">{ml_insights.get('anomaly_analysis', {}).get('anomaly_count', 0)}</span><br>

                                <strong>Anomaly Rate:</strong> {ml_insights.get('anomaly_analysis', {}).get('anomaly_score', 0):.1f}%

                            </div>

                            <div class="col-md-4">

                                <strong>Pattern Clusters:</strong> {len(ml_insights.get('pattern_analysis', {}).get('clusters', []))}<br>

                                <strong>ML Recommendations:</strong> {len(ml_insights.get('recommendations', []))}

                            </div>

                        </div>

            """

        # Anomaly Analysis

        if ml_insights.get('anomaly_analysis', {}).get('anomalies'):

            html += """

                        <h6><i class="fas fa-brain"></i>Detected Anomalies:</h6>

                        <div class='table-responsive'>

                            <table class="table table-sm">

                                <thead>

                                    <tr>

                                        <th>Timestamp</th>

                                        <th>Message</th>

                                        <th>Confidence</th>

                                    </tr>

                                </thead>

                                <tbody>

            """

            for anomaly in ml_insights['anomaly_analysis']['anomalies'][:5]:  # Show top 5

                html += f"""

                                    <tr>

                                        <td>{anomaly.get('timestamp', 'N/A')}</td>

                                        <td>{anomaly.get('message', 'N/A')[:100]}...</td>

                                        <td><span class="badge bg-danger">{anomaly.get('confidence', 0):.2f}</span></td>

                                    </tr>

                """

            html += """

                                </tbody>

                            </table>

                        </div>

            """

        # DS Agent Specific Analysis
        if ml_insights.get('ds_agent_analysis'):
            ds_analysis = ml_insights['ds_agent_analysis']
            
            html += """
                        <h6><i class="fas fa-cogs"></i>DS Agent Component Analysis:</h6>
            """
            
            # Component Health
            component_health = ds_analysis.get('component_health', {})
            if component_health:
                html += """
                        <div class='table-responsive mb-3'>
                            <table class="table table-sm">
                                <thead>
                                    <tr>
                                        <th>Component</th>
                                        <th>Entries</th>
                                        <th>Health Score</th>
                                        <th>Issues</th>
                                    </tr>
                                </thead>
                                <tbody>
                """
                
                for component, health in component_health.items():
                    health_score = health.get('health_score', 0)
                    badge_class = 'bg-success' if health_score > 90 else 'bg-warning' if health_score > 70 else 'bg-danger'
                    total_issues = health.get('warning_count', 0) + health.get('error_count', 0)
                    
                    html += f"""
                                        <tr>
                                            <td>{component}</td>
                                            <td>{health.get('total_entries', 0)}</td>
                                            <td><span class="badge {badge_class}">{health_score:.0f}%</span></td>
                                            <td>{total_issues} issues</td>
                                        </tr>
                    """
                
                html += """
                                </tbody>
                            </table>
                        </div>
                """
            
            # Error Patterns
            error_patterns = ds_analysis.get('error_patterns', {})
            if error_patterns.get('metrics_failures', 0) > 0:
                html += f"""
                        <div class="alert alert-info">
                            <strong>AMSP Metrics:</strong> {error_patterns['metrics_failures']} device control metrics failures detected. 
                            This is normal for systems without device control enabled.
                        </div>
                """

        html += """

                    </div>

                </div>

            </div>

        </div>

        """

    # RAG Analysis Section

    if analysis.get('rag_insights'):

        rag_insights = analysis['rag_insights']

        html += f"""

        <div class="row mb-4" id="rag-analysis-section">

            <div class="col-12">
            <div class="card border-success">
            <div class="card-header bg-success text-white"><i class="fas fa-brain"></i>RAG-Enhanced Knowledge Analysis</div>

                    <div class="card-body">
            <div class="row mb-3">
            <div class="col-md-6">

                                <strong>Knowledge Sources Used:</strong> {rag_insights.get('knowledge_sources_used', 0)}<br>

                                <strong>Patterns Matched:</strong> {rag_insights.get('patterns_matched', 0)}

                            </div>

                            <div class="col-md-6">

                                <strong>RAG Version:</strong> {rag_insights.get('rag_version', 'N/A')}<br>

                                <strong>Analysis Timestamp:</strong> {rag_insights.get('timestamp', 'N/A')[:19] if rag_insights.get('timestamp') else 'N/A'}

                            </div>

                        </div>

        """

        if rag_insights.get('pattern_matches'):

            html += """

                        <h6><i class="fas fa-brain"></i>Knowledge Pattern Matches:</h6>

                        <div class="list-group">

            """

            for pattern in rag_insights['pattern_matches'][:3]:  # Show top 3

                html += f"""

                            <div class="list-group-item">

                                <h6 class="mb-1">{pattern.get('pattern_name', 'Unknown Pattern')}</h6>

                                <p class="mb-1">{pattern.get('description', 'No description available')}</p>

                                <small class="text-muted">Resolution: {pattern.get("resolution", "No resolution provided")}</small>

                            </div>

                """

            html += """

                        </div>

            """

        html += """

                    </div>

                </div>

            </div>

        </div>

        """

    # Known Issues Section

    if analysis.get('known_issues'):

        html += """

        <div class="row mb-4">

            <div class="col-12">
            <div class="card border-warning">
            <div class="card-header bg-warning text-dark"><i class="fa-solid fa-exclamation-triangle me-2"></i>Known Issues Detected</div>

                    <div class="card-body">
            <div class="list-group">

        """

        for issue in analysis["known_issues"][:5]:  # Show top 5

            html += f"""

                        <div class="list-group-item">

                            <h6 class="mb-1">{issue.get('issue_type', 'Unknown Issue')}</h6>

                            <p class="mb-1">{issue.get('description', 'No description available')}</p>

                            <small class="text-muted">Line: {issue.get("line", "N/A")} | Timestamp: {issue.get("timestamp", "N/A")}</small>

                        </div>

            """

        html += """

                        </div>

                    </div>

                </div>

            </div>

        </div>

        """

    # AI-Powered Comprehensive Analysis Section

    # Connection Health Section - Cloud One Workload Security

    if analysis.get('connection_health'):

        conn_health = analysis['connection_health']

        

        # Determine status color and icon

        status_colors = {

            'healthy': ('#198754', '<i class=\"fa-solid fa-check-circle text-success\"></i>'),

            'mostly_healthy': ('#198754', '<i class=\"fa-solid fa-circle text-warning\"></i>'),

            'unstable': ('#fd7e14', '<i class="fa-solid fa-exclamation-triangle"></i>'),

            'unhealthy': ('#dc3545', '<i class="fas fa-exclamation-circle text-danger"></i>'),

            'no_connection_activity': ('#6c757d', 'â“'),

            'unknown': ('#6c757d', 'â“')

        }

        

        status_color, status_icon = status_colors.get(conn_health['overall_status'], ('#6c757d', 'â“'))

        

        html += f"""
        <div class="row mb-4" id="connection-health-section">

            <div class="col-12">
            <div class="card border-warning">
            <div class="card-header bg-warning text-dark">

                        <i class="fas fa-brain"></i><strong>Cloud One Workload Security Connection Health</strong>

                    </div>

                    <div class="card-body">
            <div class="row mb-3">

                            <div class="col-md-8">

                                <h5 style="color: {status_color};">

                                    {status_icon} Connection Status: {conn_health['overall_status'].replace('_', ' ').title()}

                                </h5>

                                <p class="text-muted mb-2">

                                    Deep Security Agent connectivity to Trend Micro Cloud One Workload Security servers

                                </p>

                            </div>

                            <div class="col-md-4 text-end">
            <div class="d-flex flex-column gap-1">

                                    <small><strong>Connection Attempts:</strong> {conn_health['connection_attempts']}</small>

                                    <small><strong>Successful:</strong> <span class="text-success">{conn_health['successful_connections']}</span></small>

                                    <small><strong>Failed:</strong> <span class="text-danger">{conn_health['failed_connections']}</span></small>

                                </div>

                            </div>

                        </div>

                        

                        <div class="row mb-3">
            <div class="col-md-6">

                                <h6><i class="fas fa-brain"></i>Connected Regions:</h6>

                                <ul class="list-unstyled mb-0">

        """

        if conn_health['connected_regions']:

            for region in conn_health['connected_regions']:

                html += f'<li><span class="badge bg-success me-1">âœ“</span> {region}</li>'

        else:

            html += '<li><span class="text-muted">No regions detected in logs</span></li>'

        

        html += f"""

                                </ul>

                            </div>

                            <div class="col-md-6">

                                <h6><i class="fas fa-brain"></i>Heartbeat Status:</h6>

                                <p class="mb-0">

                                    <span class="badge {'bg-success' if conn_health['heartbeat_status'] == 'healthy' else 'bg-secondary'}">

                                        {conn_health['heartbeat_status'].replace('_', ' ').title()}

                                    </span>

                                </p>

                                {f'<small class="text-muted">Last Success: {conn_health["last_successful_connection"]}</small>' if conn_health['last_successful_connection'] else ""}

                            </div>

                        </div>

        """

        # Connection Issues Section

        if (conn_health['dns_issues'] or conn_health['ssl_certificate_issues'] or 

            conn_health['proxy_issues'] or conn_health['firewall_issues']):

            

            html += """

                        <div class="alert alert-warning mb-3">

                            <h6 class="alert-heading"><i class="fas fa-brain"></i>Detected Connection Issues:</h6>

                            <div class="row">

            """

            if conn_health["dns_issues"]:

                html += f"""

                                <div class="col-md-6 mb-2">

                                    <strong><i class="fas fa-brain"></i>DNS Issues:</strong> {len(conn_health['dns_issues'])} detected

                                    <br><small class="text-muted">DNS resolution failures for Cloud One endpoints</small>

                                </div>

                """

            if conn_health['firewall_issues']:

                html += f"""

                                <div class="col-md-6 mb-2">

                                    <strong><i class="fas fa-brain"></i>Firewall Issues:</strong> {len(conn_health['firewall_issues'])} detected

                                    <br><small class="text-muted">Port 443 or connection blocking detected</small>

                                </div>

                """

            if conn_health['proxy_issues']:

                html += f"""

                                <div class="col-md-6 mb-2">

                                    <strong><i class="fas fa-brain"></i>Proxy Issues:</strong> {len(conn_health['proxy_issues'])} detected

                                    <br><small class="text-muted">Proxy authentication or configuration problems</small>

                                </div>

                """

            if conn_health['ssl_certificate_issues']:

                html += f"""

                                <div class="col-md-6 mb-2">

                                    <strong><i class="fas fa-brain"></i>SSL/Certificate Issues:</strong> {len(conn_health['ssl_certificate_issues'])} detected

                                    <br><small class="text-muted">Certificate validation or SSL handshake failures</small>

                                </div>

                """

            html += """

                            </div>

                        </div>

            """

        else:

            html += """

                        <div class="alert alert-success mb-3">

                            <span class="fw-bold"><i class="fa-solid fa-check-circle text-success"></i> No Connection Issues Detected</span>

                            <br><small>No DNS, firewall, proxy, or SSL certificate issues found in the logs.</small>

                        </div>

            """

        html += """

                    </div>

                </div>

            </div>

        </div>

        """

    # Multiple File Analysis Breakdown

    if is_multiple and analysis.get('file_analysis'):

        html += """

        <div class="row mb-4">

            <div class="col-12">
            <div class="card border-info">
            <div class="card-header bg-info text-white"><i class="fas fa-brain"></i>Individual File Analysis Breakdown</div>

                    <div class="card-body">
            <div class="table-responsive">

                            <table class="table table-striped">

                                <thead>

                                    <tr>

                                        <th>File Name</th>

                                        <th>Total Lines</th>

                                        <th>Critical Issues</th>

                                        <th>Errors</th>

                                        <th>Warnings</th>

                                        <th>Health Status</th>

                                    </tr>

                                </thead>

                                <tbody>

        """

        for file_name, file_stats in analysis["file_analysis"].items():

            file_summary = file_stats['summary']

            

            if file_stats['critical_count'] > 0:

                health_status = f'<span class="text-danger"><i class="fas fa-exclamation-circle text-danger"></i> Critical</span>'

                health_class = "table-danger"

            elif file_stats['error_count'] > 10:

                health_status = f'<span class="text-warning"><i class="fa-solid fa-exclamation-triangle me-2"></i>Errors</span>'

                health_class = "table-warning"

            elif file_stats['warning_count'] > 20:

                health_status = f'<span class="text-warning"><i class="fa-solid fa-exclamation-triangle me-2"></i>Warnings</span>'

                health_class = "table-warning"

            else:

                health_status = '<span class="text-success"><i class="fa-solid fa-check-circle me-2 text-success"></i>Healthy</span>'

                health_class = ""

                

            html += f"""

                                    <tr class="{health_class}">

                                        <td><strong>{file_name}</strong></td>

                                        <td>{file_summary.get('total_lines', 0):,}</td>

                                        <td>{file_stats['critical_count']}</td>

                                        <td>{file_stats['error_count']}</td>

                                        <td>{file_stats['warning_count']}</td>

                                        <td>{health_status}</td>

                                    </tr>

            """

        html += """

                                </tbody>

                            </table>

                        </div>

                        <div class="mt-3">

                            <small class="text-muted">

                                <i class="fas fa-info-circle"></i> This breakdown shows individual file health. 

                                Focus on files with critical issues or high error counts for immediate attention.

                            </small>

                        </div>

                    </div>

                </div>

            </div>

        </div>

        """

    html += f"""

    <div class="row mb-4" id="ai-analysis-section">

        <div class="col-12">
            <div class="card border-primary">
            <div class="card-header bg-primary text-white"><i class="fas fa-brain"></i>AI-Powered Comprehensive Analysis</div>

                <div class="card-body">

                    {generate_ai_summary_for_ds_logs(analysis)}

                </div>

            </div>

        </div>

    </div>

    """

    return html







def generate_ai_summary_for_ds_logs(analysis: Dict[str, Any]) -> str:

    """Generate practical AI-powered Deep Security Agent Connection Analysis for network administrators"""

    summary = analysis.get('summary', {})

    connection_health = analysis.get('connection_health', {})

    ml_insights = analysis.get('ml_insights', {})

    rag_insights = analysis.get('rag_insights', {})

    

    # Generate connection-focused AI analysis

    ai_summary = f"""

    <div class="ai-analysis-container">

        <h5><i class="fas fa-brain"></i>Deep Security Agent Connection Analysis</h5>

        <p>AI analysis of {summary.get('total_lines', 0):,} log entries focusing on Cloud One Workload Security connectivity:</p>

        

        """

    if connection_health:

        status = connection_health.get('overall_status', 'unknown')

        success_rate = 0

        if connection_health.get('connection_attempts', 0) > 0:

            success_rate = (connection_health.get('successful_connections', 0) / connection_health.get('connection_attempts', 1)) * 100

        

        # Connection Status Summary

        if status == 'healthy':

            ai_summary += f"""

            <div class="alert alert-success">

                <h6><i class="fa-solid fa-check-circle text-success"></i> Agent Connection Status: Healthy</h6>

                <p><strong>Success Rate:</strong> {success_rate:.1f}% ({connection_health.get('successful_connections', 0)}/{connection_health.get('connection_attempts', 0)} successful)</p>

                <p><strong>Assessment:</strong> DS Agent maintaining stable communication with Cloud One Workload Security.</p>

            </div>

            """

        elif status in ['mostly_healthy', 'unstable']:

            ai_summary += f"""

            <div class="alert alert-warning">

                <h6><i class="fa-solid fa-circle text-warning"></i> Agent Connection Status: {"Intermittent Issues" if status == 'mostly_healthy' else "Frequent Issues"}</h6>

                <p><strong>Success Rate:</strong> {success_rate:.1f}% - Indicates connectivity problems</p>

                <p><strong>Impact:</strong> May cause delayed policy updates or protection gaps.</p>

            </div>

            """

        elif status == 'unhealthy':

            ai_summary += f"""

            <div class="alert alert-danger">

                <h6><i class="fas fa-exclamation-circle text-danger"></i> Agent Connection Status: Critical Issues</h6>

                <p><strong>Success Rate:</strong> {success_rate:.1f}% - Agent effectively isolated</p>

                <p><strong>Impact:</strong> Security protection compromised due to communication failure.</p>

            </div>

            """

        else:

            ai_summary += f"""

            <div class="alert alert-info">

                <h6><i class="fas fa-chart-bar"></i> Agent Connection Status: Limited Activity</h6>

                <p>Minimal connection activity detected. This may be normal for short log periods.</p>

            </div>

            """

        # Log Analysis with AI Interpretation

        ai_summary += """

        <div class="mt-3">

            <h6><i class="fas fa-brain"></i>Log Analysis & AI Interpretation</h6>

        """

        # DNS Issues Analysis

        dns_issues = connection_health.get('dns_issues', [])

        if dns_issues:

            ai_summary += f"""

            <div class="card mt-2">
            <div class="card-header bg-warning text-dark"><i class="fas fa-brain"></i>DNS Resolution Issues ({len(dns_issues)} detected)</div>

                <div class="card-body">

                    <h6>Sample Log Entries:</h6>

                    <div class="bg-light p-2 mb-2 log-entry">

            """

            for issue in dns_issues[:2]:  # Show 2 sample logs

                ai_summary += f"""

                        <div class="mb-1"><strong>[{issue.get('timestamp', 'N/A')}]</strong> {issue.get('message', '')[:150]}...</div>

                """

            ai_summary += f"""

                    </div>

                    <div class="alert alert-light">

                        <strong><i class="fas fa-brain"></i>AI Interpretation:</strong> Agent unable to resolve Cloud One endpoint hostnames. 

                        This prevents communication with workload.*.cloudone.trendmicro.com servers.

                    </div>

                    <h6><i class="fas fa-brain"></i>Troubleshooting Steps:</h6>

                    <ol>

                        <li>Test DNS resolution: <code>nslookup workload.us-1.cloudone.trendmicro.com</code></li>

                        <li>Check corporate DNS server configuration</li>

                        <li>Verify *.cloudone.trendmicro.com is not blocked by DNS filtering</li>

                    </ol>

                </div>

            </div>

            """

        # Firewall Issues Analysis

        firewall_issues = connection_health.get('firewall_issues', [])

        port_issues = connection_health.get('communication_port_issues', [])

        if firewall_issues or port_issues:

            ai_summary += f"""

            <div class="card mt-2">
            <div class="card-header bg-danger text-white"><i class="fas fa-lightbulb"></i> Firewall/Network Issues ({len(firewall_issues)} detected)</div>

                <div class="card-body">

                    <h6>Sample Log Entries:</h6>

                    <div class="bg-light p-2 mb-2 log-entry">

            """

            for issue in firewall_issues[:2]:  # Show 2 sample logs

                ai_summary += f"""

                        <div class="mb-1"><strong>[{issue.get('timestamp', 'N/A')}]</strong> {issue.get('message', '')[:150]}...</div>

                """

            ai_summary += f"""

                    </div>

                    <div class="alert alert-light">

                        <strong><i class="fas fa-brain"></i>AI Interpretation:</strong> Network infrastructure blocking DS Agent communication. 

                        Ports 443, 4120, 4119 required for Cloud One connectivity.

                    </div>

                    <h6><i class="fas fa-brain"></i>Troubleshooting Steps:</h6>

                    <ol>

                        <li>Check firewall rules for outbound HTTPS (443, 4120, 4119, 4118)</li>

                        <li>Whitelist *.cloudone.trendmicro.com in firewall</li>

                        <li>Test connectivity: <code>telnet workload.us-1.cloudone.trendmicro.com 443</code></li>

                    </ol>

            """

            if port_issues:

                affected_ports = list(set([issue.get('port', 'unknown') for issue in port_issues]))

                ai_summary += f"<p><strong>Affected Ports:</strong> {', '.join(affected_ports)}</p>"

            ai_summary += """

                </div>

            </div>

            """

        # Proxy Issues Analysis

        proxy_issues = connection_health.get('proxy_issues', [])

        if proxy_issues:

            ai_summary += f"""

            <div class="card mt-2">
            <div class="card-header bg-warning text-dark"><i class="fas fa-brain"></i>Proxy Configuration Issues ({len(proxy_issues)} detected)</div>

                <div class="card-body">

                    <h6>Sample Log Entries:</h6>

                    <div class="bg-light p-2 mb-2 log-entry">

            """

            for issue in proxy_issues[:2]:  # Show 2 sample logs

                ai_summary += f"""

                        <div class="mb-1"><strong>[{issue.get('timestamp', 'N/A')}]</strong> {issue.get('message', '')[:150]}...</div>

                """

            ai_summary += f"""

                    </div>

                    <div class="alert alert-light">

                        <strong><i class="fas fa-brain"></i>AI Interpretation:</strong> Proxy server blocking or misconfiguring DS Agent traffic. 

                        HTTP 407 errors indicate authentication issues.

                    </div>

                    <h6><i class="fas fa-brain"></i>Troubleshooting Steps:</h6>

                    <ol>

                        <li>Configure DS Agent proxy: <code>dsa_control -m proxy://proxy.server:port</code></li>

                        <li>Verify proxy credentials and authentication method</li>

                        <li>Whitelist *.cloudone.trendmicro.com in proxy rules</li>

                    </ol>

                </div>

            </div>

            """

        # SSL Certificate Issues Analysis

        ssl_issues = connection_health.get('ssl_certificate_issues', [])

        if ssl_issues:

            ai_summary += f"""

            <div class="card mt-2">
            <div class="card-header bg-danger text-white"><i class="fas fa-brain"></i>SSL Certificate Issues ({len(ssl_issues)} detected)</div>

                <div class="card-body">

                    <h6>Sample Log Entries:</h6>

                    <div class="bg-light p-2 mb-2 log-entry">

            """

            for issue in ssl_issues[:2]:  # Show 2 sample logs

                ai_summary += f"""

                        <div class="mb-1"><strong>[{issue.get('timestamp', 'N/A')}]</strong> {issue.get('message', '')[:150]}...</div>

                """

            ai_summary += f"""

                    </div>

                    <div class="alert alert-light">

                        <strong><i class="fas fa-brain"></i>AI Interpretation:</strong> SSL handshake failures or certificate validation errors. 

                        Often caused by incorrect system time or SSL inspection.

                    </div>

                    <h6><i class="fas fa-brain"></i>Troubleshooting Steps:</h6>

                    <ol>

                        <li>Verify system time and timezone accuracy</li>

                        <li>Check certificate trust store and root CAs</li>

                        <li>Review corporate SSL inspection configuration</li>

                    </ol>

                </div>

            </div>

            """

        # Agent Command Failures Analysis

        agent_failures = connection_health.get('agent_command_failures', [])

        if agent_failures:

            ai_summary += f"""

            <div class="card mt-2">
            <div class="card-header bg-warning text-dark"><i class="fas fa-brain"></i>DS Agent Command Failures ({len(agent_failures)} detected)</div>

                <div class="card-body">

                    <h6>Sample Log Entries:</h6>

                    <div class="bg-light p-2 mb-2 log-entry">

            """

            for failure in agent_failures[:2]:  # Show 2 sample logs

                ai_summary += f"""

                        <div class="mb-1"><strong>[{failure.get('timestamp', 'N/A')}]</strong> {failure.get('message', '')[:150]}...</div>

                """

            ai_summary += f"""

                    </div>

                    <div class="alert alert-light">

                        <strong><i class="fas fa-brain"></i>AI Interpretation:</strong> DS Agent commands (SetSecurityConfiguration, GetAgentStatus, HeartbeatNow) failing. 

                        Indicates communication breakdown with DS Manager.

                    </div>

                    <h6><i class="fas fa-brain"></i>Troubleshooting Steps:</h6>

                    <ol>

                        <li>Check agent activation status</li>

                        <li>Verify DS Manager accessibility</li>

                        <li>Test agent-manager communication on port 4120</li>

                    </ol>

                </div>

            </div>

            """

        # Heartbeat Analysis

        heartbeat_data = connection_health.get('heartbeat_analysis', {})

        if heartbeat_data.get('total_heartbeats', 0) > 0:

            success_rate_hb = 0

            if heartbeat_data['total_heartbeats'] > 0:

                success_rate_hb = (heartbeat_data.get('successful_heartbeats', 0) / heartbeat_data['total_heartbeats']) * 100

            

            ai_summary += f"""

            <div class="card mt-2">
            <div class="card-header bg-info text-white"><i class="fas fa-brain"></i>Heartbeat Analysis</div>

                <div class="card-body">

                    <p><strong>Heartbeat Statistics:</strong> {heartbeat_data.get('successful_heartbeats', 0)}/{heartbeat_data.get('total_heartbeats', 0)} successful ({success_rate_hb:.1f}%)</p>

                    <p><strong>Average Interval:</strong> {heartbeat_data.get('average_interval', 0):.0f} seconds</p>

                    <div class="alert alert-light">

                        <strong><i class="fas fa-brain"></i>AI Interpretation:</strong> DS Agent heartbeats monitor communication health. 

                        Standard interval is ~600 seconds (10 minutes).

                    </div>

            """

            if success_rate_hb < 80:

                ai_summary += """

                    <h6><i class="fas fa-brain"></i>Troubleshooting Steps:</h6>

                    <ol>

                        <li>Check network stability between agent and manager</li>

                        <li>Verify DS Manager service availability</li>

                        <li>Monitor for network latency or packet loss</li>

                    </ol>

                """

            ai_summary += """

                </div>

            </div>

            """

        ai_summary += "</div>"  # Close Log Analysis section

        

        # Regional Connectivity Status

        if connection_health.get('connected_regions'):

            regions = ', '.join(connection_health['connected_regions'])

            ai_summary += f"""

            <div class="card mt-3">
            <div class="card-header bg-success text-white"><i class="fas fa-brain"></i>Regional Connectivity</div>

                <div class="card-body">

                    <p><strong>Connected Regions:</strong> {regions}</p>

                    <p><strong>AI Assessment:</strong> Agent successfully connected to Cloud One regional endpoints, indicating proper global load balancing.</p>

                </div>

            </div>

            """

        # No Issues Found

        if not any([dns_issues, firewall_issues, proxy_issues, ssl_issues, agent_failures]):

            ai_summary += """

            <div class="alert alert-success mt-3">

                <h6><i class="fa-solid fa-check-circle text-success"></i> No Major Connection Issues Detected</h6>

                <p><strong>AI Assessment:</strong> Log analysis shows no significant connectivity problems. Agent appears to be communicating normally with Cloud One Workload Security.</p>

            </div>

            """

    else:

        ai_summary += """

        <div class="alert alert-info">

            <h6><i class="fas fa-chart-bar"></i> Connection Analysis Unavailable</h6>

            <p>Connection health analysis could not be performed. Ensure logs contain DS Agent communication entries.</p>

        </div>

        """

    # Summary Recommendations

    recommendations = analysis.get('recommendations', [])

    if recommendations:

        ai_summary += """

        <div class="card mt-3" id="priority-actions-section">
            <div class="card-header bg-primary text-white"><i class="fa-solid fa-bullseye me-2"></i>Priority Actions</div>

            <div class="card-body">

                <ol>

        """

        for rec in recommendations[:5]:

            ai_summary += f"<li>{rec}</li>"

        ai_summary += """

                </ol>

            </div>

        </div>

        """

    # Analysis Coverage

    timespan = summary.get('timespan', {})

    if timespan.get('start') and timespan.get('end'):

        ai_summary += f"""

        <div class="mt-3">

            <small class="text-muted">

                <strong>Analysis Period:</strong> {timespan["start"]} to {timespan["end"]} | 

                <strong>Data Quality:</strong> {summary.get('parsed_lines', 0):,}/{summary.get('total_lines', 0):,} lines parsed |

                <strong>Connection Events:</strong> {connection_health.get('connection_attempts', 0)} analyzed

            </small>

        </div>

        """

    ai_summary += """

        <div class="mt-3">

            <small class="text-muted">

                <i class="fas fa-robot"></i> AI analysis combines log pattern recognition with Deep Security expertise 

                to provide practical network troubleshooting guidance.

            </small>

        </div>

    </div>

    """

    return ai_summary







def format_amsp_results(analysis: Dict[str, Any]) -> str:

    """Format AMSP analysis results as HTML"""

    summary = analysis['summary']

    

    if summary['critical_count'] > 0:

        status_color = "#dc3545"

        status_text = "CRITICAL AMSP ISSUES DETECTED"

        status_icon = '<i class="fas fa-exclamation-circle text-danger"></i>'

    elif summary['error_count'] > 5:

        status_color = "#fd7e14"

        status_text = "MULTIPLE AMSP ERRORS DETECTED"

        status_icon = '<i class="fa-solid fa-exclamation-triangle"></i>'

    elif analysis['installation_summary']['failures'] > 0:

        status_color = "#ffc107"

        status_text = "INSTALLATION ISSUES DETECTED"

        status_icon = '<i class="fa-solid fa-exclamation-triangle"></i>'

    else:

        status_color = "#198754"

        status_text = "AMSP HEALTHY"

        status_icon = '<i class="fa-solid fa-check-circle text-success"></i>'

    

    html = f"""
    <div class="mb-4">

        <h4 style="color: {status_color};">{status_icon} AMSP Anti-Malware Analysis - Status: {status_text}</h4>

    </div>

    

    <div class="row mb-4">

        <div class="col-md-6">
            <div class="card">
            <div class="card-header"><i class="fas fa-chart-bar"></i> Summary Statistics</div>

                <div class="card-body">

                    <p><strong>Total Lines:</strong> {summary['total_lines']:,}</p>

                    <p><strong>Parsed Lines:</strong> {summary['parsed_lines']:,}</p>

                    <p><strong>Critical Issues:</strong> <span style="color: #dc3545;">{summary['critical_count']}</span></p>

                    <p><strong>Errors:</strong> <span style="color: #fd7e14;">{summary['error_count']}</span></p>

                    <p><strong>Warnings:</strong> <span style="color: #ffc107;">{summary['warning_count']}</span></p>

                </div>

            </div>

        </div>

        <div class="col-md-6">

            <div class="card">
            <div class="card-header"><i class="fas fa-lightbulb"></i> Installation Summary</div>

                <div class="card-body">

                    <p><strong>Driver Installations:</strong> {analysis['installation_summary']['driver_installations']}</p>

                    <p><strong>Service Startups:</strong> {analysis['installation_summary']['service_startups']}</p>

                    <p><strong>Pattern Updates:</strong> {analysis['installation_summary']['pattern_updates']}</p>

                    <p><strong>Configuration Changes:</strong> {analysis['installation_summary']['configuration_changes']}</p>

                    <p><strong>Failures:</strong> <span style="color: #dc3545;">{analysis['installation_summary']['failures']}</span></p>

                </div>

            </div>

        </div>

    </div>

    """

    return html





def format_conflict_results(analysis: str, process_count: int) -> str:
    """Format conflict analysis results as HTML with consistent design"""
    
    def parse_analysis_text(text: str) -> dict:
        """Parse the analysis text to extract structured data"""
        lines = text.strip().split('\n')
        conflicts_detected = False
        conflicts = []
        recommendation = ""
        
        # Determine if conflicts exist
        for line in lines:
            if "CONFLICTS DETECTED" in line.upper():
                conflicts_detected = True
                break
            if "NO CONFLICTS DETECTED" in line.upper():
                conflicts_detected = False
                break
        
        # Parse conflicts
        current_software = None
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Software entries (### 1, ### 2, etc.)
            if line.startswith("###") and any(char.isdigit() for char in line):
                if current_software:
                    conflicts.append(current_software)
                
                # Extract software name
                software_name = line.replace("###", "").strip()
                if "." in software_name:
                    software_name = software_name.split(".", 1)[1].strip()
                software_name = software_name.replace("*", "").strip()
                
                current_software = {
                    'name': software_name,
                    'processes': [],
                    'reasoning': ''
                }
                
            # Process lists
            elif line.startswith("- **Processes:**") and current_software:
                process_text = line.replace("- **Processes:**", "").strip()
                if process_text:
                    processes = [p.strip() for p in process_text.split(',') if p.strip()]
                    current_software['processes'] = processes
                    
            # Reasoning sections
            elif line.startswith("- **Reasoning:**") and current_software:
                reasoning_text = line.replace("- **Reasoning:**", "").strip()
                current_software['reasoning'] = reasoning_text
                
            # Recommendation section
            elif "Recommendation:" in line:
                if current_software:
                    conflicts.append(current_software)
                    current_software = None
                recommendation = line.replace("## Recommendation:", "").replace("Recommendation:", "").strip()
        
        # Add final software if exists
        if current_software:
            conflicts.append(current_software)
            
        return {
            'conflicts_detected': conflicts_detected,
            'conflicts': conflicts,
            'recommendation': recommendation
        }
    
    parsed_data = parse_analysis_text(analysis)
    
    # Status determination (matching DS log analyzer pattern)
    if parsed_data['conflicts_detected']:
        status_color = "#dc3545"
        status_text = "CONFLICTS DETECTED"
        status_icon = '<i class="fas fa-exclamation-circle text-danger"></i>'
    else:
        status_color = "#198754"
        status_text = "NO CONFLICTS DETECTED"
        status_icon = '<i class="fas fa-check-circle text-success"></i>'
    
    # Main header (matching DS log format)
    html = f"""
    <div class="mb-4 font-consistent">
        <h4 style="color: {status_color}; font-family: Inter, 'Segoe UI', Roboto, sans-serif !important;">{status_icon} AntiVirus Conflict Analysis - Status: {status_text}</h4>
    </div>
    
    <div class="row mb-4 font-consistent" id="summary-stats-section">
        <div class="col-md-6">
            <div class="card font-consistent">
                <div class="card-header font-consistent" style="font-family: 'Inter', 'Segoe UI', 'Roboto', sans-serif !important;"><i class="fas fa-chart-bar"></i> Analysis Summary</div>
                <div class="card-body font-consistent" style="font-family: 'Inter', 'Segoe UI', 'Roboto', sans-serif !important;">
                    <p style="font-family: 'Inter', 'Segoe UI', 'Roboto', sans-serif !important;"><strong>Processes Analyzed:</strong> {process_count:,}</p>
                    <p style="font-family: 'Inter', 'Segoe UI', 'Roboto', sans-serif !important;"><strong>Conflicts Found:</strong> <span style="color: {status_color};">{len(parsed_data['conflicts'])}</span></p>
                    <p style="font-family: 'Inter', 'Segoe UI', 'Roboto', sans-serif !important;"><strong>Analysis Status:</strong> <span style="color: {status_color};">{status_text}</span></p>
                </div>
            </div>
        </div>
        <div class="col-md-6">
            <div class="card font-consistent">
                <div class="card-header font-consistent" style="font-family: 'Inter', 'Segoe UI', 'Roboto', sans-serif !important;"><i class="fas fa-shield-alt me-2"></i>Security Impact</div>
                <div class="card-body font-consistent" style="font-family: 'Inter', 'Segoe UI', 'Roboto', sans-serif !important;">
    """
    
    if parsed_data['conflicts_detected']:
        html += f"""
                    <p style="font-family: 'Inter', 'Segoe UI', 'Roboto', sans-serif !important;"><i class="fas fa-exclamation-triangle me-2 text-warning"></i><strong>Attention Required:</strong> Conflicting security software detected</p>
                    <p style="font-family: 'Inter', 'Segoe UI', 'Roboto', sans-serif !important;"><i class="fas fa-tools me-2 text-info"></i><strong>Action:</strong> Review conflicts before Deep Security installation</p>
        """
    else:
        html += f"""
                    <p style="font-family: 'Inter', 'Segoe UI', 'Roboto', sans-serif !important;"><i class="fas fa-check-circle me-2 text-success"></i><strong>System Compatible:</strong> No conflicts detected</p>
                    <p style="font-family: 'Inter', 'Segoe UI', 'Roboto', sans-serif !important;"><i class="fas fa-rocket me-2 text-success"></i><strong>Status:</strong> Ready for Deep Security installation</p>
        """
    
    html += """
                </div>
            </div>
        </div>
    </div>
    """
    
    # Conflicts section (if any found)
    if parsed_data['conflicts']:
        html += """
        <div class="row mb-4 font-consistent" id="conflicts-section">
            <div class="col-12">
                <div class="card font-consistent">
                    <div class="card-header font-consistent" style="font-family: 'Inter', 'Segoe UI', 'Roboto', sans-serif !important;"><i class="fas fa-exclamation-triangle"></i> Detected Conflicts</div>
                    <div class="card-body font-consistent" style="font-family: 'Inter', 'Segoe UI', 'Roboto', sans-serif !important;">
                        <div class="table-responsive">
                            <table class="table table-striped font-consistent" style="font-family: 'Inter', 'Segoe UI', 'Roboto', sans-serif !important;">
                                <thead>
                                    <tr style="font-family: 'Inter', 'Segoe UI', 'Roboto', sans-serif !important;">
                                        <th style="font-family: 'Inter', 'Segoe UI', 'Roboto', sans-serif !important;">Software</th>
                                        <th style="font-family: 'Inter', 'Segoe UI', 'Roboto', sans-serif !important;">Processes</th>
                                        <th style="font-family: 'Inter', 'Segoe UI', 'Roboto', sans-serif !important;">Reason for Conflict</th>
                                    </tr>
                                </thead>
                                <tbody style="font-family: 'Inter', 'Segoe UI', 'Roboto', sans-serif !important;">
        """
        
        for conflict in parsed_data['conflicts']:
            processes_html = ""
            for process in conflict['processes']:
                processes_html += f'<span class="badge bg-secondary me-1 mb-1">{process}</span>'
            
            html += f"""
                                    <tr style="font-family: 'Inter', 'Segoe UI', 'Roboto', sans-serif !important;">
                                        <td style="font-family: 'Inter', 'Segoe UI', 'Roboto', sans-serif !important;"><strong>{conflict['name']}</strong></td>
                                        <td style="font-family: 'Inter', 'Segoe UI', 'Roboto', sans-serif !important;">{processes_html}</td>
                                        <td style="font-family: 'Inter', 'Segoe UI', 'Roboto', sans-serif !important;">{conflict['reasoning']}</td>
                                    </tr>
            """
        
        html += """
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        """
    
    # Recommendation section (matching DS log AI analysis pattern)
    if parsed_data['recommendation']:
        html += f"""
        <div class="row mb-4" id="recommendation-section">
            <div class="col-12">
                <div class="card border-primary">
                    <div class="card-header bg-primary text-white"><i class="fas fa-lightbulb"></i> Expert Recommendation</div>
                    <div class="card-body">
                        <p style="font-family: 'Inter', 'Segoe UI', 'Roboto', sans-serif !important;">{parsed_data['recommendation']}</p>
                    </div>
                </div>
            </div>
        </div>
        """
    
    return html

def format_resource_results(analysis_data: dict, process_count: int, busy_count: int) -> str:
    """Format resource analysis results as HTML with enhanced styling and comprehensive information"""
    
    # Extract analysis components
    analysis_text = analysis_data.get('analysis_text', '')
    candidates = analysis_data.get('candidates', [])
    status = analysis_data.get('status', 'unknown')
    ml_insights = analysis_data.get('ml_insights')
    rag_insights = analysis_data.get('rag_insights')
    security_impact = analysis_data.get('security_impact', {})
    performance_metrics = analysis_data.get('performance_metrics', {})
    
    # Determine status styling
    if status == "error":
        status_color = "#dc3545"
        status_text = "ANALYSIS ERROR"
        status_icon = '<i class="fas fa-exclamation-circle text-danger"></i>'
    elif len(candidates) > 0:
        status_color = "#ffc107"
        status_text = "EXCLUSION CANDIDATES FOUND"
        status_icon = '<i class="fas fa-exclamation-triangle text-warning"></i>'
    elif status == "no_files":
        status_color = "#6c757d"
        status_text = "INSUFFICIENT DATA"
        status_icon = '<i class="fas fa-info-circle text-muted"></i>'
    else:
        status_color = "#198754"
        status_text = "OPTIMAL PERFORMANCE"
        status_icon = '<i class="fas fa-check-circle text-success"></i>'
    
    html = f"""
    <div class="mb-4 font-consistent">
        <h4 style="color: {status_color}; font-family: Inter, 'Segoe UI', Roboto, sans-serif !important;">{status_icon} Resource Analysis - Status: {status_text}</h4>
    </div>
    
    <div class="row mb-4 font-consistent" id="summary-stats-section">
        <div class="col-md-6">
            <div class="card font-consistent">
                <div class="card-header font-consistent" style="font-family: 'Inter', 'Segoe UI', 'Roboto', sans-serif !important;"><i class="fas fa-chart-bar"></i> Analysis Summary</div>
                <div class="card-body font-consistent" style="font-family: 'Inter', 'Segoe UI', 'Roboto', sans-serif !important;">
                    <p style="font-family: 'Inter', 'Segoe UI', 'Roboto', sans-serif !important;"><strong>Running Processes:</strong> {process_count:,}</p>
                    <p style="font-family: 'Inter', 'Segoe UI', 'Roboto', sans-serif !important;"><strong>Busy Processes:</strong> {busy_count:,}</p>
                    <p style="font-family: 'Inter', 'Segoe UI', 'Roboto', sans-serif !important;"><strong>Exclusion Candidates:</strong> <span style="color: {status_color};">{len(candidates)}</span></p>
                    <p style="font-family: 'Inter', 'Segoe UI', 'Roboto', sans-serif !important;"><strong>Analysis Status:</strong> <span style="color: {status_color};">{status_text}</span></p>
                </div>
            </div>
        </div>
        <div class="col-md-6">
            <div class="card font-consistent">
                <div class="card-header font-consistent" style="font-family: 'Inter', 'Segoe UI', 'Roboto', sans-serif !important;"><i class="fas fa-shield-alt me-2"></i>Performance Impact</div>
                <div class="card-body font-consistent" style="font-family: 'Inter', 'Segoe UI', 'Roboto', sans-serif !important;">
    """
    
    if len(candidates) > 0:
        high_impact_count = len([c for c in candidates if int(str(c.get('count', '0')).replace(',', '')) > 1000])
        html += f"""
                    <p style="font-family: 'Inter', 'Segoe UI', 'Roboto', sans-serif !important;"><i class="fas fa-exclamation-triangle me-2 text-warning"></i><strong>High Impact Processes:</strong> {high_impact_count}</p>
                    <p style="font-family: 'Inter', 'Segoe UI', 'Roboto', sans-serif !important;"><i class="fas fa-tachometer-alt me-2 text-info"></i><strong>Performance Optimization:</strong> Recommended</p>
                    <p style="font-family: 'Inter', 'Segoe UI', 'Roboto', sans-serif !important;"><i class="fas fa-shield-alt me-2 text-success"></i><strong>Security Review:</strong> Required before exclusion</p>
        """
    else:
        html += f"""
                    <p style="font-family: 'Inter', 'Segoe UI', 'Roboto', sans-serif !important;"><i class="fas fa-check-circle me-2 text-success"></i><strong>System Performance:</strong> Optimal</p>
                    <p style="font-family: 'Inter', 'Segoe UI', 'Roboto', sans-serif !important;"><i class="fas fa-clock me-2 text-info"></i><strong>Scan Efficiency:</strong> No issues detected</p>
                    <p style="font-family: 'Inter', 'Segoe UI', 'Roboto', sans-serif !important;"><i class="fas fa-cog me-2 text-muted"></i><strong>Action Required:</strong> None</p>
        """
    
    html += """
                </div>
            </div>
        </div>
    </div>
    """
    
    # Exclusion Candidates Section
    if len(candidates) > 0:
        html += """
        <div class="row mb-4 font-consistent" id="exclusion-candidates-section">
            <div class="col-12">
                <div class="card font-consistent border-warning">
                    <div class="card-header bg-warning text-dark font-consistent" style="font-family: 'Inter', 'Segoe UI', 'Roboto', sans-serif !important;"><i class="fas fa-exclamation-triangle"></i> Exclusion Candidates</div>
                    <div class="card-body font-consistent" style="font-family: 'Inter', 'Segoe UI', 'Roboto', sans-serif !important;">
                        <div class="table-responsive">
                            <table class="table table-striped font-consistent" style="font-family: 'Inter', 'Segoe UI', 'Roboto', sans-serif !important;">
                                <thead>
                                    <tr style="font-family: 'Inter', 'Segoe UI', 'Roboto', sans-serif !important;">
                                        <th style="font-family: 'Inter', 'Segoe UI', 'Roboto', sans-serif !important;">Process Name</th>
                                        <th style="font-family: 'Inter', 'Segoe UI', 'Roboto', sans-serif !important;">Scan Count</th>
                                        <th style="font-family: 'Inter', 'Segoe UI', 'Roboto', sans-serif !important;">Impact Level</th>
                                        <th style="font-family: 'Inter', 'Segoe UI', 'Roboto', sans-serif !important;">Security Risk</th>
                                    </tr>
                                </thead>
                                <tbody style="font-family: 'Inter', 'Segoe UI', 'Roboto', sans-serif !important;">
        """
        
        for candidate in candidates:
            count = int(str(candidate.get('count', '0')).replace(',', ''))
            name = candidate.get('name', 'Unknown')
            
            # Determine impact level and styling
            if count > 2000:
                impact_level = "Very High"
                impact_class = "bg-danger text-white"
                security_risk = "Medium"
                security_class = "text-warning"
            elif count > 1000:
                impact_level = "High"
                impact_class = "bg-warning text-dark"
                security_risk = "Low-Medium"
                security_class = "text-info"
            elif count > 500:
                impact_level = "Medium"
                impact_class = "bg-info text-white"
                security_risk = "Low"
                security_class = "text-success"
            else:
                impact_level = "Low"
                impact_class = "bg-secondary text-white"
                security_risk = "Minimal"
                security_class = "text-muted"
            
            html += f"""
                                    <tr style="font-family: 'Inter', 'Segoe UI', 'Roboto', sans-serif !important;">
                                        <td style="font-family: 'Inter', 'Segoe UI', 'Roboto', sans-serif !important;"><strong>{name}</strong></td>
                                        <td style="font-family: 'Inter', 'Segoe UI', 'Roboto', sans-serif !important;"><span class="badge bg-primary">{candidate.get('count', 'N/A')}</span></td>
                                        <td style="font-family: 'Inter', 'Segoe UI', 'Roboto', sans-serif !important;"><span class="badge {impact_class}">{impact_level}</span></td>
                                        <td style="font-family: 'Inter', 'Segoe UI', 'Roboto', sans-serif !important;"><span class="{security_class}">{security_risk}</span></td>
                                    </tr>
            """
        
        html += """
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        """
    
    # ML Analysis Section
    if ml_insights:
        html += f"""
        <div class="row mb-4" id="ml-analysis-section">
            <div class="col-12">
                <div class="card border-info">
                    <div class="card-header bg-info text-white"><i class="fas fa-brain"></i> Machine Learning Analysis</div>
                    <div class="card-body">
                        <div class="row mb-3">
                            <div class="col-md-4">
                                <strong>Processes Analyzed:</strong> {ml_insights.get('total_processes', 0)}<br>
                                <strong>ML Features Used:</strong> {len(ml_insights.get('features_analyzed', []))}
                            </div>
                            <div class="col-md-4">
                                <strong>Performance Score:</strong> 
                                <span class="badge bg-{'success' if ml_insights.get('performance_score', 0) > 80 else 'warning' if ml_insights.get('performance_score', 0) > 60 else 'danger'}">{ml_insights.get('performance_score', 0):.0f}%</span><br>
                                <strong>Optimization Potential:</strong> {ml_insights.get('optimization_potential', 'Unknown')}
                            </div>
                            <div class="col-md-4">
                                <strong>Resource Patterns:</strong> {len(ml_insights.get('resource_patterns', []))}<br>
                                <strong>ML Recommendations:</strong> {len(ml_insights.get('recommendations', []))}
                            </div>
                        </div>
        """
        
        if ml_insights.get('resource_patterns'):
            html += """
                        <h6><i class="fas fa-chart-line"></i> Resource Usage Patterns:</h6>
                        <div class="list-group">
            """
            for pattern in ml_insights['resource_patterns'][:3]:
                html += f"""
                            <div class="list-group-item">
                                <h6 class="mb-1">{pattern.get('pattern_name', 'Unknown Pattern')}</h6>
                                <p class="mb-1">{pattern.get('description', 'No description available')}</p>
                                <small class="text-muted">Impact: {pattern.get('impact', 'Unknown')}</small>
                            </div>
                """
            html += """
                        </div>
            """
        
        html += """
                    </div>
                </div>
            </div>
        </div>
        """
    
    # RAG Analysis Section
    if rag_insights:
        html += f"""
        <div class="row mb-4" id="rag-analysis-section">
            <div class="col-12">
                <div class="card border-success">
                    <div class="card-header bg-success text-white"><i class="fas fa-database"></i> Knowledge-Enhanced Analysis</div>
                    <div class="card-body">
                        <div class="row mb-3">
                            <div class="col-md-6">
                                <strong>Knowledge Sources:</strong> {rag_insights.get('knowledge_sources_used', 0)}<br>
                                <strong>Best Practices Matched:</strong> {rag_insights.get('patterns_matched', 0)}
                            </div>
                            <div class="col-md-6">
                                <strong>Confidence Score:</strong> {rag_insights.get('confidence_score', 0):.1f}%<br>
                                <strong>RAG Version:</strong> {rag_insights.get('rag_version', 'N/A')}
                            </div>
                        </div>
        """
        
        if rag_insights.get('best_practices'):
            html += """
                        <h6><i class="fas fa-lightbulb"></i> Deep Security Best Practices:</h6>
                        <div class="list-group">
            """
            for practice in rag_insights['best_practices'][:3]:
                html += f"""
                            <div class="list-group-item">
                                <h6 class="mb-1">{practice.get('title', 'Best Practice')}</h6>
                                <p class="mb-1">{practice.get('description', 'No description available')}</p>
                                <small class="text-muted">Category: {practice.get('category', 'General')}</small>
                            </div>
                """
            html += """
                        </div>
            """
        
        html += """
                    </div>
                </div>
            </div>
        </div>
        """
    
    # AI Analysis Section
    html += f"""
    <div class="row mb-4" id="ai-analysis-section">
        <div class="col-12">
            <div class="card border-primary">
                <div class="card-header bg-primary text-white"><i class="fas fa-robot"></i> AI-Powered Analysis & Recommendations</div>
                <div class="card-body">
                    <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; border-left: 4px solid #007bff;">
    """
    
    # Format the analysis text with better structure
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
    
    return html
    

def get_html_template():

    """Get the HTML template string"""

    from templates import HTML_TEMPLATE

    return HTML_TEMPLATE









