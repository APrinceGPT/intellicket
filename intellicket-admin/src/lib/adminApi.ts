/**
 * Intellicket Admin API Service
 * Comprehensive API service for communicating with CSDAIv2 backend admin endpoints
 * Provides type-safe methods for all admin operations with proper error handling
 */

// API Configuration
const BACKEND_URL = 'http://localhost:5003';
const ADMIN_API_BASE = `${BACKEND_URL}/admin`;

// Response Types
export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  message?: string;
  error?: string;
  timestamp: string;
}

export interface SystemOverview {
  backend: ComponentStatus;
  frontend: ComponentStatus;
  overall: ComponentStatus;
  components: {
    analyzers: ComponentStatus[];
    api: ComponentStatus;
    database: ComponentStatus;
    ml_system: ComponentStatus;
    rag_system: ComponentStatus;
    [key: string]: ComponentStatus | ComponentStatus[];
  };
  system_metrics?: SystemMetrics;
  last_updated: string;
}

export interface SystemMetrics {
  cpu: {
    percent: number;
    count_physical: number;
    count_logical: number;
    status: 'healthy' | 'warning' | 'critical';
  };
  memory: {
    percent: number;
    total: number;
    used: number;
    available: number;
    total_gb: number;
    used_gb: number;
    available_gb: number;
    status: 'healthy' | 'warning' | 'critical';
  };
  disk: {
    percent: number;
    total: number;
    used: number;
    free: number;
    total_gb: number;
    used_gb: number;
    free_gb: number;
    status: 'healthy' | 'warning' | 'critical';
  };
  network: {
    bytes_sent: number;
    bytes_recv: number;
    packets_sent: number;
    packets_recv: number;
    bytes_sent_mb: number;
    bytes_recv_mb: number;
  };
  system: {
    uptime: number;
    uptime_hours: number;
    boot_time: number;
    process_count: number;
  };
  timestamp: string;
}

export interface ProcessInfo {
  pid: number;
  name: string;
  cpu_percent: number;
  memory_mb: number;
  status: string;
  cmdline: string;
}

export interface ComponentStatus {
  id: string;
  name: string;
  status: 'online' | 'offline' | 'degraded' | 'maintenance' | 'enabled' | 'disabled';
  health: 'healthy' | 'warning' | 'critical' | 'unknown';
  uptime?: number;
  lastChecked: string;
  version?: string;
  url?: string;
  details?: Record<string, unknown>;
}

export interface AnalyzerInfo {
  id: string;
  name: string;
  display_name: string;
  description: string;
  status: 'enabled' | 'disabled' | 'error';
  health: 'healthy' | 'warning' | 'critical';
  usage_stats: {
    total_runs: number;
    success_rate: number;
    avg_duration: number;
    last_used?: string;
  };
  dependencies: string[];
  config: Record<string, unknown>;
}

export interface FileUploadStats {
  total_files: number;
  total_size_bytes: number;
  files_by_type: { [key: string]: number };
  files_by_analyzer: { [key: string]: number };
  upload_trends: Array<{
    date: string;
    count: number;
    size_bytes: number;
  }>;
  recent_uploads: Array<{
    timestamp: string;
    filename: string;
    size_bytes: number;
    analyzer: string;
    status: string;
  }>;
}

export interface ActiveSession {
  id: string;
  created_at: string;
  last_activity: string;
  status: string;
  analyzer_type?: string;
  file_count: number;
  total_size_bytes: number;
  progress: number;
  ip_address?: string;
  user_agent?: string;
}

export interface MaintenanceMode {
  enabled: boolean;
  message: string;
  scheduled_start?: string;
  scheduled_end?: string;
  affected_systems: string[];
  priority: 'low' | 'medium' | 'high' | 'critical';
}

export interface ActionResult {
  success: boolean;
  message: string;
  action: string;
  timestamp: string;
  [key: string]: unknown;
}

export interface SystemAlert {
  id: string;
  type: 'info' | 'warning' | 'error' | 'critical';
  message: string;
  timestamp: string;
  source: string;
  acknowledged?: boolean;
}

// Custom Error Class
export class AdminApiError extends Error {
  constructor(
    message: string,
    public statusCode?: number,
    public details?: Record<string, unknown>
  ) {
    super(message);
    this.name = 'AdminApiError';
  }
}

// API Service Class
export class AdminApiService {
  private static instance: AdminApiService;

  private constructor() {}

  public static getInstance(): AdminApiService {
    if (!AdminApiService.instance) {
      AdminApiService.instance = new AdminApiService();
    }
    return AdminApiService.instance;
  }

  // Generic request method with comprehensive error handling
  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<ApiResponse<T>> {
    const url = `${ADMIN_API_BASE}${endpoint}`;
    
    try {
      const response = await fetch(url, {
        ...options,
        headers: {
          'Content-Type': 'application/json',
          ...options.headers,
        },
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new AdminApiError(
          errorData.message || `HTTP ${response.status}: ${response.statusText}`,
          response.status,
          errorData
        );
      }

      const data = await response.json();
      return data as ApiResponse<T>;
    } catch (error) {
      if (error instanceof AdminApiError) {
        throw error;
      }
      
      // Network or parsing errors
      throw new AdminApiError(
        `Failed to connect to admin API: ${error instanceof Error ? error.message : 'Unknown error'}`,
        0,
        { originalError: error }
      );
    }
  }

  // Health Check
  async checkHealth(): Promise<boolean> {
    try {
      const response = await this.request<{ status: string; timestamp: string }>('/health');
      return response.success;
    } catch {
      return false;
    }
  }

  // System Overview
  async getSystemOverview(): Promise<SystemOverview> {
    const response = await this.request<SystemOverview>('/system/overview');
    if (!response.success || !response.data) {
      throw new AdminApiError('Failed to fetch system overview');
    }
    return response.data;
  }

  // System Metrics
  async getSystemMetrics(): Promise<SystemMetrics> {
    const response = await this.request<SystemMetrics>('/system/metrics');
    if (!response.success || !response.data) {
      throw new AdminApiError('Failed to fetch system metrics');
    }
    return response.data;
  }

  // Running Processes
  async getRunningProcesses(): Promise<ProcessInfo[]> {
    const response = await this.request<ProcessInfo[]>('/system/processes');
    if (!response.success || !response.data) {
      throw new AdminApiError('Failed to fetch running processes');
    }
    return response.data;
  }

  // Analyzers
  async getAnalyzers(): Promise<AnalyzerInfo[]> {
    const response = await this.request<AnalyzerInfo[]>('/analyzers');
    if (!response.success || !response.data) {
      throw new AdminApiError('Failed to fetch analyzers');
    }
    return response.data;
  }

  // File Upload Statistics
  async getFileUploadStats(timeRange: string = '24h'): Promise<FileUploadStats> {
    const response = await this.request<FileUploadStats>(`/stats/uploads?range=${timeRange}`);
    if (!response.success || !response.data) {
      throw new AdminApiError('Failed to fetch file upload statistics');
    }
    return response.data;
  }

  // Active Sessions
  async getActiveSessions(): Promise<ActiveSession[]> {
    const response = await this.request<ActiveSession[]>('/sessions/active');
    if (!response.success || !response.data) {
      throw new AdminApiError('Failed to fetch active sessions');
    }
    return response.data;
  }

  // Maintenance Mode
  async getMaintenanceStatus(): Promise<MaintenanceMode> {
    const response = await this.request<MaintenanceMode>('/maintenance/status');
    if (!response.success || !response.data) {
      throw new AdminApiError('Failed to fetch maintenance status');
    }
    return response.data;
  }

  // System Alerts
  async getAlerts(): Promise<SystemAlert[]> {
    const response = await this.request<SystemAlert[]>('/alerts');
    if (!response.success || !response.data) {
      throw new AdminApiError('Failed to fetch system alerts');
    }
    return response.data;
  }

  // ACTION METHODS

  // Restart Backend
  async restartBackend(): Promise<ActionResult> {
    const response = await this.request<ActionResult>('/actions/restart-backend', {
      method: 'POST',
    });
    if (!response.success) {
      throw new AdminApiError(response.message || 'Failed to restart backend');
    }
    return response as ActionResult;
  }

  // Toggle Maintenance Mode
  async toggleMaintenanceMode(
    enabled: boolean,
    message?: string,
    affectedSystems?: string[]
  ): Promise<ActionResult> {
    const response = await this.request<ActionResult>('/actions/maintenance-mode', {
      method: 'POST',
      body: JSON.stringify({
        enabled,
        message,
        affected_systems: affectedSystems,
      }),
    });
    if (!response.success) {
      throw new AdminApiError(response.message || 'Failed to toggle maintenance mode');
    }
    return response as ActionResult;
  }

  // Clear Cache
  async clearCache(): Promise<ActionResult> {
    const response = await this.request<ActionResult>('/actions/clear-cache', {
      method: 'POST',
    });
    if (!response.success) {
      throw new AdminApiError(response.message || 'Failed to clear cache');
    }
    return response as ActionResult;
  }

  // Export Logs
  async exportLogs(logType: string = 'all', timeRange: string = '24h'): Promise<ActionResult> {
    const response = await this.request<ActionResult>('/actions/export-logs', {
      method: 'POST',
      body: JSON.stringify({
        log_type: logType,
        time_range: timeRange,
      }),
    });
    if (!response.success) {
      throw new AdminApiError(response.message || 'Failed to export logs');
    }
    return response as ActionResult;
  }

  // UTILITY METHODS

  // Format file size
  static formatFileSize(bytes: number): string {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  }

  // Format uptime
  static formatUptime(seconds: number): string {
    if (seconds < 60) return `${Math.floor(seconds)}s`;
    if (seconds < 3600) return `${Math.floor(seconds / 60)}m`;
    if (seconds < 86400) return `${Math.floor(seconds / 3600)}h`;
    return `${Math.floor(seconds / 86400)}d`;
  }

  // Get status color
  static getStatusColor(status: string): string {
    switch (status) {
      case 'online':
      case 'healthy':
      case 'enabled':
        return 'text-green-400';
      case 'offline':
      case 'critical':
      case 'error':
        return 'text-red-400';
      case 'degraded':
      case 'warning':
      case 'disabled':
        return 'text-yellow-400';
      case 'maintenance':
        return 'text-blue-400';
      default:
        return 'text-slate-400';
    }
  }

  // Get status icon
  static getStatusIcon(status: string): string {
    switch (status) {
      case 'online':
      case 'healthy':
      case 'enabled':
        return '🟢';
      case 'offline':
      case 'critical':
      case 'error':
        return '🔴';
      case 'degraded':
      case 'warning':
      case 'disabled':
        return '🟡';
      case 'maintenance':
        return '🔵';
      default:
        return '⚪';
    }
  }
}

// Export singleton instance
export const adminApi = AdminApiService.getInstance();

// All types are already exported above with their definitions