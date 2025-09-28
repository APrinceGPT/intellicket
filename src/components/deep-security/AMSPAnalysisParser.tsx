import React from 'react';

interface AMSPAnalysisData {
  summary?: string;
  installation_summary?: string;
  errors?: Array<{ message: string; timestamp?: string; severity?: string }>;
  warnings?: Array<{ message: string; timestamp?: string; severity?: string }>;
  critical_issues?: Array<{ message: string; timestamp?: string; severity?: string }>;
  operation_analysis?: Record<string, unknown>;
  known_issues?: string[];
  recommendations?: string[];
  metadata?: Record<string, unknown>;
  [key: string]: unknown;
}

interface AMSPAnalysisParserProps {
  analysisData: AMSPAnalysisData;
}

const AMSPAnalysisParser: React.FC<AMSPAnalysisParserProps> = ({ analysisData }) => {
  // Extract key metrics from analysis data
  const extractMetrics = () => {
    const metadata = analysisData.metadata as Record<string, unknown> || {};
    const errors = analysisData.errors || [];
    const warnings = analysisData.warnings || [];
    const criticalIssues = analysisData.critical_issues || [];
    
    return {
      totalLines: (metadata.total_lines as number) || 0,
      errorsCount: errors.length,
      warningsCount: warnings.length,
      criticalCount: criticalIssues.length,
      patternFailures: (metadata.pattern_failures as number) || 0,
      bpfFailures: (metadata.bpf_failures as number) || 0,
      trendxFailures: (metadata.trendx_failures as number) || 0
    };
  };

  const metrics = extractMetrics();
  
  const getSeverityColor = (severity: string) => {
    switch (severity?.toLowerCase()) {
      case 'critical': return 'text-red-400 bg-red-900/20 border-red-400/30';
      case 'high': return 'text-orange-400 bg-orange-900/20 border-orange-400/30';
      case 'medium': return 'text-yellow-400 bg-yellow-900/20 border-yellow-400/30';
      case 'low': return 'text-green-400 bg-green-900/20 border-green-400/30';
      default: return 'text-blue-400 bg-blue-900/20 border-blue-400/30';
    }
  };

  const status = metrics.criticalCount > 0 ? 'critical' : 
                metrics.errorsCount > 0 ? 'error' : 
                metrics.warningsCount > 0 ? 'warning' : 'success';
  
  const statusConfig = {
    critical: { icon: '🔴', title: 'Critical AMSP Issues', color: 'text-red-400' },
    error: { icon: '❌', title: 'AMSP Errors Detected', color: 'text-orange-400' },
    warning: { icon: '⚠️', title: 'AMSP Warnings Found', color: 'text-yellow-400' },
    success: { icon: '✅', title: 'AMSP Analysis Complete', color: 'text-green-400' }
  }[status];

  return (
    <div className="space-y-4">
      {/* Status Overview */}
      <div className={`${getSeverityColor(status)} border rounded-xl p-4`}>
        <div className="flex items-center space-x-3 mb-3">
          <span className="text-2xl">{statusConfig.icon}</span>
          <h4 className={`text-lg font-semibold ${statusConfig.color}`}>
            {statusConfig.title}
          </h4>
        </div>
        <p className="text-gray-300 text-sm leading-relaxed">
          {analysisData.summary || 'AMSP Anti-Malware log analysis completed'}
        </p>
        {analysisData.installation_summary && (
          <p className="text-gray-400 text-xs mt-2">
            <strong>Installation:</strong> {analysisData.installation_summary}
          </p>
        )}
      </div>

      {/* Metrics Grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-white/5 rounded-lg p-4 border border-white/10">
          <div className="flex items-center space-x-2 mb-2">
            <span className="text-blue-400">📄</span>
            <h5 className="text-sm font-medium text-gray-300">Total Lines</h5>
          </div>
          <p className="text-2xl font-bold text-white">{metrics.totalLines.toLocaleString()}</p>
        </div>

        <div className="bg-white/5 rounded-lg p-4 border border-white/10">
          <div className="flex items-center space-x-2 mb-2">
            <span className="text-red-400">🔥</span>
            <h5 className="text-sm font-medium text-gray-300">Critical Issues</h5>
          </div>
          <p className="text-2xl font-bold text-white">{metrics.criticalCount}</p>
        </div>

        <div className="bg-white/5 rounded-lg p-4 border border-white/10">
          <div className="flex items-center space-x-2 mb-2">
            <span className="text-orange-400">❌</span>
            <h5 className="text-sm font-medium text-gray-300">Errors</h5>
          </div>
          <p className="text-2xl font-bold text-white">{metrics.errorsCount}</p>
        </div>

        <div className="bg-white/5 rounded-lg p-4 border border-white/10">
          <div className="flex items-center space-x-2 mb-2">
            <span className="text-yellow-400">⚠️</span>
            <h5 className="text-sm font-medium text-gray-300">Warnings</h5>
          </div>
          <p className="text-2xl font-bold text-white">{metrics.warningsCount}</p>
        </div>
      </div>

      {/* AMSP Specific Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-white/5 rounded-lg p-4 border border-white/10">
          <div className="flex items-center space-x-2 mb-2">
            <span className="text-purple-400">🔗</span>
            <h5 className="text-sm font-medium text-gray-300">Pattern Failures</h5>
          </div>
          <p className="text-2xl font-bold text-white">{metrics.patternFailures}</p>
        </div>

        <div className="bg-white/5 rounded-lg p-4 border border-white/10">
          <div className="flex items-center space-x-2 mb-2">
            <span className="text-cyan-400">🛡️</span>
            <h5 className="text-sm font-medium text-gray-300">BPF Failures</h5>
          </div>
          <p className="text-2xl font-bold text-white">{metrics.bpfFailures}</p>
        </div>

        <div className="bg-white/5 rounded-lg p-4 border border-white/10">
          <div className="flex items-center space-x-2 mb-2">
            <span className="text-green-400">🔧</span>
            <h5 className="text-sm font-medium text-gray-300">TrendX Failures</h5>
          </div>
          <p className="text-2xl font-bold text-white">{metrics.trendxFailures}</p>
        </div>
      </div>

      {/* Issues List */}
      {(metrics.criticalCount > 0 || metrics.errorsCount > 0) && (
        <div className="bg-white/5 rounded-lg p-4 border border-white/10">
          <div className="flex items-center space-x-2 mb-3">
            <span className="text-red-400">🚨</span>
            <h5 className="text-sm font-medium text-gray-300">AMSP Issues Found</h5>
          </div>
          <div className="space-y-2 max-h-60 overflow-y-auto">
            {analysisData.critical_issues?.map((issue, index) => (
              <div key={`critical-${index}`} className="bg-red-900/20 rounded-lg p-3 border border-red-400/20">
                <div className="flex items-center space-x-2 mb-1">
                  <span className="text-red-400 text-xs font-medium">CRITICAL</span>
                  {issue.timestamp && <span className="text-gray-500 text-xs">{issue.timestamp}</span>}
                </div>
                <p className="text-gray-300 text-sm">{issue.message}</p>
              </div>
            ))}
            {analysisData.errors?.map((error, index) => (
              <div key={`error-${index}`} className="bg-orange-900/20 rounded-lg p-3 border border-orange-400/20">
                <div className="flex items-center space-x-2 mb-1">
                  <span className="text-orange-400 text-xs font-medium">ERROR</span>
                  {error.timestamp && <span className="text-gray-500 text-xs">{error.timestamp}</span>}
                </div>
                <p className="text-gray-300 text-sm">{error.message}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Known Issues */}
      {analysisData.known_issues && analysisData.known_issues.length > 0 && (
        <div className="bg-white/5 rounded-lg p-4 border border-white/10">
          <div className="flex items-center space-x-2 mb-3">
            <span className="text-yellow-400">🔍</span>
            <h5 className="text-sm font-medium text-gray-300">Known Issues</h5>
          </div>
          <div className="space-y-2">
            {analysisData.known_issues.map((issue, index) => (
              <div key={index} className="bg-yellow-900/20 rounded-lg p-3 border border-yellow-400/20">
                <p className="text-gray-300 text-sm">{issue}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Recommendations */}
      {analysisData.recommendations && analysisData.recommendations.length > 0 && (
        <div className="bg-white/5 rounded-lg p-4 border border-white/10">
          <div className="flex items-center space-x-2 mb-3">
            <span className="text-blue-400">💡</span>
            <h5 className="text-sm font-medium text-gray-300">AMSP Recommendations</h5>
          </div>
          <div className="space-y-2">
            {analysisData.recommendations.map((rec, index) => (
              <div key={index} className="flex items-start space-x-2">
                <span className="text-blue-400 text-sm">•</span>
                <span className="text-gray-300 text-sm" dangerouslySetInnerHTML={{ __html: rec }} />
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Raw Data Toggle */}
      <details className="bg-black/20 rounded-lg border border-gray-600">
        <summary className="p-3 cursor-pointer text-gray-400 hover:text-gray-300 text-sm font-medium">
          🔧 View Raw Analysis Data
        </summary>
        <div className="p-3 border-t border-gray-600">
          <pre className="text-xs text-gray-500 overflow-auto max-h-40 bg-black/30 p-2 rounded">
            {JSON.stringify(analysisData, null, 2)}
          </pre>
        </div>
      </details>
    </div>
  );
};

export default AMSPAnalysisParser;