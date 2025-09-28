# -*- coding: utf-8 -*-
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

from security import (

    SecurityError, 

    validate_file, 

    create_secure_temp_file, 

    cleanup_temp_file,

    validate_host_access

)

from config import get_config

# UI components functionality moved to frontend
# from ui_components import session_manager, wizard, guidance
from simple_session_manager import simple_session_manager as session_manager

# Minimal wizard and guidance fallbacks for server-side routes (not used by Next.js frontend)
class MinimalWizard:
    STEPS = {
        1: {'name': 'Analysis Type Selection', 'description': 'Choose analysis type'},
        2: {'name': 'File Upload', 'description': 'Upload files'},
        3: {'name': 'Ready', 'description': 'Ready for analysis'},
        4: {'name': 'Processing', 'description': 'Analysis in progress'},
        5: {'name': 'Results', 'description': 'View results'}
    }
    
    def can_proceed_to_step(self, session_id, target_step):
        return True  # Frontend handles validation
    
    def get_step_info(self, step):
        return self.STEPS.get(step, {})
    
    def get_progress_percentage(self, step):
        return int((step / len(self.STEPS)) * 100)

class MinimalGuidance:
    def get_analysis_guidance(self, analysis_type):
        return {}  # Frontend handles guidance

wizard = MinimalWizard()
guidance = MinimalGuidance()

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

from analyzers import DSAgentLogAnalyzer, AMSPAnalyzer, ConflictAnalyzer, ResourceAnalyzer, DSAgentOfflineAnalyzer, DiagnosticPackageAnalyzer



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

                try:
                    analysis_results = analyzer.analyze_log_file(temp_paths[0])
                    
                    # Check if analysis succeeded
                    if not analysis_results:
                        raise Exception("Analysis returned no results")
                    
                    # Auto-select formatter version based on content
                    if should_use_enhanced_formatter(analysis_results):
                        result = format_ds_log_results_v2(analysis_results, False)
                    else:
                        result = format_ds_log_results(analysis_results, False)

                    raw_result = analysis_results  # Store full structured analysis results instead of summary text
                    
                except Exception as e:
                    print(f"❌ DS Agent analysis failed: {e}")
                    result = f"""
                    <div class="alert alert-danger">
                        <h4><i class="fas fa-exclamation-triangle"></i> DS Agent Analysis Failed</h4>
                        <p>Error: {str(e)}</p>
                        <p>Please verify the log file format and try again.</p>
                    </div>
                    """
                    raw_result = f"DS Agent Analysis Failed: {str(e)}"

            else:

                try:
                    # Multiple DS log file analysis
                    analysis_results = analyzer.analyze_multiple_log_files(temp_paths)
                    
                    # Check if analysis succeeded
                    if not analysis_results:
                        raise Exception("Multiple file analysis returned no results")

                    # Auto-select formatter version based on content
                    if should_use_enhanced_formatter(analysis_results):
                        result = format_ds_log_results_v2(analysis_results, True)
                    else:
                        result = format_ds_log_results(analysis_results, True)  # True indicates multiple files

                    file_count = len(temp_paths)
                    raw_result = analysis_results  # Store full structured analysis results instead of summary text
                    
                except Exception as e:
                    print(f"❌ Multiple DS Agent analysis failed: {e}")
                    result = f"""
                    <div class="alert alert-danger">
                        <h4><i class="fas fa-exclamation-triangle"></i> Multiple DS Agent Analysis Failed</h4>
                        <p>Error: {str(e)}</p>
                        <p>Please verify the log file formats and try again.</p>
                    </div>
                    """
                    raw_result = f"Multiple DS Agent Analysis Failed: {str(e)}"

                

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

                raise SecurityError("Resource analysis requires both RunningProcesses.xml and TopNBusyProcess.txt files")

            

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
                raise SecurityError("Could not identify RunningProcesses.xml and TopNBusyProcess.txt files. Please ensure both files are uploaded.")
            
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
- Running Processes: {len(processes)} processes from RunningProcesses.xml
- Busy Processes: {len(busy_processes)} processes from TopNBusyProcess.txt

Exclusion Candidates Found: {len(candidates)}

Analysis:
{analysis_text}

Candidates Summary:
"""
            for candidate in candidates:
                raw_result += f"- {candidate.get('name', 'Unknown')}: {candidate.get('count', 'N/A')} scans\n"
            
            if resource_analysis_data.get('rag_insights'):
                raw_result += f"\nKnowledge Sources: {resource_analysis_data['rag_insights'].get('knowledge_sources_used', 'N/A')}"

        elif analysis_type == "ds_agent_offline":
            analyzer = DSAgentOfflineAnalyzer(session_manager=session_manager, session_id=analysis_session_id)
            analysis_results = analyzer.analyze_log_file(temp_paths[0])
            result = format_ds_agent_offline_results(analysis_results)
            raw_result = f"DS Agent Offline Analysis Results:\n\n{analysis_results.get('summary', 'No summary available')}"

        elif analysis_type == "ds_agent_offline":
            analyzer = DSAgentOfflineAnalyzer(session_manager=session_manager, session_id=analysis_session_id)
            analysis_results = analyzer.analyze_log_file(temp_paths[0])
            result = format_ds_agent_offline_results(analysis_results)
            raw_result = f"DS Agent Offline Analysis Results:\n\n{analysis_results.get('summary', 'No summary available')}"

        

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

                try:
                    analysis_results = analyzer.analyze_log_file(temp_paths[0])
                    
                    # Check if analysis succeeded
                    if not analysis_results:
                        raise Exception("Analysis returned no results")
                    
                    # Auto-select formatter version based on content
                    if should_use_enhanced_formatter(analysis_results):
                        result = format_ds_log_results_v2(analysis_results, False)
                    else:
                        result = format_ds_log_results(analysis_results, False)

                    raw_result = analysis_results  # Store full structured analysis results instead of summary text
                    
                except Exception as e:
                    print(f"❌ DS Agent analysis failed: {e}")
                    result = f"""
                    <div class="alert alert-danger">
                        <h4><i class="fas fa-exclamation-triangle"></i> DS Agent Analysis Failed</h4>
                        <p>Error: {str(e)}</p>
                        <p>Please verify the log file format and try again.</p>
                    </div>
                    """
                    raw_result = f"DS Agent Analysis Failed: {str(e)}"

            else:

                try:
                    # Multiple DS log file analysis
                    analysis_results = analyzer.analyze_multiple_log_files(temp_paths)
                    
                    # Check if analysis succeeded
                    if not analysis_results:
                        raise Exception("Multiple file analysis returned no results")

                    # Auto-select formatter version based on content
                    if should_use_enhanced_formatter(analysis_results):
                        result = format_ds_log_results_v2(analysis_results, True)
                    else:
                        result = format_ds_log_results(analysis_results, True)  # True indicates multiple files

                    file_count = len(temp_paths)
                    raw_result = analysis_results  # Store full structured analysis results instead of summary text
                    
                except Exception as e:
                    print(f"❌ Multiple DS Agent analysis failed: {e}")
                    result = f"""
                    <div class="alert alert-danger">
                        <h4><i class="fas fa-exclamation-triangle"></i> Multiple DS Agent Analysis Failed</h4>
                        <p>Error: {str(e)}</p>
                        <p>Please verify the log file formats and try again.</p>
                    </div>
                    """
                    raw_result = f"Multiple DS Agent Analysis Failed: {str(e)}"

                

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

                raise SecurityError("Resource analysis requires both RunningProcesses.xml and TopNBusyProcess.txt files")

            

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
                raise SecurityError("Could not identify RunningProcesses.xml and TopNBusyProcess.txt files. Please ensure both files are uploaded.")
            
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
- Running Processes: {len(processes)} processes from RunningProcesses.xml
- Busy Processes: {len(busy_processes)} processes from TopNBusyProcess.txt

Exclusion Candidates Found: {len(candidates)}

Analysis:
{analysis_text}

Candidates Summary:
"""
            for candidate in candidates:
                raw_result += f"- {candidate.get('name', 'Unknown')}: {candidate.get('count', 'N/A')} scans\n"
            
            if resource_analysis_data.get('rag_insights'):
                raw_result += f"\nKnowledge Sources: {resource_analysis_data['rag_insights'].get('knowledge_sources_used', 'N/A')}"

        elif analysis_type == "ds_agent_offline":
            analyzer = DSAgentOfflineAnalyzer(session_manager=session_manager, session_id=analysis_session_id)
            analysis_results = analyzer.analyze_log_file(temp_paths[0])
            result = format_ds_agent_offline_results(analysis_results)
            raw_result = f"DS Agent Offline Analysis Results:\n\n{analysis_results.get('summary', 'No summary available')}"

        elif analysis_type == "diagnostic_package":
            analyzer = DiagnosticPackageAnalyzer(session_manager=session_manager, session_id=analysis_session_id)
            if len(temp_paths) == 1:
                # Single ZIP file analysis
                analysis_results = analyzer.analyze(temp_paths[0])
                result = format_diagnostic_package_results(analysis_results)
                
                files_analyzed = analysis_results.get('package_summary', {}).get('total_files_analyzed', 0)
                correlations = analysis_results.get('correlation_analysis', {})
                correlation_count = len(correlations.get('correlations', [])) if correlations else 0
                
                raw_result = f"""Diagnostic Package Analysis Results:

Package Summary:
- Files Analyzed: {files_analyzed}
- Cross-log Correlations: {correlation_count}
- Analysis Completed: {analysis_results.get('package_summary', {}).get('analysis_timestamp', 'Unknown')}

Executive Summary:
{analysis_results.get('executive_summary', {}).get('overview', 'No executive summary available')}

Key Findings:
"""
                for finding in analysis_results.get('executive_summary', {}).get('key_findings', []):
                    raw_result += f"- {finding}\n"
                    
                if analysis_results.get('ml_insights'):
                    raw_result += f"\nML Analysis: Overall Health Score {analysis_results['ml_insights'].get('overall_health_score', 'N/A')}%"
                
                if analysis_results.get('dynamic_rag_analysis'):
                    rag_data = analysis_results['dynamic_rag_analysis']
                    if rag_data.get('knowledge_sources'):
                        raw_result += f"\nKnowledge Sources: {len(rag_data['knowledge_sources'])} sources consulted"
            else:
                raise SecurityError("Diagnostic package analysis requires exactly one ZIP file.")
        
        else:
            raise SecurityError(f"Unknown analysis type: {analysis_type}")

        

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
        import traceback
        error_traceback = traceback.format_exc()
        print(f"❌ Background analysis failed for session {analysis_session_id}: {str(e)}")
        print(f"📋 Full traceback: {error_traceback}")
        session_manager.update_session(analysis_session_id, {
            'status': 'error',
            'error_message': str(e),
            'error_traceback': error_traceback
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





def should_use_enhanced_formatter(analysis: Dict[str, Any]) -> bool:
    """Determine whether to use the enhanced v2 formatter based on analysis content"""
    # Safety check for None analysis
    if not analysis or not isinstance(analysis, dict):
        return False
        
    # Use v2 if we have new sections (module_status or configuration)
    if analysis.get('module_status') or analysis.get('configuration'):
        return True
    
    # Use v2 for large files (40,000+ lines)
    summary = analysis.get('summary', {})
    if summary.get('total_lines', 0) >= 40000:
        return True
    
    # Use v2 if significant complexity (high error/warning counts)
    if summary.get('error_count', 0) + summary.get('warning_count', 0) > 100:
        return True
    
    return False


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

    # Connection Health Section Removed - Cloud One Workload Security Connection Health component eliminated

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


def format_ds_log_results_v2(analysis: Dict[str, Any], is_multiple: bool = False) -> str:
    """Enhanced DS log analysis results with 6-section output structure for 40k+ line processing"""
    # Safety check for None or invalid analysis
    if not analysis or not isinstance(analysis, dict):
        return f"""
        <div class="alert alert-danger">
            <h4><i class="fas fa-exclamation-triangle"></i> Analysis Error</h4>
            <p>The analysis data is not available. Please try again or contact support.</p>
        </div>
        """
    
    summary = analysis.get('summary', {})
    if not summary:
        return f"""
        <div class="alert alert-warning">
            <h4><i class="fas fa-exclamation-triangle"></i> Incomplete Analysis</h4>
            <p>The analysis summary is not available. The log file may not be compatible with DS Agent analysis.</p>
        </div>
        """
    
    # Status determination
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
        <h4 style="color: {status_color}; font-family: Inter, 'Segoe UI', Roboto, sans-serif !important;">{status_icon} DS Agent Log Analysis v2 - Status: {status_text}</h4>
        {'<p style="font-family: Inter, Segoe UI, Roboto, sans-serif !important;"><i class="fas fa-layer-group"></i> <strong>Multiple File Analysis:</strong> ' + str(summary.get('file_count', 1)) + ' files analyzed</p>' if is_multiple else ''}
        <p style="font-family: Inter, 'Segoe UI', Roboto, sans-serif !important; color: #6c757d;"><i class="fas fa-rocket"></i> Enhanced processing for large log files (40,000+ lines supported)</p>
    </div>
    
    <!-- Section 1: Summary Statistics -->
    <div class="row mb-4 font-consistent">
        <div class="col-12">
            <div class="card border-primary">
                <div class="card-header bg-primary text-white" style="font-family: 'Inter', 'Segoe UI', 'Roboto', sans-serif !important;">
                    <i class="fas fa-chart-bar"></i> Section 1: Summary Statistics
                </div>
                <div class="card-body" style="font-family: 'Inter', 'Segoe UI', 'Roboto', sans-serif !important;">
                    <div class="row">
                        <div class="col-md-4">
                            <h6>File Processing</h6>
                            <p><strong>Total Lines:</strong> {summary['total_lines']:,}</p>
                            <p><strong>Parsed Lines:</strong> {summary['parsed_lines']:,}</p>
                            <p><strong>Parsing Rate:</strong> {(summary['parsed_lines']/summary['total_lines']*100) if summary['total_lines'] > 0 else 0:.1f}%</p>
                        </div>
                        <div class="col-md-4">
                            <h6>Issue Counts</h6>
                            <p><strong>Critical Issues:</strong> <span style="color: #dc3545;">{summary['critical_count']}</span></p>
                            <p><strong>Errors:</strong> <span style="color: #fd7e14;">{summary['error_count']}</span></p>
                            <p><strong>Warnings:</strong> <span style="color: #ffc107;">{summary['warning_count']}</span></p>
                        </div>
                        <div class="col-md-4">
                            <h6>Time Analysis</h6>
                            <p><strong>Start Time:</strong> {summary['timespan']['start'] or 'N/A'}</p>
                            <p><strong>End Time:</strong> {summary['timespan']['end'] or 'N/A'}</p>
                            {'<p><strong>Files Analyzed:</strong> ' + str(summary.get('file_count', 1)) + '</p>' if is_multiple else ''}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <!-- Section 2: Module Status -->"""
    
    # Add Module Status section
    module_status = analysis.get('module_status', {})
    if module_status:
        html += f"""
    <div class="row mb-4 font-consistent">
        <div class="col-12">
            <div class="card border-success">
                <div class="card-header bg-success text-white" style="font-family: 'Inter', 'Segoe UI', 'Roboto', sans-serif !important;">
                    <i class="fas fa-toggle-on"></i> Section 2: Module Status
                </div>
                <div class="card-body" style="font-family: 'Inter', 'Segoe UI', 'Roboto', sans-serif !important;">
                    <div class="row">
                        <div class="col-md-6">
                            <h6 class="text-success"><i class="fas fa-check-circle"></i> Enabled Modules ({len(module_status.get('enabled_modules', []))})</h6>
                            <ul class="list-unstyled">"""
        
        for module in module_status.get('enabled_modules', []):
            html += f'<li><span class="badge bg-success me-2">ON</span>{module}</li>'
        
        html += f"""
                            </ul>
                        </div>
                        <div class="col-md-6">
                            <h6 class="text-secondary"><i class="fas fa-times-circle"></i> Disabled Modules ({len(module_status.get('disabled_modules', []))})</h6>
                            <ul class="list-unstyled">"""
        
        for module in module_status.get('disabled_modules', []):
            html += f'<li><span class="badge bg-secondary me-2">OFF</span>{module}</li>'
        
        html += """
                            </ul>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>"""
    else:
        html += """
    <div class="row mb-4 font-consistent">
        <div class="col-12">
            <div class="card border-warning">
                <div class="card-header bg-warning text-dark" style="font-family: 'Inter', 'Segoe UI', 'Roboto', sans-serif !important;">
                    <i class="fas fa-exclamation-triangle"></i> Section 2: Module Status
                </div>
                <div class="card-body text-center" style="font-family: 'Inter', 'Segoe UI', 'Roboto', sans-serif !important;">
                    <p class="text-muted">No module status information found in log file</p>
                </div>
            </div>
        </div>
    </div>"""
    
    # Add DS Configuration section
    configuration = analysis.get('configuration', {})
    html += f"""
    <!-- Section 3: DS Configuration -->
    <div class="row mb-4 font-consistent">
        <div class="col-12">
            <div class="card border-info">
                <div class="card-header bg-info text-white" style="font-family: 'Inter', 'Segoe UI', 'Roboto', sans-serif !important;">
                    <i class="fas fa-cogs"></i> Section 3: DS Configuration
                </div>
                <div class="card-body" style="font-family: 'Inter', 'Segoe UI', 'Roboto', sans-serif !important;">"""
    
    if configuration:
        html += '<div class="row">'
        config_items = []
        
        for key, value in configuration.items():
            if key == 'manager_url':
                config_items.append(f'<p><strong>Manager URL:</strong> <code>{value}</code></p>')
            elif key == 'agent_initiated':
                config_items.append(f'<p><strong>Agent Initiated:</strong> <span class="badge bg-{"success" if value.lower() == "true" else "secondary"}">{value.upper()}</span></p>')
            elif key == 'azure_status':
                config_items.append(f'<p><strong>Azure Status:</strong> <span class="badge bg-{"success" if value.lower() == "true" else "secondary"}">{value.upper()}</span></p>')
            elif key == 'secure_boot':
                config_items.append(f'<p><strong>Secure Boot:</strong> <span class="badge bg-{"success" if value.lower() == "true" else "secondary"}">{value.upper()}</span></p>')
            elif key == 'fips_available':
                config_items.append(f'<p><strong>FIPS Available:</strong> <span class="badge bg-{"success" if value == "1" else "secondary"}">{value}</span></p>')
            elif key == 'proxy_settings' and isinstance(value, dict):
                config_items.append(f'<p><strong>Proxy Settings:</strong> Auto: {value.get("auto", "N/A")}, PAC: {value.get("pac_url") or "None"}</p>')
            elif key == 'bios_uuid' and isinstance(value, dict):
                config_items.append(f'<p><strong>BIOS UUID:</strong> {value.get("new", "N/A")}</p>')
            else:
                config_items.append(f'<p><strong>{key.replace("_", " ").title()}:</strong> {value}</p>')
        
        # Split config items into columns
        mid_point = len(config_items) // 2
        html += f'<div class="col-md-6">{"".join(config_items[:mid_point])}</div>'
        html += f'<div class="col-md-6">{"".join(config_items[mid_point:])}</div>'
        html += '</div>'
    else:
        html += '<p class="text-muted text-center">No configuration information found in log file</p>'
    
    html += """
                </div>
            </div>
        </div>
    </div>
    
    <!-- Section 4: Issues Found -->
    <div class="row mb-4 font-consistent">
        <div class="col-12">
            <div class="card border-danger">
                <div class="card-header bg-danger text-white" style="font-family: 'Inter', 'Segoe UI', 'Roboto', sans-serif !important;">
                    <i class="fas fa-exclamation-triangle"></i> Section 4: Issues Found
                </div>
                <div class="card-body" style="font-family: 'Inter', 'Segoe UI', 'Roboto', sans-serif !important;">"""
    
    # Critical Issues
    if analysis.get('critical_issues'):
        html += '<h6 class="text-danger"><i class="fas fa-times-circle"></i> Critical Issues</h6><div class="list-group mb-3">'
        for issue in analysis['critical_issues'][:5]:  # Show top 5
            html += f"""
                <div class="list-group-item list-group-item-danger">
                    <div class="d-flex w-100 justify-content-between">
                        <h6 class="mb-1">Line {issue['line']} - {issue['component']}</h6>
                        <small>{issue['timestamp']}</small>
                    </div>
                    <p class="mb-1">{issue['message']}</p>
                </div>"""
        html += '</div>'
    
    # Errors
    if analysis.get('errors'):
        html += '<h6 class="text-warning"><i class="fas fa-exclamation-triangle"></i> Errors</h6><div class="list-group mb-3">'
        for error in analysis['errors'][:5]:  # Show top 5
            html += f"""
                <div class="list-group-item list-group-item-warning">
                    <div class="d-flex w-100 justify-content-between">
                        <h6 class="mb-1">Line {error['line']} - {error['component']}</h6>
                        <small>{error['timestamp']}</small>
                    </div>
                    <p class="mb-1">{error['message']}</p>
                </div>"""
        html += '</div>'
    
    # Known Issues
    if analysis.get('known_issues'):
        html += '<h6 class="text-info"><i class="fas fa-info-circle"></i> Known Issues</h6><div class="list-group mb-3">'
        for issue in analysis['known_issues'][:3]:  # Show top 3
            html += f"""
                <div class="list-group-item list-group-item-info">
                    <div class="d-flex w-100 justify-content-between">
                        <h6 class="mb-1">{issue['issue_type']}</h6>
                        <span class="badge bg-{{"danger" if issue["severity"] == "critical" else "warning" if issue["severity"] == "warning" else "info"}}">{issue['severity'].upper()}</span>
                    </div>
                    <p class="mb-1">{issue['description']}</p>
                    <small class="text-muted">Resolution: {issue['resolution']}</small>
                </div>"""
        html += '</div>'
    
    if not any([analysis.get('critical_issues'), analysis.get('errors'), analysis.get('known_issues')]):
        html += '<p class="text-success text-center"><i class="fas fa-check-circle"></i> No significant issues found in the log file</p>'
    
    html += """
                </div>
            </div>
        </div>
    </div>
    
    <!-- Section 5: Recommendations -->
    <div class="row mb-4 font-consistent">
        <div class="col-12">
            <div class="card border-primary">
                <div class="card-header bg-primary text-white" style="font-family: 'Inter', 'Segoe UI', 'Roboto', sans-serif !important;">
                    <i class="fas fa-lightbulb"></i> Section 5: Recommendations
                </div>
                <div class="card-body" style="font-family: 'Inter', 'Segoe UI', 'Roboto', sans-serif !important;">
                    <ul class="list-unstyled">"""
    
    for rec in analysis.get('recommendations', []):
        html += f'<li class="mb-2"><i class="fas fa-arrow-right text-primary me-2"></i>{rec}</li>'
    
    if not analysis.get('recommendations'):
        html += '<li class="text-muted">No specific recommendations available</li>'
    
    html += """
                    </ul>
                </div>
            </div>
        </div>
    </div>
    
    <!-- Section 6: Component Analysis -->
    <div class="row mb-4 font-consistent">
        <div class="col-12">
            <div class="card border-secondary">
                <div class="card-header bg-secondary text-white" style="font-family: 'Inter', 'Segoe UI', 'Roboto', sans-serif !important;">
                    <i class="fas fa-puzzle-piece"></i> Section 6: Component Analysis
                </div>
                <div class="card-body" style="font-family: 'Inter', 'Segoe UI', 'Roboto', sans-serif !important;">"""
    
    if analysis.get('component_analysis'):
        html += '<div class="table-responsive"><table class="table table-striped">'
        html += '''
                    <thead>
                        <tr>
                            <th>Component</th>
                            <th>Total Entries</th>
                            <th>Errors</th>
                            <th>Warnings</th>
                            <th>Health Status</th>
                        </tr>
                    </thead>
                    <tbody>'''
        
        for component, stats in analysis['component_analysis'].items():
            total = stats['total_entries']
            errors = stats['errors']
            warnings = stats['warnings']
            
            # Calculate health status
            if errors > 0:
                health = 'Poor'
                health_color = 'danger'
            elif warnings > 5:
                health = 'Warning'
                health_color = 'warning'
            else:
                health = 'Good'
                health_color = 'success'
            
            html += f'''
                        <tr>
                            <td>{component}</td>
                            <td>{total}</td>
                            <td><span class="text-danger">{errors}</span></td>
                            <td><span class="text-warning">{warnings}</span></td>
                            <td><span class="badge bg-{health_color}">{health}</span></td>
                        </tr>'''
        
        html += '</tbody></table></div>'
    else:
        html += '<p class="text-muted text-center">No component analysis data available</p>'
    
    html += """
                </div>
            </div>
        </div>
    </div>
    
    <!-- AI Enhancement Footer -->"""
    
    # Add AI/ML/RAG insights if available
    if analysis.get('rag_insights') or analysis.get('ml_insights'):
        html += '''
    <div class="row mb-4 font-consistent">
        <div class="col-12">
            <div class="card border-info">
                <div class="card-header bg-info text-white" style="font-family: 'Inter', 'Segoe UI', 'Roboto', sans-serif !important;">
                    <i class="fas fa-brain"></i> AI Enhanced Analysis
                </div>
                <div class="card-body" style="font-family: 'Inter', 'Segoe UI', 'Roboto', sans-serif !important;">'''
        
        # Safe null checking for AI analysis
        rag_insights = analysis.get('rag_insights') or {}
        if rag_insights.get('ai_analysis'):
            html += f'<h6><i class="fas fa-robot"></i> AI Analysis</h6><p>{rag_insights["ai_analysis"]}</p>'
        
        if analysis.get('ml_insights'):
            html += '<h6><i class="fas fa-chart-line"></i> ML Insights</h6><p>Machine learning patterns and anomaly detection applied</p>'
        
        html += '''
                </div>
            </div>
        </div>
    </div>'''
    
    html += '''
    </div>
    <script>
        // Enhanced version indicator
        console.log("DS Agent Log Analyzer v2 - Enhanced for 40k+ line processing");
    </script>
    '''
    
    return html


def generate_ai_summary_for_ds_logs(analysis: Dict[str, Any]) -> str:
    """Generate practical AI-powered Deep Security Agent Analysis for network administrators"""
    summary = analysis.get('summary', {})
    # Connection Health Analysis Removed - Cloud One Workload Security Connection Health component eliminated
    rag_insights = analysis.get('rag_insights', {})
    
    ai_summary = f"""
    <div class="row mb-4">
        <div class="col-12">
            <div class="card border-info">
                <div class="card-header bg-info text-white">
                    <h5><i class="fas fa-brain"></i>Deep Security Agent Analysis</h5>
                </div>
                <div class="card-body">
                    <div class="alert alert-info">
                        <h6><i class="fa-solid fa-info-circle"></i> Connection Health Analysis Unavailable</h6>
                        <p>Connection health analysis has been removed from this system. Analyzing log patterns, errors, and general DS Agent functionality only.</p>
                    </div>
                    
                    <div class="row mb-3">
                        <div class="col-md-6">
                            <h6><i class="fas fa-chart-bar"></i> Log Analysis Summary</h6>
                            <ul class="list-unstyled">
                                <li><strong>Total Lines:</strong> {summary.get('total_lines', 0):,}</li>
                                <li><strong>Errors:</strong> <span class="text-danger">{summary.get('error_count', 0)}</span></li>
                                <li><strong>Warnings:</strong> <span class="text-warning">{summary.get('warning_count', 0)}</span></li>
                                <li><strong>Critical Issues:</strong> <span class="text-danger">{summary.get('critical_count', 0)}</span></li>
                            </ul>
                        </div>
                        
                        <div class="col-md-6">
                            <h6><i class="fas fa-recommendations"></i> Analysis Focus</h6>
                            <p>This analysis focuses on DS Agent log patterns, error identification, and general troubleshooting guidance without connection health monitoring.</p>
                        </div>
                    </div>
                </div>
            </div>
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
        # IMPORTANT: Check "NO CONFLICTS" first to avoid substring matching bug
        # "NO CONFLICTS DETECTED" contains "CONFLICTS DETECTED" as substring
        for line in lines:
            if "NO CONFLICTS DETECTED" in line.upper():
                conflicts_detected = False
                break
            if "CONFLICTS DETECTED" in line.upper():
                conflicts_detected = True
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
    warning = analysis_data.get('warning', '')
    rag_insights = analysis_data.get('rag_insights')
    security_impact = analysis_data.get('security_impact', {})
    performance_metrics = analysis_data.get('performance_metrics', {})
    
    # Determine status styling
    if status == "error":
        status_color = "#dc3545"
        status_text = "ANALYSIS ERROR"
        status_icon = '<i class="fas fa-exclamation-circle text-danger"></i>'
    elif status == "partial_xml_only":
        status_color = "#fd7e14"
        status_text = "XML-ONLY ANALYSIS (LIMITED DATA)"
        status_icon = '<i class="fas fa-exclamation-triangle text-warning"></i>'
    elif status == "partial_txt_only":
        status_color = "#fd7e14" 
        status_text = "TXT-ONLY ANALYSIS (LIMITED DATA)"
        status_icon = '<i class="fas fa-exclamation-triangle text-warning"></i>'
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
    """
    
    # Add warning section if present
    if warning:
        html += f"""
    <div class="alert alert-warning mb-4 font-consistent" role="alert">
        <h5 class="alert-heading font-consistent" style="font-family: 'Inter', 'Segoe UI', 'Roboto', sans-serif !important;">
            <i class="fas fa-exclamation-triangle me-2"></i>Analysis Limitation Notice
        </h5>
        <p class="mb-0 font-consistent" style="font-family: 'Inter', 'Segoe UI', 'Roboto', sans-serif !important;">{warning}</p>
    </div>
    """
    
    html += f"""
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


def format_ds_agent_offline_results(analysis: Dict[str, Any]) -> str:
    """Format DS Agent Offline analysis results for display"""
    
    # Handle case where analysis failed
    if 'error' in analysis:
        return f"""
        <div class="analysis-container">
            <div class="header">
                <h2>🔴 DS Agent Offline Analysis Failed</h2>
                <div class="error-message">
                    <strong>Error:</strong> {analysis['error']}
                </div>
            </div>
        </div>
        """
    
    summary = analysis.get('summary', {})
    offline_analysis = analysis.get('offline_analysis', {})
    recommendations = analysis.get('recommendations', [])
    
    # Calculate severity levels
    severity = offline_analysis.get('severity_summary', {})
    total_issues = summary.get('offline_issues', 0)
    critical_issues = summary.get('critical_issues', 0)
    
    # Determine overall status
    if critical_issues > 0:
        status_icon = "🔥"
        status_text = "CRITICAL OFFLINE ISSUES DETECTED"
        status_class = "critical"
    elif total_issues > 0:
        status_icon = "⚠️"
        status_text = "OFFLINE ISSUES DETECTED"
        status_class = "warning"
    else:
        status_icon = "✅"
        status_text = "NO CRITICAL OFFLINE ISSUES"
        status_class = "success"
    
    # Build HTML result
    result = f"""
    <div class="analysis-container">
        <div class="header">
            <h2>{status_icon} DS Agent Offline Analysis Results</h2>
            <div class="status-badge {status_class}">
                <strong>{status_text}</strong>
            </div>
        </div>
        
        <div class="summary-section">
            <h3>📊 Analysis Summary</h3>
            <div class="summary-grid">
                <div class="summary-item">
                    <span class="label">File Analyzed:</span>
                    <span class="value">{summary.get('file_path', 'Unknown')}</span>
                </div>
                <div class="summary-item">
                    <span class="label">Total Log Lines:</span>
                    <span class="value">{summary.get('total_lines', 0):,}</span>
                </div>
                <div class="summary-item">
                    <span class="label">Parsed Lines:</span>
                    <span class="value">{summary.get('parsed_lines', 0):,}</span>
                </div>
                <div class="summary-item">
                    <span class="label">Offline Issues Found:</span>
                    <span class="value">{total_issues}</span>
                </div>
            </div>
        </div>
    """
    
    # Add severity breakdown if issues found
    if total_issues > 0:
        result += f"""
        <div class="severity-section">
            <h3>🎯 Issue Severity Breakdown</h3>
            <div class="severity-grid">
                <div class="severity-item critical">
                    <span class="count">{severity.get('critical', 0)}</span>
                    <span class="label">Critical</span>
                </div>
                <div class="severity-item high">
                    <span class="count">{severity.get('high', 0)}</span>
                    <span class="label">High</span>
                </div>
                <div class="severity-item medium">
                    <span class="count">{severity.get('medium', 0)}</span>
                    <span class="label">Medium</span>
                </div>
                <div class="severity-item low">
                    <span class="count">{severity.get('low', 0)}</span>
                    <span class="label">Low</span>
                </div>
            </div>
        </div>
        """
    
    # Add root cause analysis
    root_causes = offline_analysis.get('root_cause_analysis', [])
    if root_causes:
        result += """
        <div class="root-cause-section">
            <h3>🔍 Root Cause Analysis</h3>
            <div class="root-causes">
        """
        
        for cause in root_causes:
            severity_class = cause.get('severity', 'medium')
            result += f"""
                <div class="root-cause-item {severity_class}">
                    <div class="cause-header">
                        <h4>{cause.get('type', 'Unknown').replace('_', ' ').title()}</h4>
                        <span class="severity-badge {severity_class}">{cause.get('severity', 'Unknown').upper()}</span>
                    </div>
                    <div class="cause-description">{cause.get('description', 'No description available')}</div>
                    <div class="cause-impact"><strong>Impact:</strong> {cause.get('impact', 'Unknown impact')}</div>
                    <div class="cause-count"><strong>Occurrences:</strong> {cause.get('count', 0)}</div>
                </div>
            """
        
        result += """
            </div>
        </div>
        """
    
    # Add issue categories
    categories = ['communication_issues', 'service_issues', 'cloud_one_issues', 'system_issues']
    category_titles = {
        'communication_issues': '📡 Communication Issues',
        'service_issues': '⚙️ Service Issues', 
        'cloud_one_issues': '☁️ Cloud One Issues',
        'system_issues': '🖥️ System Issues'
    }
    
    for category in categories:
        issues = offline_analysis.get(category, [])
        if issues:
            result += f"""
            <div class="issues-section">
                <h3>{category_titles.get(category, category.replace('_', ' ').title())}</h3>
                <div class="issues-list">
            """
            
            for issue in issues[:10]:  # Limit to first 10 for display
                severity_class = issue.get('severity', 'medium')
                result += f"""
                    <div class="issue-item {severity_class}">
                        <div class="issue-header">
                            <span class="timestamp">{issue.get('timestamp', 'Unknown time')}</span>
                            <span class="severity-badge {severity_class}">{issue.get('severity', 'Unknown').upper()}</span>
                        </div>
                        <div class="issue-category">{issue.get('category', 'Unknown category').replace('_', ' ').title()}</div>
                        <div class="issue-message">{issue.get('message', 'No message available')[:200]}...</div>
                        <div class="issue-component"><strong>Component:</strong> {issue.get('component', 'Unknown')}</div>
                    </div>
                """
            
            if len(issues) > 10:
                result += f"""
                    <div class="more-issues">
                        <em>... and {len(issues) - 10} more {category.replace('_', ' ')} issues</em>
                    </div>
                """
            
            result += """
                </div>
            </div>
            """
    
    # Add timeline analysis
    timeline_analysis = offline_analysis.get('timeline_analysis', {})
    patterns = timeline_analysis.get('patterns', [])
    
    if patterns:
        result += """
        <div class="timeline-section">
            <h3>📈 Timeline Patterns</h3>
            <div class="patterns-list">
        """
        
        for pattern in patterns:
            result += f"""
                <div class="pattern-item">
                    <span class="pattern-text">{pattern}</span>
                </div>
            """
        
        result += """
            </div>
        </div>
        """
    
    # Add RAG insights if available
    rag_insights = analysis.get('rag_insights')
    if rag_insights and not rag_insights.get('error'):
        result += f"""
        <div class="rag-section">
            <h3>🧠 Enhanced AI Analysis</h3>
            <div class="rag-content">
                {rag_insights}
            </div>
        </div>
        """
    
    result += """
    </div>
    <style>
        .analysis-container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
            text-align: center;
        }
        
        .status-badge {
            display: inline-block;
            padding: 10px 20px;
            border-radius: 5px;
            margin-top: 10px;
        }
        
        .status-badge.critical { background-color: #dc3545; }
        .status-badge.warning { background-color: #ffc107; color: #000; }
        .status-badge.success { background-color: #28a745; }
        
        .summary-section, .severity-section, .root-cause-section, 
        .issues-section, .timeline-section,
        .ml-section, .rag-section {
            background: white;
            border: 1px solid #dee2e6;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 20px;
        }
        
        .summary-grid, .severity-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-top: 15px;
        }
        
        .summary-item, .severity-item {
            padding: 15px;
            background: #f8f9fa;
            border-radius: 5px;
            text-align: center;
        }
        
        .severity-item.critical { border-left: 4px solid #dc3545; }
        .severity-item.high { border-left: 4px solid #fd7e14; }
        .severity-item.medium { border-left: 4px solid #ffc107; }
        .severity-item.low { border-left: 4px solid #20c997; }
        
        .root-cause-item {
            border: 1px solid #dee2e6;
            border-radius: 5px;
            padding: 15px;
            margin-bottom: 15px;
        }
        
        .root-cause-item.critical { border-left: 4px solid #dc3545; }
        .root-cause-item.high { border-left: 4px solid #fd7e14; }
        .root-cause-item.medium { border-left: 4px solid #ffc107; }
        
        .cause-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
        }
        
        .severity-badge {
            padding: 4px 8px;
            border-radius: 3px;
            font-size: 0.8em;
            font-weight: bold;
        }
        
        .severity-badge.critical { background-color: #dc3545; color: white; }
        .severity-badge.high { background-color: #fd7e14; color: white; }
        .severity-badge.medium { background-color: #ffc107; color: black; }
        .severity-badge.low { background-color: #20c997; color: white; }
        
        .issue-item {
            border: 1px solid #dee2e6;
            border-radius: 5px;
            padding: 15px;
            margin-bottom: 10px;
        }
        
        .issue-item.critical { border-left: 4px solid #dc3545; }
        .issue-item.high { border-left: 4px solid #fd7e14; }
        .issue-item.medium { border-left: 4px solid #ffc107; }
        .issue-item.low { border-left: 4px solid #20c997; }
        
        .issue-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 8px;
        }
        
        .timestamp {
            font-family: monospace;
            background: #f8f9fa;
            padding: 2px 6px;
            border-radius: 3px;
        }
        
        .pattern-item {
            background: #e3f2fd;
            padding: 10px;
            border-radius: 5px;
            margin-bottom: 8px;
            border-left: 4px solid #2196f3;
        }
        
        .ml-content, .rag-content {
            background: #f8f9fa;
            padding: 15px;
            border-radius: 5px;
            border-left: 4px solid #007bff;
        }
        
        .more-issues {
            text-align: center;
            padding: 10px;
            color: #6c757d;
            font-style: italic;
        }
        
        .label {
            font-weight: bold;
            color: #495057;
        }
        
        .value {
            color: #007bff;
            font-weight: 500;
        }
        
        .count {
            font-size: 1.5em;
            font-weight: bold;
            display: block;
        }
    </style>
    """
    
    return result


def format_diagnostic_package_results(analysis: Dict[str, Any]) -> str:
    """Format diagnostic package analysis results for display"""
    result = """
    <style>
        .diagnostic-package-container {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 100%;
            margin: 0 auto;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            border-radius: 15px;
        }
        .diagnostic-header {
            background: rgba(255,255,255,0.95);
            border-radius: 10px;
            padding: 25px;
            margin-bottom: 20px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        }
        .diagnostic-title {
            color: #2c3e50;
            font-size: 2.2em;
            font-weight: 700;
            margin-bottom: 10px;
            text-align: center;
        }
        .diagnostic-subtitle {
            color: #34495e;
            font-size: 1.1em;
            text-align: center;
            opacity: 0.8;
        }
        .package-stats {
            background: rgba(255,255,255,0.95);
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 4px 16px rgba(0,0,0,0.1);
        }
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-top: 15px;
        }
        .stat-item {
            background: linear-gradient(45deg, #3498db, #2980b9);
            color: white;
            padding: 15px;
            border-radius: 8px;
            text-align: center;
        }
        .stat-value {
            font-size: 1.8em;
            font-weight: bold;
            display: block;
        }
        .stat-label {
            font-size: 0.9em;
            opacity: 0.9;
        }
        .executive-summary {
            background: rgba(255,255,255,0.95);
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 4px 16px rgba(0,0,0,0.1);
        }
        .summary-header {
            color: #2c3e50;
            font-size: 1.4em;
            font-weight: 600;
            margin-bottom: 15px;
            display: flex;
            align-items: center;
        }
        .summary-content {
            color: #34495e;
            line-height: 1.7;
            margin-bottom: 15px;
        }
        .key-findings {
            background: #f8f9fa;
            border-left: 4px solid #3498db;
            padding: 15px;
            border-radius: 0 8px 8px 0;
        }
        .finding-item {
            margin: 10px 0;
            padding: 8px 0;
            border-bottom: 1px solid #e9ecef;
        }
        .finding-item:last-child {
            border-bottom: none;
        }
        .correlations-section {
            background: rgba(255,255,255,0.95);
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 4px 16px rgba(0,0,0,0.1);
        }
        .correlation-item {
            background: #f1f8ff;
            border: 1px solid #c6e2ff;
            border-radius: 8px;
            padding: 15px;
            margin: 10px 0;
        }
        .correlation-title {
            font-weight: 600;
            color: #0366d6;
            margin-bottom: 8px;
        }
        .correlation-details {
            color: #586069;
            font-size: 0.95em;
        }
        .analysis-section {
            background: rgba(255,255,255,0.95);
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 4px 16px rgba(0,0,0,0.1);
        }
        .section-header {
            color: #2c3e50;
            font-size: 1.3em;
            font-weight: 600;
            margin-bottom: 15px;
            display: flex;
            align-items: center;
        }
        .health-score {
            background: linear-gradient(45deg, #27ae60, #2ecc71);
            color: white;
            padding: 10px 20px;
            border-radius: 20px;
            display: inline-block;
            font-weight: bold;
        }
        .health-score.warning {
            background: linear-gradient(45deg, #f39c12, #e67e22);
        }
        .health-score.critical {
            background: linear-gradient(45deg, #e74c3c, #c0392b);
        }
        .rag-insights {
            background: #fff3cd;
            border: 1px solid #ffeaa7;
            border-radius: 8px;
            padding: 15px;
            margin-top: 15px;
        }
        .knowledge-source {
            background: white;
            border-radius: 6px;
            padding: 10px;
            margin: 8px 0;
            border-left: 3px solid #f39c12;
        }
        .files-analyzed {
            background: rgba(255,255,255,0.95);
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 4px 16px rgba(0,0,0,0.1);
        }
        .file-item {
            background: #f8f9fa;
            border-radius: 6px;
            padding: 12px;
            margin: 8px 0;
            border-left: 4px solid #6c757d;
        }
        .file-name {
            font-weight: 600;
            color: #495057;
        }
        .file-details {
            font-size: 0.9em;
            color: #6c757d;
            margin-top: 5px;
        }
    </style>
    
    <div class="diagnostic-package-container">
        <div class="diagnostic-header">
            <h1 class="diagnostic-title">🔍 Diagnostic Package Analysis</h1>
            <p class="diagnostic-subtitle">Comprehensive Multi-Log Analysis with Cross-Correlation</p>
        </div>
    """
    
    
    # Package statistics - extract from the correct keys
    package_summary = analysis.get('package_summary', {})
    files_analyzed = package_summary.get('total_files_analyzed', 0)
    
    correlation_analysis = analysis.get('correlation_analysis', {})
    correlation_count = 0
    if correlation_analysis:
        correlation_count += len(correlation_analysis.get('timing_correlations', []))
        correlation_count += len(correlation_analysis.get('component_correlations', []))
        correlation_count += len(correlation_analysis.get('issue_correlations', []))
        correlation_count += len(correlation_analysis.get('cross_log_patterns', []))
    
    # Extract duration from package summary
    duration_str = package_summary.get('analysis_duration', '0s')
    try:
        # Parse duration string like "0:00:01.234567" to seconds
        if ':' in duration_str:
            parts = duration_str.split(':')
            if len(parts) == 3:
                hours, minutes, seconds = parts
                analysis_duration = float(hours) * 3600 + float(minutes) * 60 + float(seconds)
            else:
                analysis_duration = float(parts[-1])
        else:
            # Handle simple number or "Xs" format
            analysis_duration = float(duration_str.replace('s', ''))
    except:
        analysis_duration = 0.0
    
    result += f"""
        <div class="package-stats">
            <h3 class="section-header">📊 Package Overview</h3>
            <div class="stats-grid">
                <div class="stat-item">
                    <span class="stat-value">{files_analyzed}</span>
                    <span class="stat-label">Files Analyzed</span>
                </div>
                <div class="stat-item">
                    <span class="stat-value">{correlation_count}</span>
                    <span class="stat-label">Cross-Correlations</span>
                </div>
                <div class="stat-item">
                    <span class="stat-value">{analysis_duration:.1f}s</span>
                    <span class="stat-label">Analysis Duration</span>
                </div>
            </div>
        </div>
    """
    
    # Executive Summary
    executive_summary = analysis.get('executive_summary', {})
    top_level_recommendations = analysis.get('recommendations', [])
    
    # Always show executive summary section, even if empty
    result += """
        <div class="executive-summary">
            <h3 class="summary-header">📋 Executive Summary</h3>
    """
    
    if executive_summary:
        overview = executive_summary.get('overview', '')
        key_findings = executive_summary.get('key_findings', [])
        
        if overview:
            result += f'<div class="summary-content">{overview}</div>'
        
        result += """
            <div class="key-findings">
                <h4>🔑 Key Findings</h4>
        """
        
        if key_findings:
            for finding in key_findings:
                result += f'<div class="finding-item">• {finding}</div>'
        else:
            result += '<div class="finding-item">• Analysis completed successfully</div>'
        
        result += """
            </div>
        """
    else:
        # No executive summary, but show basic info
        result += """
            <div class="summary-content">Diagnostic package analysis has been completed.</div>
            
            <div class="key-findings">
                <h4>🔑 Key Findings</h4>
                <div class="finding-item">• Analysis completed successfully</div>
            </div>
        """
    
    result += "</div>"
    
    # Cross-log correlations
    if correlation_count > 0:
        result += """
            <div class="correlations-section">
                <h3 class="section-header">🔗 Cross-Log Correlations</h3>
        """
        
        # Display different types of correlations from correlation_analysis
        for correlation_type in ['timing_correlations', 'component_correlations', 'issue_correlations', 'cross_log_patterns']:
            correlations_list = correlation_analysis.get(correlation_type, [])
            if correlations_list:
                for correlation in correlations_list:
                    if isinstance(correlation, dict):
                        description = correlation.get('description', str(correlation))
                        correlation_name = correlation_type.replace('_', ' ').title()
                        
                        result += f"""
                            <div class="correlation-item">
                                <div class="correlation-title">{correlation_name}</div>
                                <div class="correlation-details">{description}</div>
                            </div>
                        """
                    else:
                        # Simple string correlation
                        correlation_name = correlation_type.replace('_', ' ').title()
                        result += f"""
                            <div class="correlation-item">
                                <div class="correlation-title">{correlation_name}</div>
                                <div class="correlation-details">{str(correlation)}</div>
                            </div>
                        """
        
        result += "</div>"
    
    # Individual Analysis Results - use correct key
    individual_analyses = analysis.get('individual_analyses', {})
    if individual_analyses:
        result += """
            <div class="analysis-section">
                <h3 class="section-header">📄 Individual File Analysis</h3>
        """
        
        for analysis_type, file_analysis in individual_analyses.items():
            if file_analysis and not isinstance(file_analysis, dict) or 'error' in (file_analysis if isinstance(file_analysis, dict) else {}):
                continue
                
            display_name = analysis_type.replace('_', ' ').title()
            
            if isinstance(file_analysis, dict):
                summary = file_analysis.get('summary', 'Analysis completed')
                if 'analysis_text' in file_analysis:
                    summary = file_analysis['analysis_text'][:200] + "..." if len(file_analysis.get('analysis_text', '')) > 200 else file_analysis.get('analysis_text', 'Analysis completed')
                
                result += f"""
                    <div class="file-item">
                        <div class="file-name">{display_name}</div>
                        <div class="file-details">
                            <strong>Type:</strong> {analysis_type}<br>
                            <strong>Summary:</strong> {summary}
                        </div>
                    </div>
                """
        
        result += "</div>"
    
    # ML Insights
    ml_insights = analysis.get('ml_insights')
    if ml_insights:
        health_score = ml_insights.get('overall_health_score', 0)
        health_class = 'health-score'
        if health_score < 30:
            health_class += ' critical'
        elif health_score < 70:
            health_class += ' warning'
        
        result += f"""
            <div class="analysis-section">
                <h3 class="section-header">🤖 ML-Enhanced Analysis</h3>
                <p><span class="{health_class}">Overall Health Score: {health_score}%</span></p>
        """
        
        component_scores = ml_insights.get('component_health_scores', {})
        if component_scores:
            result += "<h4>Component Health Breakdown:</h4>"
            for component, score in component_scores.items():
                result += f"<p><strong>{component}:</strong> {score}%</p>"
        
        anomalies = ml_insights.get('anomalies_detected', [])
        if anomalies:
            result += "<h4>🚨 Anomalies Detected:</h4>"
            for anomaly in anomalies:
                result += f"<p>• {anomaly}</p>"
        
        result += "</div>"
    
    # RAG Insights
    rag_insights = analysis.get('rag_insights')
    if rag_insights:
        result += """
            <div class="analysis-section">
                <h3 class="section-header">📚 Knowledge Base Insights</h3>
                <div class="rag-insights">
        """
        
        ai_summary = rag_insights.get('ai_summary', '')
        if ai_summary:
            result += f"<p><strong>AI Analysis:</strong> {ai_summary}</p>"
        
        knowledge_sources = rag_insights.get('knowledge_sources_used', [])
        if knowledge_sources:
            result += "<h4>📖 Knowledge Sources Referenced:</h4>"
            for source in knowledge_sources:
                source_name = source.get('source', 'Unknown')
                relevance = source.get('relevance_score', 0)
                result += f"""
                    <div class="knowledge-source">
                        <strong>{source_name}</strong> (Relevance: {relevance:.1f})
                    </div>
                """
        
        result += """
                </div>
            </div>
        """
    
    result += """
    </div>
    """
    
    return result









