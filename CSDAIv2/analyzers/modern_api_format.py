#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Modern AMSP API Format - Direct Backend-to-Frontend Response
============================================================

This module defines the modern API response format that eliminates
the need for legacy format conversions between backend and frontend.

The format is optimized for React frontend consumption and provides
comprehensive AMSP analysis data with AI/ML/RAG insights.
"""

from datetime import datetime
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, asdict
import json

@dataclass
class AMSPLogEntry:
    """Modern API format for AMSP log entries"""
    timestamp: str
    component: str
    level: str  # 'INFO' | 'WARN' | 'ERROR' | 'CRITICAL'
    message: str
    event_type: str
    severity_score: int
    source_file: Optional[str] = None
    line_number: Optional[int] = None
    thread_id: Optional[str] = None
    category: Optional[str] = None

@dataclass 
class AIRecommendation:
    """Modern API format for AI-generated recommendations"""
    priority: str  # 'critical' | 'high' | 'medium' | 'low'
    category: str  # 'security' | 'performance' | 'configuration' | 'maintenance'
    title: str
    description: str
    action_items: List[str]
    impact: str
    html_formatted: bool = True  # Indicates if description contains HTML

@dataclass
class RootCauseAnalysis:
    """Modern API format for root cause analysis"""
    issue_type: str
    pattern_detected: str
    occurrences: int
    severity: str  # 'critical' | 'high' | 'medium' | 'low'
    root_cause: str
    resolution_steps: List[str]
    kb_reference: Optional[str] = None
    affected_components: Optional[List[str]] = None

@dataclass
class ComponentAnalysis:
    """Modern API format for component analysis"""
    total_entries: int
    error_count: int
    warning_count: int
    error_rate: float
    status: str  # 'healthy' | 'degraded' | 'failed'
    key_events: List[AMSPLogEntry]
    health_score: int  # 0-100

@dataclass
class ProcessingStatistics:
    """Modern API format for processing statistics"""
    total_lines: int
    processed_lines: int
    success_rate: float
    encoding_detected: str
    processing_time_seconds: float
    fallback_mode: bool
    intelligent_processing: bool

@dataclass
class SystemHealth:
    """Modern API format for system health assessment"""
    system_score: int  # 0-100
    status: str  # 'critical' | 'warning' | 'caution' | 'healthy'
    overall_severity: str  # 'low' | 'medium' | 'high' | 'critical'
    status_message: str
    status_icon: str

@dataclass
class AIAnalysis:
    """Modern API format for AI analysis results"""
    applied: bool
    ml_enhanced: bool
    rag_enhanced: bool
    processing_mode: str  # 'intelligent' | 'fallback' | 'legacy'
    recommendations: List[AIRecommendation]
    key_findings: List[str]
    root_cause_analysis: List[RootCauseAnalysis]
    confidence_score: float  # 0.0-1.0

@dataclass
class TimelinePhase:
    """Modern API format for timeline phases"""
    phase_name: str
    start_time: str
    end_time: str
    duration_seconds: float
    status: str  # 'completed' | 'failed' | 'partial' | 'ongoing'
    key_events: List[AMSPLogEntry]
    success_rate: float

@dataclass
class Timeline:
    """Modern API format for timeline analysis"""
    start_time: str
    end_time: str
    total_duration_seconds: float
    phases: List[TimelinePhase]
    key_milestones: List[AMSPLogEntry]

@dataclass
class Issues:
    """Modern API format for categorized issues"""
    critical: List[AMSPLogEntry]
    errors: List[AMSPLogEntry]
    warnings: List[AMSPLogEntry]
    important_events: List[AMSPLogEntry]

@dataclass
class ModernAMSPAnalysisResponse:
    """
    Modern AMSP Analysis API Response Format
    
    This format is optimized for direct React frontend consumption
    without any legacy conversion layers.
    """
    
    # API Metadata (required fields first)
    success: bool
    analysis_type: str  # 'amsp_installation' | 'amsp_logs' | 'amsp_diagnostic'
    session_id: str
    timestamp: str
    
    # Processing Statistics
    processing: ProcessingStatistics
    
    # System Health Assessment
    health: SystemHealth
    
    # Categorized Issues and Events
    issues: Issues
    
    # AI Analysis Results
    ai_analysis: AIAnalysis
    
    # Component Analysis
    components: Dict[str, ComponentAnalysis]
    
    # Timeline Analysis
    timeline: Timeline
    
    # Optional fields with defaults (must come last)
    format_version: str = "modern_v1"
    raw_data: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return asdict(self)
    
    def to_json(self) -> str:
        """Convert to JSON string"""
        return json.dumps(self.to_dict(), default=str, indent=2)

class ModernAPIResponseBuilder:
    """Builder class for creating modern API responses"""
    
    @staticmethod
    def build_amsp_response(
        processing_result,
        session_id: str,
        processing_time: float = 0.0,
        encoding_detected: str = "utf-16-le",
        fallback_mode: bool = False
    ) -> ModernAMSPAnalysisResponse:
        """Build modern AMSP analysis response from processing result"""
        
        start_time = datetime.now()
        
        # Convert log entries to modern format
        critical_entries = ModernAPIResponseBuilder._convert_log_entries(
            processing_result.critical_entries
        )
        error_entries = ModernAPIResponseBuilder._convert_log_entries(
            processing_result.error_entries
        )
        warning_entries = ModernAPIResponseBuilder._convert_log_entries(
            processing_result.warning_entries
        )
        important_events = ModernAPIResponseBuilder._convert_log_entries(
            processing_result.important_entries
        )
        
        # Build AI recommendations
        recommendations = ModernAPIResponseBuilder._build_ai_recommendations(
            processing_result.ai_insights
        )
        
        # Build root cause analysis
        root_cause_analysis = ModernAPIResponseBuilder._build_root_cause_analysis(
            processing_result.ai_insights
        )
        
        # Build component analysis
        components = ModernAPIResponseBuilder._build_component_analysis(
            processing_result.component_analysis
        )
        
        # Calculate system health
        health = ModernAPIResponseBuilder._calculate_system_health(
            processing_result, len(critical_entries), len(error_entries)
        )
        
        # Build timeline
        timeline = ModernAPIResponseBuilder._build_timeline(
            processing_result, important_events
        )
        
        # Build processing statistics
        processing_stats = ProcessingStatistics(
            total_lines=processing_result.total_lines,
            processed_lines=processing_result.processed_lines,
            success_rate=(processing_result.processed_lines / processing_result.total_lines * 100) 
                         if processing_result.total_lines > 0 else 0.0,
            encoding_detected=encoding_detected,
            processing_time_seconds=processing_time,
            fallback_mode=fallback_mode,
            intelligent_processing=not fallback_mode
        )
        
        # Build AI analysis
        ai_analysis = AIAnalysis(
            applied=True,
            ml_enhanced=False,  # Could be determined from context
            rag_enhanced=False,  # Could be determined from context
            processing_mode='intelligent' if not fallback_mode else 'fallback',
            recommendations=recommendations,
            key_findings=processing_result.ai_insights.get('key_findings', []),
            root_cause_analysis=root_cause_analysis,
            confidence_score=0.85  # Could be calculated based on processing quality
        )
        
        return ModernAMSPAnalysisResponse(
            success=True,
            analysis_type='amsp_installation',
            session_id=session_id,
            timestamp=start_time.isoformat(),
            processing=processing_stats,
            health=health,
            issues=Issues(
                critical=critical_entries,
                errors=error_entries,
                warnings=warning_entries,
                important_events=important_events
            ),
            ai_analysis=ai_analysis,
            components=components,
            timeline=timeline,
            raw_data={
                'pattern_analysis': processing_result.pattern_analysis,
                'component_analysis': processing_result.component_analysis,
                'timeline_analysis': processing_result.timeline_analysis
            }
        )
    
    @staticmethod
    def _convert_log_entries(entries) -> List[AMSPLogEntry]:
        """Convert LogEntry objects to modern API format"""
        converted = []
        for entry in entries:
            converted.append(AMSPLogEntry(
                timestamp=entry.timestamp.isoformat(),
                component=entry.component,
                level=entry.log_level,
                message=entry.message,
                event_type=entry.event_type,
                severity_score=entry.severity_score,
                source_file=entry.source_file,
                line_number=entry.line_number,
                thread_id=entry.thread_id,
                category=entry.category
            ))
        return converted
    
    @staticmethod
    def _build_ai_recommendations(ai_insights: Dict[str, Any]) -> List[AIRecommendation]:
        """Build AI recommendations from insights"""
        recommendations = []
        raw_recommendations = ai_insights.get('recommendations', [])
        
        for rec in raw_recommendations:
            # Parse recommendation text to extract structured data
            priority = 'critical' if any(kw in rec.lower() for kw in ['critical', 'urgent', 'immediate']) else 'medium'
            category = ModernAPIResponseBuilder._categorize_recommendation(rec)
            
            recommendations.append(AIRecommendation(
                priority=priority,
                category=category,
                title=ModernAPIResponseBuilder._extract_title(rec),
                description=rec,
                action_items=[rec],  # Could be enhanced to extract specific actions
                impact='System stability and security',
                html_formatted=True
            ))
        
        return recommendations
    
    @staticmethod
    def _build_root_cause_analysis(ai_insights: Dict[str, Any]) -> List[RootCauseAnalysis]:
        """Build root cause analysis from AI insights"""
        root_causes = []
        
        # Extract root cause indicators from AI insights
        indicators = ai_insights.get('root_cause_indicators', [])
        for indicator in indicators:
            root_causes.append(RootCauseAnalysis(
                issue_type=indicator.get('pattern', 'Unknown Issue'),
                pattern_detected=indicator.get('pattern', ''),
                occurrences=indicator.get('occurrences', 1),
                severity=indicator.get('severity', 'medium'),
                root_cause=indicator.get('suggestion', 'Analysis required'),
                resolution_steps=[indicator.get('suggestion', 'Review system logs')],
                kb_reference=None,
                affected_components=[]
            ))
        
        return root_causes
    
    @staticmethod
    def _build_component_analysis(component_analysis: Dict[str, Any]) -> Dict[str, ComponentAnalysis]:
        """Build component analysis from processing result"""
        components = {}
        
        for comp_name, analysis in component_analysis.items():
            error_count = analysis.get('error_count', 0)
            total_entries = analysis.get('total_entries', 1)
            error_rate = error_count / total_entries if total_entries > 0 else 0.0
            
            # Determine component status
            if error_rate > 0.1:
                status = 'failed'
                health_score = max(0, 100 - int(error_rate * 100))
            elif error_rate > 0.05:
                status = 'degraded'
                health_score = max(50, 100 - int(error_rate * 200))
            else:
                status = 'healthy'
                health_score = 100 - int(error_rate * 50)
            
            components[comp_name] = ComponentAnalysis(
                total_entries=total_entries,
                error_count=error_count,
                warning_count=analysis.get('warning_count', 0),
                error_rate=error_rate,
                status=status,
                key_events=[],  # Could be populated with relevant entries
                health_score=health_score
            )
        
        return components
    
    @staticmethod
    def _calculate_system_health(processing_result, critical_count: int, error_count: int) -> SystemHealth:
        """Calculate overall system health"""
        base_score = processing_result.ai_insights.get('system_health_score', 50)
        
        # Adjust score based on issues
        score_penalty = (critical_count * 10) + (error_count * 2)
        final_score = max(0, base_score - score_penalty)
        
        # Determine status
        if final_score < 30:
            status = 'critical'
            status_message = 'System requires immediate attention'
            status_icon = '🔴'
        elif final_score < 50:
            status = 'warning'
            status_message = 'System has significant issues'
            status_icon = '🟡'
        elif final_score < 80:
            status = 'caution'
            status_message = 'System has minor issues'
            status_icon = '🟠'
        else:
            status = 'healthy'
            status_message = 'System operating normally'
            status_icon = '🟢'
        
        # Determine overall severity
        if critical_count > 5:
            overall_severity = 'critical'
        elif critical_count > 0 or error_count > 20:
            overall_severity = 'high'
        elif error_count > 5:
            overall_severity = 'medium'
        else:
            overall_severity = 'low'
        
        return SystemHealth(
            system_score=final_score,
            status=status,
            overall_severity=overall_severity,
            status_message=status_message,
            status_icon=status_icon
        )
    
    @staticmethod
    def _build_timeline(processing_result, important_events: List[AMSPLogEntry]) -> Timeline:
        """Build timeline analysis"""
        start_time = processing_result.time_range[1] if processing_result.time_range[1] else datetime.now()
        end_time = processing_result.time_range[0] if processing_result.time_range[0] else datetime.now()
        
        duration = (end_time - start_time).total_seconds()
        
        # Create phases based on important events
        phases = []
        if important_events:
            # Group events into phases (could be enhanced with more sophisticated logic)
            phases.append(TimelinePhase(
                phase_name='Installation Process',
                start_time=start_time.isoformat(),
                end_time=end_time.isoformat(),
                duration_seconds=duration,
                status='completed',
                key_events=important_events[:10],  # First 10 events
                success_rate=0.9  # Could be calculated based on success/failure events
            ))
        
        return Timeline(
            start_time=start_time.isoformat(),
            end_time=end_time.isoformat(),
            total_duration_seconds=duration,
            phases=phases,
            key_milestones=important_events[:5]  # Top 5 most important events
        )
    
    @staticmethod
    def _categorize_recommendation(recommendation: str) -> str:
        """Categorize recommendation by content"""
        rec_lower = recommendation.lower()
        if any(kw in rec_lower for kw in ['security', 'malware', 'threat', 'attack']):
            return 'security'
        elif any(kw in rec_lower for kw in ['performance', 'slow', 'memory', 'cpu']):
            return 'performance'
        elif any(kw in rec_lower for kw in ['config', 'setting', 'parameter']):
            return 'configuration'
        else:
            return 'maintenance'
    
    @staticmethod
    def _extract_title(recommendation: str) -> str:
        """Extract title from recommendation text"""
        # Look for HTML strong tags first
        if '<strong>' in recommendation:
            import re
            match = re.search(r'<strong>(.*?)</strong>', recommendation)
            if match:
                return match.group(1)
        
        # Look for patterns like "CRITICAL:", "WARNING:", etc.
        if ':' in recommendation:
            parts = recommendation.split(':', 1)
            if len(parts[0]) < 50:  # Reasonable title length
                return parts[0].strip()
        
        # Fallback to first 50 characters
        return recommendation[:50] + '...' if len(recommendation) > 50 else recommendation