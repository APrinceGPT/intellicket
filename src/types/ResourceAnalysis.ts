// TypeScript interfaces for Resource Analyzer data structures
export interface ResourceCandidate {
  name: string;
  count: string;
  process_type: string;
  details: Record<string, unknown>;
}

export interface PerformanceMetrics {
  total_scan_count: number;
  high_impact_processes: number;
  process_types: string[];
  optimization_potential: 'Low' | 'Medium' | 'High';
}

export interface ResourceAnalysisData {
  analysis_type: string;
  status: string;
  summary: string;
  details: string[];
  recommendations: string[];
  severity: 'low' | 'medium' | 'high' | 'critical';
  candidates?: ResourceCandidate[];
  performance_metrics?: PerformanceMetrics;
  ml_insights?: Record<string, unknown>;
  rag_insights?: Record<string, unknown>;
  metadata?: {
    files_processed: number;
    xml_files: number;
    txt_files: number;
    processes_found: number;
    busy_processes_found: number;
    exclusion_candidates: number;
  };
  [key: string]: unknown;
}

export interface ResourceMetric {
  label: string;
  value: string | number;
  icon: string;
  color?: string;
  trend?: 'up' | 'down' | 'stable';
}
