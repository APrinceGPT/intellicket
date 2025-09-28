import React from 'react';
import { PerformanceMetrics } from '../../types/ResourceAnalysis';

interface PerformanceMetricsCardProps {
  metrics: PerformanceMetrics;
}

const PerformanceMetricsCard: React.FC<PerformanceMetricsCardProps> = ({ metrics }) => {
  const getOptimizationColor = (potential: string) => {
    switch (potential) {
      case 'High': return 'text-red-400 bg-red-900/20 border-red-400/30';
      case 'Medium': return 'text-yellow-400 bg-yellow-900/20 border-yellow-400/30';
      case 'Low': return 'text-green-400 bg-green-900/20 border-green-400/30';
      default: return 'text-blue-400 bg-blue-900/20 border-blue-400/30';
    }
  };

  const getOptimizationIcon = (potential: string) => {
    switch (potential) {
      case 'High': return '🚨';
      case 'Medium': return '⚠️';
      case 'Low': return '✅';
      default: return 'ℹ️';
    }
  };

  const formatNumber = (num: number) => {
    if (num >= 1000000) return `${(num / 1000000).toFixed(1)}M`;
    if (num >= 1000) return `${(num / 1000).toFixed(1)}K`;
    return num.toString();
  };

  return (
    <div className="bg-white/5 rounded-xl border border-white/10 p-6">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center space-x-3">
          <span className="text-2xl">⚡</span>
          <h3 className="text-lg font-semibold text-white">Performance Metrics</h3>
        </div>
        <div className={`px-3 py-1 rounded-full border text-sm font-medium ${getOptimizationColor(metrics.optimization_potential)}`}>
          {getOptimizationIcon(metrics.optimization_potential)} {metrics.optimization_potential} Impact
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {/* Total Scan Count */}
        <div className="bg-black/20 rounded-lg p-4 border border-white/5">
          <div className="flex items-center space-x-2 mb-2">
            <span className="text-lg">📊</span>
            <h4 className="text-sm font-medium text-gray-300">Total Scans</h4>
          </div>
          <p className="text-2xl font-bold text-white">{formatNumber(metrics.total_scan_count)}</p>
          <p className="text-xs text-gray-400 mt-1">Scan events detected</p>
        </div>

        {/* High Impact Processes */}
        <div className="bg-black/20 rounded-lg p-4 border border-white/5">
          <div className="flex items-center space-x-2 mb-2">
            <span className="text-lg">🎯</span>
            <h4 className="text-sm font-medium text-gray-300">High Impact</h4>
          </div>
          <p className="text-2xl font-bold text-white">{metrics.high_impact_processes}</p>
          <p className="text-xs text-gray-400 mt-1">Processes (&gt;1K scans)</p>
        </div>

        {/* Process Types */}
        <div className="bg-black/20 rounded-lg p-4 border border-white/5">
          <div className="flex items-center space-x-2 mb-2">
            <span className="text-lg">🔧</span>
            <h4 className="text-sm font-medium text-gray-300">Process Types</h4>
          </div>
          <p className="text-2xl font-bold text-white">{metrics.process_types?.length || 0}</p>
          <p className="text-xs text-gray-400 mt-1">Different categories</p>
        </div>
      </div>

      {/* Process Types Breakdown */}
      {metrics.process_types && metrics.process_types.length > 0 && (
        <div className="mt-4 pt-4 border-t border-white/10">
          <h4 className="text-sm font-medium text-gray-300 mb-3">📋 Process Categories</h4>
          <div className="flex flex-wrap gap-2">
            {metrics.process_types.map((type, index) => (
              <span
                key={index}
                className="px-2 py-1 bg-blue-900/20 border border-blue-400/30 rounded text-xs text-blue-400"
              >
                {type}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Optimization Recommendation */}
      <div className="mt-4 pt-4 border-t border-white/10">
        <div className="flex items-start space-x-3">
          <span className="text-lg flex-shrink-0 mt-0.5">💡</span>
          <div>
            <h4 className="text-sm font-medium text-gray-300 mb-1">Optimization Recommendation</h4>
            <p className="text-xs text-gray-400">
              {metrics.optimization_potential === 'High' && 
                'Immediate attention required. Consider implementing exclusions for high-impact processes.'}
              {metrics.optimization_potential === 'Medium' && 
                'Moderate optimization opportunities available. Review top candidates for exclusion.'}
              {metrics.optimization_potential === 'Low' && 
                'System running efficiently. Monitor periodically for changes.'}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PerformanceMetricsCard;
