import React from 'react';
import { ResourceAnalysisData, ResourceCandidate, PerformanceMetrics } from '../../types/ResourceAnalysis';
import PerformanceMetricsCard from './PerformanceMetricsCard';
import ExclusionCandidatesTable from './ExclusionCandidatesTable';

interface ResourceAnalysisParserProps {
  analysisData: ResourceAnalysisData;
}

const ResourceAnalysisParser: React.FC<ResourceAnalysisParserProps> = ({ analysisData }) => {
  console.log('🔍 ResourceAnalysisParser received data:', {
    keys: Object.keys(analysisData),
    candidates: analysisData.candidates?.length || 0,
    hasPerformanceMetrics: !!analysisData.performance_metrics,
    recommendations: analysisData.recommendations?.length || 0
  });

  // Extract resource-specific data with fallbacks
  const extractResourceData = () => {
    // Try to get data from different possible locations in the response
    const rawData = analysisData.raw_data as Record<string, unknown>;
    const candidates = analysisData.candidates || 
                      (rawData?.candidates as ResourceCandidate[]) || 
                      [];

    const performanceMetrics = analysisData.performance_metrics || 
                              (rawData?.performance_metrics as PerformanceMetrics) || 
                              {
                                total_scan_count: 0,
                                high_impact_processes: 0,
                                process_types: [],
                                optimization_potential: 'Low' as const
                              };

    const metadata = analysisData.metadata as Record<string, unknown> || {};

    return { candidates, performanceMetrics, metadata };
  };

  const { candidates, performanceMetrics, metadata } = extractResourceData();

  // Status determination
  const getAnalysisStatus = () => {
    if (analysisData.status === 'error') {
      return {
        icon: '❌',
        color: 'text-red-400',
        bgColor: 'bg-red-900/20',
        borderColor: 'border-red-400/30',
        title: 'Analysis Error'
      };
    } else if (candidates.length === 0) {
      return {
        icon: '✅',
        color: 'text-green-400',
        bgColor: 'bg-green-900/20',
        borderColor: 'border-green-400/30',
        title: 'Optimal Performance'
      };
    } else if (performanceMetrics.optimization_potential === 'High') {
      return {
        icon: '🚨',
        color: 'text-red-400',
        bgColor: 'bg-red-900/20',
        borderColor: 'border-red-400/30',
        title: 'High Impact Detected'
      };
    } else {
      return {
        icon: '⚡',
        color: 'text-yellow-400',
        bgColor: 'bg-yellow-900/20',
        borderColor: 'border-yellow-400/30',
        title: 'Optimization Available'
      };
    }
  };

  const statusConfig = getAnalysisStatus();

  return (
    <div className="space-y-6">
      {/* Status Overview Header */}
      <div className={`${statusConfig.bgColor} ${statusConfig.borderColor} border rounded-xl p-6`}>
        <div className="flex items-center space-x-3 mb-4">
          <span className="text-3xl">{statusConfig.icon}</span>
          <div>
            <h3 className={`text-xl font-semibold ${statusConfig.color}`}>
              Resource Analysis - {statusConfig.title}
            </h3>
            <p className="text-gray-300 text-sm mt-1">
              {analysisData.summary || 'System resource utilization analysis completed'}
            </p>
          </div>
        </div>

        {/* Quick Stats */}
        {metadata && (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-4">
            {typeof metadata.files_processed === 'number' && (
              <div className="text-center">
                <p className="text-lg font-bold text-white">{metadata.files_processed}</p>
                <p className="text-xs text-gray-400">Files Processed</p>
              </div>
            )}
            {typeof metadata.processes_found === 'number' && (
              <div className="text-center">
                <p className="text-lg font-bold text-white">{metadata.processes_found.toLocaleString()}</p>
                <p className="text-xs text-gray-400">Running Processes</p>
              </div>
            )}
            {typeof metadata.busy_processes_found === 'number' && (
              <div className="text-center">
                <p className="text-lg font-bold text-white">{metadata.busy_processes_found}</p>
                <p className="text-xs text-gray-400">Busy Processes</p>
              </div>
            )}
            <div className="text-center">
              <p className="text-lg font-bold text-white">{candidates.length}</p>
              <p className="text-xs text-gray-400">Exclusion Candidates</p>
            </div>
          </div>
        )}
      </div>

      {/* Performance Metrics Card */}
      <PerformanceMetricsCard metrics={performanceMetrics} />

      {/* Exclusion Candidates Table */}
      <ExclusionCandidatesTable candidates={candidates} />

      {/* Debug Information (Development Only) */}
      {process.env.NODE_ENV === 'development' && (
        <details className="bg-black/20 rounded-lg border border-gray-600">
          <summary className="p-3 cursor-pointer text-gray-400 hover:text-gray-300 text-sm font-medium">
            🔧 Debug: Raw Analysis Data
          </summary>
          <div className="p-3 border-t border-gray-600">
            <pre className="text-xs text-gray-500 overflow-auto max-h-96 bg-black/30 p-2 rounded">
              {JSON.stringify(analysisData, null, 2)}
            </pre>
          </div>
        </details>
      )}
    </div>
  );
};

export default ResourceAnalysisParser;
