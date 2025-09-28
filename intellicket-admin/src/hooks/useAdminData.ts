// Intellicket Unified Admin Hooks - Custom React hooks for admin functionality
'use client';

import { useState, useEffect, useCallback } from 'react';
import { adminClient } from '@/api/unified-admin-client';
import { 
  UnifiedSystemOverview, 
  SystemMetrics, 
  AnalyzerInfo, 
  FileUploadStats,
  SystemAlert,
  SessionInfo,
  MaintenanceMode,
  UseSystemHealthReturn
} from '@/types/admin';

// System Health Hook
export function useSystemHealth(refreshInterval = 30000): UseSystemHealthReturn {
  const [overview, setOverview] = useState<UnifiedSystemOverview | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchHealth = useCallback(async () => {
    try {
      setLoading(true);
      const response = await adminClient.getSystemOverview();
      
      if (response.success && response.data) {
        setOverview(response.data);
        setError(null);
      } else {
        setError(response.error || 'Failed to fetch system health');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchHealth();
    
    if (refreshInterval > 0) {
      const interval = setInterval(fetchHealth, refreshInterval);
      return () => clearInterval(interval);
    }
  }, [fetchHealth, refreshInterval]);

  return {
    overview,
    loading,
    error,
    refresh: fetchHealth,
  };
}

// System Metrics Hook
export function useSystemMetrics(timeRange = '1h', refreshInterval = 60000) {
  const [metrics, setMetrics] = useState<SystemMetrics[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchMetrics = useCallback(async () => {
    try {
      setLoading(true);
      const response = await adminClient.getSystemMetrics(timeRange);
      
      if (response.success && response.data) {
        setMetrics(response.data);
        setError(null);
      } else {
        setError(response.error || 'Failed to fetch metrics');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setLoading(false);
    }
  }, [timeRange]);

  useEffect(() => {
    fetchMetrics();
    
    if (refreshInterval > 0) {
      const interval = setInterval(fetchMetrics, refreshInterval);
      return () => clearInterval(interval);
    }
  }, [fetchMetrics, refreshInterval]);

  return {
    metrics,
    loading,
    error,
    refresh: fetchMetrics,
  };
}

// Analyzers Hook
export function useAnalyzers() {
  const [analyzers, setAnalyzers] = useState<AnalyzerInfo[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchAnalyzers = useCallback(async () => {
    try {
      setLoading(true);
      const response = await adminClient.getAnalyzers();
      
      if (response.success && response.data) {
        setAnalyzers(response.data);
        setError(null);
      } else {
        setError(response.error || 'Failed to fetch analyzers');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setLoading(false);
    }
  }, []);

  const enableAnalyzer = useCallback(async (analyzerId: string) => {
    try {
      const response = await adminClient.enableAnalyzer(analyzerId);
      if (response.success) {
        await fetchAnalyzers(); // Refresh the list
        return true;
      } else {
        setError(response.error || 'Failed to enable analyzer');
        return false;
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
      return false;
    }
  }, [fetchAnalyzers]);

  const disableAnalyzer = useCallback(async (analyzerId: string, reason?: string) => {
    try {
      const response = await adminClient.disableAnalyzer(analyzerId, reason);
      if (response.success) {
        await fetchAnalyzers(); // Refresh the list
        return true;
      } else {
        setError(response.error || 'Failed to disable analyzer');
        return false;
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
      return false;
    }
  }, [fetchAnalyzers]);

  const restartAnalyzer = useCallback(async (analyzerId: string) => {
    try {
      const response = await adminClient.restartAnalyzer(analyzerId);
      if (response.success) {
        await fetchAnalyzers(); // Refresh the list
        return true;
      } else {
        setError(response.error || 'Failed to restart analyzer');
        return false;
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
      return false;
    }
  }, [fetchAnalyzers]);

  useEffect(() => {
    fetchAnalyzers();
  }, [fetchAnalyzers]);

  return {
    analyzers,
    loading,
    error,
    refresh: fetchAnalyzers,
    enableAnalyzer,
    disableAnalyzer,
    restartAnalyzer,
  };
}

// File Upload Statistics Hook
export function useFileStats(timeRange = '24h', refreshInterval = 300000) {
  const [stats, setStats] = useState<FileUploadStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchStats = useCallback(async () => {
    try {
      setLoading(true);
      const response = await adminClient.getFileUploadStats(timeRange);
      
      if (response.success && response.data) {
        setStats(response.data);
        setError(null);
      } else {
        setError(response.error || 'Failed to fetch file statistics');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setLoading(false);
    }
  }, [timeRange]);

  useEffect(() => {
    fetchStats();
    
    if (refreshInterval > 0) {
      const interval = setInterval(fetchStats, refreshInterval);
      return () => clearInterval(interval);
    }
  }, [fetchStats, refreshInterval]);

  return {
    stats,
    loading,
    error,
    refresh: fetchStats,
  };
}

// System Alerts Hook
export function useSystemAlerts(refreshInterval = 60000) {
  const [alerts, setAlerts] = useState<SystemAlert[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchAlerts = useCallback(async () => {
    try {
      setLoading(true);
      const response = await adminClient.getAlerts();
      
      if (response.success && response.data) {
        setAlerts(response.data);
        setError(null);
      } else {
        setError(response.error || 'Failed to fetch alerts');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setLoading(false);
    }
  }, []);

  const acknowledgeAlert = useCallback(async (alertId: string) => {
    try {
      const response = await adminClient.acknowledgeAlert(alertId);
      if (response.success) {
        await fetchAlerts(); // Refresh alerts
        return true;
      } else {
        setError(response.error || 'Failed to acknowledge alert');
        return false;
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
      return false;
    }
  }, [fetchAlerts]);

  const resolveAlert = useCallback(async (alertId: string) => {
    try {
      const response = await adminClient.resolveAlert(alertId);
      if (response.success) {
        await fetchAlerts(); // Refresh alerts
        return true;
      } else {
        setError(response.error || 'Failed to resolve alert');
        return false;
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
      return false;
    }
  }, [fetchAlerts]);

  useEffect(() => {
    fetchAlerts();
    
    if (refreshInterval > 0) {
      const interval = setInterval(fetchAlerts, refreshInterval);
      return () => clearInterval(interval);
    }
  }, [fetchAlerts, refreshInterval]);

  return {
    alerts,
    loading,
    error,
    refresh: fetchAlerts,
    acknowledgeAlert,
    resolveAlert,
  };
}

// Active Sessions Hook
export function useActiveSessions(refreshInterval = 30000) {
  const [sessions, setSessions] = useState<SessionInfo[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchSessions = useCallback(async () => {
    try {
      setLoading(true);
      const response = await adminClient.getActiveSessions();
      
      if (response.success && response.data) {
        setSessions(response.data);
        setError(null);
      } else {
        setError(response.error || 'Failed to fetch sessions');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setLoading(false);
    }
  }, []);

  const terminateSession = useCallback(async (sessionId: string) => {
    try {
      const response = await adminClient.terminateSession(sessionId);
      if (response.success) {
        await fetchSessions(); // Refresh sessions
        return true;
      } else {
        setError(response.error || 'Failed to terminate session');
        return false;
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
      return false;
    }
  }, [fetchSessions]);

  useEffect(() => {
    fetchSessions();
    
    if (refreshInterval > 0) {
      const interval = setInterval(fetchSessions, refreshInterval);
      return () => clearInterval(interval);
    }
  }, [fetchSessions, refreshInterval]);

  return {
    sessions,
    loading,
    error,
    refresh: fetchSessions,
    terminateSession,
  };
}

// Maintenance Mode Hook
export function useMaintenanceMode() {
  const [maintenanceMode, setMaintenanceMode] = useState<MaintenanceMode | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchMaintenanceMode = useCallback(async () => {
    try {
      setLoading(true);
      const response = await adminClient.getMaintenanceMode();
      
      if (response.success && response.data) {
        setMaintenanceMode(response.data);
        setError(null);
      } else {
        setError(response.error || 'Failed to fetch maintenance mode');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setLoading(false);
    }
  }, []);

  const setMaintenance = useCallback(async (config: Partial<MaintenanceMode>) => {
    try {
      const response = await adminClient.setMaintenanceMode(config);
      if (response.success) {
        await fetchMaintenanceMode(); // Refresh maintenance mode
        return true;
      } else {
        setError(response.error || 'Failed to set maintenance mode');
        return false;
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
      return false;
    }
  }, [fetchMaintenanceMode]);

  useEffect(() => {
    fetchMaintenanceMode();
  }, [fetchMaintenanceMode]);

  return {
    maintenanceMode,
    loading,
    error,
    refresh: fetchMaintenanceMode,
    setMaintenance,
  };
}

// WebSocket Hook for Real-time Updates
export function useWebSocket(url: string) {
  const [connected, setConnected] = useState(false);
  const [lastMessage, setLastMessage] = useState<unknown>(null);
  const [socket, setSocket] = useState<WebSocket | null>(null);

  useEffect(() => {
    const ws = new WebSocket(url);
    
    ws.onopen = () => {
      setConnected(true);
      setSocket(ws);
    };

    ws.onclose = () => {
      setConnected(false);
      setSocket(null);
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        setLastMessage(data);
      } catch {
        setLastMessage(event.data);
      }
    };

    ws.onerror = () => {
      setConnected(false);
    };

    return () => {
      ws.close();
    };
  }, [url]);

  const sendMessage = useCallback((message: unknown) => {
    if (socket && connected) {
      socket.send(JSON.stringify(message));
    }
  }, [socket, connected]);

  return {
    connected,
    lastMessage,
    sendMessage,
  };
}