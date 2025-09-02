"""
Enhanced User Interface Components for CSDAI Unified Analyzer
Implements improved UX/Navigation with multi-step wizard and session management
"""

import json
import uuid
from datetime import datetime
from typing import Dict, List, Optional
from flask import session as flask_session

class AnalysisSession:
    """Manages analysis sessions with state persistence"""
    
    def __init__(self):
        self.sessions = {}  # In production, this would be stored in Redis/Database
    
    def create_session(self, user_id: str = None) -> str:
        """Create a new analysis session"""
        session_id = str(uuid.uuid4())
        session_data = {
            'session_id': session_id,
            'user_id': user_id or 'anonymous',
            'created_at': datetime.now().isoformat(),
            'current_step': 1,
            'analysis_type': None,
            'uploaded_files': [],
            'configuration': {},
            'results': None,
            'status': 'initialized'
        }
        self.sessions[session_id] = session_data
        return session_id
    
    def get_session(self, session_id: str) -> Optional[Dict]:
        """Get session data"""
        return self.sessions.get(session_id)
    
    def update_session(self, session_id: str, updates: Dict) -> bool:
        """Update session data"""
        if session_id in self.sessions:
            self.sessions[session_id].update(updates)
            self.sessions[session_id]['updated_at'] = datetime.now().isoformat()
            return True
        return False
    
    def save_session_state(self, session_id: str, step: int, data: Dict) -> bool:
        """Save current step state"""
        session_data = self.get_session(session_id)
        if session_data:
            session_data['current_step'] = step
            session_data['status'] = 'in_progress'
            session_data.update(data)
            return True
        return False
    
    def get_user_sessions(self, user_id: str) -> List[Dict]:
        """Get all sessions for a user"""
        return [
            session for session in self.sessions.values() 
            if session['user_id'] == user_id
        ]
    
    def delete_session(self, session_id: str) -> bool:
        """Delete a specific session and clean up its data"""
        if session_id in self.sessions:
            session_data = self.sessions[session_id]
            
            # Clean up temporary files if they exist
            if 'uploaded_files' in session_data:
                for file_info in session_data['uploaded_files']:
                    if 'temp_path' in file_info:
                        try:
                            from security import cleanup_temp_file
                            cleanup_temp_file(file_info['temp_path'])
                        except Exception:
                            pass  # Continue cleanup even if one file fails
            
            # Remove session from memory
            del self.sessions[session_id]
            return True
        return False
    
    def cleanup_all_sessions(self, user_id: str = None) -> int:
        """Clean up all sessions for a user or all sessions if no user specified"""
        sessions_to_delete = []
        
        if user_id:
            sessions_to_delete = [
                session_id for session_id, session_data in self.sessions.items()
                if session_data['user_id'] == user_id
            ]
        else:
            sessions_to_delete = list(self.sessions.keys())
        
        cleaned_count = 0
        for session_id in sessions_to_delete:
            if self.delete_session(session_id):
                cleaned_count += 1
        
        return cleaned_count

class AnalysisWizard:
    """Multi-step analysis wizard controller"""
    
    STEPS = {
        1: {
            'name': 'Analysis Type Selection',
            'description': 'Choose the type of analysis to perform',
            'required_fields': ['analysis_type'],
            'template': 'wizard_step_1.html'
        },
        2: {
            'name': 'File Upload',
            'description': 'Upload your log files for analysis',
            'required_fields': ['files'],
            'template': 'wizard_step_2.html'
        },
        3: {
            'name': 'Ready',
            'description': 'Analysis configuration ready',
            'required_fields': [],
            'template': 'wizard_step_3.html'
        },
        4: {
            'name': 'Processing',
            'description': 'Analysis in progress',
            'required_fields': [],
            'template': 'wizard_step_4.html'
        },
        5: {
            'name': 'Results',
            'description': 'View and export your analysis results',
            'required_fields': [],
            'template': 'wizard_step_5.html'
        }
    }
    
    def __init__(self, session_manager: AnalysisSession):
        self.session_manager = session_manager
    
    def get_step_info(self, step: int) -> Dict:
        """Get information about a specific step"""
        return self.STEPS.get(step, {})
    
    def validate_step(self, session_id: str, step: int, data: Dict) -> tuple:
        """Validate if step can be completed with provided data"""
        step_info = self.get_step_info(step)
        required_fields = step_info.get('required_fields', [])
        
        missing_fields = []
        for field in required_fields:
            if field not in data or not data[field]:
                missing_fields.append(field)
        
        is_valid = len(missing_fields) == 0
        return is_valid, missing_fields
    
    def can_proceed_to_step(self, session_id: str, target_step: int) -> bool:
        """Check if user can proceed to target step"""
        session_data = self.session_manager.get_session(session_id)
        if not session_data:
            return False
        
        current_step = session_data.get('current_step', 1)
        
        # Can always go to current step or previous steps
        if target_step <= current_step:
            return True
        
        # Can only proceed one step at a time
        if target_step == current_step + 1:
            # Validate current step is complete
            step_info = self.get_step_info(current_step)
            required_fields = step_info.get('required_fields', [])
            
            for field in required_fields:
                if field not in session_data or not session_data[field]:
                    return False
            return True
        
        return False
    
    def get_progress_percentage(self, current_step: int) -> int:
        """Calculate progress percentage"""
        total_steps = len(self.STEPS)
        return int((current_step / total_steps) * 100)

class UserGuidance:
    """Provides contextual help and guidance"""
    
    GUIDANCE = {
        'analysis_types': {
            'ds_logs': {
                'title': 'Deep Security Agent Logs',
                'description': 'Analyze ds_agent.log files for errors, warnings, and performance issues',
                'file_requirements': ['ds_agent.log files'],
                'typical_use_cases': [
                    'Troubleshooting agent connectivity issues',
                    'Identifying performance bottlenecks',
                    'Detecting component failures',
                    'Monitoring agent health'
                ],
                'preparation_tips': [
                    'Collect logs from the time period when issues occurred',
                    'Include logs from multiple agents if investigating widespread issues',
                    'Ensure logs are complete and not truncated'
                ]
            },
            'amsp_logs': {
                'title': 'AMSP Anti-Malware Logs',
                'description': 'Analyze AMSP installation and debug logs',
                'file_requirements': ['AMSP-Inst_LocalDebugLog files'],
                'typical_use_cases': [
                    'Diagnosing anti-malware installation failures',
                    'Troubleshooting real-time protection issues',
                    'Analyzing pattern update problems',
                    'Investigating service startup failures'
                ],
                'preparation_tips': [
                    'Collect logs from installation time',
                    'Include both installation and runtime logs',
                    'Note any error messages from Windows Event Viewer'
                ]
            },
            'av_conflicts': {
                'title': 'Antivirus Conflict Detection',
                'description': 'Detect conflicting security software',
                'file_requirements': ['RunningProcess.xml'],
                'typical_use_cases': [
                    'Pre-installation conflict assessment',
                    'Identifying competing security products'
                ],
                'preparation_tips': [
                    'Generate process list during normal system operation',
                    'Include all running processes and services'
                ]
            },
            'resource_analysis': {
                'title': 'Resource Usage Analysis & Exclusion Optimization',
                'description': 'Analyze system performance and identify scan exclusion candidates to optimize Deep Security Anti-Malware performance',
                'file_requirements': ['RunningProcess.xml', 'TopNBusyProcess.txt'],
                'typical_use_cases': [
                    'Performance optimization and scan exclusion recommendations',
                    'Identifying processes causing high CPU usage during scans',
                    'Reducing system resource impact of anti-malware scanning',
                    'Troubleshooting high CPU usage and system slowdown',
                    'Balancing security protection with system performance'
                ],
                'preparation_tips': [
                    'Collect RunningProcess.xml during normal system operation',
                    'Generate TopNBusyProcess.txt during peak usage periods',
                    'Include data from systems experiencing performance issues',
                    'Monitor for extended periods (24-48 hours) for accurate data',
                    'Ensure both files are from the same time period'
                ],
                'file_details': {
                    'RunningProcess.xml': 'Complete list of all running processes and services',
                    'TopNBusyProcess.txt': 'Performance data showing processes with highest scan activity'
                },
                'expected_outcomes': [
                    'Identification of high-impact processes suitable for exclusion',
                    'Security assessment of potential exclusion candidates',
                    'Performance optimization recommendations',
                    'Deep Security policy configuration guidance'
                ]
            },
            'ds_agent_offline': {
                'title': 'DS Agent Offline Analysis',
                'description': 'Specialized analysis for diagnosing Deep Security Agent offline issues',
                'file_requirements': ['ds_agent.log files'],
                'typical_use_cases': [
                    'Troubleshooting agent offline status in manager',
                    'Diagnosing heartbeat failures',
                    'Identifying connectivity and communication issues',
                    'Analyzing Cloud One Workload Security connection problems',
                    'Detecting service crashes and startup failures',
                    'Investigating network and DNS resolution issues'
                ],
                'preparation_tips': [
                    'Collect logs from when agent went offline',
                    'Include logs showing the transition from online to offline',
                    'Gather logs from both agent and manager if possible',
                    'Check network connectivity and firewall rules',
                    'Verify DNS resolution for manager hostname',
                    'Test ports 4119, 4120, 4118 connectivity'
                ],
                'file_details': {
                    'ds_agent.log': 'Deep Security Agent log containing communication, service, and system events'
                },
                'expected_outcomes': [
                    'Root cause analysis of offline issues',
                    'Specific connectivity problem identification',
                    'Service and system issue detection',
                    'Step-by-step resolution recommendations',
                    'Network configuration guidance',
                    'Cloud One connectivity troubleshooting'
                ]
            },
            'diagnostic_package': {
                'title': 'Deep Security Diagnostic Package',
                'description': 'Comprehensive analysis of Deep Security diagnostic packages with multi-log correlation',
                'file_requirements': ['Diagnostic package ZIP files'],
                'typical_use_cases': [
                    'Complete system health assessment',
                    'Multi-component issue correlation',
                    'Comprehensive troubleshooting analysis',
                    'End-to-end Deep Security environment review',
                    'Complex issue investigation with multiple logs',
                    'Performance and configuration optimization'
                ],
                'preparation_tips': [
                    'Generate diagnostic package from Deep Security Manager',
                    'Include diagnostic data from the problem timeframe',
                    'Ensure package contains all relevant log files',
                    'Use fresh diagnostic packages (within 7 days)',
                    'Include both agent and manager diagnostic data if available'
                ],
                'file_details': {
                    'diagnostic_package.zip': 'Complete diagnostic package from Deep Security Manager containing multiple log files and configuration data'
                },
                'expected_outcomes': [
                    'Comprehensive multi-log analysis with correlation',
                    'System-wide health assessment',
                    'Component interaction analysis',
                    'Performance optimization recommendations',
                    'Configuration review and recommendations',
                    'AI-enhanced pattern detection across multiple logs'
                ]
            }
        },
        'common_issues': {
            'file_upload': [
                'Ensure files are in correct format (log, txt, xml)',
                'Check file size limits (max 100MB per file)',
                'Verify files are not corrupted or empty',
                'Use recent files (within last 30 days for best results)'
            ],
            'analysis_errors': [
                'Verify your OpenAI API key is configured correctly',
                'Check network connectivity',
                'Ensure uploaded files contain valid log data',
                'Try with smaller file sizes if analysis fails'
            ]
        }
    }
    
    def get_analysis_guidance(self, analysis_type: str) -> Dict:
        """Get guidance for specific analysis type"""
        return self.GUIDANCE['analysis_types'].get(analysis_type, {})
    
    def get_troubleshooting_tips(self, issue_type: str) -> List[str]:
        """Get troubleshooting tips for common issues"""
        return self.GUIDANCE['common_issues'].get(issue_type, [])

# Global instances
session_manager = AnalysisSession()
wizard = AnalysisWizard(session_manager)
guidance = UserGuidance()
