# -*- coding: utf-8 -*-
"""
AnalyzerOutputStandardizer - Base class for standardizing analyzer output structures
Extracted from analyzers.py lines 39-302 with safety enhancements
"""

from ..shared_imports import *

class AnalyzerOutputStandardizer:
    """Mixin class for standardizing analyzer output structures"""
    
    def _standardize_analyzer_output(self, raw_results, analysis_type):
        """Standardize analyzer output structure for frontend compatibility"""
        try:
            # Handle None input - this is the critical fix
            if raw_results is None:
                print(f"⚠️ Warning: _standardize_analyzer_output received None for analysis_type: {analysis_type}")
                raw_results = {
                    'summary': {'error': 'Analysis returned no data'},
                    'errors': ['Analysis failed to produce results'],
                    'warnings': [],
                    'recommendations': ['Please check the log file format and try again']
                }
            
            # Ensure raw_results is a dictionary
            if not isinstance(raw_results, dict):
                print(f"⚠️ Warning: raw_results is not a dictionary: {type(raw_results)}")
                raw_results = {
                    'summary': {'error': f'Invalid result type: {type(raw_results)}'},
                    'errors': [f'Expected dictionary, got {type(raw_results)}'],
                    'warnings': [],
                    'recommendations': ['Please check the analysis method implementation']
                }
            
            # DEBUG: Check what we're actually receiving
            print(f"🔍 DEBUG: Standardizing {analysis_type} with result type: {type(raw_results)}")
            if isinstance(raw_results, dict):
                print(f"🔍 DEBUG: Result keys: {list(raw_results.keys())}")
            
            standardized = {
                'analysis_type': analysis_type,
                'status': 'completed',
                'timestamp': datetime.now().isoformat(),
                
                # Core data - standardized fields with safe extraction
                'summary': self._extract_summary(raw_results),
                'details': self._extract_details(raw_results),
                'recommendations': self._extract_recommendations(raw_results),
                'severity': self._determine_overall_severity(raw_results),
                
                # Enhanced data structure for frontend compatibility
                'statistics': self._extract_enhanced_statistics(raw_results),
                'component_analysis': self._extract_component_analysis(raw_results),
                'ai_analysis': self._extract_ai_analysis(raw_results),
                'validation_steps': self._extract_validation_steps(raw_results),
                
                # Extended data with safe extraction  
                'correlations': self._extract_correlations(raw_results),
                'ml_insights': raw_results.get('ml_insights') if isinstance(raw_results, dict) else None,
                'rag_insights': (raw_results.get('rag_insights') or raw_results.get('dynamic_rag_analysis')) if isinstance(raw_results, dict) else None,
                
                # Original raw data for backward compatibility
                'raw_data': raw_results,
                'formatted_html': None  # Will be populated by formatters if needed
            }
            
            return standardized
            
        except Exception as e:
            print(f"⚠️ Failed to standardize output: {e}")
            print(f"🔍 DEBUG: Exception details - raw_results type: {type(raw_results)}")
            print(f"🔍 DEBUG: Exception traceback: {e}")
            # Fallback to safe structure
            return {
                'analysis_type': analysis_type,
                'status': 'error',
                'summary': f'Standardization failed: {str(e)}',
                'details': ['Analysis standardization encountered an error'],
                'recommendations': ['Please try again or contact support'],
                'severity': 'medium',
                'statistics': {},
                'correlations': {},
                'ml_insights': None,
                'rag_insights': None,
                'raw_data': raw_results,
                'formatted_html': None
            }
    
    def _extract_summary(self, data):
        """Extract summary information from raw results"""
        if data is None or not isinstance(data, dict):
            return "Analysis completed successfully"
        
        try:
            if isinstance(data.get('summary'), dict):
                summary_data = data['summary']
                return f"Analyzed {summary_data.get('total_lines', 0)} log entries, found {summary_data.get('error_count', 0)} errors and {summary_data.get('warning_count', 0)} warnings"
            elif isinstance(data.get('summary'), str):
                return data['summary']
            else:
                return "Analysis completed successfully"
        except Exception as e:
            print(f"⚠️ Error extracting summary: {e}")
            return "Analysis completed with summary extraction error"
    
    def _extract_details(self, data):
        """Extract detailed analysis information from raw results"""
        if data is None or not isinstance(data, dict):
            return []
        
        try:
            details = []
            
            # Extract from analysis_details if available (new enhanced format)
            if 'analysis_details' in data and isinstance(data['analysis_details'], dict):
                analysis_details = data['analysis_details']
                for section, content in analysis_details.items():
                    if content and isinstance(content, str):
                        details.append(f"<strong>{section.replace('_', ' ').title()}:</strong><br>{content}")
            
            # Extract from errors, warnings, critical_issues
            if 'errors' in data and data['errors']:
                error_count = len(data['errors'])
                details.append(f"Error Analysis: {error_count} error conditions detected requiring attention")
            
            if 'critical_issues' in data and data['critical_issues']:
                critical_count = len(data['critical_issues'])
                details.append(f"Critical Issues: {critical_count} critical conditions requiring immediate action")
            
            if 'known_issues' in data and data['known_issues']:
                known_count = len(data['known_issues'])
                details.append(f"Known Issues: {known_count} recognized patterns matched against knowledge base")
            
            # Extract from cross-component relations if available
            if 'cross_component_relations' in data:
                cross_relations = data['cross_component_relations']
                if isinstance(cross_relations, dict) and cross_relations.get('relationship_summary'):
                    summary = cross_relations['relationship_summary']
                    complexity = summary.get('complexity_score', 0)
                    details.append(f"Cross-Component Analysis: System complexity score {complexity}/100 with {summary.get('communicating_components', 0)} inter-component communications detected")
            
            # Fallback to basic information if no detailed analysis available
            if not details:
                details = ['Analysis completed successfully', 'No specific issues identified', 'System appears to be operating normally']
            
            return details
            
        except Exception as e:
            print(f"⚠️ Error extracting details: {e}")
            return ['Analysis completed with detail extraction error']
    
    def _extract_recommendations(self, data):
        """Extract recommendations as structured list"""
        if data is None or not isinstance(data, dict):
            return ["Monitor system for recurring issues"]
            
        try:
            recommendations = []
            
            if data.get('recommendations'):
                for rec in data['recommendations']:
                    if isinstance(rec, str):
                        recommendations.append(rec)
                    elif isinstance(rec, dict):
                        recommendations.append(rec.get('text', str(rec)))
            
            # Add ML-based recommendations
            ml_insights = data.get('ml_insights')
            if ml_insights and isinstance(ml_insights, dict) and ml_insights.get('recommendations'):
                for rec in ml_insights['recommendations']:
                    recommendations.append(f"ML Insight: {rec}")
            
            # Add RAG-based recommendations
            rag_data = data.get('rag_insights') or data.get('dynamic_rag_analysis')
            if rag_data and isinstance(rag_data, dict) and rag_data.get('ai_response'):
                ai_response = rag_data['ai_response']
                if isinstance(ai_response, str) and len(ai_response) > 200:
                    ai_response = ai_response[:200] + "..."
                recommendations.append(f"AI Analysis: {ai_response}")
            
            return recommendations if recommendations else ["Monitor system for recurring issues"]
        except Exception as e:
            print(f"⚠️ Error extracting recommendations: {e}")
            return ["Error extracting recommendations"]
    
    def _determine_overall_severity(self, data):
        """Determine overall severity level"""
        if data is None or not isinstance(data, dict):
            return 'low'
            
        try:
            critical_count = 0
            error_count = 0
            warning_count = 0
            
            if isinstance(data.get('summary'), dict):
                summary = data['summary']
                critical_count = summary.get('critical_count', 0)
                error_count = summary.get('error_count', 0)
                warning_count = summary.get('warning_count', 0)
            
            # Check individual items
            if data.get('errors'):
                error_count += len([e for e in data['errors'] if 'critical' not in str(e).lower()])
                critical_count += len([e for e in data['errors'] if 'critical' in str(e).lower()])
            
            if critical_count > 0:
                return 'critical'
            elif error_count > 5:
                return 'high'
            elif error_count > 0 or warning_count > 10:
                return 'medium'
            else:
                return 'low'
        except Exception as e:
            print(f"⚠️ Error determining severity: {e}")
            return 'medium'
    
    def _extract_statistics(self, data):
        """Extract statistical information"""
        if data is None or not isinstance(data, dict):
            return {}
            
        try:
            stats = {}
            
            if isinstance(data.get('summary'), dict):
                summary = data['summary']
                stats = {
                    'total_lines': summary.get('total_lines', 0),
                    'parsed_lines': summary.get('parsed_lines', 0),
                    'error_count': summary.get('error_count', 0),
                    'warning_count': summary.get('warning_count', 0),
                    'critical_count': summary.get('critical_count', 0)
                }
            
            if data.get('components'):
                stats['component_count'] = len(data['components'])
            
            return stats
        except Exception as e:
            print(f"⚠️ Error extracting statistics: {e}")
            return {}
    
    def _extract_correlations(self, data):
        """Extract correlation information"""
        if data is None or not isinstance(data, dict):
            return {
                'cross_log_correlations': {},
                'timing_correlations': [],
                'component_correlations': [],
                'issue_correlations': []
            }
            
        try:
            correlations = {
                'cross_log_correlations': {},
                'timing_correlations': [],
                'component_correlations': [],
                'issue_correlations': []
            }
            
            # Extract correlation data if present
            if data.get('correlation_analysis'):
                correlation_data = data['correlation_analysis']
                correlations.update({
                    'timing_correlations': correlation_data.get('timing_correlations', []),
                    'component_correlations': correlation_data.get('component_correlations', []),
                    'issue_correlations': correlation_data.get('issue_correlations', []),
                    'correlation_score': correlation_data.get('correlation_score', 0)
                })
            
            # For diagnostic package results
            if data.get('cross_log_correlations'):
                correlations['cross_log_correlations'] = data['cross_log_correlations']
            
            return correlations
        except Exception as e:
            print(f"⚠️ Error extracting correlations: {e}")
            return {
                'cross_log_correlations': {},
                'timing_correlations': [],
                'component_correlations': [],
                'issue_correlations': []
            }
    
    def _extract_enhanced_statistics(self, data):
        """Extract enhanced statistics for frontend display"""
        if data is None or not isinstance(data, dict):
            return {}
        
        try:
            summary = data.get('summary', {})
            
            enhanced_stats = {
                'file_processing': {
                    'total_lines': summary.get('total_lines', 0),
                    'parsed_lines': summary.get('parsed_lines', 0),
                    'parsing_rate': f"{(summary.get('parsed_lines', 0) / max(summary.get('total_lines', 1), 1) * 100):.1f}%"
                },
                'issue_counts': {
                    'critical_issues': summary.get('critical_count', 0),
                    'errors': summary.get('error_count', 0),
                    'warnings': summary.get('warning_count', 0)
                },
                'time_analysis': {
                    'time_range': f"{summary.get('timespan', {}).get('start', 'Unknown')} to {summary.get('timespan', {}).get('end', 'Unknown')}",
                    'analysis_duration': 'Real-time',
                    'start_time': summary.get('timespan', {}).get('start', 'Unknown'),
                    'end_time': summary.get('timespan', {}).get('end', 'Unknown')
                }
            }
            
            return enhanced_stats
            
        except Exception as e:
            print(f"⚠️ Error extracting enhanced statistics: {e}")
            return {}
    
    def _extract_component_analysis(self, data):
        """Extract component analysis for frontend display"""
        if data is None or not isinstance(data, dict):
            return {}
        
        try:
            component_analysis = data.get('component_analysis', {})
            enhanced_components = {}
            
            for component, stats in component_analysis.items():
                total_entries = stats.get('total_entries', 0)
                errors = stats.get('errors', 0)
                warnings = stats.get('warnings', 0)
                
                # Calculate health score
                health_score = max(0, 100 - (errors * 10) - (warnings * 2))
                
                # Determine status
                if errors > 0:
                    status = 'Error'
                elif warnings > 5:
                    status = 'Warning'  
                else:
                    status = 'Healthy'
                
                enhanced_components[component] = {
                    'name': component,
                    'status': status,
                    'health_score': health_score,
                    'details': f"{total_entries} entries, {errors} errors, {warnings} warnings",
                    'issues': [f"{errors} errors detected", f"{warnings} warnings logged"] if errors > 0 or warnings > 0 else [],
                    'recommendations': [f"Monitor {component} component for recurring issues"] if errors > 0 else []
                }
            
            return enhanced_components
            
        except Exception as e:
            print(f"⚠️ Error extracting component analysis: {e}")
            return {}
    
    def _extract_ai_analysis(self, data):
        """Extract AI analysis information"""
        if data is None or not isinstance(data, dict):
            return {}
        
        try:
            ai_analysis = {
                'classification': 'Standard Analysis',
                'anomaly_detection': {
                    'anomalies_found': 0,
                    'severity_distribution': 'Normal',
                    'pattern_analysis': 'No unusual patterns detected'
                },
                'intelligent_insights': [],
                'confidence_score': 85
            }
            
            # Extract ML insights if available
            ml_insights = data.get('ml_insights')
            if ml_insights:
                ai_analysis['classification'] = 'ML-Enhanced Analysis'
                ai_analysis['confidence_score'] = 95
                ai_analysis['intelligent_insights'].append('Machine Learning pattern recognition applied')
            
            # Extract RAG insights if available
            rag_insights = data.get('rag_insights') or data.get('dynamic_rag_analysis')
            if rag_insights and not rag_insights.get('error'):
                ai_analysis['classification'] = 'AI-Enhanced Analysis'
                ai_analysis['confidence_score'] = 98
                
                sources_used = rag_insights.get('analysis_metadata', {}).get('knowledge_sources_used', 0)
                if sources_used > 0:
                    ai_analysis['intelligent_insights'].append(f'Dynamic RAG system consulted {sources_used} knowledge sources')
                
                if rag_insights.get('ai_response'):
                    ai_analysis['intelligent_insights'].append('Expert AI analysis and recommendations generated')
            
            return ai_analysis
            
        except Exception as e:
            print(f"⚠️ Error extracting AI analysis: {e}")
            return {}
    
    def _extract_validation_steps(self, data):
        """Extract validation steps for frontend display"""
        if data is None or not isinstance(data, dict):
            return []
        
        try:
            validation_steps = []
            
            # Generate validation steps based on findings
            summary = data.get('summary', {})
            critical_count = summary.get('critical_count', 0)
            error_count = summary.get('error_count', 0)
            
            if critical_count > 0:
                validation_steps.append({
                    'id': 'critical_review',
                    'title': 'Critical Issue Review',
                    'description': f'Review and address {critical_count} critical issues identified',
                    'status': 'required',
                    'priority': 'critical'
                })
            
            if error_count > 0:
                validation_steps.append({
                    'id': 'error_analysis',
                    'title': 'Error Analysis',
                    'description': f'Investigate and resolve {error_count} error conditions',
                    'status': 'recommended',
                    'priority': 'high'
                })
            
            validation_steps.append({
                'id': 'monitoring_setup',
                'title': 'Monitoring Configuration',
                'description': 'Verify monitoring and alerting configurations are optimal',
                'status': 'recommended',
                'priority': 'medium'
            })
            
            return validation_steps
            
        except Exception as e:
            print(f"⚠️ Error extracting validation steps: {e}")
            return []
