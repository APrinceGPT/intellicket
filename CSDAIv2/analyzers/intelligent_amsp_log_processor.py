# -*- coding: utf-8 -*-
"""
Intelligent AMSP Log Processing Algorithm
Comprehensive log analysis system for AMSP logs with AI-driven insights
"""

import re
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Tuple, Optional
from dataclasses import dataclass
from collections import defaultdict

@dataclass
class LogEntry:
    """Structured log entry with timestamp, level, and content"""
    timestamp: datetime
    raw_timestamp: str
    log_level: str
    component: str
    thread_id: str
    message: str
    source_file: str
    function_name: str
    line_number: int
    full_line: str
    severity_score: int
    category: str
    event_type: str

@dataclass
class LogProcessingResult:
    """Results from intelligent log processing"""
    total_lines: int
    processed_lines: int
    time_range: Tuple[datetime, datetime]
    critical_entries: List[LogEntry]
    warning_entries: List[LogEntry]
    error_entries: List[LogEntry]
    important_entries: List[LogEntry]
    pattern_analysis: Dict[str, Any]
    component_analysis: Dict[str, Any]
    timeline_analysis: Dict[str, Any]
    ai_insights: Dict[str, Any]

class IntelligentAMSPLogProcessor:
    """
    Intelligent log processor implementing the 3-phase algorithm:
    1. Latest date selection and time window optimization
    2. Priority-based filtering (errors/warnings first)  
    3. Important event detection for normal operations
    """
    
    def __init__(self):
        self.amsp_knowledge_base = self._load_amsp_knowledge()
        self.log_patterns = self._initialize_log_patterns()
        self.severity_weights = self._initialize_severity_weights()
        self.component_categories = self._initialize_component_categories()
        
    def _load_amsp_knowledge(self) -> Dict[str, Any]:
        """Load AMSP technical knowledge from JSON analysis"""
        return {
            "event_categories": {
                "malware_detection": {"range": "1000-1999", "priority": 10},
                "pattern_update": {"range": "2000-2999", "priority": 8},
                "scan_engine": {"range": "3000-3999", "priority": 7},
                "amsp_service": {"range": "4000-4999", "priority": 9}
            },
            "critical_components": [
                "TMCCSF.exe", "TMCCSc", "tmsservice.exe", 
                "tmcomm.sys", "tmlwf.sys", "tmbm.sys"
            ],
            "critical_processes": [
                "pattern_update", "service_startup", "driver_loading",
                "scan_engine_init", "behavior_monitoring"
            ],
            "error_indicators": [
                "failed", "error", "timeout", "corrupted", "unavailable",
                "denied", "invalid", "missing", "critical", "fatal"
            ]
        }
    
    def _initialize_log_patterns(self) -> Dict[str, re.Pattern]:
        """Initialize regex patterns for different log formats"""
        return {
            # ds_am.log format: 2025-08-12 00:00:14.778069: [ds_am/4] | [COMPONENT] message | file:line:function | thread:id::
            'ds_am': re.compile(
                r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d+):\s*\[([^/]+)/(\d+)\]\s*\|\s*\[([^\]]*)\]\s*([^|]+)\s*\|\s*([^|]+)\s*\|\s*([^:]+):([^:]+):(\d+)::'
            ),
            # ds_am-icrc.log format: 2025/05/03 06:47:22:746 +0000 [11038:139952553707072] [ WARN] [crc0ptn_load.cpp ( 47)] [LoadCrc0PatternFromFile] message
            'ds_am_icrc': re.compile(
                r'(\d{4}/\d{2}/\d{2} \d{2}:\d{2}:\d{2}:\d+) [+-]\d{4} \[(\d+):(\d+)\] \[\s*(\w+)\s*\] \[([^\]]+)\s*\(\s*(\d+)\)\] \[([^\]]+)\]\s*(.+)'
            ),
            # AMSP installation logs format: 2024/11/14 11:42:50.139,[07124:06044],[INFO],[Installation Library], ==> AMSP_INST_Init,,[instInstallationLibrary.cpp(199)]
            'amsp_install': re.compile(
                r'(\d{4}/\d{2}/\d{2} \d{2}:\d{2}:\d{2}\.\d+),\[([^:]+):([^\]]+)\],\[([^\]]+)\],\[([^\]]+)\],\s*([^,]+),,\[([^\(]+)\((\d+)\)\]'
            )
        }
    
    def _initialize_severity_weights(self) -> Dict[str, int]:
        """Initialize severity scoring weights"""
        return {
            # Log levels
            'FATAL': 100, 'CRITICAL': 95, 'ERROR': 80, 'WARN': 60, 'WARNING': 60,
            'INFO': 30, 'DEBUG': 10, 'TRACE': 5,
            
            # ds_am numeric levels (higher number = lower severity in ds_am logs)
            '1': 90, '2': 70, '3': 50, '4': 30, '5': 10,
            
            # Component criticality
            'SCAN': 85, 'PATTERN': 90, 'SERVICE': 95, 'DRIVER': 100,
            'ICRC': 75, 'TRENDX': 85, 'BPF': 80, 'BMTRAP': 75,
            
            # Error keywords
            'failed': 80, 'error': 85, 'timeout': 65, 'corrupted': 90,
            'unavailable': 85, 'denied': 75, 'critical': 95, 'fatal': 100
        }
    
    def _initialize_component_categories(self) -> Dict[str, Dict[str, Any]]:
        """Initialize AMSP component categories with importance"""
        return {
            "core_services": {
                "components": ["TMCCSc", "TMCCSF", "TMUCP"],
                "importance": 100,
                "keywords": ["service", "startup", "initialization"]
            },
            "scan_engines": {
                "components": ["SCAN", "RTSCAN", "TRENDX", "VSScan"],
                "importance": 95,
                "keywords": ["scan", "engine", "pattern", "virus"]
            },
            "behavior_monitoring": {
                "components": ["BMTRAP", "BPF", "BMEvt"],
                "importance": 90,
                "keywords": ["behavior", "monitoring", "bpf", "bmtrap"]
            },
            "network_security": {
                "components": ["ICRC", "SMARTSCAN", "CLOUD"],
                "importance": 85,
                "keywords": ["icrc", "network", "cloud", "smart"]
            },
            "pattern_management": {
                "components": ["PATTERN", "UPDATE", "DOWNLOAD"],
                "importance": 90,
                "keywords": ["pattern", "update", "download", "signature"]
            }
        }

    def process_logs_intelligently(self, file_paths: List[str], max_lines: int = 50000) -> LogProcessingResult:
        """
        Main intelligent processing algorithm implementing the 3-phase approach:
        
        Phase 1: Latest Date Selection & Time Window Optimization
        Phase 2: Priority-Based Filtering (Critical/Error/Warning First)
        Phase 3: Important Event Detection for Normal Operations
        """
        print("🧠 Starting Intelligent AMSP Log Processing...")
        
        # Phase 1: Latest Date Selection & Time Window Optimization
        print("📅 Phase 1: Latest Date Selection & Time Window Optimization")
        all_entries = []
        file_metadata = {}
        
        for file_path in file_paths:
            entries, metadata = self._extract_and_parse_logs(file_path)
            all_entries.extend(entries)
            file_metadata[file_path] = metadata
            print(f"   📁 {file_path}: {len(entries)} entries parsed")
        
        if not all_entries:
            raise ValueError("No valid log entries found in provided files")
        
        # Sort by timestamp and select optimal time window
        all_entries.sort(key=lambda x: x.timestamp, reverse=True)
        time_window_entries = self._select_optimal_time_window(all_entries, max_lines)
        
        print(f"   ⏰ Time window: {time_window_entries[-1].timestamp} to {time_window_entries[0].timestamp}")
        print(f"   📊 Selected {len(time_window_entries)} entries from latest time period")
        
        # Phase 2: Priority-Based Filtering (Critical/Error/Warning First)
        print("🚨 Phase 2: Priority-Based Filtering")
        prioritized_entries = self._prioritize_by_severity(time_window_entries)
        
        critical_entries = [e for e in prioritized_entries if e.severity_score >= 80]
        warning_entries = [e for e in prioritized_entries if 60 <= e.severity_score < 80]
        error_entries = [e for e in prioritized_entries if e.severity_score >= 70]
        
        print(f"   🔴 Critical entries: {len(critical_entries)}")
        print(f"   🟡 Warning entries: {len(warning_entries)}")
        print(f"   🔶 Error entries: {len(error_entries)}")
        
        # Phase 3: Important Event Detection for Normal Operations
        print("🔍 Phase 3: Important Event Detection")
        important_entries = self._detect_important_events(prioritized_entries)
        
        print(f"   ⭐ Important normal operations: {len(important_entries)}")
        
        # Advanced Analysis
        pattern_analysis = self._analyze_patterns(prioritized_entries)
        component_analysis = self._analyze_components(prioritized_entries)
        timeline_analysis = self._analyze_timeline(prioritized_entries)
        ai_insights = self._generate_ai_insights(prioritized_entries, pattern_analysis, component_analysis)
        
        result = LogProcessingResult(
            total_lines=len(all_entries),
            processed_lines=len(prioritized_entries),
            time_range=(all_entries[-1].timestamp, all_entries[0].timestamp),
            critical_entries=critical_entries,
            warning_entries=warning_entries,
            error_entries=error_entries,
            important_entries=important_entries,
            pattern_analysis=pattern_analysis,
            component_analysis=component_analysis,
            timeline_analysis=timeline_analysis,
            ai_insights=ai_insights
        )
        
        print("✅ Intelligent AMSP Log Processing Complete")
        return result
    
    def _extract_and_parse_logs(self, file_path: str) -> Tuple[List[LogEntry], Dict[str, Any]]:
        """Extract and parse logs from a single file"""
        entries = []
        metadata = {"file_path": file_path, "total_lines": 0, "parsed_lines": 0, "errors": []}
        
        # Try different encodings for AMSP log files
        encodings_to_try = ['utf-16-le', 'utf-16', 'utf-8', 'latin-1']
        
        for encoding in encodings_to_try:
            try:
                with open(file_path, 'r', encoding=encoding, errors='ignore') as f:
                    # Test read first line to validate encoding
                    f.seek(0)
                    first_line = f.readline().strip()
                    if not first_line or len(first_line) < 10:
                        continue
                    
                    # Reset and read all lines with this encoding
                    f.seek(0)
                    for line_num, line in enumerate(f, 1):
                        metadata["total_lines"] += 1
                        line = line.strip()
                        if not line:
                            continue
                        
                        entry = self._parse_log_line(line, line_num, file_path)
                        if entry:
                            entries.append(entry)
                            metadata["parsed_lines"] += 1
                        else:
                            metadata["errors"].append(f"Line {line_num}: Could not parse")
                    
                    # If we successfully parsed some entries, use this encoding
                    if entries:
                        print(f"📝 Successfully read file with {encoding} encoding")
                        break
                        
            except Exception as e:
                if encoding == encodings_to_try[-1]:  # Last encoding attempt
                    metadata["errors"].append(f"File read error: {str(e)}")
                continue
        
        return entries, metadata
    
    def _parse_log_line(self, line: str, line_num: int, file_path: str) -> Optional[LogEntry]:
        """Parse a single log line into structured LogEntry"""
        
        # Try different log formats
        for format_name, pattern in self.log_patterns.items():
            match = pattern.match(line)
            if match:
                return self._create_log_entry_from_match(match, format_name, line, line_num, file_path)
        
        # Fallback parsing for unrecognized formats
        return self._parse_fallback_format(line, line_num, file_path)
    
    def _create_log_entry_from_match(self, match: re.Match, format_name: str, line: str, line_num: int, file_path: str) -> LogEntry:
        """Create LogEntry from regex match based on format"""
        
        if format_name == 'ds_am':
            timestamp_str, component, level, tag, message, source_info, thread1, thread2, line_no = match.groups()
            timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S.%f')
            
            return LogEntry(
                timestamp=timestamp,
                raw_timestamp=timestamp_str,
                log_level=level,
                component=tag or component,
                thread_id=f"{thread1}:{thread2}",
                message=message.strip(),
                source_file=source_info.split(':')[0] if ':' in source_info else source_info,
                function_name=source_info.split(':')[1] if ':' in source_info and len(source_info.split(':')) > 1 else "",
                line_number=int(line_no) if line_no.isdigit() else 0,
                full_line=line,
                severity_score=self._calculate_severity_score(level, tag, message),
                category=self._categorize_entry(tag, message),
                event_type=self._determine_event_type(tag, message)
            )
            
        elif format_name == 'ds_am_icrc':
            timestamp_str, process_id, thread_id, level, source_file, line_no, function, message = match.groups()
            timestamp = datetime.strptime(timestamp_str, '%Y/%m/%d %H:%M:%S:%f')
            
            return LogEntry(
                timestamp=timestamp,
                raw_timestamp=timestamp_str,
                log_level=level,
                component="ICRC",
                thread_id=f"{process_id}:{thread_id}",
                message=message.strip(),
                source_file=source_file,
                function_name=function,
                line_number=int(line_no) if line_no.isdigit() else 0,
                full_line=line,
                severity_score=self._calculate_severity_score(level, "ICRC", message),
                category=self._categorize_entry("ICRC", message),  
                event_type=self._determine_event_type("ICRC", message)
            )
            
        elif format_name == 'amsp_install':
            timestamp_str, process_id, thread_id, level, component, message, source_file, line_no = match.groups()
            timestamp = datetime.strptime(timestamp_str, '%Y/%m/%d %H:%M:%S.%f')
            
            return LogEntry(
                timestamp=timestamp,
                raw_timestamp=timestamp_str,
                log_level=level,
                component=component,
                thread_id=f"{process_id}:{thread_id}",
                message=message.strip(),
                source_file=source_file,
                function_name="",  # Not available in this format
                line_number=int(line_no) if line_no.isdigit() else 0,
                full_line=line,
                severity_score=self._calculate_severity_score(level, component, message),
                category=self._categorize_entry(component, message),
                event_type=self._determine_event_type(component, message)
            )
        
        # Fallback for other formats
        return self._parse_fallback_format(line, line_num, file_path)
    
    def _parse_fallback_format(self, line: str, line_num: int, file_path: str) -> Optional[LogEntry]:
        """Fallback parser for unrecognized log formats"""
        
        # Try to extract timestamp from common patterns
        timestamp_patterns = [
            r'(\d{4}-\d{2}-\d{2}[T\s]\d{2}:\d{2}:\d{2}(?:\.\d+)?)',
            r'(\d{4}/\d{2}/\d{2}\s+\d{2}:\d{2}:\d{2})',
            r'(\d{2}/\d{2}/\d{4}\s+\d{2}:\d{2}:\d{2})'
        ]
        
        timestamp = None
        timestamp_str = ""
        
        for pattern in timestamp_patterns:
            match = re.search(pattern, line)
            if match:
                timestamp_str = match.group(1)
                try:
                    if 'T' in timestamp_str:
                        timestamp = datetime.fromisoformat(timestamp_str.replace('T', ' '))
                    elif '/' in timestamp_str:
                        if timestamp_str.count('/') == 2 and len(timestamp_str.split('/')[0]) == 4:
                            timestamp = datetime.strptime(timestamp_str, '%Y/%m/%d %H:%M:%S')
                        else:
                            timestamp = datetime.strptime(timestamp_str, '%m/%d/%Y %H:%M:%S')
                    else:
                        timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
                    break
                except ValueError:
                    continue
        
        if not timestamp:
            return None
        
        # Extract level and component if possible
        level_match = re.search(r'\b(FATAL|ERROR|WARN|WARNING|INFO|DEBUG|TRACE|CRITICAL)\b', line, re.IGNORECASE)
        level = level_match.group(1).upper() if level_match else "INFO"
        
        component_match = re.search(r'\[([A-Z_]+)\]|\b([A-Z_]{3,})\b', line)
        component = component_match.group(1) or component_match.group(2) if component_match else "UNKNOWN"
        
        return LogEntry(
            timestamp=timestamp,
            raw_timestamp=timestamp_str,
            log_level=level,
            component=component,
            thread_id="",
            message=line,
            source_file=file_path,
            function_name="",
            line_number=line_num,
            full_line=line,
            severity_score=self._calculate_severity_score(level, component, line),
            category=self._categorize_entry(component, line),
            event_type=self._determine_event_type(component, line)
        )
    
    def _select_optimal_time_window(self, entries: List[LogEntry], max_lines: int) -> List[LogEntry]:
        """Select optimal time window focusing on recent activity with issues"""
        
        if len(entries) <= max_lines:
            return entries
        
        # Strategy 1: Recent time window with error concentration
        recent_entries = entries[:max_lines]
        
        # Strategy 2: Find time windows with high error density
        error_entries = [e for e in entries if e.severity_score >= 70]
        
        if error_entries:
            # Find time windows around critical events
            critical_windows = []
            for error_entry in error_entries[:10]:  # Top 10 critical events
                window_start = error_entry.timestamp - timedelta(minutes=30)
                window_end = error_entry.timestamp + timedelta(minutes=30)
                
                window_entries = [
                    e for e in entries 
                    if window_start <= e.timestamp <= window_end
                ]
                critical_windows.extend(window_entries)
            
            # Remove duplicates and sort
            seen = set()
            unique_critical = []
            for entry in critical_windows:
                if entry.full_line not in seen:
                    seen.add(entry.full_line)
                    unique_critical.append(entry)
            
            unique_critical.sort(key=lambda x: x.timestamp, reverse=True)
            
            if len(unique_critical) >= max_lines * 0.7:
                return unique_critical[:max_lines]
        
        # Default: Most recent entries
        return recent_entries
    
    def _prioritize_by_severity(self, entries: List[LogEntry]) -> List[LogEntry]:
        """Prioritize entries by severity score and importance"""
        
        # Multi-criteria sorting
        def priority_key(entry: LogEntry) -> Tuple[int, int, datetime]:
            return (
                -entry.severity_score,  # Higher severity first (negative for desc order)
                -len([kw for kw in self.amsp_knowledge_base["error_indicators"] if kw in entry.message.lower()]),  # More error keywords first
                entry.timestamp  # More recent first
            )
        
        return sorted(entries, key=priority_key)
    
    def _detect_important_events(self, entries: List[LogEntry]) -> List[LogEntry]:
        """Detect important events in normal operations"""
        
        important_events = []
        
        # Important event patterns
        important_patterns = [
            # Service lifecycle
            r'service.*(start|stop|restart)',
            r'(initialization|startup|shutdown)',
            
            # Pattern and engine operations
            r'pattern.*(load|update|download|install)',
            r'engine.*(start|initialize|ready)',
            r'scan.*(begin|complete|finish)',
            
            # Configuration changes
            r'config.*(load|update|change|apply)',
            r'policy.*(update|apply|change)',
            
            # Performance metrics
            r'(metrics|performance|stats)',
            r'(cpu|memory|disk).*(usage|available)',
            
            # Network and connectivity
            r'(connect|disconnect|timeout)',
            r'(server|network|connection)',
            
            # Security events
            r'(quarantine|clean|detect|block)',
            r'(threat|malware|virus)'
        ]
        
        for entry in entries:
            if entry.severity_score < 60:  # Focus on non-error entries
                for pattern in important_patterns:
                    if re.search(pattern, entry.message, re.IGNORECASE):
                        important_events.append(entry)
                        break
        
        return important_events
    
    def _calculate_severity_score(self, level: str, component: str, message: str) -> int:
        """Calculate severity score based on multiple factors"""
        
        score = 0
        
        # Base score from log level
        score += self.severity_weights.get(level.upper(), 30)
        
        # Component importance
        score += self.severity_weights.get(component.upper(), 0)
        
        # Keyword analysis
        message_lower = message.lower()
        for keyword, weight in self.severity_weights.items():
            if keyword.lower() in message_lower and keyword.islower():
                score += weight
        
        # Critical error patterns
        critical_patterns = [
            r'failed.*start', r'cannot.*load', r'initialization.*failed',
            r'driver.*error', r'service.*unavailable', r'critical.*error'
        ]
        
        for pattern in critical_patterns:
            if re.search(pattern, message_lower):
                score += 20
        
        return min(score, 100)  # Cap at 100
    
    def _categorize_entry(self, component: str, message: str) -> str:
        """Categorize log entry based on component and message"""
        
        message_lower = message.lower()
        component_upper = component.upper()
        
        # Check component categories
        for category, info in self.component_categories.items():
            if component_upper in info["components"]:
                return category
                
            for keyword in info["keywords"]:
                if keyword in message_lower:
                    return category
        
        # Fallback categorization
        if any(kw in message_lower for kw in ['scan', 'virus', 'malware']):
            return 'scan_engines'
        elif any(kw in message_lower for kw in ['service', 'startup', 'daemon']):
            return 'core_services'
        elif any(kw in message_lower for kw in ['pattern', 'update', 'download']):
            return 'pattern_management'
        elif any(kw in message_lower for kw in ['network', 'connect', 'timeout']):
            return 'network_security'
        else:
            return 'general'
    
    def _determine_event_type(self, component: str, message: str) -> str:
        """Determine specific event type"""
        
        message_lower = message.lower()
        
        event_patterns = {
            'service_lifecycle': [r'start', r'stop', r'restart', r'shutdown'],
            'pattern_management': [r'pattern.*update', r'download', r'signature'],
            'scan_operations': [r'scan.*start', r'scan.*complete', r'scanning'],
            'error_conditions': [r'failed', r'error', r'timeout', r'unable'],
            'security_events': [r'detect', r'block', r'quarantine', r'threat'],
            'configuration': [r'config', r'policy', r'setting'],
            'performance': [r'metric', r'usage', r'performance', r'stats'],
            'network': [r'connect', r'network', r'timeout', r'server']
        }
        
        for event_type, patterns in event_patterns.items():
            for pattern in patterns:
                if re.search(pattern, message_lower):
                    return event_type
        
        return 'general'
    
    def _analyze_patterns(self, entries: List[LogEntry]) -> Dict[str, Any]:
        """Analyze patterns in log entries"""
        
        analysis = {
            'error_patterns': defaultdict(int),
            'component_patterns': defaultdict(int),
            'temporal_patterns': defaultdict(int),
            'severity_distribution': defaultdict(int),
            'event_type_distribution': defaultdict(int)
        }
        
        for entry in entries:
            # Error pattern analysis
            if entry.severity_score >= 70:
                for indicator in self.amsp_knowledge_base["error_indicators"]:
                    if indicator in entry.message.lower():
                        analysis['error_patterns'][indicator] += 1
            
            # Component analysis
            analysis['component_patterns'][entry.component] += 1
            
            # Temporal analysis (by hour)
            hour = entry.timestamp.hour
            analysis['temporal_patterns'][hour] += 1
            
            # Severity distribution
            if entry.severity_score >= 90:
                analysis['severity_distribution']['critical'] += 1
            elif entry.severity_score >= 70:
                analysis['severity_distribution']['error'] += 1
            elif entry.severity_score >= 50:
                analysis['severity_distribution']['warning'] += 1
            else:
                analysis['severity_distribution']['info'] += 1
            
            # Event type distribution
            analysis['event_type_distribution'][entry.event_type] += 1
        
        return dict(analysis)
    
    def _analyze_components(self, entries: List[LogEntry]) -> Dict[str, Any]:
        """Analyze component-specific patterns"""
        
        component_analysis = {}
        
        for entry in entries:
            component = entry.component
            if component not in component_analysis:
                component_analysis[component] = {
                    'total_entries': 0,
                    'error_count': 0,
                    'warning_count': 0,
                    'severity_avg': 0,
                    'categories': defaultdict(int),
                    'recent_errors': []
                }
            
            comp_data = component_analysis[component]
            comp_data['total_entries'] += 1
            
            if entry.severity_score >= 80:
                comp_data['error_count'] += 1
                comp_data['recent_errors'].append({
                    'timestamp': entry.timestamp.isoformat(),
                    'message': entry.message[:200],
                    'severity': entry.severity_score
                })
            elif entry.severity_score >= 60:
                comp_data['warning_count'] += 1
            
            comp_data['categories'][entry.category] += 1
        
        # Calculate averages
        for component, data in component_analysis.items():
            if data['total_entries'] > 0:
                data['error_rate'] = data['error_count'] / data['total_entries']
                data['warning_rate'] = data['warning_count'] / data['total_entries']
                
                # Keep only top 5 recent errors
                data['recent_errors'] = data['recent_errors'][:5]
        
        return component_analysis
    
    def _analyze_timeline(self, entries: List[LogEntry]) -> Dict[str, Any]:
        """Analyze temporal patterns and timeline"""
        
        if not entries:
            return {}
        
        timeline = {
            'start_time': entries[-1].timestamp.isoformat(),
            'end_time': entries[0].timestamp.isoformat(),
            'duration_hours': (entries[0].timestamp - entries[-1].timestamp).total_seconds() / 3600,
            'entries_per_hour': {},
            'error_timeline': [],
            'significant_events': []
        }
        
        # Hourly distribution
        hourly_counts = defaultdict(int)
        hourly_errors = defaultdict(int)
        
        for entry in entries:
            hour_key = entry.timestamp.strftime('%Y-%m-%d %H:00')
            hourly_counts[hour_key] += 1
            
            if entry.severity_score >= 70:
                hourly_errors[hour_key] += 1
                timeline['error_timeline'].append({
                    'timestamp': entry.timestamp.isoformat(),
                    'component': entry.component,
                    'message': entry.message[:150],
                    'severity': entry.severity_score
                })
        
        timeline['entries_per_hour'] = dict(hourly_counts)
        timeline['errors_per_hour'] = dict(hourly_errors)
        
        # Keep top 20 errors by severity
        timeline['error_timeline'] = sorted(
            timeline['error_timeline'], 
            key=lambda x: x['severity'], 
            reverse=True
        )[:20]
        
        return timeline
    
    def _generate_ai_insights(self, entries: List[LogEntry], pattern_analysis: Dict, component_analysis: Dict) -> Dict[str, Any]:
        """Generate AI-driven insights for RAG system"""
        
        insights = {
            'key_findings': [],
            'root_cause_indicators': [],
            'recommendations': [],
            'system_health_score': 0,
            'critical_components': [],
            'trend_analysis': {}
        }
        
        total_entries = len(entries)
        if total_entries == 0:
            return insights
        
        # Calculate system health score
        critical_count = len([e for e in entries if e.severity_score >= 90])
        error_count = len([e for e in entries if e.severity_score >= 70])
        warning_count = len([e for e in entries if e.severity_score >= 50])
        
        health_score = max(0, 100 - (critical_count * 10 + error_count * 5 + warning_count * 2))
        insights['system_health_score'] = min(health_score, 100)
        
        # Key findings
        if critical_count > 0:
            insights['key_findings'].append(f"CRITICAL: {critical_count} critical issues detected requiring immediate attention")
        
        if error_count > total_entries * 0.1:
            insights['key_findings'].append(f"HIGH ERROR RATE: {error_count} errors found ({error_count/total_entries*100:.1f}% of all entries)")
        
        # Component analysis
        for component, data in component_analysis.items():
            if data['error_rate'] > 0.2:  # More than 20% errors
                insights['critical_components'].append({
                    'component': component,
                    'error_rate': data['error_rate'],
                    'total_entries': data['total_entries'],
                    'issues': data['recent_errors'][:3]
                })
        
        # Pattern-based root cause indicators
        top_error_patterns = sorted(
            pattern_analysis.get('error_patterns', {}).items(),
            key=lambda x: x[1],
            reverse=True
        )[:5]
        
        for pattern, count in top_error_patterns:
            if count > 3:  # Recurring pattern
                insights['root_cause_indicators'].append({
                    'pattern': pattern,
                    'occurrences': count,
                    'suggestion': self._get_pattern_suggestion(pattern)
                })
        
        # Generate recommendations based on findings
        insights['recommendations'] = self._generate_contextual_recommendations(
            insights, pattern_analysis, component_analysis
        )
        
        return insights
    
    def _get_pattern_suggestion(self, pattern: str) -> str:
        """Get suggestion based on error pattern"""
        
        suggestions = {
            'failed': "Check system resources and dependencies. Review error logs for specific failure reasons.",
            'timeout': "Investigate network connectivity and increase timeout values if necessary.",
            'corrupted': "Verify file integrity and consider reinstalling affected components.",
            'unavailable': "Check service status and restart if needed. Verify system dependencies.",
            'denied': "Review permissions and security policies. Ensure proper access rights.",
            'critical': "Immediate investigation required. Check system stability and core services."
        }
        
        return suggestions.get(pattern, "Review system logs and documentation for troubleshooting steps.")
    
    def _generate_contextual_recommendations(self, insights: Dict, pattern_analysis: Dict, component_analysis: Dict) -> List[str]:
        """Generate contextual recommendations based on analysis"""
        
        recommendations = []
        
        # Health-based recommendations
        health_score = insights['system_health_score']
        
        if health_score < 50:
            recommendations.append("🚨 URGENT: System health is critically low. Immediate investigation and remediation required.")
        elif health_score < 70:
            recommendations.append("⚠️ WARNING: System health is degraded. Address identified issues promptly.")
        elif health_score < 90:
            recommendations.append("📊 NOTICE: Minor issues detected. Consider preventive maintenance.")
        else:
            recommendations.append("✅ GOOD: System appears healthy with minimal issues.")
        
        # Component-specific recommendations
        for comp_info in insights['critical_components']:
            component = comp_info['component']
            error_rate = comp_info['error_rate']
            
            if component in ['SCAN', 'TRENDX', 'PATTERN']:
                recommendations.append(f"🔧 {component}: High error rate ({error_rate:.1%}). Check pattern updates and engine configuration.")
            elif component in ['SERVICE', 'DRIVER']:
                recommendations.append(f"🔧 {component}: Service issues detected. Verify installation and restart services.")
            elif component == 'ICRC':
                recommendations.append(f"🔧 {component}: Network connectivity issues. Check proxy settings and server accessibility.")
        
        # Pattern-based recommendations
        error_patterns = pattern_analysis.get('error_patterns', {})
        
        if error_patterns.get('timeout', 0) > 5:
            recommendations.append("🌐 NETWORK: Multiple timeout errors detected. Check network connectivity and proxy configuration.")
        
        if error_patterns.get('failed', 0) > 10:
            recommendations.append("⚙️ SYSTEM: High number of failures. Consider system resource review and component reinstallation.")
        
        if error_patterns.get('corrupted', 0) > 2:
            recommendations.append("💾 DATA: Data corruption detected. Perform integrity checks and restore from backup if needed.")
        
        return recommendations