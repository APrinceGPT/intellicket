/**
 * PROPOSED: Modern API Response Format
 * 
 * This eliminates the "legacy format" conversion and creates a direct
 * backend-to-frontend API contract that's easier to maintain and extend.
 */

// Backend Python Response (JSON)
interface ModernAMSPAnalysisResponse {
  success: boolean;
  analysis_type: 'amsp_installation' | 'amsp_logs' | 'amsp_diagnostic';
  session_id: string;
  timestamp: string;
  
  // Core Analysis Data
  processing: {
    total_lines: number;
    processed_lines: number;
    success_rate: number;
    encoding_detected: string;
    processing_time_seconds: number;
  };
  
  // System Health & Severity
  health: {
    system_score: number; // 0-100
    status: 'critical' | 'warning' | 'caution' | 'healthy';
    overall_severity: 'low' | 'medium' | 'high' | 'critical';
  };
  
  // Issues & Events
  issues: {
    critical: AMSPLogEntry[];
    errors: AMSPLogEntry[];
    warnings: AMSPLogEntry[];
    important_events: AMSPLogEntry[];
  };
  
  // AI Enhancement Data
  ai_analysis: {
    applied: boolean;
    ml_enhanced: boolean;
    rag_enhanced: boolean;
    processing_mode: 'intelligent' | 'fallback' | 'legacy';
    recommendations: AIRecommendation[];
    key_findings: string[];
    root_cause_analysis?: RootCauseAnalysis[];
  };
  
  // Component Analysis
  components: {
    [component_name: string]: {
      total_entries: number;
      error_rate: number;
      status: 'healthy' | 'degraded' | 'failed';
      key_events: AMSPLogEntry[];
    };
  };
  
  // Timeline Analysis
  timeline: {
    start_time: string;
    end_time: string;
    duration_seconds: number;
    key_phases: TimelinePhase[];
  };
  
  // Raw Data (for advanced users)
  raw_data?: {
    pattern_analysis: Record<string, unknown>;
    statistical_data: Record<string, unknown>;
  };
}

interface AMSPLogEntry {
  timestamp: string;
  component: string;
  level: 'INFO' | 'WARN' | 'ERROR' | 'CRITICAL';
  message: string;
  event_type: string;
  severity_score: number;
  source_file?: string;
  line_number?: number;
}

interface AIRecommendation {
  priority: 'high' | 'medium' | 'low';
  category: 'security' | 'performance' | 'configuration' | 'maintenance';
  title: string;
  description: string;
  action_items: string[];
  impact: string;
}

interface RootCauseAnalysis {
  issue_type: string;
  pattern_detected: string;
  occurrences: number;
  severity: 'critical' | 'high' | 'medium' | 'low';
  root_cause: string;
  resolution_steps: string[];
  kb_reference?: string;
}

interface TimelinePhase {
  phase_name: string;
  start_time: string;
  end_time: string;
  status: 'completed' | 'failed' | 'partial';
  key_events: AMSPLogEntry[];
}

// Frontend React Component Interface (matches backend 1:1)
interface AMSPAnalysisResult extends ModernAMSPAnalysisResponse {
  // No conversion needed - direct mapping!
}