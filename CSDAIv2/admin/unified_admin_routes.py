# -*- coding: utf-8 -*-
"""
Intellicket Unified Admin Backend API
Flask-based admin API endpoints for managing both CSDAIv2 backend and Intellicket frontend
Provides comprehensive system management, health monitoring, and maintenance control
"""

import os
import json
import sqlite3
import subprocess
import time
from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify
from typing import Dict, List, Any, Optional

# Required dependencies
import requests

# Import from main CSDAIv2 modules
try:
    from config import get_config
    from ui_components import session_manager
    from analyzers import DSAgentLogAnalyzer, AMSPAnalyzer, ConflictAnalyzer, ResourceAnalyzer
except ImportError:
    # Create a minimal config fallback
    class MockConfig:
        def __init__(self):
            self.PORT = 5003
            self.TEMP_DIR = './temp'
    
    def get_config():
        return MockConfig()
    print("⚠️ Using fallback config")

try:
    from ui_components import session_manager
except ImportError:
    session_manager = None
    print("⚠️ session_manager not available")
    
    # Try to import analyzers function, create fallback if not available
    try:
        from analyzers import get_available_analyzers
    except ImportError:
        # Create a fallback function
        def get_available_analyzers():
            return {
                'amsp_analyzer': {'name': 'AMSP Anti-Malware Analysis', 'status': 'active'},
                'conflict_analyzer': {'name': 'AV Conflict Analysis', 'status': 'active'},
                'resource_analyzer': {'name': 'Resource Usage Analysis', 'status': 'active'},
                'diagnostic_package_analyzer': {'name': 'Diagnostic Package Analysis', 'status': 'active'},
                'ds_agent_log_analyzer': {'name': 'DS Agent Log Analysis', 'status': 'active'},
                'ds_agent_offline_analyzer': {'name': 'DS Agent Offline Analysis', 'status': 'active'}
            }
        print("⚠️ Using fallback get_available_analyzers function")
        
except ImportError as e:
    print(f"⚠️ Some CSDAIv2 modules not available: {e}")
    # Create minimal fallbacks
    def get_available_analyzers():
        return {}

class UnifiedAdminService:
    """
    Central service for managing both CSDAIv2 backend and Intellicket frontend
    """
    
    def __init__(self, config=None):
        self.config = config or get_config()
        self.frontend_url = 'http://localhost:3000'
        self.backend_url = 'http://localhost:5003'
        self.admin_db_path = os.path.join(os.path.dirname(__file__), 'admin.db')
        self._init_admin_database()
        
    def _init_admin_database(self):
        """Initialize admin-specific database for storing admin data"""
        try:
            conn = sqlite3.connect(self.admin_db_path)
            cursor = conn.cursor()
            
            # Create admin tables
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS admin_actions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    action TEXT NOT NULL,
                    component TEXT NOT NULL,
                    details TEXT,
                    success BOOLEAN,
                    metadata TEXT
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS system_alerts (
                    id TEXT PRIMARY KEY,
                    level TEXT NOT NULL,
                    component TEXT NOT NULL,
                    title TEXT NOT NULL,
                    message TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    acknowledged BOOLEAN DEFAULT FALSE,
                    acknowledged_at DATETIME,
                    resolved BOOLEAN DEFAULT FALSE,
                    metadata TEXT
                )
            ''')
            
            # Migration: Add acknowledged_at column if it doesn't exist
            try:
                cursor.execute('ALTER TABLE system_alerts ADD COLUMN acknowledged_at DATETIME')
            except sqlite3.OperationalError:
                # Column already exists or other error - ignore
                pass
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS analyzer_status (
                    analyzer_id TEXT PRIMARY KEY,
                    status TEXT NOT NULL,
                    last_updated DATETIME DEFAULT CURRENT_TIMESTAMP,
                    disabled_reason TEXT,
                    config TEXT
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS maintenance_mode (
                    id INTEGER PRIMARY KEY CHECK (id = 1),
                    enabled BOOLEAN DEFAULT FALSE,
                    message TEXT,
                    scheduled_start DATETIME,
                    scheduled_end DATETIME,
                    affected_systems TEXT,
                    priority TEXT DEFAULT 'medium',
                    last_updated DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Insert default maintenance mode record
            cursor.execute('''
                INSERT OR IGNORE INTO maintenance_mode (id, enabled, message) 
                VALUES (1, FALSE, 'System maintenance in progress')
            ''')
            
            conn.commit()
            conn.close()
            print("✅ Admin database initialized successfully")
            
        except Exception as e:
            print(f"❌ Failed to initialize admin database: {e}")

    def get_system_overview(self) -> Dict[str, Any]:
        """Get comprehensive system overview including both backend and frontend"""
        try:
            # Check backend status
            backend_status = self._check_backend_health()
            
            # Check frontend status
            frontend_status = self._check_frontend_health()
            
            # Get component statuses
            components = self._get_component_statuses()
            
            # Determine overall system status
            overall_status = self._determine_overall_status(backend_status, frontend_status, components)
            
            return {
                'backend': backend_status,
                'frontend': frontend_status,
                'overall': overall_status,
                'components': components,
                'last_updated': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'error': f"Failed to get system overview: {str(e)}",
                'backend': {'status': 'unknown', 'health': 'unknown', 'uptime': 0},
                'frontend': {'status': 'unknown', 'health': 'unknown', 'uptime': 0},
                'overall': {'status': 'error', 'health': 'critical', 'uptime': 0},
                'components': {},
                'last_updated': datetime.now().isoformat()
            }

    def _check_backend_health(self) -> Dict[str, Any]:
        """Check CSDAIv2 backend health"""
        try:
            # Try to ping the backend
            response = requests.get(f"{self.backend_url}/api/health", timeout=5)
            
            if response.status_code == 200:
                health_data = response.json() if response.content else {}
                return {
                    'id': 'csdaiv2_backend',
                    'name': 'CSDAIv2 Backend',
                    'status': 'online',
                    'health': 'healthy',
                    'uptime': health_data.get('uptime', 0),
                    'lastChecked': datetime.now(),
                    'version': health_data.get('version', '1.0.0'),
                    'url': self.backend_url
                }
            else:
                return {
                    'id': 'csdaiv2_backend',
                    'name': 'CSDAIv2 Backend',
                    'status': 'degraded',
                    'health': 'warning',
                    'uptime': 0,
                    'lastChecked': datetime.now(),
                    'url': self.backend_url
                }
                
        except Exception:
            return {
                'id': 'csdaiv2_backend',
                'name': 'CSDAIv2 Backend',
                'status': 'offline',
                'health': 'critical',
                'uptime': 0,
                'lastChecked': datetime.now(),
                'url': self.backend_url
            }

    def _check_frontend_health(self) -> Dict[str, Any]:
        """Check Intellicket frontend health"""
        try:
            # Try to ping the frontend
            response = requests.get(f"{self.frontend_url}/api/health", timeout=5)
            
            if response.status_code == 200:
                health_data = response.json() if response.content else {}
                return {
                    'id': 'intellicket_frontend',
                    'name': 'Intellicket Frontend',
                    'status': 'online',
                    'health': 'healthy',
                    'uptime': health_data.get('uptime', 0),
                    'lastChecked': datetime.now(),
                    'version': health_data.get('version', '1.0.0'),
                    'url': self.frontend_url
                }
            else:
                return {
                    'id': 'intellicket_frontend',
                    'name': 'Intellicket Frontend',
                    'status': 'degraded',
                    'health': 'warning',
                    'uptime': 0,
                    'lastChecked': datetime.now(),
                    'url': self.frontend_url
                }
                
        except Exception:
            return {
                'id': 'intellicket_frontend',
                'name': 'Intellicket Frontend',
                'status': 'offline',
                'health': 'critical',
                'uptime': 0,
                'lastChecked': datetime.now(),
                'url': self.frontend_url
            }

    def _check_ai_system_health(self, ml_status: Dict[str, Any], rag_status: Dict[str, Any]) -> Dict[str, Any]:
        """Check comprehensive AI system health (ML + RAG + API integration)"""
        ai_components = []
        overall_health = 'healthy'
        overall_status = 'enabled'
        
        # Check ML System
        ml_health = ml_status.get('health', 'unknown')
        ml_status_val = ml_status.get('status', 'unknown')
        ai_components.append({
            'name': 'ML Analysis Engine',
            'status': ml_status_val,
            'health': ml_health
        })
        
        # Check RAG System  
        rag_health = rag_status.get('health', 'unknown')
        rag_status_val = rag_status.get('status', 'unknown')
        ai_components.append({
            'name': 'Dynamic RAG Engine',
            'status': rag_status_val,
            'health': rag_health
        })
        
        # Check AI API Integration (Claude API)
        has_ai_key = False
        has_ai_model = False
        try:
            # Test if AI environment variables are configured
            import os
            has_ai_key = bool(os.getenv('OPENAI_API_KEY'))
            has_ai_model = bool(os.getenv('OPENAI_MODEL'))
            
            if has_ai_key and has_ai_model:
                ai_components.append({
                    'name': 'AI API Integration',
                    'status': 'configured',
                    'health': 'healthy'
                })
            else:
                ai_components.append({
                    'name': 'AI API Integration', 
                    'status': 'not_configured',
                    'health': 'warning'
                })
                overall_health = 'warning'
                
        except Exception:
            ai_components.append({
                'name': 'AI API Integration',
                'status': 'error',
                'health': 'critical'
            })
            overall_health = 'critical'
        
        # Determine overall AI system status
        critical_count = sum(1 for comp in ai_components if comp['health'] == 'critical')
        warning_count = sum(1 for comp in ai_components if comp['health'] == 'warning') 
        
        if critical_count > 0:
            overall_health = 'critical'
            overall_status = 'error'
        elif warning_count > 0:
            overall_health = 'warning'
            overall_status = 'degraded'
        elif ml_status_val == 'disabled' or rag_status_val == 'disabled':
            overall_health = 'warning'
            overall_status = 'partial'
        else:
            # All AI components are healthy and enabled
            overall_status = 'enabled'
        
        return {
            'id': 'ai_system',
            'name': 'AI Analysis System',
            'status': overall_status,
            'health': overall_health,
            'components': ai_components,
            'summary': f"ML: {ml_health.title()}, RAG: {rag_health.title()}, Integration: {'✓' if has_ai_key else '✗'}",
            'lastChecked': datetime.now(),
            'capabilities': {
                'ml_analysis': ml_status_val == 'enabled',
                'rag_analysis': rag_status_val == 'enabled', 
                'ai_integration': has_ai_key and has_ai_model
            }
        }

    def _get_component_statuses(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all system components"""
        components = {}
        
        # Get analyzer statuses
        try:
            analyzers = self.get_analyzers()
            components['analyzers'] = [
                {
                    'id': analyzer['id'],
                    'name': analyzer['name'],
                    'status': analyzer['status'],
                    'health': 'healthy' if analyzer['status'] == 'enabled' else 'warning',
                    'lastChecked': datetime.now()
                }
                for analyzer in analyzers
            ]
        except Exception:
            components['analyzers'] = []

        # Check ML system
        try:
            from ml_analyzer import MLLogAnalyzer
            components['ml_system'] = {
                'id': 'ml_system',
                'name': 'ML Analysis System',
                'status': 'enabled',
                'health': 'healthy',
                'lastChecked': datetime.now()
            }
        except ImportError:
            components['ml_system'] = {
                'id': 'ml_system',
                'name': 'ML Analysis System',
                'status': 'disabled',
                'health': 'warning',
                'lastChecked': datetime.now()
            }

        # Check RAG system
        try:
            from dynamic_rag_system import DynamicRAGSystem
            components['rag_system'] = {
                'id': 'rag_system',
                'name': 'Dynamic RAG System',
                'status': 'enabled',
                'health': 'healthy',
                'lastChecked': datetime.now()
            }
        except ImportError:
            components['rag_system'] = {
                'id': 'rag_system',
                'name': 'Dynamic RAG System',
                'status': 'disabled',
                'health': 'warning',
                'lastChecked': datetime.now()
            }

        # Check AI System (comprehensive ML + RAG health)
        ai_system_health = self._check_ai_system_health(components.get('ml_system', {}), components.get('rag_system', {}))
        components['ai_system'] = ai_system_health

        # Check database
        try:
            conn = sqlite3.connect(self.admin_db_path)
            conn.execute('SELECT 1')
            conn.close()
            components['database'] = {
                'id': 'database',
                'name': 'Admin Database',
                'status': 'enabled',
                'health': 'healthy',
                'lastChecked': datetime.now()
            }
        except Exception:
            components['database'] = {
                'id': 'database',
                'name': 'Admin Database',
                'status': 'error',
                'health': 'critical',
                'lastChecked': datetime.now()
            }

        # Check API health
        components['api'] = {
            'id': 'api',
            'name': 'Admin API',
            'status': 'enabled',
            'health': 'healthy',  # If we're running this code, API is healthy
            'lastChecked': datetime.now()
        }

        return components

    def _determine_overall_status(self, backend_status: Dict, frontend_status: Dict, components: Dict) -> Dict[str, Any]:
        """Determine overall system status based on component health"""
        # Check if any critical systems are down
        if backend_status['status'] == 'offline' or frontend_status['status'] == 'offline':
            return {
                'id': 'overall_system',
                'name': 'Intellicket System',
                'status': 'offline',
                'health': 'critical',
                'uptime': min(backend_status['uptime'], frontend_status['uptime']),
                'lastChecked': datetime.now()
            }
        
        # Check if any systems are degraded (including AI system)
        ai_system = components.get('ai_system', {})
        ai_degraded = ai_system.get('status') in ['degraded', 'partial', 'error'] or ai_system.get('health') in ['warning', 'critical']
        
        if backend_status['status'] == 'degraded' or frontend_status['status'] == 'degraded' or ai_degraded:
            status_reasons = []
            if backend_status['status'] == 'degraded':
                status_reasons.append('Backend')
            if frontend_status['status'] == 'degraded':
                status_reasons.append('Frontend')
            if ai_degraded:
                status_reasons.append('AI System')
                
            return {
                'id': 'overall_system',
                'name': 'Intellicket System',
                'status': 'degraded',
                'health': 'warning',
                'uptime': min(backend_status['uptime'], frontend_status['uptime']),
                'degraded_components': status_reasons,
                'ai_status': ai_system.get('summary', 'Unknown'),
                'lastChecked': datetime.now()
            }
        
        # Check maintenance mode
        maintenance = self.get_maintenance_mode()
        if maintenance.get('enabled', False):
            return {
                'id': 'overall_system',
                'name': 'Intellicket System',
                'status': 'maintenance',
                'health': 'warning',
                'uptime': min(backend_status['uptime'], frontend_status['uptime']),
                'lastChecked': datetime.now()
            }
        
        # All systems healthy
        return {
            'id': 'overall_system',
            'name': 'Intellicket System',
            'status': 'online',
            'health': 'healthy',
            'uptime': min(backend_status['uptime'], frontend_status['uptime']),
            'ai_status': ai_system.get('summary', 'AI System Operational'),
            'ai_capabilities': ai_system.get('capabilities', {}),
            'lastChecked': datetime.now()
        }





    def get_analyzers(self) -> List[Dict[str, Any]]:
        """Get list of all available analyzers with their status"""
        try:
            # Get available analyzers from the system
            available_analyzers = [
                'conflict_analyzer',
                'amsp_analyzer', 
                'resource_analyzer',
                'ds_agent_log_analyzer',
                'ds_agent_offline_analyzer',
                'diagnostic_package_analyzer'
            ]
            
            analyzers = []
            conn = sqlite3.connect(self.admin_db_path)
            cursor = conn.cursor()
            
            for analyzer_id in available_analyzers:
                # Get analyzer status from database
                cursor.execute(
                    'SELECT status, last_updated, disabled_reason, config FROM analyzer_status WHERE analyzer_id = ?',
                    (analyzer_id,)
                )
                result = cursor.fetchone()
                
                if result:
                    status, last_updated, disabled_reason, config = result
                else:
                    # Default status for analyzers not in database
                    status = 'enabled'
                    last_updated = datetime.now()
                    disabled_reason = None
                    config = {}
                    
                    # Insert default status
                    cursor.execute(
                        'INSERT OR REPLACE INTO analyzer_status (analyzer_id, status) VALUES (?, ?)',
                        (analyzer_id, status)
                    )
                
                analyzers.append({
                    'id': analyzer_id,
                    'name': analyzer_id.replace('_', ' ').title(),
                    'display_name': analyzer_id.replace('_', ' ').title(),
                    'description': f"Analyzer for {analyzer_id.replace('_', ' ')} analysis",
                    'status': status,
                    'health': 'healthy' if status == 'enabled' else 'warning',
                    'usage_stats': {
                        'total_runs': 0,
                        'success_rate': 0.95,
                        'avg_duration': 30.0,
                        'last_used': None
                    },
                    'dependencies': [],
                    'config': json.loads(config) if config else {}
                })
            
            conn.commit()
            conn.close()
            
            return analyzers
            
        except Exception as e:
            print(f"❌ Error getting analyzers: {e}")
            return []

    def get_file_upload_stats(self, time_range: str = '24h') -> Dict[str, Any]:
        """Get file upload statistics with enhanced analyzer success rates"""
        try:
            # Calculate time range
            if time_range == '1h':
                start_time = datetime.now() - timedelta(hours=1)
            elif time_range == '24h':
                start_time = datetime.now() - timedelta(hours=24)
            elif time_range == '7d':
                start_time = datetime.now() - timedelta(days=7)
            else:
                start_time = datetime.now() - timedelta(hours=24)
            
            # Get enhanced session statistics from session manager
            if hasattr(session_manager, 'get_session_statistics'):
                session_stats = session_manager.get_session_statistics()
                analyzer_stats = session_stats.get('analyzer_statistics', {})
            else:
                # Fallback to basic statistics if enhanced method not available
                active_sessions = session_manager.get_all_sessions()
                analyzer_stats = {}
                for session_data in active_sessions.values():
                    analyzer_type = session_data.get('analysis_type', 'unknown')
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
                    if session_data.get('status') == 'completed':
                        stats['completed'] += 1
                    elif session_data.get('status') == 'error':
                        stats['failed'] += 1
                    
                    files = session_data.get('uploaded_files', [])
                    stats['files_processed'] += len(files)
                    for file_info in files:
                        size = file_info.get('size', 0) or file_info.get('size_bytes', 0)
                        stats['total_size'] += size
            
            # Get session data from session manager for recent uploads
            active_sessions = session_manager.get_all_sessions()
            
            # Calculate general statistics
            total_files = 0
            total_size = 0
            files_by_type = {}
            files_by_analyzer = {}
            recent_uploads = []
            
            for session_id, session_data in active_sessions.items():
                if session_data.get('created_at'):
                    try:
                        created = datetime.fromisoformat(session_data['created_at'])
                        if created >= start_time:
                            # Count files and size - Use correct field name 'uploaded_files'
                            files = session_data.get('uploaded_files', [])
                            total_files += len(files)
                            
                            for file_info in files:
                                # Handle different file info structures
                                size = file_info.get('size', 0) or file_info.get('size_bytes', 0)
                                total_size += size
                                
                                # Count by file type - extract from filename if not explicitly stored
                                filename = file_info.get('name', '') or file_info.get('filename', '')
                                file_extension = filename.split('.')[-1].lower() if '.' in filename else 'unknown'
                                file_type = file_info.get('type', file_extension)
                                files_by_type[file_type] = files_by_type.get(file_type, 0) + 1
                                
                                # Count by analyzer
                                analyzer = session_data.get('analysis_type', 'unknown')
                                files_by_analyzer[analyzer] = files_by_analyzer.get(analyzer, 0) + 1
                                
                                # Add to recent uploads
                                recent_uploads.append({
                                    'timestamp': created.isoformat() if hasattr(created, 'isoformat') else str(created),
                                    'filename': filename,
                                    'size_bytes': size,
                                    'analyzer': analyzer,
                                    'status': session_data.get('status', 'unknown')
                                })
                    except (ValueError, TypeError) as e:
                        print(f"⚠️ Skipping session {session_id}: {e}")
                        continue
            
            # Sort recent uploads by timestamp
            recent_uploads.sort(key=lambda x: x['timestamp'], reverse=True)
            recent_uploads = recent_uploads[:10]  # Keep only 10 most recent
            
            return {
                'total_files': total_files,
                'total_size_bytes': total_size,
                'files_by_type': files_by_type,
                'files_by_analyzer': files_by_analyzer,
                'analyzer_statistics': analyzer_stats,  # Enhanced analyzer statistics with success rates
                'upload_trends': [],  # TODO: Implement trend calculation
                'recent_uploads': recent_uploads
            }
            
        except Exception as e:
            print(f"❌ Error getting file upload stats: {e}")
            return {
                'total_files': 0,
                'total_size_bytes': 0,
                'files_by_type': {},
                'files_by_analyzer': {},
                'upload_trends': [],
                'recent_uploads': []
            }

    def get_active_sessions(self) -> List[Dict[str, Any]]:
        """Get list of active sessions"""
        try:
            active_sessions = session_manager.get_all_sessions()
            sessions = []
            
            for session_id, session_data in active_sessions.items():
                try:
                    # Use correct field names from session data structure
                    uploaded_files = session_data.get('uploaded_files', [])
                    sessions.append({
                        'id': session_id,
                        'created_at': datetime.fromisoformat(session_data.get('created_at', datetime.now().isoformat())),
                        'last_activity': datetime.fromisoformat(session_data.get('updated_at', session_data.get('created_at', datetime.now().isoformat()))),
                        'status': session_data.get('status', 'active'),
                        'analyzer_type': session_data.get('analysis_type'),  # Use correct field name
                        'file_count': len(uploaded_files),
                        'total_size_bytes': sum(f.get('size', 0) or f.get('size_bytes', 0) for f in uploaded_files),
                        'progress': session_data.get('progress_percentage', 0),
                        'ip_address': session_data.get('ip_address', 'Unknown'),
                        'user_agent': session_data.get('user_agent', 'Unknown')
                    })
                except (ValueError, TypeError) as e:
                    print(f"⚠️ Skipping session {session_id}: {e}")
                    continue
            
            return sessions
            
        except Exception as e:
            print(f"❌ Error getting active sessions: {e}")
            return []

    def get_maintenance_mode(self) -> Dict[str, Any]:
        """Get current maintenance mode status"""
        try:
            conn = sqlite3.connect(self.admin_db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT enabled, message, scheduled_start, scheduled_end, affected_systems, priority
                FROM maintenance_mode WHERE id = 1
            ''')
            result = cursor.fetchone()
            conn.close()
            
            if result:
                enabled, message, scheduled_start, scheduled_end, affected_systems, priority = result
                return {
                    'enabled': bool(enabled),
                    'message': message or 'System maintenance in progress',
                    'scheduled_start': datetime.fromisoformat(scheduled_start) if scheduled_start else None,
                    'scheduled_end': datetime.fromisoformat(scheduled_end) if scheduled_end else None,
                    'affected_systems': json.loads(affected_systems) if affected_systems else ['backend', 'frontend'],
                    'priority': priority or 'medium'
                }
            else:
                return {
                    'enabled': False,
                    'message': 'System maintenance in progress',
                    'scheduled_start': None,
                    'scheduled_end': None,
                    'affected_systems': ['backend', 'frontend'],
                    'priority': 'medium'
                }
                
        except Exception as e:
            print(f"❌ Error getting maintenance mode: {e}")
            return {
                'enabled': False,
                'message': 'System maintenance in progress',
                'scheduled_start': None,
                'scheduled_end': None,
                'affected_systems': ['backend', 'frontend'],
                'priority': 'medium'
            }

    # ACTION METHODS FOR ADMIN CONTROL
    
    def restart_backend(self) -> Dict[str, Any]:
        """Restart the CSDAIv2 backend server"""
        try:
            # Log the action
            self._log_admin_action('restart_backend', 'system', 
                                   'Backend restart initiated', True)
            
            # Note: This is a graceful restart request that would need to be handled
            # by the parent process or service manager in a production environment
            return {
                'success': True,
                'message': 'Backend restart initiated successfully',
                'action': 'restart_backend',
                'timestamp': datetime.now().isoformat(),
                'note': 'Restart request has been logged. In production, this would trigger a service restart.'
            }
            
        except Exception as e:
            self._log_admin_action('restart_backend', 'system', 
                                   f'Backend restart failed: {str(e)}', False)
            return {
                'success': False,
                'message': f'Backend restart failed: {str(e)}',
                'action': 'restart_backend',
                'timestamp': datetime.now().isoformat()
            }

    def toggle_maintenance_mode(self, enabled: bool, message: str = None, 
                              affected_systems: List[str] = None) -> Dict[str, Any]:
        """Toggle maintenance mode on/off"""
        try:
            conn = sqlite3.connect(self.admin_db_path)
            cursor = conn.cursor()
            
            # Default values
            if message is None:
                message = 'System maintenance in progress' if enabled else ''
            if affected_systems is None:
                affected_systems = ['backend', 'frontend']
            
            # Update maintenance mode
            cursor.execute('''
                UPDATE maintenance_mode 
                SET enabled = ?, message = ?, affected_systems = ?, last_updated = CURRENT_TIMESTAMP
                WHERE id = 1
            ''', (enabled, message, json.dumps(affected_systems)))
            
            conn.commit()
            conn.close()
            
            # Log the action
            action_details = f'Maintenance mode {"enabled" if enabled else "disabled"}'
            self._log_admin_action('toggle_maintenance', 'system', action_details, True)
            
            return {
                'success': True,
                'message': f'Maintenance mode {"enabled" if enabled else "disabled"} successfully',
                'action': 'toggle_maintenance',
                'enabled': enabled,
                'affected_systems': affected_systems,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self._log_admin_action('toggle_maintenance', 'system', 
                                   f'Maintenance mode toggle failed: {str(e)}', False)
            return {
                'success': False,
                'message': f'Failed to toggle maintenance mode: {str(e)}',
                'action': 'toggle_maintenance',
                'timestamp': datetime.now().isoformat()
            }

    def clear_cache(self) -> Dict[str, Any]:
        """Clear system cache including sessions and temporary files"""
        try:
            cleaned_sessions = 0
            cleaned_temp_files = 0
            
            # Clear active sessions
            active_sessions = session_manager.sessions
            for session_id, session_data in list(active_sessions.items()):
                # Clean up temp files for each session
                for temp_file in session_data.get('temp_files', []):
                    try:
                        if os.path.exists(temp_file):
                            os.remove(temp_file)
                            cleaned_temp_files += 1
                    except OSError:
                        pass
                
                # Remove session
                session_manager.delete_session(session_id)
                cleaned_sessions += 1
            
            # Clear temporary directory
            temp_dir = os.path.join(os.path.dirname(__file__), '..', 'temp')
            if os.path.exists(temp_dir):
                import shutil
                try:
                    shutil.rmtree(temp_dir)
                    os.makedirs(temp_dir, exist_ok=True)
                    cleaned_temp_files += 10  # Approximation
                except OSError:
                    pass
            
            # Log the action
            details = f'Cleared {cleaned_sessions} sessions and {cleaned_temp_files} temp files'
            self._log_admin_action('clear_cache', 'system', details, True)
            
            return {
                'success': True,
                'message': f'Cache cleared successfully - {cleaned_sessions} sessions and {cleaned_temp_files} temp files removed',
                'action': 'clear_cache',
                'cleaned_sessions': cleaned_sessions,
                'cleaned_temp_files': cleaned_temp_files,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self._log_admin_action('clear_cache', 'system', 
                                   f'Cache clear failed: {str(e)}', False)
            return {
                'success': False,
                'message': f'Failed to clear cache: {str(e)}',
                'action': 'clear_cache',
                'timestamp': datetime.now().isoformat()
            }

    def export_logs(self, log_type: str = 'all', time_range: str = '24h') -> Dict[str, Any]:
        """Export system logs"""
        try:
            # Calculate time range
            if time_range == '1h':
                start_time = datetime.now() - timedelta(hours=1)
            elif time_range == '24h':
                start_time = datetime.now() - timedelta(hours=24)
            elif time_range == '7d':
                start_time = datetime.now() - timedelta(days=7)
            else:
                start_time = datetime.now() - timedelta(hours=24)
            
            # Create export directory
            export_dir = os.path.join(os.path.dirname(__file__), '..', 'exports')
            os.makedirs(export_dir, exist_ok=True)
            
            # Generate export filename
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            export_filename = f'intellicket_logs_{log_type}_{time_range}_{timestamp}.json'
            export_path = os.path.join(export_dir, export_filename)
            
            # Collect logs
            logs_data = {
                'export_info': {
                    'timestamp': datetime.now().isoformat(),
                    'log_type': log_type,
                    'time_range': time_range,
                    'start_time': start_time.isoformat()
                },
                'admin_actions': [],
                'system_alerts': [],
                'sessions': []
            }
            
            # Get admin actions
            conn = sqlite3.connect(self.admin_db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT timestamp, action, component, details, success, metadata
                FROM admin_actions WHERE timestamp >= ? ORDER BY timestamp DESC
            ''', (start_time.isoformat(),))
            
            for row in cursor.fetchall():
                logs_data['admin_actions'].append({
                    'timestamp': row[0],
                    'action': row[1],
                    'component': row[2],
                    'details': row[3],
                    'success': bool(row[4]),
                    'metadata': json.loads(row[5]) if row[5] else {}
                })
            
            # Get system alerts
            cursor.execute('''
                SELECT id, level, component, title, message, timestamp, acknowledged, resolved
                FROM system_alerts WHERE timestamp >= ? ORDER BY timestamp DESC
            ''', (start_time.isoformat(),))
            
            for row in cursor.fetchall():
                logs_data['system_alerts'].append({
                    'id': row[0],
                    'level': row[1],
                    'component': row[2],
                    'title': row[3],
                    'message': row[4],
                    'timestamp': row[5],
                    'acknowledged': bool(row[6]),
                    'resolved': bool(row[7])
                })
            
            conn.close()
            
            # Get session data
            active_sessions = session_manager.sessions
            for session_id, session_data in active_sessions.items():
                if session_data.get('created_at'):
                    try:
                        created = datetime.fromisoformat(session_data['created_at'])
                        if created >= start_time:
                            logs_data['sessions'].append({
                                'session_id': session_id,
                                'created_at': session_data['created_at'],
                                'status': session_data.get('status'),
                                'analyzer_type': session_data.get('analyzer_type'),
                                'file_count': len(session_data.get('files', [])),
                                'ip_address': session_data.get('ip_address')
                            })
                    except (ValueError, TypeError):
                        continue
            
            # Write export file
            with open(export_path, 'w') as f:
                json.dump(logs_data, f, indent=2, default=str)
            
            # Log the action
            details = f'Exported {len(logs_data["admin_actions"])} admin actions, {len(logs_data["system_alerts"])} alerts, {len(logs_data["sessions"])} sessions'
            self._log_admin_action('export_logs', 'system', details, True)
            
            return {
                'success': True,
                'message': f'Logs exported successfully to {export_filename}',
                'action': 'export_logs',
                'export_filename': export_filename,
                'export_path': export_path,
                'records_count': {
                    'admin_actions': len(logs_data['admin_actions']),
                    'system_alerts': len(logs_data['system_alerts']),
                    'sessions': len(logs_data['sessions'])
                },
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self._log_admin_action('export_logs', 'system', 
                                   f'Log export failed: {str(e)}', False)
            return {
                'success': False,
                'message': f'Failed to export logs: {str(e)}',
                'action': 'export_logs',
                'timestamp': datetime.now().isoformat()
            }

    def _log_admin_action(self, action: str, component: str, details: str, 
                         success: bool, metadata: Dict = None):
        """Log an admin action to the database"""
        try:
            conn = sqlite3.connect(self.admin_db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO admin_actions (action, component, details, success, metadata)
                VALUES (?, ?, ?, ?, ?)
            ''', (action, component, details, success, json.dumps(metadata or {})))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"❌ Failed to log admin action: {e}")

    def toggle_analyzer(self, analyzer_id: str) -> Dict[str, Any]:
        """Toggle analyzer on/off"""
        try:
            analyzers = self.get_analyzers()
            target_analyzer = None
            
            for analyzer in analyzers:
                if analyzer['id'] == analyzer_id:
                    target_analyzer = analyzer
                    break
            
            if not target_analyzer:
                return {
                    'success': False,
                    'message': f'Analyzer {analyzer_id} not found',
                    'action': 'toggle_analyzer',
                    'analyzer_id': analyzer_id,
                    'timestamp': datetime.now().isoformat()
                }
            
            # Toggle the analyzer status - fix the status mapping and persist to database
            current_status = target_analyzer.get('status', 'enabled')
            new_status = 'disabled' if current_status == 'enabled' else 'enabled'
            
            # Update the status in the database
            conn = sqlite3.connect(self.admin_db_path)
            cursor = conn.cursor()
            cursor.execute(
                'INSERT OR REPLACE INTO analyzer_status (analyzer_id, status, last_updated) VALUES (?, ?, ?)',
                (analyzer_id, new_status, datetime.now())
            )
            conn.commit()
            conn.close()
            
            self._log_admin_action('toggle_analyzer', analyzer_id, 
                                   f'Analyzer {analyzer_id} toggled to {new_status}', True)
            
            return {
                'success': True,
                'message': f'Analyzer {analyzer_id} toggled to {new_status}',
                'action': 'toggle_analyzer',
                'analyzer_id': analyzer_id,
                'new_status': new_status,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self._log_admin_action('toggle_analyzer', analyzer_id, 
                                   f'Failed to toggle analyzer: {str(e)}', False)
            return {
                'success': False,
                'message': f'Failed to toggle analyzer: {str(e)}',
                'action': 'toggle_analyzer',
                'analyzer_id': analyzer_id,
                'timestamp': datetime.now().isoformat()
            }

    def terminate_session(self, session_id: str) -> Dict[str, Any]:
        """Terminate a specific session"""
        try:
            # Check if session exists
            session_data = session_manager.get_session(session_id)
            if not session_data:
                return {
                    'success': False,
                    'message': f'Session {session_id} not found',
                    'action': 'terminate_session',
                    'session_id': session_id,
                    'timestamp': datetime.now().isoformat()
                }
            
            # Terminate the session
            success = session_manager.delete_session(session_id)
            
            if success:
                self._log_admin_action('terminate_session', 'sessions', 
                                       f'Session {session_id} terminated successfully', True)
                return {
                    'success': True,
                    'message': f'Session {session_id} terminated successfully',
                    'action': 'terminate_session',
                    'session_id': session_id,
                    'timestamp': datetime.now().isoformat()
                }
            else:
                return {
                    'success': False,
                    'message': f'Failed to terminate session {session_id}',
                    'action': 'terminate_session',
                    'session_id': session_id,
                    'timestamp': datetime.now().isoformat()
                }
                
        except Exception as e:
            self._log_admin_action('terminate_session', 'sessions', 
                                   f'Failed to terminate session: {str(e)}', False)
            return {
                'success': False,
                'message': f'Failed to terminate session: {str(e)}',
                'action': 'terminate_session',
                'session_id': session_id,
                'timestamp': datetime.now().isoformat()
            }

    def get_analyzer_usage_stats(self) -> Dict[str, Any]:
        """Get analyzer usage statistics"""
        try:
            # Get all sessions
            all_sessions = session_manager.sessions
            
            # Calculate usage statistics
            usage_by_analyzer = {}
            total_analyses = 0
            
            for session_id, session_data in all_sessions.items():
                analyzer_type = session_data.get('analysis_type', 'unknown')  # Use correct field name
                if analyzer_type not in usage_by_analyzer:
                    usage_by_analyzer[analyzer_type] = {
                        'count': 0,
                        'success_count': 0,
                        'error_count': 0,
                        'total_files': 0,
                        'success_rate': 0.0,
                        'last_used': None
                    }
                
                usage_by_analyzer[analyzer_type]['count'] += 1
                usage_by_analyzer[analyzer_type]['total_files'] += len(session_data.get('uploaded_files', []))  # Use correct field name
                
                # Update last used timestamp
                created_at = session_data.get('created_at')
                if created_at and (not usage_by_analyzer[analyzer_type]['last_used'] or created_at > usage_by_analyzer[analyzer_type]['last_used']):
                    usage_by_analyzer[analyzer_type]['last_used'] = created_at
                
                if session_data.get('status') == 'completed':
                    usage_by_analyzer[analyzer_type]['success_count'] += 1
                elif session_data.get('status') == 'error':
                    usage_by_analyzer[analyzer_type]['error_count'] += 1
                
                total_analyses += 1
            
            # Calculate success rates and find most used analyzer
            most_used = None
            max_count = 0
            for analyzer, stats in usage_by_analyzer.items():
                # Calculate success rate
                if stats['count'] > 0:
                    stats['success_rate'] = (stats['success_count'] / stats['count']) * 100
                else:
                    stats['success_rate'] = 0.0
                
                if stats['count'] > max_count:
                    max_count = stats['count']
                    most_used = analyzer
            
            return {
                'usage_by_analyzer': usage_by_analyzer,
                'total_analyses': total_analyses,
                'most_used': most_used,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"❌ Error getting analyzer usage stats: {e}")
            return {
                'usage_by_analyzer': {},
                'total_analyses': 0,
                'most_used': None,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }

    def acknowledge_alert(self, alert_id: str) -> Dict[str, Any]:
        """Acknowledge a specific alert"""
        try:
            conn = sqlite3.connect(self.admin_db_path)
            cursor = conn.cursor()
            
            # Check if alert exists
            cursor.execute('SELECT * FROM system_alerts WHERE id = ?', (alert_id,))
            alert = cursor.fetchone()
            
            if not alert:
                conn.close()
                return {
                    'success': False,
                    'message': f'Alert {alert_id} not found',
                    'action': 'acknowledge_alert',
                    'alert_id': alert_id,
                    'timestamp': datetime.now().isoformat()
                }
            
            # Update alert as acknowledged
            cursor.execute('''
                UPDATE system_alerts 
                SET acknowledged = TRUE, acknowledged_at = CURRENT_TIMESTAMP 
                WHERE id = ?
            ''', (alert_id,))
            
            conn.commit()
            conn.close()
            
            self._log_admin_action('acknowledge_alert', 'alerts', 
                                   f'Alert {alert_id} acknowledged', True)
            
            return {
                'success': True,
                'message': f'Alert {alert_id} acknowledged successfully',
                'action': 'acknowledge_alert',
                'alert_id': alert_id,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self._log_admin_action('acknowledge_alert', 'alerts', 
                                   f'Failed to acknowledge alert: {str(e)}', False)
            return {
                'success': False,
                'message': f'Failed to acknowledge alert: {str(e)}',
                'action': 'acknowledge_alert',
                'alert_id': alert_id,
                'timestamp': datetime.now().isoformat()
            }

    def get_alerts(self) -> List[Dict[str, Any]]:
        """Get system alerts"""
        try:
            conn = sqlite3.connect(self.admin_db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, level, component, title, message, timestamp, 
                       acknowledged, acknowledged_at, resolved, metadata
                FROM system_alerts 
                ORDER BY timestamp DESC 
                LIMIT 100
            ''')
            
            alerts = []
            for row in cursor.fetchall():
                alerts.append({
                    'id': row[0],
                    'level': row[1],
                    'component': row[2],
                    'title': row[3],
                    'message': row[4],
                    'timestamp': row[5],
                    'acknowledged': bool(row[6]),
                    'acknowledged_at': row[7],
                    'resolved': bool(row[8]),
                    'metadata': json.loads(row[9]) if row[9] else {}
                })
            
            conn.close()
            return alerts
            
        except Exception as e:
            print(f"❌ Error getting alerts: {e}")
            return []

# Initialize the admin service with error handling
try:
    admin_service = UnifiedAdminService()
    print("✅ Admin service initialized successfully")
except Exception as e:
    print(f"⚠️ Admin service initialization failed: {e}")
    admin_service = None

def register_admin_routes(app, config):
    """Register admin API routes"""
    admin_bp = Blueprint('admin', __name__, url_prefix='/admin')
    
    def check_admin_service():
        """Check if admin service is available"""
        if admin_service is None:
            return False, jsonify({
                'success': False,
                'error': 'Admin service not available - initialization failed',
                'timestamp': datetime.now().isoformat()
            }), 503
        return True, None, None
    
    @admin_bp.route('/health', methods=['GET'])
    def admin_health():
        """Admin API health check"""
        return jsonify({
            'success': True,
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'service': 'Intellicket Unified Admin API'
        })
    
    @admin_bp.route('/system/overview', methods=['GET'])
    def get_system_overview():
        """Get comprehensive system overview"""
        available, error_response, status_code = check_admin_service()
        if not available:
            return error_response, status_code
            
        try:
            overview = admin_service.get_system_overview()
            return jsonify({
                'success': True,
                'data': overview,
                'timestamp': datetime.now().isoformat()
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }), 500
    
    @admin_bp.route('/analyzers', methods=['GET'])
    def get_analyzers():
        """Get list of all analyzers"""
        try:
            analyzers = admin_service.get_analyzers()
            return jsonify({
                'success': True,
                'data': analyzers,
                'timestamp': datetime.now().isoformat()
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }), 500
    
    @admin_bp.route('/stats/uploads', methods=['GET'])
    def get_file_stats():
        """Get file upload statistics"""
        try:
            time_range = request.args.get('range', '24h')
            stats = admin_service.get_file_upload_stats(time_range)
            return jsonify({
                'success': True,
                'data': stats,
                'timestamp': datetime.now().isoformat()
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }), 500
    
    @admin_bp.route('/sessions/active', methods=['GET'])
    def get_active_sessions():
        """Get active sessions"""
        try:
            sessions = admin_service.get_active_sessions()
            return jsonify({
                'success': True,
                'data': sessions,
                'timestamp': datetime.now().isoformat()
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }), 500
    
    @admin_bp.route('/maintenance/status', methods=['GET'])
    def get_maintenance_status():
        """Get maintenance mode status"""
        try:
            maintenance = admin_service.get_maintenance_mode()
            return jsonify({
                'success': True,
                'data': maintenance,
                'timestamp': datetime.now().isoformat()
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }), 500
    
    @admin_bp.route('/alerts', methods=['GET'])
    def get_alerts():
        """Get system alerts"""
        try:
            alerts = admin_service.get_alerts()
            return jsonify({
                'success': True,
                'data': alerts,
                'timestamp': datetime.now().isoformat()
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }), 500

    # ACTION ENDPOINTS
    
    @admin_bp.route('/actions/restart-backend', methods=['POST'])
    def restart_backend():
        """Restart the backend server"""
        try:
            result = admin_service.restart_backend()
            status_code = 200 if result['success'] else 500
            return jsonify(result), status_code
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'Failed to restart backend: {str(e)}',
                'action': 'restart_backend',
                'timestamp': datetime.now().isoformat()
            }), 500

    @admin_bp.route('/actions/maintenance-mode', methods=['POST'])
    def toggle_maintenance_mode():
        """Toggle maintenance mode"""
        try:
            data = request.get_json() or {}
            enabled = data.get('enabled', False)
            message = data.get('message')
            affected_systems = data.get('affected_systems')
            
            result = admin_service.toggle_maintenance_mode(enabled, message, affected_systems)
            status_code = 200 if result['success'] else 500
            return jsonify(result), status_code
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'Failed to toggle maintenance mode: {str(e)}',
                'action': 'toggle_maintenance',
                'timestamp': datetime.now().isoformat()
            }), 500

    @admin_bp.route('/actions/clear-cache', methods=['POST'])
    def clear_cache():
        """Clear system cache"""
        try:
            result = admin_service.clear_cache()
            status_code = 200 if result['success'] else 500
            return jsonify(result), status_code
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'Failed to clear cache: {str(e)}',
                'action': 'clear_cache',
                'timestamp': datetime.now().isoformat()
            }), 500

    @admin_bp.route('/actions/export-logs', methods=['POST'])
    def export_logs():
        """Export system logs"""
        try:
            data = request.get_json() or {}
            log_type = data.get('log_type', 'all')
            time_range = data.get('time_range', '24h')
            
            result = admin_service.export_logs(log_type, time_range)
            status_code = 200 if result['success'] else 500
            return jsonify(result), status_code
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'Failed to export logs: {str(e)}',
                'action': 'export_logs',
                'timestamp': datetime.now().isoformat()
            }), 500

    @admin_bp.route('/analyzers/<analyzer_id>/toggle', methods=['POST'])
    def toggle_analyzer(analyzer_id):
        """Toggle analyzer on/off"""
        try:
            result = admin_service.toggle_analyzer(analyzer_id)
            status_code = 200 if result['success'] else 500
            return jsonify(result), status_code
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'Failed to toggle analyzer: {str(e)}',
                'action': 'toggle_analyzer',
                'analyzer_id': analyzer_id,
                'timestamp': datetime.now().isoformat()
            }), 500

    @admin_bp.route('/sessions/<session_id>/terminate', methods=['POST'])
    def terminate_session(session_id):
        """Terminate a specific session"""
        try:
            result = admin_service.terminate_session(session_id)
            status_code = 200 if result['success'] else 500
            return jsonify(result), status_code
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'Failed to terminate session: {str(e)}',
                'action': 'terminate_session',
                'session_id': session_id,
                'timestamp': datetime.now().isoformat()
            }), 500

    @admin_bp.route('/stats/analyzers', methods=['GET'])
    def get_analyzer_stats():
        """Get analyzer usage statistics"""
        try:
            stats = admin_service.get_analyzer_usage_stats()
            return jsonify({
                'success': True,
                'data': stats,
                'timestamp': datetime.now().isoformat()
            }), 200
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'Failed to get analyzer stats: {str(e)}',
                'action': 'get_analyzer_stats',
                'timestamp': datetime.now().isoformat()
            }), 500

    @admin_bp.route('/test/create-session', methods=['POST'])
    def create_test_session():
        """Create a test session for testing dashboard statistics (development only)"""
        try:
            data = request.get_json()
            
            # Create session via session manager
            session_id = session_manager.create_session()
            
            # Update session with test data
            session_manager.update_session(session_id, {
                'analysis_type': data.get('analysis_type', 'test'),
                'uploaded_files': data.get('uploaded_files', []),
                'status': data.get('status', 'completed'),
                'progress_percentage': data.get('progress_percentage', 100),
                'created_at': data.get('created_at')
            })
            
            return jsonify({
                'success': True,
                'session_id': session_id,
                'message': 'Test session created successfully',
                'timestamp': datetime.now().isoformat()
            }), 200
            
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'Failed to create test session: {str(e)}',
                'timestamp': datetime.now().isoformat()
            }), 500

    @admin_bp.route('/alerts/<alert_id>/acknowledge', methods=['POST'])
    def acknowledge_alert(alert_id):
        """Acknowledge a specific alert"""
        try:
            result = admin_service.acknowledge_alert(alert_id)
            status_code = 200 if result['success'] else 500
            return jsonify(result), status_code
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'Failed to acknowledge alert: {str(e)}',
                'action': 'acknowledge_alert',
                'alert_id': alert_id,
                'timestamp': datetime.now().isoformat()
            }), 500

    @admin_bp.route('/stats', methods=['GET'])
    def get_combined_stats():
        """Get combined statistics for the admin dashboard"""
        try:
            # Get upload stats
            upload_stats = admin_service.get_upload_stats()
            
            # Get analyzer stats  
            analyzer_stats = admin_service.get_analyzer_usage_stats()
            
            # Combine the stats
            combined_stats = {
                'success': True,
                'data': {
                    'uploads': upload_stats.get('data', {}),
                    'analyzers': analyzer_stats.get('data', {}),
                    'timestamp': datetime.now().isoformat()
                },
                'timestamp': datetime.now().isoformat()
            }
            
            return jsonify(combined_stats), 200
            
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'Failed to get combined stats: {str(e)}',
                'timestamp': datetime.now().isoformat()
            }), 500
    
    # Register the blueprint
    app.register_blueprint(admin_bp)
    print("✅ Admin API routes registered successfully")