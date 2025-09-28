import React from 'react';
import ConflictAnalysisParser from './ConflictAnalysisParser';
import ResourceAnalysisParser from '../resource-analysis/ResourceAnalysisParser';
import AMSPAnalysisParser from './AMSPAnalysisParser';
import DiagnosticPackageParser from './DiagnosticPackageParser';
import { ResourceAnalysisData } from '../../types/ResourceAnalysis';

interface AnalysisDataParserProps {
  analysisData: Record<string, unknown>;
  analysisType: string;
}

const AnalysisDataParser: React.FC<AnalysisDataParserProps> = ({ analysisData, analysisType }) => {
  // Route to specific parsers based on analysis type
  const renderSpecificParser = () => {
    switch (analysisType.toLowerCase()) {
      case 'conflict':
      case 'av_conflicts':
        return <ConflictAnalysisParser analysisData={analysisData} />;
      
      case 'amsp':
      case 'amsp_logs':
        return <AMSPAnalysisParser analysisData={analysisData} />;
      
      case 'resource':
      case 'resource_analysis':
        return <ResourceAnalysisParser analysisData={analysisData as ResourceAnalysisData} />;
      
      case 'diagnostic_package':
        return <DiagnosticPackageParser analysisData={analysisData} />;
      
      default:
        return <GenericAnalysisParser analysisData={analysisData} />;
    }
  };

  return (
    <div className="analysis-data-parser">
      {renderSpecificParser()}
    </div>
  );
};

// Generic parser for unknown or simple analysis types
const GenericAnalysisParser: React.FC<{ analysisData: Record<string, unknown> }> = ({ analysisData }) => {
  const extractKeyMetrics = () => {
    const metrics: Array<{ label: string; value: string | number; icon: string }> = [];
    
    // Common patterns to extract
    if (analysisData.errors_found !== undefined) {
      metrics.push({ label: 'Errors Found', value: analysisData.errors_found as number, icon: '🚨' });
    }
    if (analysisData.warnings_found !== undefined) {
      metrics.push({ label: 'Warnings', value: analysisData.warnings_found as number, icon: '⚠️' });
    }
    if (analysisData.files_processed !== undefined) {
      metrics.push({ label: 'Files Processed', value: analysisData.files_processed as number, icon: '📁' });
    }
    if (analysisData.total_lines !== undefined) {
      metrics.push({ label: 'Lines Analyzed', value: analysisData.total_lines as number, icon: '📄' });
    }
    
    return metrics;
  };

  const metrics = extractKeyMetrics();

  return (
    <div className="space-y-4">
      {/* Metrics Grid */}
      {metrics.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {metrics.map((metric, index) => (
            <div key={index} className="bg-white/5 rounded-lg p-4 border border-white/10">
              <div className="flex items-center space-x-2 mb-2">
                <span className="text-xl">{metric.icon}</span>
                <h5 className="text-sm font-medium text-gray-300">{metric.label}</h5>
              </div>
              <p className="text-2xl font-bold text-white">
                {typeof metric.value === 'number' ? metric.value.toLocaleString() : metric.value}
              </p>
            </div>
          ))}
        </div>
      )}

      {/* Raw Data */}
      <details className="bg-black/20 rounded-lg border border-gray-600">
        <summary className="p-3 cursor-pointer text-gray-400 hover:text-gray-300 text-sm font-medium">
          🔧 View Analysis Data
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

export default AnalysisDataParser;
