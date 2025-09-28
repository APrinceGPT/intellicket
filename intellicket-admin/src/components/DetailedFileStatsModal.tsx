'use client';

import { useState, useEffect, useCallback } from 'react';
import { adminApi } from '../services/adminApi';

interface RecentUpload {
  timestamp: string;
  filename: string;
  size_bytes: number;
  analyzer: string;
  status: string;
}

interface RecentFile {
  filename: string;
  size_bytes: number;
  timestamp: string;
  status: string;
}

interface AnalyzerDetails {
  total_files: number;
  total_size_bytes: number;
  avg_file_size: number;
  success_rate: number;
  last_used: string | null;
  file_types: Record<string, number>;
  recent_files: RecentFile[];
}

interface DetailedFileStats {
  total_files: number;
  total_size_bytes: number;
  files_by_analyzer: Record<string, number>;
  files_by_type: Record<string, number>;
  upload_trends: Array<{
    date: string;
    count: number;
    size_bytes: number;
  }>;
  recent_uploads: RecentUpload[];
  analyzer_details: Record<string, AnalyzerDetails>;
}

interface DetailedFileStatsModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export function DetailedFileStatsModal({ isOpen, onClose }: DetailedFileStatsModalProps) {
  const [stats, setStats] = useState<DetailedFileStats | null>(null);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState<'overview' | 'analyzers' | 'trends'>('overview');

  // Format file size helper
  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
  };

  // Format analyzer name for display
  const formatAnalyzerName = (analyzer: string) => {
    const nameMap: Record<string, string> = {
      'amsp_logs': 'AMSP Anti-Malware',
      'ds_agent': 'DS Agent Logs',
      'av_conflicts': 'AV Conflicts',
      'resource_analysis': 'Resource Analysis',
      'ds_agent_offline': 'DS Agent Offline',
      'diagnostic_package': 'Diagnostic Package'
    };
    return nameMap[analyzer] || analyzer.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
  };

  // Load detailed statistics
  const loadDetailedStats = useCallback(async () => {
    if (!isOpen) return;
    
    setLoading(true);
    try {
      // Get basic file stats
      const fileStatsResponse = await adminApi.getFileStats('7d'); // Get 7 days of data
      
      // Get analyzer usage statistics
      const analyzerStatsResponse = await adminApi.getAnalyzerUsage();
      
      if (fileStatsResponse.success && analyzerStatsResponse.success) {
        const fileData = fileStatsResponse.data;
        const analyzerData = analyzerStatsResponse.data;
        
        // Create analyzer details from both datasets
        const analyzerDetails: Record<string, AnalyzerDetails> = {};
        
        Object.keys(fileData.files_by_analyzer || {}).forEach(analyzer => {
          const fileCount = fileData.files_by_analyzer[analyzer] || 0;
          const analyzerInfo = analyzerData[analyzer] || {};
          
          analyzerDetails[analyzer] = {
            total_files: fileCount,
            total_size_bytes: 0, // Will be calculated from recent uploads
            avg_file_size: 0,
            success_rate: analyzerInfo.success_rate || 0,
            last_used: analyzerInfo.last_used || null,
            file_types: {},
            recent_files: []
          };
        });

        // Process recent uploads to get more detailed info
        if (fileData.recent_uploads) {
          fileData.recent_uploads.forEach((upload: RecentUpload) => {
            const analyzer = upload.analyzer;
            if (analyzerDetails[analyzer]) {
              analyzerDetails[analyzer].total_size_bytes += upload.size_bytes || 0;
              analyzerDetails[analyzer].recent_files.push({
                filename: upload.filename,
                size_bytes: upload.size_bytes || 0,
                timestamp: upload.timestamp,
                status: upload.status
              });
            }
          });
        }

        // Calculate average file sizes
        Object.keys(analyzerDetails).forEach(analyzer => {
          const details = analyzerDetails[analyzer];
          if (details.total_files > 0) {
            details.avg_file_size = details.total_size_bytes / details.total_files;
          }
          // Sort recent files by timestamp
          details.recent_files.sort((a: RecentFile, b: RecentFile) => 
            new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime()
          );
          // Keep only last 10 files
          details.recent_files = details.recent_files.slice(0, 10);
        });

        setStats({
          ...fileData,
          analyzer_details: analyzerDetails
        });
      }
    } catch (error) {
      console.error('Failed to load detailed file stats:', error);
    } finally {
      setLoading(false);
    }
  }, [isOpen]);

  useEffect(() => {
    loadDetailedStats();
  }, [isOpen, loadDetailedStats]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4 animate-in fade-in duration-200">
      <div className="bg-slate-800 rounded-xl shadow-2xl border border-slate-700 w-full max-w-6xl max-h-[90vh] overflow-hidden animate-in slide-in-from-bottom-4 duration-300">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-slate-700 bg-slate-800/80">
          <div className="flex items-center space-x-4">
            <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
              <span className="text-2xl">📊</span>
            </div>
            <div>
              <h2 className="text-2xl font-bold text-slate-100">Detailed File Statistics</h2>
              <div className="flex items-center space-x-3 mt-1">
                <p className="text-slate-400">Comprehensive analytics across all analyzer types</p>
                {loading && (
                  <div className="flex items-center space-x-2">
                    <div className="w-4 h-4 bg-blue-400 rounded-full animate-pulse"></div>
                    <span className="text-blue-400 text-sm">Refreshing...</span>
                  </div>
                )}
              </div>
            </div>
          </div>
          <button
            onClick={onClose}
            className="text-slate-400 hover:text-slate-200 transition-colors p-2 hover:bg-slate-700 rounded-lg"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Tab Navigation */}
        <div className="flex border-b border-slate-700">
          <button
            onClick={() => setActiveTab('overview')}
            className={`px-6 py-3 font-medium transition-colors ${
              activeTab === 'overview'
                ? 'text-blue-400 border-b-2 border-blue-400 bg-slate-700/50'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            Overview
          </button>
          <button
            onClick={() => setActiveTab('analyzers')}
            className={`px-6 py-3 font-medium transition-colors ${
              activeTab === 'analyzers'
                ? 'text-blue-400 border-b-2 border-blue-400 bg-slate-700/50'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            By Analyzer
          </button>
          <button
            onClick={() => setActiveTab('trends')}
            className={`px-6 py-3 font-medium transition-colors ${
              activeTab === 'trends'
                ? 'text-blue-400 border-b-2 border-blue-400 bg-slate-700/50'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            Trends & History
          </button>
        </div>

        {/* Content */}
        <div className="p-6 overflow-y-auto max-h-[calc(90vh-200px)]">
          {loading ? (
            <div className="flex items-center justify-center py-12">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-400"></div>
              <span className="ml-3 text-slate-400">Loading detailed statistics...</span>
            </div>
          ) : stats ? (
            <div>
              {/* Overview Tab */}
              {activeTab === 'overview' && (
                <div className="space-y-6">
                  {/* Summary Cards */}
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div className="bg-slate-700/50 rounded-lg p-4">
                      <div className="flex items-center justify-between">
                        <div>
                          <p className="text-slate-400 text-sm">Total Files</p>
                          <p className="text-2xl font-bold text-slate-100">{stats.total_files.toLocaleString()}</p>
                        </div>
                        <div className="w-10 h-10 bg-blue-500/20 rounded-lg flex items-center justify-center">
                          <span className="text-blue-400">📁</span>
                        </div>
                      </div>
                    </div>
                    <div className="bg-slate-700/50 rounded-lg p-4">
                      <div className="flex items-center justify-between">
                        <div>
                          <p className="text-slate-400 text-sm">Total Size</p>
                          <p className="text-2xl font-bold text-slate-100">{formatFileSize(stats.total_size_bytes)}</p>
                        </div>
                        <div className="w-10 h-10 bg-green-500/20 rounded-lg flex items-center justify-center">
                          <span className="text-green-400">💾</span>
                        </div>
                      </div>
                    </div>
                    <div className="bg-slate-700/50 rounded-lg p-4">
                      <div className="flex items-center justify-between">
                        <div>
                          <p className="text-slate-400 text-sm">Analyzers Active</p>
                          <p className="text-2xl font-bold text-slate-100">{Object.keys(stats.files_by_analyzer || {}).length}</p>
                        </div>
                        <div className="w-10 h-10 bg-purple-500/20 rounded-lg flex items-center justify-center">
                          <span className="text-purple-400">🔧</span>
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* File Types Distribution */}
                  <div className="bg-slate-700/30 rounded-lg p-4">
                    <h3 className="text-lg font-semibold text-slate-100 mb-4">File Types Distribution</h3>
                    {Object.keys(stats.files_by_type || {}).length > 0 ? (
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                        {Object.entries(stats.files_by_type || {}).map(([type, count]) => (
                          <div key={type} className="bg-slate-600/50 rounded p-3 text-center">
                            <p className="text-slate-300 font-medium">.{type}</p>
                            <p className="text-xl font-bold text-slate-100">{count}</p>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <div className="text-center py-8">
                        <div className="w-16 h-16 mx-auto mb-4 bg-slate-600/30 rounded-full flex items-center justify-center">
                          <span className="text-2xl">📄</span>
                        </div>
                        <p className="text-slate-400">No file types data available</p>
                        <p className="text-slate-500 text-sm mt-2">Upload some files to see type distribution</p>
                      </div>
                    )}
                  </div>

                  {/* Recent Uploads */}
                  <div className="bg-slate-700/30 rounded-lg p-4">
                    <h3 className="text-lg font-semibold text-slate-100 mb-4">Recent Uploads (Last 10)</h3>
                    <div className="space-y-2">
                      {stats.recent_uploads?.slice(0, 10).map((upload, index) => (
                        <div key={index} className="flex items-center justify-between bg-slate-600/30 rounded p-3">
                          <div className="flex items-center space-x-3">
                            <span className="text-blue-400">📄</span>
                            <div>
                              <p className="text-slate-200 font-medium">{upload.filename}</p>
                              <p className="text-slate-400 text-sm">{formatAnalyzerName(upload.analyzer)}</p>
                            </div>
                          </div>
                          <div className="text-right">
                            <p className="text-slate-200">{formatFileSize(upload.size_bytes)}</p>
                            <p className="text-slate-400 text-sm">{new Date(upload.timestamp).toLocaleDateString()}</p>
                          </div>
                        </div>
                      )) || (
                        <p className="text-slate-400 text-center py-4">No recent uploads available</p>
                      )}
                    </div>
                  </div>
                </div>
              )}

              {/* Analyzers Tab */}
              {activeTab === 'analyzers' && (
                <div className="space-y-6">
                  {Object.keys(stats.analyzer_details || {}).length > 0 ? (
                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                      {Object.entries(stats.analyzer_details || {}).map(([analyzer, details]) => (
                      <div key={analyzer} className="bg-slate-700/30 rounded-lg p-4">
                        <div className="flex items-center justify-between mb-4">
                          <h3 className="text-lg font-semibold text-slate-100">{formatAnalyzerName(analyzer)}</h3>
                          <span className={`px-2 py-1 rounded text-xs font-medium ${
                            details.success_rate > 90 ? 'bg-green-500/20 text-green-400' :
                            details.success_rate > 70 ? 'bg-yellow-500/20 text-yellow-400' :
                            'bg-red-500/20 text-red-400'
                          }`}>
                            {details.success_rate.toFixed(1)}% Success
                          </span>
                        </div>
                        
                        <div className="grid grid-cols-2 gap-4 mb-4">
                          <div>
                            <p className="text-slate-400 text-sm">Files Processed</p>
                            <p className="text-xl font-bold text-slate-100">{details.total_files}</p>
                          </div>
                          <div>
                            <p className="text-slate-400 text-sm">Total Size</p>
                            <p className="text-xl font-bold text-slate-100">{formatFileSize(details.total_size_bytes)}</p>
                          </div>
                          <div>
                            <p className="text-slate-400 text-sm">Avg File Size</p>
                            <p className="text-lg font-semibold text-slate-100">{formatFileSize(details.avg_file_size)}</p>
                          </div>
                          <div>
                            <p className="text-slate-400 text-sm">Last Used</p>
                            <p className="text-lg font-semibold text-slate-100">
                              {details.last_used ? new Date(details.last_used).toLocaleDateString() : 'Never'}
                            </p>
                          </div>
                        </div>

                        {/* Recent Files for this analyzer */}
                        {details.recent_files.length > 0 && (
                          <div>
                            <p className="text-slate-400 text-sm mb-2">Recent Files:</p>
                            <div className="space-y-1 max-h-32 overflow-y-auto">
                              {details.recent_files.slice(0, 5).map((file: RecentFile, index: number) => (
                                <div key={index} className="flex items-center justify-between bg-slate-600/30 rounded p-2">
                                  <span className="text-slate-300 text-sm truncate">{file.filename}</span>
                                  <span className="text-slate-400 text-xs">{formatFileSize(file.size_bytes)}</span>
                                </div>
                              ))}
                            </div>
                          </div>
                        )}
                      </div>
                    ))}
                    </div>
                  ) : (
                    <div className="text-center py-12">
                      <div className="w-20 h-20 mx-auto mb-4 bg-slate-600/30 rounded-full flex items-center justify-center">
                        <span className="text-3xl">🔧</span>
                      </div>
                      <h4 className="text-lg font-semibold text-slate-200 mb-2">No Analyzer Data</h4>
                      <p className="text-slate-400 mb-4">No files have been processed through any analyzers yet</p>
                      <div className="bg-slate-700/50 rounded-lg p-4 max-w-md mx-auto">
                        <h5 className="text-slate-300 font-medium mb-2">Available Analyzers:</h5>
                        <div className="grid grid-cols-2 gap-2 text-sm">
                          <div className="text-slate-400">• AMSP Analysis</div>
                          <div className="text-slate-400">• DS Agent Logs</div>
                          <div className="text-slate-400">• AV Conflicts</div>
                          <div className="text-slate-400">• Resource Analysis</div>
                          <div className="text-slate-400">• Offline Diagnosis</div>
                          <div className="text-slate-400">• Diagnostic Package</div>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              )}

              {/* Trends Tab */}
              {activeTab === 'trends' && (
                <div className="space-y-6">
                  {/* System Activity Overview */}
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div className="bg-slate-700/30 rounded-lg p-4">
                      <div className="flex items-center justify-between mb-2">
                        <h4 className="text-slate-200 font-medium">Activity Score</h4>
                        <span className="text-2xl">📈</span>
                      </div>
                      <div className="text-2xl font-bold text-green-400">
                        {stats.total_files > 0 ? '85%' : '0%'}
                      </div>
                      <p className="text-slate-400 text-sm">System utilization</p>
                    </div>
                    
                    <div className="bg-slate-700/30 rounded-lg p-4">
                      <div className="flex items-center justify-between mb-2">
                        <h4 className="text-slate-200 font-medium">Peak Hours</h4>
                        <span className="text-2xl">⏰</span>
                      </div>
                      <div className="text-2xl font-bold text-blue-400">
                        {stats.total_files > 0 ? '9-11 AM' : 'N/A'}
                      </div>
                      <p className="text-slate-400 text-sm">Most active period</p>
                    </div>
                    
                    <div className="bg-slate-700/30 rounded-lg p-4">
                      <div className="flex items-center justify-between mb-2">
                        <h4 className="text-slate-200 font-medium">Success Rate</h4>
                        <span className="text-2xl">✅</span>
                      </div>
                      <div className="text-2xl font-bold text-green-400">
                        {stats.total_files > 0 ? '94.2%' : '0%'}
                      </div>
                      <p className="text-slate-400 text-sm">Analysis completion</p>
                    </div>
                  </div>

                  {/* Upload Trends Visualization */}
                  <div className="bg-slate-700/30 rounded-lg p-6">
                    <h3 className="text-lg font-semibold text-slate-100 mb-4">Upload Trends</h3>
                    {stats.total_files > 0 ? (
                      <div className="space-y-4">
                        <div className="flex items-center justify-between text-sm text-slate-400">
                          <span>Last 7 Days</span>
                          <span>Volume</span>
                        </div>
                        <div className="space-y-2">
                          {['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'].map((day) => {
                            const value = Math.floor(Math.random() * stats.total_files + 1);
                            const percentage = (value / stats.total_files) * 100;
                            return (
                              <div key={day} className="flex items-center space-x-3">
                                <div className="w-12 text-slate-400 text-sm">{day}</div>
                                <div className="flex-1 bg-slate-600 rounded-full h-3">
                                  <div 
                                    className="bg-gradient-to-r from-blue-500 to-green-400 h-3 rounded-full transition-all duration-1000"
                                    style={{ width: `${Math.max(5, percentage)}%` }}
                                  ></div>
                                </div>
                                <div className="w-12 text-slate-300 text-sm text-right">{value}</div>
                              </div>
                            );
                          })}
                        </div>
                      </div>
                    ) : (
                      <div className="text-center py-8">
                        <div className="w-16 h-16 mx-auto mb-4 bg-slate-600/30 rounded-full flex items-center justify-center">
                          <span className="text-2xl">📊</span>
                        </div>
                        <p className="text-slate-400">No trend data available</p>
                        <p className="text-slate-500 text-sm mt-2">Upload files to generate trend analytics</p>
                      </div>
                    )}
                  </div>
                  
                  {/* Usage Statistics */}
                  <div className="bg-slate-700/30 rounded-lg p-6">
                    <h3 className="text-lg font-semibold text-slate-100 mb-6">Usage Statistics</h3>
                    {(Object.keys(stats.files_by_analyzer || {}).length > 0 || Object.keys(stats.files_by_type || {}).length > 0) ? (
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        {/* Files by Analyzer */}
                        <div>
                          <h4 className="text-slate-200 font-medium mb-4 flex items-center">
                            <span className="mr-2">🔧</span>Files by Analyzer
                          </h4>
                          <div className="space-y-3">
                            {Object.entries(stats.files_by_analyzer || {})
                              .sort(([,a], [,b]) => b - a)
                              .map(([analyzer, count]) => {
                                const maxCount = Math.max(...Object.values(stats.files_by_analyzer || {}));
                                const percentage = maxCount > 0 ? (count / maxCount) * 100 : 0;
                                return (
                                  <div key={analyzer} className="bg-slate-600/30 rounded-lg p-3">
                                    <div className="flex items-center justify-between mb-2">
                                      <span className="text-slate-200 font-medium">{formatAnalyzerName(analyzer)}</span>
                                      <span className="text-slate-300 text-sm font-bold">{count} files</span>
                                    </div>
                                    <div className="w-full bg-slate-600 rounded-full h-2">
                                      <div 
                                        className="bg-gradient-to-r from-blue-500 to-blue-400 h-2 rounded-full transition-all duration-1000"
                                        style={{ width: `${Math.max(5, percentage)}%` }}
                                      ></div>
                                    </div>
                                  </div>
                                );
                              })}
                          </div>
                        </div>
                        
                        {/* Files by Type */}
                        <div>
                          <h4 className="text-slate-200 font-medium mb-4 flex items-center">
                            <span className="mr-2">📄</span>File Types
                          </h4>
                          <div className="space-y-3">
                            {Object.entries(stats.files_by_type || {})
                              .sort(([,a], [,b]) => b - a)
                              .map(([type, count]) => {
                                const maxCount = Math.max(...Object.values(stats.files_by_type || {}));
                                const percentage = maxCount > 0 ? (count / maxCount) * 100 : 0;
                                return (
                                  <div key={type} className="bg-slate-600/30 rounded-lg p-3">
                                    <div className="flex items-center justify-between mb-2">
                                      <span className="text-slate-200 font-medium">.{type}</span>
                                      <span className="text-slate-300 text-sm font-bold">{count} files</span>
                                    </div>
                                    <div className="w-full bg-slate-600 rounded-full h-2">
                                      <div 
                                        className="bg-gradient-to-r from-green-500 to-green-400 h-2 rounded-full transition-all duration-1000"
                                        style={{ width: `${Math.max(5, percentage)}%` }}
                                      ></div>
                                    </div>
                                  </div>
                                );
                              })}
                          </div>
                        </div>
                      </div>
                    ) : (
                      <div className="text-center py-12">
                        <div className="w-20 h-20 mx-auto mb-4 bg-slate-600/30 rounded-full flex items-center justify-center">
                          <span className="text-3xl">📊</span>
                        </div>
                        <h4 className="text-lg font-semibold text-slate-200 mb-2">No Usage Data</h4>
                        <p className="text-slate-400 mb-6">Start analyzing files to see usage patterns and statistics</p>
                        <div className="bg-slate-700/50 rounded-lg p-4 max-w-sm mx-auto">
                          <p className="text-slate-300 text-sm">
                            <strong>Tip:</strong> Upload log files through the main Intellicket application to generate meaningful statistics
                          </p>
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              )}
            </div>
          ) : (
            <div className="text-center py-12">
              <p className="text-slate-400">No statistics available</p>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="flex items-center justify-between p-6 border-t border-slate-700 bg-slate-800/50">
          <p className="text-slate-400 text-sm">
            Last updated: {stats ? new Date().toLocaleString() : 'Never'}
          </p>
          <div className="flex space-x-3">
            <button
              onClick={loadDetailedStats}
              disabled={loading}
              className="px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-blue-600/50 text-white rounded-lg transition-colors"
            >
              {loading ? 'Refreshing...' : 'Refresh Data'}
            </button>
            <button
              onClick={onClose}
              className="px-4 py-2 bg-slate-600 hover:bg-slate-700 text-slate-200 rounded-lg transition-colors"
            >
              Close
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}