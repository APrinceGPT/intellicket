"""
Simple Session Manager for CSDAIv2 Backend
Lightweight session management without UI components
"""

import json
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any

class SimpleSessionManager:
    """Lightweight session manager for backend-only operations"""
    
    def __init__(self):
        self.sessions = {}  # In production, this would be stored in Redis/Database
    
    def create_session(self, user_id: str = None) -> str:
        """Create a new analysis session"""
        session_id = str(uuid.uuid4())
        session_data = {
            'session_id': session_id,
            'user_id': user_id or 'anonymous',
            'created_at': datetime.now().isoformat(),
            'analysis_type': None,
            'uploaded_files': [],
            'results': None,
            'status': 'initialized',
            'progress_percentage': 0,
            'progress_message': '',
            'analysis_stage': 'ready'
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
    
    def store_results(self, session_id: str, results: Any) -> bool:
        """Store analysis results"""
        if session_id in self.sessions:
            self.sessions[session_id]['results'] = results
            self.sessions[session_id]['status'] = 'completed'
            self.sessions[session_id]['updated_at'] = datetime.now().isoformat()
            return True
        return False
    
    def update_progress(self, session_id: str, stage: str, message: str, percentage: int) -> bool:
        """Update progress information"""
        if session_id in self.sessions:
            self.sessions[session_id].update({
                'analysis_stage': stage,
                'progress_message': message,
                'progress_percentage': percentage,
                'status': 'processing' if percentage < 100 else 'completed',
                'updated_at': datetime.now().isoformat()
            })
            return True
        return False
    
    def delete_session(self, session_id: str) -> bool:
        """Delete a specific session"""
        if session_id in self.sessions:
            del self.sessions[session_id]
            return True
        return False
    
    def cleanup_old_sessions(self, hours: int = 24) -> int:
        """Clean up old sessions"""
        from datetime import timedelta
        cutoff_time = datetime.now() - timedelta(hours=hours)
        sessions_to_delete = []
        
        for session_id, session_data in self.sessions.items():
            try:
                created_at = datetime.fromisoformat(session_data['created_at'])
                if created_at < cutoff_time:
                    sessions_to_delete.append(session_id)
            except (ValueError, KeyError):
                # If we can't parse the date, delete the session
                sessions_to_delete.append(session_id)
        
        cleaned_count = 0
        for session_id in sessions_to_delete:
            if self.delete_session(session_id):
                cleaned_count += 1
        
        return cleaned_count
    
    def get_all_sessions(self) -> Dict[str, Dict]:
        """Get all sessions - required by admin interface"""
        return self.sessions.copy()
    
    def get_session_statistics(self) -> Dict[str, Any]:
        """Get session statistics for admin dashboard"""
        total_sessions = len(self.sessions)
        completed_sessions = len([s for s in self.sessions.values() if s.get('status') == 'completed'])
        processing_sessions = len([s for s in self.sessions.values() if s.get('status') == 'processing'])
        failed_sessions = len([s for s in self.sessions.values() if s.get('status') == 'error'])
        
        # Calculate statistics by analyzer type
        analyzer_stats = {}
        for session in self.sessions.values():
            analyzer_type = session.get('analysis_type', 'unknown')
            if analyzer_type not in analyzer_stats:
                analyzer_stats[analyzer_type] = {
                    'total': 0,
                    'completed': 0,
                    'failed': 0,
                    'files_processed': 0,
                    'total_size': 0
                }
            
            stats = analyzer_stats[analyzer_type]
            stats['total'] += 1
            
            if session.get('status') == 'completed':
                stats['completed'] += 1
            elif session.get('status') == 'error':
                stats['failed'] += 1
            
            # Count files and size
            files = session.get('uploaded_files', [])
            stats['files_processed'] += len(files)
            for file_info in files:
                size = file_info.get('size', 0) or file_info.get('size_bytes', 0)
                stats['total_size'] += size
        
        return {
            'total_sessions': total_sessions,
            'completed_sessions': completed_sessions,
            'processing_sessions': processing_sessions,
            'failed_sessions': failed_sessions,
            'success_rate': completed_sessions / total_sessions if total_sessions > 0 else 0,
            'analyzer_statistics': analyzer_stats
        }

# Global instance
simple_session_manager = SimpleSessionManager()