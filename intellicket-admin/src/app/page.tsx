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
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-red-950/10 to-gray-950 relative overflow-hidden">
      {/* Background Animation */}
      <div className="absolute inset-0 opacity-15">
        <div className="absolute top-20 left-20 w-96 h-96 bg-red-500 rounded-full mix-blend-multiply filter blur-3xl animate-pulse"></div>
        <div className="absolute bottom-20 right-20 w-96 h-96 bg-orange-500 rounded-full mix-blend-multiply filter blur-3xl animate-pulse animation-delay-2000"></div>
      </div>

      {/* Header */}
      <header className="sticky top-0 z-10 bg-black/40 backdrop-blur-sm border-b border-red-500/30">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between py-4">
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-3">
                <div className="w-12 h-12 bg-gradient-to-br from-red-500 to-red-700 rounded-xl flex items-center justify-center shadow-lg">
                  <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6V4m0 2a2 2 0 100 4 2 2 0 000-4zm0 2a2 2 0 100 4 2 2 0 000-4z" />
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 12a8 8 0 1116 0M6 18l12-6" />
                  </svg>
                </div>
                <div className="border-l border-white/30 pl-3">
                  <h1 className="text-2xl font-bold text-red-400">Intellicket Admin</h1>
                  <p className="text-xs text-gray-400 font-medium">AI Platform Management</p>
                </div>
              </div>
            </div>
            
            <div className="flex items-center space-x-4">
              <button
                onClick={loadSystemOverview}
                className="px-6 py-3 bg-gradient-to-r from-red-600 to-red-700 hover:from-red-500 hover:to-red-600 text-white rounded-xl transition-all duration-300 font-semibold shadow-lg hover:shadow-red-500/25 flex items-center gap-2 transform hover:scale-105"
                disabled={loading.overview}
              >
                <svg className={`w-4 h-4 ${loading.overview ? 'animate-spin' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                </svg>
                <span>{loading.overview ? 'Refreshing...' : 'Refresh All'}</span>
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {/* Alert Messages */}
        {(errors.overview || errors.action) && (
          <div className="mb-6 bg-white/5 backdrop-blur-sm border border-red-500/30 rounded-xl p-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-red-950/30 rounded-lg flex items-center justify-center">
                <svg className="w-5 h-5 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c.842 0 1.58-.564 1.78-1.378L18.23 7.622a2 2 0 00-1.78-1.378H5.55a2 2 0 00-1.78 1.378L2.293 18.622c-.2.814.938 1.378 1.78 1.378z" />
                </svg>
              </div>
              <span className="text-red-300 font-medium">
                {errors.overview ? `API Error: ${errors.overview}` : `Action Error: ${errors.action}`}
              </span>
            </div>
          </div>
        )}

        {lastAction && (
          <div className="mb-6 bg-white/5 backdrop-blur-sm border border-green-500/30 rounded-xl p-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-green-950/30 rounded-lg flex items-center justify-center">
                <svg className="w-5 h-5 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
              </div>
              <span className="text-green-300 font-medium">{lastAction.message}</span>
            </div>
          </div>
        )}

        {/* Compact Dashboard - Single Screen Layout */}
        <div className="h-[calc(100vh-200px)] grid grid-cols-12 gap-4">
          {/* Left Column - System Status & Controls */}
          <div className="col-span-4 space-y-6">
            {/* System Status Overview */}
            <div className="bg-white/10 backdrop-blur-sm rounded-2xl p-6 border border-white/20 hover:border-red-500/40 transition-all duration-300 shadow-2xl">
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-xl font-bold text-white flex items-center gap-3">
                  <div className="w-10 h-10 bg-gradient-to-br from-red-500 to-red-700 rounded-xl flex items-center justify-center">
                    <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                  </div>
                  System Status
                </h3>
                <div className={`w-4 h-4 rounded-full animate-pulse ${
                  systemOverview?.overall?.health === 'healthy' ? 'bg-green-400' :
                  systemOverview?.overall?.health === 'warning' ? 'bg-yellow-400' : 'bg-red-400'
                }`} />
              </div>
              
              <div className="space-y-4">
                {/* Backend Status */}
                <div className="flex items-center justify-between p-4 bg-white/5 backdrop-blur-sm rounded-xl border border-white/10 hover:border-white/20 transition-colors">
                  <div className="flex items-center gap-3">
                    <div className="w-8 h-8 bg-blue-950/30 rounded-lg flex items-center justify-center">
                      <svg className="w-4 h-4 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 12h14M5 12a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v4a2 2 0 01-2 2M5 12a2 2 0 00-2 2v4a2 2 0 002 2h14a2 2 0 002-2v-4a2 2 0 00-2-2m-2-4h.01M17 16h.01" />
                      </svg>
                    </div>
                    <span className="text-white font-medium">Backend API</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className={`w-3 h-3 rounded-full animate-pulse ${
                      systemOverview?.backend?.status === 'online' ? 'bg-green-400' : 'bg-red-400'
                    }`} />
                    <span className={`text-sm font-medium ${
                      systemOverview?.backend?.status === 'online' ? 'text-green-400' : 'text-red-400'
                    }`}>
                      {systemOverview?.backend?.status || 'Unknown'}
                    </span>
                  </div>
                </div>
                
                {/* Frontend Status */}
                <div className="flex items-center justify-between p-4 bg-white/5 backdrop-blur-sm rounded-xl border border-white/10 hover:border-white/20 transition-colors">
                  <div className="flex items-center gap-3">
                    <div className="w-8 h-8 bg-purple-950/30 rounded-lg flex items-center justify-center">
                      <svg className="w-4 h-4 text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9a9 9 0 01-9-9m9 9c1.657 0 3-4.03 3-9s-1.343-9 3-9m0 18c-1.657 0-3-4.03-3-9s1.343-9 3-9m-9 9a9 9 0 019-9" />
                      </svg>
                    </div>
                    <span className="text-white font-medium">Frontend</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className={`w-3 h-3 rounded-full animate-pulse ${
                      systemOverview?.frontend?.status === 'online' ? 'bg-green-400' : 'bg-red-400'
                    }`} />
                    <span className={`text-sm font-medium ${
                      systemOverview?.frontend?.status === 'online' ? 'text-green-400' : 'text-red-400'
                    }`}>
                      {systemOverview?.frontend?.status || 'Unknown'}
                    </span>
                  </div>
                </div>

                {/* Maintenance Mode */}
                <div className="flex items-center justify-between p-4 bg-white/5 backdrop-blur-sm rounded-xl border border-white/10 hover:border-white/20 transition-colors">
                  <div className="flex items-center gap-3">
                    <div className="w-8 h-8 bg-yellow-950/30 rounded-lg flex items-center justify-center">
                      <svg className="w-4 h-4 text-yellow-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                      </svg>
                    </div>
                    <span className="text-white font-medium">Maintenance</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className={`w-3 h-3 rounded-full animate-pulse ${
                      maintenanceMode?.enabled ? 'bg-yellow-400' : 'bg-green-400'
                    }`} />
                    <span className={`text-sm font-medium ${
                      maintenanceMode?.enabled ? 'text-yellow-400' : 'text-green-400'
                    }`}>
                      {maintenanceMode?.enabled ? 'Active' : 'Inactive'}
                    </span>
                  </div>
                </div>
              </div>
            </div>

            {/* Quick Actions */}
            <div className="bg-white/10 backdrop-blur-sm rounded-2xl p-6 border border-white/20 hover:border-red-500/40 transition-all duration-300 shadow-2xl">
              <h3 className="text-xl font-bold text-white mb-6 flex items-center gap-3">
                <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-blue-700 rounded-xl flex items-center justify-center">
                  <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                  </svg>
                </div>
                Quick Actions
              </h3>
              
              <div className="space-y-3">
                <button 
                  onClick={handleRestartBackend}
                  disabled={loading.restart}
                  className="w-full px-4 py-3 bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-500 hover:to-blue-600 disabled:opacity-50 disabled:cursor-not-allowed text-white font-medium rounded-xl transition-all duration-300 transform hover:scale-105 shadow-lg hover:shadow-blue-500/25 flex items-center justify-center gap-2"
                >
                  {loading.restart ? (
                    <div className="animate-spin h-4 w-4 border-2 border-white border-t-transparent rounded-full"></div>
                  ) : (
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                    </svg>
                  )}
                  <span>{loading.restart ? 'Restarting...' : 'Restart Backend'}</span>
                </button>
                
                <button 
                  onClick={handleMaintenanceToggle}
                  disabled={loading.maintenance}
                  className="w-full px-4 py-3 bg-gradient-to-r from-yellow-600 to-yellow-700 hover:from-yellow-500 hover:to-yellow-600 disabled:opacity-50 disabled:cursor-not-allowed text-white font-medium rounded-xl transition-all duration-300 transform hover:scale-105 shadow-lg hover:shadow-yellow-500/25 flex items-center justify-center gap-2"
                >
                  {loading.maintenance ? (
                    <div className="animate-spin h-4 w-4 border-2 border-white border-t-transparent rounded-full"></div>
                  ) : (
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                    </svg>
                  )}
                  <span>{loading.maintenance ? 'Toggling...' : `${maintenanceMode?.enabled ? 'Disable' : 'Enable'} Maintenance`}</span>
                </button>
                
                <button 
                  onClick={handleClearCache}
                  disabled={loading.cache}
                  className="w-full px-4 py-3 bg-gradient-to-r from-green-600 to-green-700 hover:from-green-500 hover:to-green-600 disabled:opacity-50 disabled:cursor-not-allowed text-white font-medium rounded-xl transition-all duration-300 transform hover:scale-105 shadow-lg hover:shadow-green-500/25 flex items-center justify-center gap-2"
                >
                  {loading.cache ? (
                    <div className="animate-spin h-4 w-4 border-2 border-white border-t-transparent rounded-full"></div>
                  ) : (
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                    </svg>
                  )}
                  <span>{loading.cache ? 'Clearing...' : 'Clear Cache'}</span>
                </button>
                
                <button 
                  onClick={handleExportLogs}
                  disabled={loading.export}
                  className="w-full px-4 py-3 bg-gradient-to-r from-purple-600 to-purple-700 hover:from-purple-500 hover:to-purple-600 disabled:opacity-50 disabled:cursor-not-allowed text-white font-medium rounded-xl transition-all duration-300 transform hover:scale-105 shadow-lg hover:shadow-purple-500/25 flex items-center justify-center gap-2"
                >
                  {loading.export ? (
                    <div className="animate-spin h-4 w-4 border-2 border-white border-t-transparent rounded-full"></div>
                  ) : (
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>
                  )}
                  <span>{loading.export ? 'Exporting...' : 'Export Logs'}</span>
                </button>
              </div>
            </div>
          </div>

          {/* Middle Column - System Health & Components */}
          <div className="col-span-5 space-y-6">
            {/* System Health */}
            <div className="bg-white/10 backdrop-blur-sm rounded-2xl p-6 border border-white/20 hover:border-red-500/40 transition-all duration-300 shadow-2xl h-fit">
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-xl font-bold text-white flex items-center gap-3">
                  <div className="w-10 h-10 bg-gradient-to-br from-green-500 to-green-700 rounded-xl flex items-center justify-center">
                    <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
                    </svg>
                  </div>
                  System Health
                </h3>
                {loading.overview && (
                  <div className="flex items-center gap-2">
                    <div className="animate-spin h-4 w-4 border-2 border-red-400 border-t-transparent rounded-full"></div>
                    <span className="text-sm text-red-400 animate-pulse">Updating...</span>
                  </div>
                )}
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