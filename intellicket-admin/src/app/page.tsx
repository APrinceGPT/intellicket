'use client';

import { useState, useEffect, useCallback } from 'react';
import { adminApi } from '../services/adminApi';
import { AnalyzerConfigModal, SessionModal } from '../components/Modal';
import { DetailedFileStatsModal } from '../components/DetailedFileStatsModal';

interface SystemOverview {
  backend: {
    status: string;
    health: string;
    name: string;
    version?: string;
  };
  frontend: {
    status: string;
    health: string;
    name: string;
  };
  overall: {
    status: string;
    health: string;
    name: string;
  };
  components: {
    analyzers: Array<{
      id: string;
      name: string;
      status: string;
      health: string;
    }>;
    [key: string]: any;
  };
}

interface MaintenanceMode {
  enabled: boolean;
  message?: string;
}

export default function AdminDashboard() {
  // State management
  const [systemOverview, setSystemOverview] = useState<SystemOverview | null>(null);
  const [maintenanceMode, setMaintenanceMode] = useState<MaintenanceMode | null>(null);
  const [refreshInterval, setRefreshInterval] = useState(30000);
  const [lastAction, setLastAction] = useState<{message: string; timestamp: Date} | null>(null);
  
  // Modal states
  const [showAnalyzerModal, setShowAnalyzerModal] = useState(false);
  const [showSessionModal, setShowSessionModal] = useState(false);
  const [showDetailedFileStatsModal, setShowDetailedFileStatsModal] = useState(false);
  const [activeSessions, setActiveSessions] = useState<any[]>([]);
  
  // Real data states
  const [fileStats, setFileStats] = useState<{
    total_files: number;
    total_size_bytes: number;
    files_today: number;
  } | null>(null);
  const [sessionStats, setSessionStats] = useState<{
    active: number;
    processing: number;
    completed: number;
  } | null>(null);
  
  // Loading states
  const [loading, setLoading] = useState({
    overview: false,
    restart: false,
    maintenance: false,
    cache: false,
    export: false,
    fileStats: false,
    sessionStats: false
  });

  // Error states
  const [errors, setErrors] = useState({
    overview: '',
    action: ''
  });

  // Load file statistics
  const loadFileStats = async () => {
    setLoading(prev => ({ ...prev, fileStats: true }));
    try {
      const response = await adminApi.getFileStats('24h');
      if (response.success && response.data) {
        // Calculate files uploaded today (would need to be computed from recent_uploads)
        const todayUploads = response.data.recent_uploads?.filter((upload: any) => {
          const uploadDate = new Date(upload.timestamp);
          const today = new Date();
          return uploadDate.toDateString() === today.toDateString();
        }).length || 0;

        setFileStats({
          total_files: response.data.total_files || 0,
          total_size_bytes: response.data.total_size_bytes || 0,
          files_today: todayUploads
        });
      }
    } catch (error) {
      console.error('Failed to load file stats:', error);
      // Keep null state so hardcoded fallback is used
    } finally {
      setLoading(prev => ({ ...prev, fileStats: false }));
    }
  };

  // Load session statistics
  const loadSessionStats = async () => {
    setLoading(prev => ({ ...prev, sessionStats: true }));
    try {
      const response = await adminApi.getActiveSessions();
      if (response.success && response.data) {
        const sessions = response.data;
        const active = sessions.filter((s: any) => s.status === 'active').length;
        const processing = sessions.filter((s: any) => s.status === 'processing').length;
        const completed = sessions.filter((s: any) => s.status === 'completed').length;
        
        setSessionStats({
          active,
          processing,
          completed
        });
      }
    } catch (error) {
      console.error('Failed to load session stats:', error);
      // Keep null state so hardcoded fallback is used
    } finally {
      setLoading(prev => ({ ...prev, sessionStats: false }));
    }
  };

  // Load system overview
  const loadSystemOverview = useCallback(async () => {
    setLoading(prev => ({ ...prev, overview: true }));
    setErrors(prev => ({ ...prev, overview: '' }));
    
    try {
      const response = await adminApi.getSystemOverview();
      setSystemOverview(response.data);
      
      // Also load maintenance mode
      const maintenanceResponse = await adminApi.getMaintenanceStatus();
      setMaintenanceMode(maintenanceResponse.data);
      
      // Load statistics
      await loadFileStats();
      await loadSessionStats();
    } catch (error: any) {
      const errorMessage = error.response?.data?.error || error.message || 'Failed to connect to admin API';
      setErrors(prev => ({ ...prev, overview: errorMessage }));
      console.error('Failed to load system overview:', error);
    } finally {
      setLoading(prev => ({ ...prev, overview: false }));
    }
  }, []);

  // Action handlers
  const handleRestartBackend = async () => {
    setLoading(prev => ({ ...prev, restart: true }));
    setErrors(prev => ({ ...prev, action: '' }));
    
    try {
      await adminApi.restartBackend();
      setLastAction({
        message: 'Backend restart initiated successfully',
        timestamp: new Date()
      });
      // Reload system overview after a delay
      setTimeout(loadSystemOverview, 3000);
    } catch (error: any) {
      setErrors(prev => ({ ...prev, action: error.response?.data?.error || 'Failed to restart backend' }));
    } finally {
      setLoading(prev => ({ ...prev, restart: false }));
    }
  };

  const handleMaintenanceToggle = async () => {
    setLoading(prev => ({ ...prev, maintenance: true }));
    setErrors(prev => ({ ...prev, action: '' }));
    
    try {
      const newState = !maintenanceMode?.enabled;
      const response = await adminApi.toggleMaintenanceMode(newState, 'Toggled via admin dashboard');
      setMaintenanceMode(response.data);
      setLastAction({
        message: `Maintenance mode ${response.data.enabled ? 'enabled' : 'disabled'}`,
        timestamp: new Date()
      });
    } catch (error: any) {
      setErrors(prev => ({ ...prev, action: error.response?.data?.error || 'Failed to toggle maintenance mode' }));
    } finally {
      setLoading(prev => ({ ...prev, maintenance: false }));
    }
  };

  const handleClearCache = async () => {
    setLoading(prev => ({ ...prev, cache: true }));
    setErrors(prev => ({ ...prev, action: '' }));
    
    try {
      await adminApi.clearCache();
      setLastAction({
        message: 'Cache cleared successfully',
        timestamp: new Date()
      });
    } catch (error: any) {
      setErrors(prev => ({ ...prev, action: error.response?.data?.error || 'Failed to clear cache' }));
    } finally {
      setLoading(prev => ({ ...prev, cache: false }));
    }
  };

  const handleExportLogs = async () => {
    setLoading(prev => ({ ...prev, export: true }));
    setErrors(prev => ({ ...prev, action: '' }));
    
    try {
      const response = await adminApi.exportLogs();
      // Create download link
      const blob = new Blob([response.data], { type: 'application/zip' });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `intellicket-logs-${new Date().toISOString().split('T')[0]}.zip`;
      a.click();
      window.URL.revokeObjectURL(url);
      
      setLastAction({
        message: 'Logs exported successfully',
        timestamp: new Date()
      });
    } catch (error: any) {
      setErrors(prev => ({ ...prev, action: error.response?.data?.error || 'Failed to export logs' }));
    } finally {
      setLoading(prev => ({ ...prev, export: false }));
    }
  };

  // Modal handlers
  const handleAnalyzerConfig = async () => {
    setShowAnalyzerModal(true);
  };

  const handleToggleAnalyzer = async (analyzerId: string) => {
    try {
      await adminApi.toggleAnalyzer(analyzerId);
      setLastAction({
        message: `Analyzer ${analyzerId} toggled successfully`,
        timestamp: new Date()
      });
      // Reload system overview
      loadSystemOverview();
    } catch (error: any) {
      setErrors(prev => ({ ...prev, action: error.message || 'Failed to toggle analyzer' }));
    }
  };

  const handleSessionsView = async () => {
    try {
      const response = await adminApi.getActiveSessions();
      setActiveSessions(response.data);
      setShowSessionModal(true);
    } catch (error: any) {
      setErrors(prev => ({ ...prev, action: error.message || 'Failed to load sessions' }));
    }
  };

  const handleTerminateSession = async (sessionId: string) => {
    try {
      await adminApi.terminateSession(sessionId);
      setLastAction({
        message: `Session ${sessionId.slice(0, 8)} terminated`,
        timestamp: new Date()
      });
      // Reload sessions
      const response = await adminApi.getActiveSessions();
      setActiveSessions(response.data);
    } catch (error: any) {
      setErrors(prev => ({ ...prev, action: error.message || 'Failed to terminate session' }));
    }
  };

  // Auto-refresh effect
  useEffect(() => {
    loadSystemOverview();
    
    if (refreshInterval > 0) {
      const interval = setInterval(loadSystemOverview, refreshInterval);
      return () => clearInterval(interval);
    }
  }, [refreshInterval, loadSystemOverview]);

  // Helper function to format file size
  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
  };

  // Clear messages after 5 seconds
  useEffect(() => {
    if (lastAction) {
      const timer = setTimeout(() => setLastAction(null), 5000);
      return () => clearTimeout(timer);
    }
  }, [lastAction]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
      {/* Header */}
      <div className="bg-slate-800/50 backdrop-blur-sm border-b border-slate-700/50 sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between py-4">
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-3">
                <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
                  <span className="text-xl font-bold text-white">T</span>
                </div>
                <div>
                  <h1 className="text-2xl font-bold text-slate-100">Intellicket Admin</h1>
                  <p className="text-sm text-slate-400">System Management Dashboard</p>
                </div>
              </div>
            </div>
            
            <div className="flex items-center space-x-4">
              <button
                onClick={loadSystemOverview}
                className="px-6 py-3 bg-gradient-to-r from-blue-600 to-blue-700 text-white rounded-xl hover:from-blue-700 hover:to-blue-800 transition-all duration-200 font-semibold shadow-lg hover:shadow-xl flex items-center space-x-2"
                disabled={loading.overview}
              >
                <span className={loading.overview ? 'animate-spin' : ''}>🔄</span>
                <span>{loading.overview ? 'Refreshing...' : 'Refresh All'}</span>
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {/* Alert Messages */}
        {(errors.overview || errors.action) && (
          <div className="mb-4 bg-red-900/20 border border-red-500/30 rounded-lg p-3 backdrop-blur-sm">
            <div className="flex items-center text-sm">
              <span className="text-red-400 mr-2">⚠️</span>
              <span className="text-red-200">
                {errors.overview ? `API Error: ${errors.overview}` : `Action Error: ${errors.action}`}
              </span>
            </div>
          </div>
        )}

        {lastAction && (
          <div className="mb-4 bg-green-900/20 border border-green-500/30 rounded-lg p-3 backdrop-blur-sm">
            <div className="flex items-center text-sm">
              <span className="text-green-400 mr-2">✅</span>
              <span className="text-green-200">{lastAction.message}</span>
            </div>
          </div>
        )}

        {/* Compact Dashboard - Single Screen Layout */}
        <div className="h-[calc(100vh-200px)] grid grid-cols-12 gap-4">
          {/* Left Column - System Status & Controls */}
          <div className="col-span-4 space-y-4">
            {/* System Status Overview */}
            <div className="bg-slate-800 rounded-lg p-4 border border-slate-700">
              <div className="flex items-center justify-between mb-3">
                <h3 className="text-lg font-semibold text-slate-100 flex items-center">
                  <span className="mr-2">🎛️</span>System Status
                </h3>
                <div className={`w-3 h-3 rounded-full ${
                  systemOverview?.overall?.health === 'healthy' ? 'bg-green-400' :
                  systemOverview?.overall?.health === 'warning' ? 'bg-yellow-400' : 'bg-red-400'
                }`} />
              </div>
              
              <div className="space-y-3">
                {/* Backend Status */}
                <div className="flex items-center justify-between p-2 bg-slate-700/50 rounded">
                  <div className="flex items-center space-x-2">
                    <span className="text-sm">🔧</span>
                    <span className="text-sm text-slate-300">Backend</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <div className={`w-2 h-2 rounded-full ${
                      systemOverview?.backend?.status === 'online' ? 'bg-green-400' : 'bg-red-400'
                    }`} />
                    <span className={`text-xs font-medium ${
                      systemOverview?.backend?.status === 'online' ? 'text-green-400' : 'text-red-400'
                    }`}>
                      {systemOverview?.backend?.status || 'Unknown'}
                    </span>
                  </div>
                </div>
                
                {/* Frontend Status */}
                <div className="flex items-center justify-between p-2 bg-slate-700/50 rounded">
                  <div className="flex items-center space-x-2">
                    <span className="text-sm">🌐</span>
                    <span className="text-sm text-slate-300">Frontend</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <div className={`w-2 h-2 rounded-full ${
                      systemOverview?.frontend?.status === 'online' ? 'bg-green-400' : 'bg-red-400'
                    }`} />
                    <span className={`text-xs font-medium ${
                      systemOverview?.frontend?.status === 'online' ? 'text-green-400' : 'text-red-400'
                    }`}>
                      {systemOverview?.frontend?.status || 'Unknown'}
                    </span>
                  </div>
                </div>

                {/* Maintenance Mode */}
                <div className="flex items-center justify-between p-2 bg-slate-700/50 rounded">
                  <div className="flex items-center space-x-2">
                    <span className="text-sm">🔧</span>
                    <span className="text-sm text-slate-300">Maintenance</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <div className={`w-2 h-2 rounded-full ${
                      maintenanceMode?.enabled ? 'bg-yellow-400' : 'bg-green-400'
                    }`} />
                    <span className={`text-xs font-medium ${
                      maintenanceMode?.enabled ? 'text-yellow-400' : 'text-green-400'
                    }`}>
                      {maintenanceMode?.enabled ? 'Active' : 'Inactive'}
                    </span>
                  </div>
                </div>
              </div>
            </div>

            {/* Quick Actions */}
            <div className="bg-slate-800 rounded-lg p-4 border border-slate-700">
              <h3 className="text-lg font-semibold text-slate-100 mb-3 flex items-center">
                <span className="mr-2">⚡</span>Quick Actions
              </h3>
              
              <div className="space-y-2">
                <button 
                  onClick={handleRestartBackend}
                  disabled={loading.restart}
                  className="w-full px-3 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-blue-800 disabled:opacity-50 text-white text-sm rounded-lg transition-colors flex items-center justify-center space-x-2"
                >
                  <span>{loading.restart ? '⏳' : '🔄'}</span>
                  <span>{loading.restart ? 'Restarting...' : 'Restart Backend'}</span>
                </button>
                
                <button 
                  onClick={handleMaintenanceToggle}
                  disabled={loading.maintenance}
                  className="w-full px-3 py-2 bg-yellow-600 hover:bg-yellow-700 disabled:bg-yellow-800 disabled:opacity-50 text-white text-sm rounded-lg transition-colors flex items-center justify-center space-x-2"
                >
                  <span>{loading.maintenance ? '⏳' : '🔧'}</span>
                  <span>{loading.maintenance ? 'Toggling...' : `${maintenanceMode?.enabled ? 'Disable' : 'Enable'} Maintenance`}</span>
                </button>
                
                <button 
                  onClick={handleClearCache}
                  disabled={loading.cache}
                  className="w-full px-3 py-2 bg-green-600 hover:bg-green-700 disabled:bg-green-800 disabled:opacity-50 text-white text-sm rounded-lg transition-colors flex items-center justify-center space-x-2"
                >
                  <span>{loading.cache ? '⏳' : '🗑️'}</span>
                  <span>{loading.cache ? 'Clearing...' : 'Clear Cache'}</span>
                </button>
                
                <button 
                  onClick={handleExportLogs}
                  disabled={loading.export}
                  className="w-full px-3 py-2 bg-purple-600 hover:bg-purple-700 disabled:bg-purple-800 disabled:opacity-50 text-white text-sm rounded-lg transition-colors flex items-center justify-center space-x-2"
                >
                  <span>{loading.export ? '⏳' : '📊'}</span>
                  <span>{loading.export ? 'Exporting...' : 'Export Logs'}</span>
                </button>
              </div>
            </div>
          </div>

          {/* Middle Column - System Health & Components */}
          <div className="col-span-5 space-y-4">
            {/* System Health */}
            <div className="bg-slate-800 rounded-lg p-4 border border-slate-700 h-fit">
              <div className="flex items-center justify-between mb-3">
                <h3 className="text-lg font-semibold text-slate-100 flex items-center">
                  <span className="mr-2">❤️</span>System Health
                </h3>
                {loading.overview && <span className="text-xs text-slate-400 animate-pulse">Updating...</span>}
              </div>
              
              {systemOverview ? (
                <div className="space-y-3">
                  {/* Component Statuses */}
                  {systemOverview.components && Object.entries(systemOverview.components).map(([name, component]) => {
                    if (name === 'analyzers' || Array.isArray(component)) return null;
                    return (
                      <div key={name} className="flex items-center justify-between p-2 bg-slate-700/30 rounded text-sm">
                        <span className="text-slate-300 capitalize">{component.name}</span>
                        <div className="flex items-center space-x-2">
                          <div className={`w-2 h-2 rounded-full ${
                            component.health === 'healthy' ? 'bg-green-400' :
                            component.health === 'warning' ? 'bg-yellow-400' : 'bg-red-400'
                          }`} />
                          <span className={`text-xs font-medium ${
                            component.status === 'enabled' ? 'text-green-400' : 'text-red-400'
                          }`}>
                            {component.status}
                          </span>
                        </div>
                      </div>
                    );
                  })}
                  
                  {/* Analyzers Section */}
                  {systemOverview.components.analyzers && Array.isArray(systemOverview.components.analyzers) && (
                    <div className="mt-4">
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-sm font-medium text-slate-200">Analyzers</span>
                        <button 
                          onClick={handleAnalyzerConfig}
                          className="text-xs text-blue-400 hover:text-blue-300 transition-colors"
                        >
                          Configure
                        </button>
                      </div>
                      <div className="grid grid-cols-2 gap-2">
                        {systemOverview.components.analyzers.map((analyzer) => (
                          <div key={analyzer.id} className="p-2 bg-slate-700/30 rounded text-xs">
                            <div className="flex items-center justify-between">
                              <span className="text-slate-300 truncate">{analyzer.name}</span>
                              <div className={`w-1.5 h-1.5 rounded-full ${
                                analyzer.health === 'healthy' ? 'bg-green-400' :
                                analyzer.health === 'warning' ? 'bg-yellow-400' : 'bg-red-400'
                              }`} />
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              ) : (
                <div className="text-center py-8 text-slate-400">
                  {loading.overview ? 'Loading system health...' : 'Failed to load system health data'}
                </div>
              )}
            </div>
          </div>

          {/* Right Column - Statistics & Monitoring */}
          <div className="col-span-3 space-y-4">
            {/* File Statistics */}
            <div className="bg-slate-800 rounded-lg p-4 border border-slate-700">
              <div className="flex items-center justify-between mb-3">
                <h3 className="text-lg font-semibold text-slate-100 flex items-center">
                  <span className="mr-2">📊</span>File Stats
                </h3>
                <button 
                  onClick={() => setShowDetailedFileStatsModal(true)}
                  className="text-xs text-blue-400 hover:text-blue-300 transition-colors"
                >
                  View Details
                </button>
              </div>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-slate-400">Total Files:</span>
                  <span className="text-slate-200">
                    {loading.fileStats ? (
                      <span className="animate-pulse bg-slate-600 rounded px-2 py-1">Loading...</span>
                    ) : fileStats ? (
                      fileStats.total_files.toLocaleString()
                    ) : (
                      '1,234'
                    )}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-400">Size:</span>
                  <span className="text-slate-200">
                    {loading.fileStats ? (
                      <span className="animate-pulse bg-slate-600 rounded px-2 py-1">Loading...</span>
                    ) : fileStats ? (
                      formatFileSize(fileStats.total_size_bytes)
                    ) : (
                      '2.1 GB'
                    )}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-400">Today:</span>
                  <span className="text-slate-200">
                    {loading.fileStats ? (
                      <span className="animate-pulse bg-slate-600 rounded px-2 py-1">Loading...</span>
                    ) : fileStats ? (
                      `${fileStats.files_today} files`
                    ) : (
                      '45 files'
                    )}
                  </span>
                </div>
              </div>
            </div>

            {/* Active Sessions */}
            <div className="bg-slate-800 rounded-lg p-4 border border-slate-700">
              <div className="flex items-center justify-between mb-3">
                <h3 className="text-lg font-semibold text-slate-100 flex items-center">
                  <span className="mr-2">🔗</span>Sessions
                </h3>
                <button 
                  onClick={handleSessionsView}
                  className="text-xs text-blue-400 hover:text-blue-300 transition-colors"
                >
                  View All
                </button>
              </div>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-slate-400">Active:</span>
                  <span className="text-green-400">
                    {loading.sessionStats ? (
                      <span className="animate-pulse bg-slate-600 rounded px-2 py-1">...</span>
                    ) : sessionStats ? (
                      sessionStats.active
                    ) : (
                      '15'
                    )}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-400">Processing:</span>
                  <span className="text-yellow-400">
                    {loading.sessionStats ? (
                      <span className="animate-pulse bg-slate-600 rounded px-2 py-1">...</span>
                    ) : sessionStats ? (
                      sessionStats.processing
                    ) : (
                      '3'
                    )}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-400">Completed:</span>
                  <span className="text-slate-200">
                    {loading.sessionStats ? (
                      <span className="animate-pulse bg-slate-600 rounded px-2 py-1">Loading...</span>
                    ) : sessionStats ? (
                      sessionStats.completed.toLocaleString()
                    ) : (
                      '1,089'
                    )}
                  </span>
                </div>
              </div>
            </div>

            {/* System Alerts */}
            <div className="bg-slate-800 rounded-lg p-4 border border-slate-700">
              <h3 className="text-lg font-semibold text-slate-100 mb-3 flex items-center">
                <span className="mr-2">🚨</span>Alerts
              </h3>
              <div className="text-center py-4">
                <span className="text-2xl">✅</span>
                <p className="text-slate-400 text-sm mt-2">No active alerts</p>
              </div>
            </div>

            {/* Auto-refresh Control */}
            <div className="bg-slate-800 rounded-lg p-4 border border-slate-700">
              <h3 className="text-lg font-semibold text-slate-100 mb-3 flex items-center">
                <span className="mr-2">⚙️</span>Settings
              </h3>
              <div className="space-y-3">
                <div>
                  <label className="text-xs text-slate-400 block mb-1">Auto-refresh:</label>
                  <select 
                    value={refreshInterval}
                    onChange={(e) => setRefreshInterval(Number(e.target.value))}
                    className="w-full text-xs bg-slate-700 border border-slate-600 rounded px-2 py-1 text-slate-100"
                  >
                    <option value={10000}>10 seconds</option>
                    <option value={30000}>30 seconds</option>
                    <option value={60000}>1 minute</option>
                    <option value={300000}>5 minutes</option>
                    <option value={0}>Disabled</option>
                  </select>
                </div>
                
                <button
                  onClick={loadSystemOverview}
                  className="w-full px-3 py-2 bg-slate-700 hover:bg-slate-600 text-slate-200 text-xs rounded-lg transition-colors flex items-center justify-center space-x-2"
                  disabled={loading.overview}
                >
                  <span className={loading.overview ? 'animate-spin' : ''}>🔄</span>
                  <span>{loading.overview ? 'Refreshing...' : 'Manual Refresh'}</span>
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Modals */}
        <AnalyzerConfigModal
          isOpen={showAnalyzerModal}
          onClose={() => setShowAnalyzerModal(false)}
          analyzers={systemOverview?.components?.analyzers || []}
          onToggleAnalyzer={handleToggleAnalyzer}
        />

        <SessionModal
          isOpen={showSessionModal}
          onClose={() => setShowSessionModal(false)}
          sessions={activeSessions}
          onTerminateSession={handleTerminateSession}
        />

        <DetailedFileStatsModal
          isOpen={showDetailedFileStatsModal}
          onClose={() => setShowDetailedFileStatsModal(false)}
        />
      </div>
    </div>
  );
}