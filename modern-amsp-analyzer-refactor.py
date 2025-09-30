#!/usr/bin/env python3
"""
AMSP Analyzer Refactor: Direct API Response Format
==================================================

This removes the "legacy format" conversion and returns data directly
optimized for the React frontend consumption.
"""

from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import json

@dataclass
class AMSPLogEntry:
    """Direct API format for log entries"""
    timestamp: str
    component: str
    level: str
    message: str
    event_type: str
    severity_score: int
    source_file: Optional[str] = None
    line_number: Optional[int] = None

@dataclass 
class AIRecommendation:
    """Direct API format for AI recommendations"""
    priority: str  # 'high' | 'medium' | 'low'
    category: str  # 'security' | 'performance' | 'configuration' | 'maintenance'
    title: str
    description: str
    action_items: List[str]
    impact: str

@dataclass
class RootCauseAnalysis:
    """Direct API format for root cause analysis"""
    issue_type: str
    pattern_detected: str
    occurrences: int
    severity: str
    root_cause: str
    resolution_steps: List[str]
    kb_reference: Optional[str] = None

@dataclass
class ComponentStatus:
    """Direct API format for component analysis"""
    total_entries: int
    error_rate: float
    status: str  # 'healthy' | 'degraded' | 'failed'
    key_events: List[AMSPLogEntry]

@dataclass
class ModernAMSPAnalysisResponse:
    """Modern API response format - no legacy conversion needed"""
    
    # API Metadata
    success: bool
    analysis_type: str
    session_id: str
    timestamp: str
    
    # Processing Statistics
    processing: Dict[str, Any]  # total_lines, processed_lines, success_rate, etc.
    
    # System Health
    health: Dict[str, Any]  # system_score, status, overall_severity
    
    # Issues & Events
    issues: Dict[str, List[AMSPLogEntry]]  # critical, errors, warnings, important_events
    
    # AI Analysis Results
    ai_analysis: Dict[str, Any]  # applied, recommendations, key_findings, etc.
    
    # Component Analysis
    components: Dict[str, ComponentStatus]
    
    # Timeline Analysis
    timeline: Dict[str, Any]
    
    # Optional Raw Data
    raw_data: Optional[Dict[str, Any]] = None

class ModernAMSPAnalyzer:
    """Refactored AMSP Analyzer with direct API format"""
    
    def analyze_log_file(self, file_path: str) -> ModernAMSPAnalysisResponse:
        """Analyze AMSP log file and return modern API format"""
        
        # Use intelligent processor
        processing_result = self.intelligent_processor.process_logs_intelligently([file_path])
        
        # Convert to modern API format (no legacy conversion!)
        return self._create_modern_response(processing_result, file_path)
    
    def _create_modern_response(self, processing_result, file_path: str) -> ModernAMSPAnalysisResponse:
        """Create direct API response optimized for React frontend"""
        
        # Convert log entries to API format
        critical_entries = [
            AMSPLogEntry(
                timestamp=entry.timestamp.isoformat(),
                component=entry.component,
                level=entry.log_level,
                message=entry.message,
                event_type=entry.event_type,
                severity_score=entry.severity_score,
                source_file=entry.source_file,
                line_number=entry.line_number
            ) for entry in processing_result.critical_entries
        ]
        
        # Convert AI recommendations
        recommendations = [
            AIRecommendation(
                priority='high' if 'CRITICAL' in rec else 'medium',
                category='security' if any(kw in rec.lower() for kw in ['security', 'malware', 'threat']) else 'configuration',
                title=rec.split(':')[0] if ':' in rec else rec[:50] + '...',
                description=rec,
                action_items=[rec],  # Could be enhanced
                impact='System stability and security'
            ) for rec in processing_result.ai_insights.get('recommendations', [])
        ]
        
        # Convert component analysis
        components = {
            comp_name: ComponentStatus(
                total_entries=analysis['total_entries'],
                error_rate=analysis.get('error_rate', 0.0),
                status='healthy' if analysis.get('error_rate', 0) < 0.1 else 'degraded',
                key_events=[]  # Could be populated with relevant entries
            ) for comp_name, analysis in processing_result.component_analysis.items()
        }
        
        # Build response
        return ModernAMSPAnalysisResponse(
            success=True,
            analysis_type='amsp_installation',
            session_id=getattr(self, 'session_id', 'unknown'),
            timestamp=datetime.now().isoformat(),
            
            processing={
                'total_lines': processing_result.total_lines,
                'processed_lines': processing_result.processed_lines,
                'success_rate': (processing_result.processed_lines / processing_result.total_lines) * 100 if processing_result.total_lines > 0 else 0,
                'encoding_detected': 'utf-16-le',  # From our recent fix
                'processing_time_seconds': 0  # Could be measured
            },
            
            health={
                'system_score': processing_result.ai_insights.get('system_health_score', 0),
                'status': self._get_health_status(processing_result.ai_insights.get('system_health_score', 0)),
                'overall_severity': self._determine_severity(processing_result)
            },
            
            issues={
                'critical': critical_entries,
                'errors': [],  # Convert similarly
                'warnings': [],  # Convert similarly  
                'important_events': []  # Convert similarly
            },
            
            ai_analysis={
                'applied': True,
                'ml_enhanced': hasattr(self, 'ml_analyzer') and self.ml_analyzer is not None,
                'rag_enhanced': hasattr(self, 'rag_system') and self.rag_system is not None,
                'processing_mode': 'intelligent',
                'recommendations': recommendations,
                'key_findings': processing_result.ai_insights.get('key_findings', []),
                'root_cause_analysis': []  # Could be enhanced
            },
            
            components=components,
            
            timeline={
                'start_time': processing_result.time_range[1].isoformat() if processing_result.time_range[1] else None,
                'end_time': processing_result.time_range[0].isoformat() if processing_result.time_range[0] else None,
                'duration_seconds': 0,  # Could be calculated
                'key_phases': []  # Could be extracted from timeline analysis
            },
            
            raw_data={
                'pattern_analysis': processing_result.pattern_analysis,
                'component_analysis': processing_result.component_analysis,
                'timeline_analysis': processing_result.timeline_analysis
            }
        )
    
    def _get_health_status(self, score: int) -> str:
        """Convert health score to status"""
        if score < 50: return 'critical'
        if score < 70: return 'warning' 
        if score < 90: return 'caution'
        return 'healthy'
    
    def _determine_severity(self, processing_result) -> str:
        """Determine overall severity"""
        if len(processing_result.critical_entries) > 0:
            return 'critical'
        if len(processing_result.error_entries) > 10:
            return 'high'
        if len(processing_result.warning_entries) > 100:
            return 'medium'
        return 'low'

# Usage in API route:
def amsp_analysis_endpoint(file_path: str) -> dict:
    """API endpoint that returns modern format directly"""
    analyzer = ModernAMSPAnalyzer()
    result = analyzer.analyze_log_file(file_path)
    
    # Convert dataclass to dict for JSON serialization
    return asdict(result)