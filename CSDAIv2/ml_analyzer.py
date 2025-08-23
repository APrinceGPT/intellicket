"""
Machine Learning Enhanced Log Analyzer
Provides intelligent analysis, anomaly detection, and predictive insights for cybersecurity logs
Uses free, open-source ML libraries for local processing
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest, RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix
import joblib
import os
import re
from datetime import datetime, timedelta
from typing import Dict, List, Any, Tuple
import warnings
warnings.filterwarnings('ignore')

class MLLogAnalyzer:
    """Machine Learning powered log analyzer for enhanced cybersecurity insights"""
    
    def __init__(self, model_dir: str = "ml_models"):
        self.model_dir = model_dir
        self.anomaly_detector = None
        self.severity_classifier = None
        self.log_vectorizer = None
        self.scaler = StandardScaler()
        
        # Ensure model directory exists
        os.makedirs(model_dir, exist_ok=True)
        
        # Load existing models if available
        self._load_models()
    
    def _load_models(self):
        """Load pre-trained models if they exist"""
        try:
            anomaly_path = os.path.join(self.model_dir, "anomaly_detector.joblib")
            classifier_path = os.path.join(self.model_dir, "severity_classifier.joblib")
            vectorizer_path = os.path.join(self.model_dir, "log_vectorizer.joblib")
            scaler_path = os.path.join(self.model_dir, "scaler.joblib")
            
            if os.path.exists(anomaly_path):
                self.anomaly_detector = joblib.load(anomaly_path)
            if os.path.exists(classifier_path):
                self.severity_classifier = joblib.load(classifier_path)
            if os.path.exists(vectorizer_path):
                self.log_vectorizer = joblib.load(vectorizer_path)
            if os.path.exists(scaler_path):
                self.scaler = joblib.load(scaler_path)
                
        except Exception as e:
            print(f"Warning: Could not load existing models: {e}")
    
    def _save_models(self):
        """Save trained models for future use"""
        try:
            if self.anomaly_detector:
                joblib.dump(self.anomaly_detector, os.path.join(self.model_dir, "anomaly_detector.joblib"))
            if self.severity_classifier:
                joblib.dump(self.severity_classifier, os.path.join(self.model_dir, "severity_classifier.joblib"))
            if self.log_vectorizer:
                joblib.dump(self.log_vectorizer, os.path.join(self.model_dir, "log_vectorizer.joblib"))
            if self.scaler:
                joblib.dump(self.scaler, os.path.join(self.model_dir, "scaler.joblib"))
        except Exception as e:
            print(f"Warning: Could not save models: {e}")
    
    def parse_log_entries(self, log_content: str) -> pd.DataFrame:
        """Parse log content into structured DataFrame for ML analysis"""
        entries = []
        lines = log_content.strip().split('\n')
        
        for line in lines:
            if not line.strip():
                continue
                
            entry = self._parse_single_log_entry(line)
            if entry:
                entries.append(entry)
        
        return pd.DataFrame(entries)
    
    def _parse_single_log_entry(self, line: str) -> Dict[str, Any]:
        """Parse a single log entry into structured data"""
        # Enhanced regex patterns for various log formats including DS Agent
        patterns = [
            # DS Agent format: 2025-07-25 00:03:47.451678 [+0100]: [Component/Level] | Message | Source | ThreadID
            r'(?P<timestamp>\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}\.\d+)\s+\[(?P<timezone>[^\]]+)\]:\s+\[(?P<component>[^/]+)/(?P<level>\d+)\]\s+\|\s+(?P<message>[^|]+?)\s+\|\s+(?P<source>[^|]+?)\s+\|\s+(?P<thread_id>.*)',
            # DS Agent alternative: timestamp [timezone]: [component/level] | message
            r'(?P<timestamp>\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}\.\d+)\s+\[(?P<timezone>[^\]]+)\]:\s+\[(?P<component>[^/]+)/(?P<level>\d+)\]\s+\|\s+(?P<message>.*)',
            # Standard format: 2024-08-12 10:00:00 LEVEL [Component] Message
            r'(?P<timestamp>\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})\s+(?P<level>\w+)\s+\[(?P<component>[^\]]+)\]\s+(?P<message>.*)',
            # Alternative format: 2024-08-12 10:00:00 LEVEL Component: Message
            r'(?P<timestamp>\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})\s+(?P<level>\w+)\s+(?P<component>\w+):\s+(?P<message>.*)',
            # Simple format: 2024-08-12 10:00:00 LEVEL Message
            r'(?P<timestamp>\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})\s+(?P<level>\w+)\s+(?P<message>.*)',
        ]
        
        for pattern in patterns:
            match = re.match(pattern, line.strip())
            if match:
                entry = match.groupdict()
                
                # Add derived features for ML
                entry['message_length'] = len(entry['message'])
                entry['has_error_keywords'] = any(keyword in entry['message'].lower() 
                                                for keyword in ['error', 'failed', 'exception', 'crash'])
                entry['has_warning_keywords'] = any(keyword in entry['message'].lower() 
                                                  for keyword in ['warning', 'timeout', 'retry'])
                entry['has_critical_keywords'] = any(keyword in entry['message'].lower() 
                                                   for keyword in ['critical', 'fatal', 'emergency'])
                entry['numeric_codes'] = len(re.findall(r'\b\d{3,}\b', entry['message']))
                entry['ip_addresses'] = len(re.findall(r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b', entry['message']))
                
                # DS Agent specific features
                entry['is_command'] = 'command' in entry['message'].lower() or entry.get('component', '').lower() == 'cmd'
                entry['is_heartbeat'] = 'heartbeat' in entry.get('component', '').lower()
                entry['is_connection'] = any(conn in entry['message'].lower() for conn in ['connection', 'connect', 'disconnect'])
                entry['has_http'] = 'http' in entry['message'].lower()
                entry['has_lua_error'] = '.lua:' in entry['message']
                entry['thread_id_present'] = bool(entry.get('thread_id'))
                entry['source_file_present'] = bool(entry.get('source'))
                entry['metrics_failure'] = 'metrics failed' in entry['message'].lower()
                entry['amsp_related'] = 'amsp' in entry['message'].lower() or 'AMSP' in entry['message']
                
                # Convert numeric level to meaningful severity for DS Agent logs
                level_num = entry.get('level', '0')
                if level_num.isdigit():
                    level_mapping = {'1': 'CRITICAL', '2': 'WARNING', '3': 'INFO', '4': 'DEBUG', '5': 'TRACE'}
                    entry['severity'] = level_mapping.get(level_num, 'UNKNOWN')
                else:
                    entry['severity'] = entry.get('level', 'UNKNOWN').upper()
                
                # Extract hour for time-based analysis (handle microseconds)
                try:
                    # Try DS agent format first (with microseconds)
                    if '.' in entry['timestamp']:
                        dt = datetime.strptime(entry['timestamp'].split('.')[0], '%Y-%m-%d %H:%M:%S')
                    else:
                        dt = datetime.strptime(entry['timestamp'], '%Y-%m-%d %H:%M:%S')
                    entry['hour'] = dt.hour
                    entry['day_of_week'] = dt.weekday()
                except:
                    entry['hour'] = 0
                    entry['day_of_week'] = 0
                
                return entry
        
        return None
    
    def detect_anomalies(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Detect anomalous log entries using Isolation Forest"""
        if df.empty:
            return {'anomalies': [], 'anomaly_score': 0, 'total_entries': 0}
        
        # Prepare features for anomaly detection
        features = self._extract_anomaly_features(df)
        
        if features.empty:
            return {'anomalies': [], 'anomaly_score': 0, 'total_entries': len(df)}
        
        # Train anomaly detector if not exists or retrain with new data
        if self.anomaly_detector is None or len(features) > 100:
            self.anomaly_detector = IsolationForest(
                contamination=0.1,  # Expect 10% anomalies
                random_state=42,
                n_estimators=100
            )
            
            # Scale features
            features_scaled = self.scaler.fit_transform(features)
            self.anomaly_detector.fit(features_scaled)
            self._save_models()
        else:
            features_scaled = self.scaler.transform(features)
        
        # Predict anomalies
        anomaly_predictions = self.anomaly_detector.predict(features_scaled)
        anomaly_scores = self.anomaly_detector.decision_function(features_scaled)
        
        # Identify anomalous entries
        anomalies = []
        for idx, (prediction, score) in enumerate(zip(anomaly_predictions, anomaly_scores)):
            if prediction == -1:  # Anomaly detected
                anomaly_entry = {
                    'index': idx,
                    'timestamp': df.iloc[idx]['timestamp'],
                    'level': df.iloc[idx]['level'],
                    'message': df.iloc[idx]['message'],
                    'anomaly_score': score,
                    'confidence': abs(score)
                }
                anomalies.append(anomaly_entry)
        
        # Sort by confidence (most anomalous first)
        anomalies.sort(key=lambda x: x['confidence'], reverse=True)
        
        return {
            'anomalies': anomalies,
            'anomaly_score': len(anomalies) / len(df) * 100,
            'total_entries': len(df),
            'anomaly_count': len(anomalies)
        }
    
    def _extract_anomaly_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Extract numerical features for anomaly detection"""
        features = []
        
        for _, row in df.iterrows():
            feature_vector = [
                row.get('message_length', 0),
                int(row.get('has_error_keywords', False)),
                int(row.get('has_warning_keywords', False)),
                int(row.get('has_critical_keywords', False)),
                row.get('numeric_codes', 0),
                row.get('ip_addresses', 0),
                row.get('hour', 0),
                row.get('day_of_week', 0),
                1 if row.get('severity', '').upper() == 'CRITICAL' else 0,
                1 if row.get('severity', '').upper() == 'WARNING' else 0,
                1 if row.get('level', '').upper() == 'ERROR' else 0,
                # DS Agent specific features
                int(row.get('is_command', False)),
                int(row.get('is_heartbeat', False)),
                int(row.get('is_connection', False)),
                int(row.get('has_http', False)),
                int(row.get('has_lua_error', False)),
                int(row.get('thread_id_present', False)),
                int(row.get('metrics_failure', False)),
                int(row.get('amsp_related', False)),
            ]
            features.append(feature_vector)
        
        feature_names = [
            'message_length', 'has_error_keywords', 'has_warning_keywords',
            'has_critical_keywords', 'numeric_codes', 'ip_addresses',
            'hour', 'day_of_week', 'is_critical', 'is_warning', 'is_error',
            'is_command', 'is_heartbeat', 'is_connection', 'has_http',
            'has_lua_error', 'thread_id_present', 'metrics_failure', 'amsp_related'
        ]
        
        return pd.DataFrame(features, columns=feature_names)
    
    def classify_severity(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Intelligently classify log entry severity using ML"""
        if df.empty:
            return {'predictions': [], 'confidence_scores': []}
        
        # Prepare text features
        if self.log_vectorizer is None:
            self.log_vectorizer = TfidfVectorizer(
                max_features=1000,
                stop_words='english',
                ngram_range=(1, 2)
            )
            
            # Train on existing log messages
            messages = df['message'].fillna('').tolist()
            self.log_vectorizer.fit(messages)
        
        # Transform messages to feature vectors
        message_features = self.log_vectorizer.transform(df['message'].fillna(''))
        
        # If we don't have a trained classifier, use rule-based classification
        if self.severity_classifier is None:
            predictions = self._rule_based_severity_classification(df)
            confidences = [0.8] * len(predictions)  # Medium confidence for rule-based
        else:
            predictions = self.severity_classifier.predict(message_features)
            confidences = self.severity_classifier.predict_proba(message_features).max(axis=1)
        
        return {
            'predictions': predictions.tolist() if hasattr(predictions, 'tolist') else predictions,
            'confidence_scores': confidences.tolist() if hasattr(confidences, 'tolist') else confidences
        }
    
    def _rule_based_severity_classification(self, df: pd.DataFrame) -> List[str]:
        """Enhanced rule-based severity classification for DS Agent logs"""
        severities = []
        
        for _, row in df.iterrows():
            message = row.get('message', '').lower()
            level = row.get('level', '').upper()
            severity_mapped = row.get('severity', '').upper()
            component = row.get('component', '').lower()
            
            # DS Agent specific critical indicators
            if (severity_mapped == 'CRITICAL' or level == '1' or 
                any(word in message for word in ['crash', 'fatal', 'emergency', 'system failure', 'scan engine crashed'])):
                severity = 'CRITICAL'
            
            # DS Agent high severity indicators
            elif (severity_mapped == 'WARNING' or level == '2' or
                  row.get('metrics_failure', False) or
                  row.get('has_lua_error', False) or
                  any(word in message for word in ['error', 'failed', 'exception', 'denied', 'timeout', 'not_support'])):
                severity = 'HIGH'
            
            # Medium severity for connection issues and commands
            elif (row.get('is_connection', False) or 
                  row.get('is_command', False) or
                  'heartbeat' in component or
                  any(word in message for word in ['warning', 'retry', 'slow', 'notification'])):
                severity = 'MEDIUM'
            
            # Low severity for normal operations
            else:
                severity = 'LOW'
            
            severities.append(severity)
        
        return severities
    
    def analyze_patterns(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze patterns in log data using clustering"""
        if df.empty or len(df) < 5:
            return {'clusters': [], 'pattern_summary': 'Insufficient data for pattern analysis'}
        
        # Prepare features for clustering
        if self.log_vectorizer is None:
            self.log_vectorizer = TfidfVectorizer(
                max_features=500,
                stop_words='english',
                ngram_range=(1, 2)
            )
            messages = df['message'].fillna('').tolist()
            self.log_vectorizer.fit(messages)
        
        message_features = self.log_vectorizer.transform(df['message'].fillna(''))
        
        # Determine optimal number of clusters (max 5 for readability)
        n_clusters = min(5, max(2, len(df) // 10))
        
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        cluster_labels = kmeans.fit_predict(message_features)
        
        # Analyze clusters
        clusters = []
        for cluster_id in range(n_clusters):
            cluster_mask = cluster_labels == cluster_id
            cluster_entries = df[cluster_mask]
            
            if len(cluster_entries) > 0:
                # Get most common words in this cluster
                cluster_messages = ' '.join(cluster_entries['message'].fillna(''))
                common_levels = cluster_entries['level'].value_counts().head(3).to_dict()
                
                cluster_info = {
                    'cluster_id': cluster_id,
                    'entry_count': len(cluster_entries),
                    'percentage': len(cluster_entries) / len(df) * 100,
                    'common_levels': common_levels,
                    'sample_messages': cluster_entries['message'].head(3).tolist(),
                    'time_distribution': self._analyze_time_distribution(cluster_entries)
                }
                clusters.append(cluster_info)
        
        # Sort clusters by size
        clusters.sort(key=lambda x: x['entry_count'], reverse=True)
        
        return {
            'clusters': clusters,
            'pattern_summary': f"Identified {len(clusters)} distinct log patterns",
            'total_entries_analyzed': len(df)
        }
    
    def _analyze_time_distribution(self, cluster_df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze time distribution of cluster entries"""
        if 'hour' not in cluster_df.columns:
            return {'peak_hours': [], 'time_pattern': 'Unknown'}
        
        hour_counts = cluster_df['hour'].value_counts().head(3)
        peak_hours = hour_counts.index.tolist()
        
        return {
            'peak_hours': peak_hours,
            'time_pattern': 'Business hours' if any(9 <= hour <= 17 for hour in peak_hours) else 'Off hours'
        }
    
    def generate_ml_insights(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Generate comprehensive ML-powered insights"""
        insights = {
            'overview': {
                'total_entries': len(df),
                'analysis_timestamp': datetime.now().isoformat(),
                'ml_features_used': ['anomaly_detection', 'severity_classification', 'pattern_analysis', 'ds_agent_analysis']
            }
        }
        
        if not df.empty:
            # Run all ML analyses
            insights['anomaly_analysis'] = self.detect_anomalies(df)
            insights['severity_analysis'] = self.classify_severity(df)
            insights['pattern_analysis'] = self.analyze_patterns(df)
            
            # DS Agent specific analysis
            insights['ds_agent_analysis'] = self._analyze_ds_agent_patterns(df)
            
            # Generate summary recommendations
            insights['recommendations'] = self._generate_recommendations(insights)
        else:
            insights['error'] = 'No log entries to analyze'
        
        return insights
    
    def _analyze_ds_agent_patterns(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze DS Agent specific patterns and behaviors"""
        if df.empty:
            return {}
        
        analysis = {
            'component_health': {},
            'connection_patterns': {},
            'command_frequency': {},
            'error_patterns': {},
            'performance_indicators': {}
        }
        
        # Component health analysis
        components = df['component'].value_counts() if 'component' in df.columns else {}
        total_entries = len(df)
        
        for component, count in components.items():
            if component and component != 'nan':
                component_df = df[df['component'] == component]
                warnings = component_df[component_df.get('severity', '') == 'WARNING'].shape[0]
                errors = component_df[component_df.get('has_lua_error', False) == True].shape[0]
                
                analysis['component_health'][component] = {
                    'total_entries': count,
                    'percentage': (count / total_entries) * 100,
                    'warning_count': warnings,
                    'error_count': errors,
                    'health_score': max(0, 100 - (warnings * 5) - (errors * 10))
                }
        
        # Connection pattern analysis
        connection_entries = df[df.get('is_connection', False) == True] if 'is_connection' in df.columns else pd.DataFrame()
        heartbeat_entries = df[df.get('is_heartbeat', False) == True] if 'is_heartbeat' in df.columns else pd.DataFrame()
        
        analysis['connection_patterns'] = {
            'total_connection_events': len(connection_entries),
            'heartbeat_frequency': len(heartbeat_entries),
            'connection_health': 'healthy' if len(connection_entries) > 0 else 'no_data'
        }
        
        # Command analysis
        command_entries = df[df.get('is_command', False) == True] if 'is_command' in df.columns else pd.DataFrame()
        if not command_entries.empty:
            command_types = command_entries['message'].str.extract(r'command (\w+)', expand=False).value_counts()
            analysis['command_frequency'] = command_types.head(10).to_dict()
        
        # AMSP error pattern analysis
        amsp_entries = df[df.get('amsp_related', False) == True] if 'amsp_related' in df.columns else pd.DataFrame()
        metrics_failures = df[df.get('metrics_failure', False) == True] if 'metrics_failure' in df.columns else pd.DataFrame()
        
        analysis['error_patterns'] = {
            'amsp_related_entries': len(amsp_entries),
            'metrics_failures': len(metrics_failures),
            'common_failures': []
        }
        
        if not metrics_failures.empty:
            failure_types = metrics_failures['message'].value_counts().head(5)
            analysis['error_patterns']['common_failures'] = failure_types.to_dict()
        
        return analysis
    
    def _generate_recommendations(self, insights: Dict[str, Any]) -> List[str]:
        """Generate intelligent recommendations based on ML analysis"""
        recommendations = []
        
        # DS Agent-specific recommendations
        ds_analysis = insights.get('ds_agent_analysis', {})
        if ds_analysis:
            # Component health recommendations
            component_health = ds_analysis.get('component_health', {})
            for component, health in component_health.items():
                if health['health_score'] < 70:
                    recommendations.append(
                        f"⚠️ Component '{component}' health score: {health['health_score']:.0f}%. "
                        f"Found {health['warning_count']} warnings, {health['error_count']} errors."
                    )
            
            # AMSP-specific recommendations
            error_patterns = ds_analysis.get('error_patterns', {})
            metrics_failures = error_patterns.get('metrics_failures', 0)
            if metrics_failures > 10:
                recommendations.append(
                    f"🔧 {metrics_failures} device control metrics failures detected. "
                    "This is typically normal for systems without device control enabled."
                )
            
            # Connection health recommendations
            connection_patterns = ds_analysis.get('connection_patterns', {})
            if connection_patterns.get('connection_health') == 'no_data':
                recommendations.append(
                    "📡 No connection events detected. Verify agent connectivity to Deep Security Manager."
                )
        
        # Anomaly-based recommendations
        anomaly_count = insights.get('anomaly_analysis', {}).get('anomaly_count', 0)
        if anomaly_count > 0:
            recommendations.append(
                f"🔍 {anomaly_count} anomalous log entries detected. "
                "Review these entries for potential security incidents or system issues."
            )
        
        # Severity-based recommendations
        severity_analysis = insights.get('severity_analysis', {})
        predictions = severity_analysis.get('predictions', [])
        if predictions:
            critical_count = predictions.count('CRITICAL')
            high_count = predictions.count('HIGH')
            
            if critical_count > 0:
                recommendations.append(
                    f"🚨 {critical_count} critical-severity entries identified. "
                    "Immediate investigation recommended."
                )
            elif high_count > 0:
                recommendations.append(
                    f"⚠️ {high_count} high-severity entries found. "
                    "Schedule review within 24 hours."
                )
        
        # Pattern-based recommendations
        pattern_analysis = insights.get('pattern_analysis', {})
        clusters = pattern_analysis.get('clusters', [])
        if len(clusters) > 3:
            recommendations.append(
                f"📊 {len(clusters)} distinct log patterns detected. "
                "Consider consolidating similar issues or improving logging consistency."
            )
        
        if not recommendations:
            recommendations.append("✅ No significant issues detected. DS Agent appears to be operating normally.")
        
        return recommendations

def enhance_analysis_with_ml(log_content: str, analysis_type: str = 'ds_logs') -> Dict[str, Any]:
    """
    Enhance existing log analysis with ML insights
    
    Args:
        log_content: Raw log file content
        analysis_type: Type of analysis being performed
    
    Returns:
        Dict containing ML-enhanced analysis results
    """
    ml_analyzer = MLLogAnalyzer()
    
    # Parse log content
    df = ml_analyzer.parse_log_entries(log_content)
    
    # Generate ML insights
    ml_insights = ml_analyzer.generate_ml_insights(df)
    
    # Add analysis type context
    ml_insights['analysis_type'] = analysis_type
    ml_insights['ml_version'] = '1.0'
    
    return ml_insights

if __name__ == "__main__":
    # Test the ML analyzer
    test_log = """
2024-08-12 10:00:00 INFO [DS Agent] Service started successfully
2024-08-12 10:00:01 WARNING [DS Agent] Connection timeout detected
2024-08-12 10:00:02 ERROR [DS Agent] Failed to connect after 3 attempts
2024-08-12 10:00:03 CRITICAL [AM] Scan engine crashed
"""
    
    results = enhance_analysis_with_ml(test_log)
    print("ML Analysis Results:")
    for key, value in results.items():
        print(f"{key}: {value}")
