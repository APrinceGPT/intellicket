// Intellicket Unified Admin API Client
// Single API client managing both CSDAIv2 backend and Intellicket frontend

import { 
  UnifiedSystemOverview, 
  AnalyzerInfo, 
  FileUploadStats, 
  SystemMetrics, 
  MaintenanceMode, 
  SystemAlert, 
  SessionInfo, 
  AdminAction,
  ConfigurationItem,
  ApiResponse,
  PaginatedResponse 
} from '@/types/admin';

class UnifiedAdminClient {
  private readonly backendUrl: string;
  private readonly frontendUrl: string;
  private readonly adminApiUrl: string;

  constructor() {
    this.backendUrl = process.env.BACKEND_URL || 'http://localhost:5003';
    this.frontendUrl = process.env.FRONTEND_URL || 'http://localhost:3000';
    this.adminApiUrl = `${this.backendUrl}/admin`;
  }

  // Helper method for making API requests
  private async makeRequest<T>(
    endpoint: string, 
    options: RequestInit = {}
  ): Promise<ApiResponse<T>> {
    try {
      const response = await fetch(`${this.adminApiUrl}${endpoint}`, {
        headers: {
          'Content-Type': 'application/json',
          ...options.headers,
        },
        ...options,
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return {
        success: true,
        data: data.data || data,
        message: data.message,
        timestamp: new Date(),
      };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error',
        timestamp: new Date(),
      };
    }
  }

  // System Overview & Health Monitoring
  async getSystemOverview(): Promise<ApiResponse<UnifiedSystemOverview>> {
    return this.makeRequest<UnifiedSystemOverview>('/system/overview');
  }

  async getSystemHealth(): Promise<ApiResponse<UnifiedSystemOverview>> {
    return this.makeRequest<UnifiedSystemOverview>('/system/health');
  }

  async getSystemMetrics(timeRange?: string): Promise<ApiResponse<SystemMetrics[]>> {
    const query = timeRange ? `?range=${timeRange}` : '';
    return this.makeRequest<SystemMetrics[]>(`/system/metrics${query}`);
  }

  // Frontend System Control
  async getFrontendStatus(): Promise<ApiResponse<{ status: string; health: string }>> {
    try {
      const response = await fetch(`${this.frontendUrl}/api/health`);
      const data = await response.json();
      return {
        success: true,
        data: data,
        timestamp: new Date(),
      };
    } catch {
      return {
        success: false,
        error: 'Frontend unreachable',
        timestamp: new Date(),
      };
    }
  }

  async setFrontendMaintenanceMode(enabled: boolean, message?: string): Promise<ApiResponse<void>> {
    return this.makeRequest<void>('/system/frontend/maintenance', {
      method: 'POST',
      body: JSON.stringify({ enabled, message }),
    });
  }

  // Backend System Control
  async getBackendStatus(): Promise<ApiResponse<{ status: string; health: string }>> {
    return this.makeRequest<{ status: string; health: string }>('/system/backend/status');
  }

  async setBackendMaintenanceMode(enabled: boolean, message?: string): Promise<ApiResponse<void>> {
    return this.makeRequest<void>('/system/backend/maintenance', {
      method: 'POST',
      body: JSON.stringify({ enabled, message }),
    });
  }

  async restartBackendService(): Promise<ApiResponse<void>> {
    return this.makeRequest<void>('/system/backend/restart', {
      method: 'POST',
    });
  }

  // Unified Maintenance Mode
  async getMaintenanceMode(): Promise<ApiResponse<MaintenanceMode>> {
    return this.makeRequest<MaintenanceMode>('/maintenance/status');
  }

  async setMaintenanceMode(config: Partial<MaintenanceMode>): Promise<ApiResponse<void>> {
    return this.makeRequest<void>('/maintenance/set', {
      method: 'POST',
      body: JSON.stringify(config),
    });
  }

  async scheduleMaintenance(
    start: Date, 
    end: Date, 
    message: string, 
    systems: string[]
  ): Promise<ApiResponse<void>> {
    return this.makeRequest<void>('/maintenance/schedule', {
      method: 'POST',
      body: JSON.stringify({
        scheduled_start: start.toISOString(),
        scheduled_end: end.toISOString(),
        message,
        affected_systems: systems,
      }),
    });
  }

  // Analyzer Management
  async getAnalyzers(): Promise<ApiResponse<AnalyzerInfo[]>> {
    return this.makeRequest<AnalyzerInfo[]>('/analyzers');
  }

  async getAnalyzerStatus(analyzerId: string): Promise<ApiResponse<AnalyzerInfo>> {
    return this.makeRequest<AnalyzerInfo>(`/analyzers/${analyzerId}`);
  }

  async enableAnalyzer(analyzerId: string): Promise<ApiResponse<void>> {
    return this.makeRequest<void>(`/analyzers/${analyzerId}/enable`, {
      method: 'POST',
    });
  }

  async disableAnalyzer(analyzerId: string, reason?: string): Promise<ApiResponse<void>> {
    return this.makeRequest<void>(`/analyzers/${analyzerId}/disable`, {
      method: 'POST',
      body: JSON.stringify({ reason }),
    });
  }

  async restartAnalyzer(analyzerId: string): Promise<ApiResponse<void>> {
    return this.makeRequest<void>(`/analyzers/${analyzerId}/restart`, {
      method: 'POST',
    });
  }

  async updateAnalyzerConfig(
    analyzerId: string, 
    config: Record<string, string | number | boolean>
  ): Promise<ApiResponse<void>> {
    return this.makeRequest<void>(`/analyzers/${analyzerId}/config`, {
      method: 'PUT',
      body: JSON.stringify(config),
    });
  }

  // File Upload Statistics
  async getFileUploadStats(timeRange?: string): Promise<ApiResponse<FileUploadStats>> {
    const query = timeRange ? `?range=${timeRange}` : '';
    return this.makeRequest<FileUploadStats>(`/stats/uploads${query}`);
  }

  async getAnalyzerUsageStats(timeRange?: string): Promise<ApiResponse<Record<string, number>>> {
    const query = timeRange ? `?range=${timeRange}` : '';
    return this.makeRequest<Record<string, number>>(`/stats/analyzer-usage${query}`);
  }

  // Session Management
  async getActiveSessions(): Promise<ApiResponse<SessionInfo[]>> {
    return this.makeRequest<SessionInfo[]>('/sessions/active');
  }

  async getAllSessions(page = 1, limit = 50): Promise<PaginatedResponse<SessionInfo>> {
    return this.makeRequest<SessionInfo[]>(`/sessions?page=${page}&limit=${limit}`) as Promise<PaginatedResponse<SessionInfo>>;
  }

  async getSession(sessionId: string): Promise<ApiResponse<SessionInfo>> {
    return this.makeRequest<SessionInfo>(`/sessions/${sessionId}`);
  }

  async terminateSession(sessionId: string): Promise<ApiResponse<void>> {
    return this.makeRequest<void>(`/sessions/${sessionId}/terminate`, {
      method: 'POST',
    });
  }

  async cleanupExpiredSessions(): Promise<ApiResponse<{ cleaned: number }>> {
    return this.makeRequest<{ cleaned: number }>('/sessions/cleanup', {
      method: 'POST',
    });
  }

  // Alerts & Monitoring
  async getAlerts(level?: string): Promise<ApiResponse<SystemAlert[]>> {
    const query = level ? `?level=${level}` : '';
    return this.makeRequest<SystemAlert[]>(`/alerts${query}`);
  }

  async acknowledgeAlert(alertId: string): Promise<ApiResponse<void>> {
    return this.makeRequest<void>(`/alerts/${alertId}/acknowledge`, {
      method: 'POST',
    });
  }

  async resolveAlert(alertId: string): Promise<ApiResponse<void>> {
    return this.makeRequest<void>(`/alerts/${alertId}/resolve`, {
      method: 'POST',
    });
  }

  // Admin Actions & Audit Trail
  async getAdminActions(page = 1, limit = 50): Promise<PaginatedResponse<AdminAction>> {
    return this.makeRequest<AdminAction[]>(`/actions?page=${page}&limit=${limit}`) as Promise<PaginatedResponse<AdminAction>>;
  }

  async logAdminAction(
    action: string, 
    component: string, 
    details: string, 
    metadata?: Record<string, string | number | boolean>
  ): Promise<ApiResponse<void>> {
    return this.makeRequest<void>('/actions/log', {
      method: 'POST',
      body: JSON.stringify({
        action,
        component,
        details,
        metadata,
      }),
    });
  }

  // Configuration Management
  async getConfiguration(category?: string): Promise<ApiResponse<ConfigurationItem[]>> {
    const query = category ? `?category=${category}` : '';
    return this.makeRequest<ConfigurationItem[]>(`/config${query}`);
  }

  async updateConfiguration(
    key: string, 
    value: string | number | boolean | object
  ): Promise<ApiResponse<void>> {
    return this.makeRequest<void>('/config/update', {
      method: 'PUT',
      body: JSON.stringify({ key, value }),
    });
  }

  async resetConfiguration(key: string): Promise<ApiResponse<void>> {
    return this.makeRequest<void>(`/config/${key}/reset`, {
      method: 'POST',
    });
  }

  // System Operations
  async exportSystemData(dataType: string, format = 'json'): Promise<ApiResponse<string>> {
    return this.makeRequest<string>(`/export/${dataType}?format=${format}`);
  }

  async importSystemData(dataType: string, data: string): Promise<ApiResponse<void>> {
    return this.makeRequest<void>(`/import/${dataType}`, {
      method: 'POST',
      body: JSON.stringify({ data }),
    });
  }

  async runSystemDiagnostics(): Promise<ApiResponse<Record<string, unknown>>> {
    return this.makeRequest<Record<string, unknown>>('/diagnostics/run', {
      method: 'POST',
    });
  }

  // Health Check Utilities
  async pingBackend(): Promise<boolean> {
    try {
      const response = await fetch(`${this.backendUrl}/health`);
      return response.ok;
    } catch {
      return false;
    }
  }

  async pingFrontend(): Promise<boolean> {
    try {
      const response = await fetch(`${this.frontendUrl}/api/health`);
      return response.ok;
    } catch {
      return false;
    }
  }

  async pingAdminApi(): Promise<boolean> {
    try {
      const response = await fetch(`${this.adminApiUrl}/health`);
      return response.ok;
    } catch {
      return false;
    }
  }
}

// Export singleton instance
export const adminClient = new UnifiedAdminClient();
export default adminClient;