// Admin API service for connecting to the main frontend admin proxy endpoints
// Data flow: Admin Dashboard (3001) → Main Frontend (3000) → Backend (5003)

const API_BASE_URL = 'http://localhost:3000/api/admin';

class AdminApiService {
  private async request(endpoint: string, options: RequestInit = {}) {
    const url = `${API_BASE_URL}${endpoint}`;
    
    const config: RequestInit = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    };

    const response = await fetch(url, config);
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => null);
      throw new Error(errorData?.error || `HTTP ${response.status}: ${response.statusText}`);
    }

    return response.json();
  }

  // System Overview
  async getSystemOverview() {
    return this.request('/system/overview');
  }

  // System Health
  async getSystemHealth() {
    return this.request('/health');
  }

  // Maintenance Mode
  async getMaintenanceStatus() {
    return this.request('/maintenance/status');
  }

  async toggleMaintenanceMode(enabled: boolean, message?: string) {
    return this.request('/actions/maintenance-mode', {
      method: 'POST',
      body: JSON.stringify({ enabled, message }),
    });
  }

  // Backend Control
  async restartBackend() {
    return this.request('/actions/restart-backend', {
      method: 'POST',
    });
  }

  // Cache Management
  async clearCache() {
    return this.request('/actions/clear-cache', {
      method: 'POST',
    });
  }

  // Log Export
  async exportLogs(logType: string = 'all', timeRange: string = '24h') {
    return this.request('/actions/export-logs', {
      method: 'POST',
      body: JSON.stringify({ log_type: logType, time_range: timeRange }),
    });
  }

  // Analyzers
  async getAnalyzers() {
    return this.request('/analyzers');
  }

  async toggleAnalyzer(analyzerId: string) {
    return this.request(`/analyzers/${analyzerId}/toggle`, {
      method: 'POST',
    });
  }

  // Sessions
  async getActiveSessions() {
    return this.request('/sessions/active');
  }

  async terminateSession(sessionId: string) {
    return this.request(`/sessions/${sessionId}/terminate`, {
      method: 'POST',
    });
  }

  // Statistics (now proxied through main frontend)
  async getFileStats(timeRange: string = '24h') {
    // Note: timeRange parameter currently ignored by proxy, but kept for future enhancement
    return this.request('/stats/uploads');
  }

  async getAnalyzerUsage() {
    return this.request('/stats/analyzers');
  }

  // Combined statistics endpoint
  async getAllStats() {
    return this.request('/stats');
  }

  // Alerts
  async getSystemAlerts() {
    return this.request('/alerts');
  }

  async acknowledgeAlert(alertId: string) {
    return this.request(`/alerts/${alertId}/acknowledge`, {
      method: 'POST',
    });
  }
}

export const adminApi = new AdminApiService();