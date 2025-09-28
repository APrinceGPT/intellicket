// Intellicket Unified Admin Interface - Type Definitions
// Comprehensive type system for managing both CSDAIv2 backend and Intellicket frontend

export interface SystemStatus {
  id: string;
  name: string;
  status: 'online' | 'offline' | 'maintenance' | 'degraded' | 'starting' | 'stopping';
  health: 'healthy' | 'warning' | 'critical' | 'unknown';
  uptime: number;
  lastChecked: Date;
  version?: string;
  url?: string;
}

export interface UnifiedSystemOverview {
  backend: SystemStatus;
  frontend: SystemStatus;
  overall: SystemStatus;
  components: {
    analyzers: ComponentStatus[];
    ml_system: ComponentStatus;
    rag_system: ComponentStatus;
    database: ComponentStatus;
    api: ComponentStatus;
  };
}

export interface ComponentStatus {
  id: string;
  name: string;
  status: 'enabled' | 'disabled' | 'error' | 'maintenance';
  health: 'healthy' | 'warning' | 'critical' | 'unknown';
  lastChecked: Date;
  dependencies?: string[];
  metrics?: ComponentMetrics;
}

export interface ComponentMetrics {
  cpu_usage?: number;
  memory_usage?: number;
  response_time?: number;
  success_rate?: number;
  error_count?: number;
  requests_per_minute?: number;
}

export interface AnalyzerInfo {
  id: string;
  name: string;
  display_name: string;
  description: string;
  status: 'enabled' | 'disabled' | 'maintenance' | 'error';
  health: ComponentStatus['health'];
  usage_stats: {
    total_runs: number;
    success_rate: number;
    avg_duration: number;
    last_used: Date | null;
  };
  dependencies: string[];
  config: Record<string, string | number | boolean>;
}

export interface FileUploadStats {
  total_files: number;
  total_size_bytes: number;
  files_by_type: Record<string, number>;
  files_by_analyzer: Record<string, number>;
  upload_trends: {
    date: string;
    count: number;
    size_bytes: number;
  }[];
  recent_uploads: {
    timestamp: Date;
    filename: string;
    size_bytes: number;
    analyzer: string;
    status: 'processing' | 'completed' | 'failed';
  }[];
}

export interface SystemMetrics {
  timestamp: Date;
  backend: {
    cpu_usage: number;
    memory_usage: number;
    disk_usage: number;
    active_sessions: number;
    response_time: number;
  };
  frontend: {
    active_users: number;
    page_views: number;
    bounce_rate: number;
    avg_session_duration: number;
  };
  analyzers: {
    total_analyses: number;
    active_analyses: number;
    queue_length: number;
    avg_processing_time: number;
  };
}

export interface MaintenanceMode {
  enabled: boolean;
  message: string;
  scheduled_start?: Date;
  scheduled_end?: Date;
  affected_systems: ('backend' | 'frontend' | 'analyzers')[];
  priority: 'low' | 'medium' | 'high' | 'critical';
}

export interface SystemAlert {
  id: string;
  level: 'info' | 'warning' | 'error' | 'critical';
  component: string;
  title: string;
  message: string;
  timestamp: Date;
  acknowledged: boolean;
  resolved: boolean;
  metadata?: Record<string, string | number | boolean>;
}

export interface SessionInfo {
  id: string;
  created_at: Date;
  last_activity: Date;
  status: 'active' | 'processing' | 'completed' | 'failed' | 'expired';
  analyzer_type?: string;
  file_count: number;
  total_size_bytes: number;
  progress?: number;
  ip_address?: string;
  user_agent?: string;
}

export interface AdminAction {
  id: string;
  timestamp: Date;
  action: string;
  component: string;
  details: string;
  success: boolean;
  metadata?: Record<string, string | number | boolean>;
}

export interface ConfigurationItem {
  key: string;
  value: string | number | boolean | object;
  type: 'string' | 'number' | 'boolean' | 'object' | 'array';
  description: string;
  category: string;
  requires_restart: boolean;
  validation?: {
    min?: number;
    max?: number;
    pattern?: string;
    options?: string[];
  };
}

// API Response Types
export interface ApiResponse<T = unknown> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
  timestamp: Date;
}

export interface PaginatedResponse<T> extends ApiResponse<T[]> {
  pagination: {
    page: number;
    limit: number;
    total: number;
    total_pages: number;
  };
}

// WebSocket Event Types
export interface WebSocketEvent {
  type: 'system_status' | 'alert' | 'metrics' | 'session_update' | 'maintenance_update';
  data: unknown;
  timestamp: Date;
}

// Admin Dashboard State
export interface AdminDashboardState {
  systemOverview: UnifiedSystemOverview | null;
  alerts: SystemAlert[];
  metrics: SystemMetrics | null;
  sessions: SessionInfo[];
  maintenanceMode: MaintenanceMode;
  loading: boolean;
  error: string | null;
  lastUpdate: Date | null;
}

// Utility Types
export type SystemComponent = 'backend' | 'frontend' | 'analyzer' | 'ml' | 'rag' | 'database' | 'api';
export type AdminPermission = 'read' | 'control' | 'maintenance' | 'config' | 'admin';

export interface AdminUser {
  id: string;
  name: string;
  permissions: AdminPermission[];
  last_login?: Date;
}

// Hook Return Types
export interface UseSystemHealthReturn {
  overview: UnifiedSystemOverview | null;
  loading: boolean;
  error: string | null;
  refresh: () => void;
}

export interface UseWebSocketReturn {
  connected: boolean;
  lastMessage: WebSocketEvent | null;
  sendMessage: (message: unknown) => void;
  subscribe: (eventType: string, callback: (data: unknown) => void) => void;
  unsubscribe: (eventType: string) => void;
}