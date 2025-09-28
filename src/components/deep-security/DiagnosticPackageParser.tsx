import React from 'react';

interface DiagnosticAnalysisData {
  summary?: string;
  diagnostic_overview?: {
    package_name?: string;
    total_files?: number;
    analyzed_files?: number;
    file_types?: Record<string, number>;
  };
  individual_analyses?: {
    [filename: string]: {
      analyzer?: string;
      summary?: string;
      status?: string;
      issues_count?: number;
      recommendations?: string[];
      raw_data?: unknown;
    };
  };
  correlation_analysis?: {
    cross_file_patterns?: string[];
    common_issues?: string[];
    severity_distribution?: Record<string, number>;
  };
  overall_health_score?: number;
  critical_findings?: Array<{
    file?: string;
    analyzer?: string;
    issue?: string;
    severity?: string;
    recommendation?: string;
  }>;
  recommendations?: string[];
  metadata?: Record<string, unknown>;
  [key: string]: unknown;
}

interface DiagnosticPackageParserProps {
  analysisData: DiagnosticAnalysisData;
}

const DiagnosticPackageParser: React.FC<DiagnosticPackageParserProps> = ({ analysisData }) => {
  const extractMetrics = () => {
    const overview = analysisData.diagnostic_overview || {};
    const correlation = analysisData.correlation_analysis || {};
    const criticalFindings = analysisData.critical_findings || [];
    const individualAnalyses = analysisData.individual_analyses || {};
    
    const totalIssues = Object.values(individualAnalyses).reduce(
      (sum, analysis) => sum + ((analysis.issues_count as number) || 0), 0
    );
    
    return {
      packageName: overview.package_name || 'Unknown Package',
      totalFiles: (overview.total_files as number) || 0,
      analyzedFiles: (overview.analyzed_files as number) || 0,
      totalIssues: totalIssues,
      criticalCount: criticalFindings.length,
      healthScore: analysisData.overall_health_score || 0,
      fileTypes: overview.file_types || {},
      severityDistribution: correlation.severity_distribution || {}
    };
  };

  const metrics = extractMetrics();
  
  const getHealthColor = (score: number) => {
    if (score >= 80) return 'text-green-400 bg-green-900/20 border-green-400/30';
    if (score >= 60) return 'text-yellow-400 bg-yellow-900/20 border-yellow-400/30';
    if (score >= 40) return 'text-orange-400 bg-orange-900/20 border-orange-400/30';
    return 'text-red-400 bg-red-900/20 border-red-400/30';
  };

  const getSeverityColor = (severity: string) => {
    switch (severity?.toLowerCase()) {
      case 'critical': return 'text-red-400 bg-red-900/20 border-red-400/30';
      case 'high': return 'text-orange-400 bg-orange-900/20 border-orange-400/30';
      case 'medium': return 'text-yellow-400 bg-yellow-900/20 border-yellow-400/30';
      case 'low': return 'text-green-400 bg-green-900/20 border-green-400/30';
      default: return 'text-blue-400 bg-blue-900/20 border-blue-400/30';
    }
  };

  const status = metrics.healthScore >= 80 ? 'excellent' :
                metrics.healthScore >= 60 ? 'good' :
                metrics.healthScore >= 40 ? 'warning' : 'critical';
  
  const statusConfig = {
    excellent: { icon: '🟢', title: 'Excellent System Health', color: 'text-green-400' },
    good: { icon: '🟡', title: 'Good System Health', color: 'text-yellow-400' },
    warning: { icon: '🟠', title: 'System Issues Detected', color: 'text-orange-400' },
    critical: { icon: '🔴', title: 'Critical System Issues', color: 'text-red-400' }
  }[status];

  return (
    <div className="space-y-4">
      {/* Package Overview */}
      <div className={`${getHealthColor(metrics.healthScore)} border rounded-xl p-4`}>
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center space-x-3">
            <span className="text-2xl">{statusConfig.icon}</span>
            <h4 className={`text-lg font-semibold ${statusConfig.color}`}>
              {statusConfig.title}
            </h4>
          </div>
          <div className="text-right">
            <div className="text-2xl font-bold text-white">{metrics.healthScore}%</div>
            <div className="text-xs text-gray-400">Health Score</div>
          </div>
        </div>
        <p className="text-gray-300 text-sm leading-relaxed mb-2">
          {analysisData.summary || 'Comprehensive diagnostic package analysis completed'}
        </p>
        <div className="text-gray-400 text-xs">
          <strong>Package:</strong> {metrics.packageName} • 
          <strong> Files:</strong> {metrics.analyzedFiles}/{metrics.totalFiles} analyzed
        </div>
      </div>

      {/* Overview Metrics */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-white/5 rounded-lg p-4 border border-white/10">
          <div className="flex items-center space-x-2 mb-2">
            <span className="text-blue-400">📦</span>
            <h5 className="text-sm font-medium text-gray-300">Total Files</h5>
          </div>
          <p className="text-2xl font-bold text-white">{metrics.totalFiles}</p>
        </div>

        <div className="bg-white/5 rounded-lg p-4 border border-white/10">
          <div className="flex items-center space-x-2 mb-2">
            <span className="text-green-400">🔍</span>
            <h5 className="text-sm font-medium text-gray-300">Analyzed</h5>
          </div>
          <p className="text-2xl font-bold text-white">{metrics.analyzedFiles}</p>
        </div>

        <div className="bg-white/5 rounded-lg p-4 border border-white/10">
          <div className="flex items-center space-x-2 mb-2">
            <span className="text-yellow-400">⚠️</span>
            <h5 className="text-sm font-medium text-gray-300">Total Issues</h5>
          </div>
          <p className="text-2xl font-bold text-white">{metrics.totalIssues}</p>
        </div>

        <div className="bg-white/5 rounded-lg p-4 border border-white/10">
          <div className="flex items-center space-x-2 mb-2">
            <span className="text-red-400">🔥</span>
            <h5 className="text-sm font-medium text-gray-300">Critical</h5>
          </div>
          <p className="text-2xl font-bold text-white">{metrics.criticalCount}</p>
        </div>
      </div>

      {/* File Types Distribution */}
      {Object.keys(metrics.fileTypes).length > 0 && (
        <div className="bg-white/5 rounded-lg p-4 border border-white/10">
          <div className="flex items-center space-x-2 mb-3">
            <span className="text-purple-400">📊</span>
            <h5 className="text-sm font-medium text-gray-300">File Types Distribution</h5>
          </div>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
            {Object.entries(metrics.fileTypes).map(([type, count]) => (
              <div key={type} className="bg-black/20 rounded p-2 text-center">
                <div className="text-sm font-medium text-white">{count}</div>
                <div className="text-xs text-gray-400">{type}</div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Critical Findings */}
      {analysisData.critical_findings && analysisData.critical_findings.length > 0 && (
        <div className="bg-white/5 rounded-lg p-4 border border-white/10">
          <div className="flex items-center space-x-2 mb-3">
            <span className="text-red-400">🚨</span>
            <h5 className="text-sm font-medium text-gray-300">Critical Findings</h5>
          </div>
          <div className="space-y-3 max-h-80 overflow-y-auto">
            {analysisData.critical_findings.map((finding, index) => (
              <div key={index} className={`${getSeverityColor(finding.severity || 'critical')} rounded-lg p-3 border`}>
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center space-x-2">
                    <span className="text-xs font-medium uppercase">{finding.severity || 'CRITICAL'}</span>
                    <span className="text-gray-500 text-xs">{finding.analyzer}</span>
                  </div>
                  <span className="text-gray-500 text-xs">{finding.file}</span>
                </div>
                <p className="text-gray-300 text-sm mb-2">{finding.issue}</p>
                {finding.recommendation && (
                  <p className="text-gray-400 text-xs">
                    <strong>Recommendation:</strong> {finding.recommendation}
                  </p>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Individual File Analyses */}
      {analysisData.individual_analyses && Object.keys(analysisData.individual_analyses).length > 0 && (
        <div className="bg-white/5 rounded-lg p-4 border border-white/10">
          <div className="flex items-center space-x-2 mb-3">
            <span className="text-cyan-400">📋</span>
            <h5 className="text-sm font-medium text-gray-300">Individual File Analyses</h5>
          </div>
          <div className="space-y-3 max-h-80 overflow-y-auto">
            {Object.entries(analysisData.individual_analyses).map(([filename, analysis]) => (
              <div key={filename} className="bg-black/20 rounded-lg p-3 border border-gray-600">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium text-white truncate">{filename}</span>
                  <div className="flex items-center space-x-2">
                    <span className="text-xs text-gray-400">{analysis.analyzer}</span>
                    {analysis.issues_count !== undefined && (
                      <span className="bg-yellow-900/30 text-yellow-400 text-xs px-2 py-1 rounded">
                        {analysis.issues_count} issues
                      </span>
                    )}
                  </div>
                </div>
                {analysis.summary && (
                  <p className="text-gray-300 text-xs mb-2">{analysis.summary}</p>
                )}
                {analysis.recommendations && analysis.recommendations.length > 0 && (
                  <div className="text-xs text-gray-400">
                    <strong>Recommendations:</strong> {analysis.recommendations.slice(0, 2).join(', ')}
                    {analysis.recommendations.length > 2 && '...'}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Cross-File Correlation Analysis */}
      {analysisData.correlation_analysis && (
        <div className="bg-white/5 rounded-lg p-4 border border-white/10">
          <div className="flex items-center space-x-2 mb-3">
            <span className="text-blue-400">🔗</span>
            <h5 className="text-sm font-medium text-gray-300">Correlation Analysis</h5>
          </div>
          
          {analysisData.correlation_analysis.cross_file_patterns && (
            <div className="mb-3">
              <h6 className="text-xs font-medium text-gray-400 mb-2">Cross-File Patterns:</h6>
              <div className="space-y-1">
                {analysisData.correlation_analysis.cross_file_patterns.map((pattern, index) => (
                  <div key={index} className="text-xs text-gray-300 bg-black/20 rounded p-2">
                    {pattern}
                  </div>
                ))}
              </div>
            </div>
          )}

          {analysisData.correlation_analysis.common_issues && (
            <div className="mb-3">
              <h6 className="text-xs font-medium text-gray-400 mb-2">Common Issues:</h6>
              <div className="space-y-1">
                {analysisData.correlation_analysis.common_issues.map((issue, index) => (
                  <div key={index} className="text-xs text-gray-300 bg-black/20 rounded p-2">
                    {issue}
                  </div>
                ))}
              </div>
            </div>
          )}

          {Object.keys(metrics.severityDistribution).length > 0 && (
            <div>
              <h6 className="text-xs font-medium text-gray-400 mb-2">Severity Distribution:</h6>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
                {Object.entries(metrics.severityDistribution).map(([severity, count]) => (
                  <div key={severity} className={`${getSeverityColor(severity)} rounded p-2 text-center`}>
                    <div className="text-sm font-medium">{count}</div>
                    <div className="text-xs uppercase">{severity}</div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Overall Recommendations */}
      {analysisData.recommendations && analysisData.recommendations.length > 0 && (
        <div className="bg-white/5 rounded-lg p-4 border border-white/10">
          <div className="flex items-center space-x-2 mb-3">
            <span className="text-green-400">💡</span>
            <h5 className="text-sm font-medium text-gray-300">Overall Recommendations</h5>
          </div>
          <div className="space-y-2">
            {analysisData.recommendations.map((rec, index) => (
              <div key={index} className="flex items-start space-x-2">
                <span className="text-green-400 text-sm">•</span>
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

export default DiagnosticPackageParser;