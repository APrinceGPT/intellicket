import React, { useState } from 'react';
import { ResourceCandidate } from '../../types/ResourceAnalysis';

interface RecommendationsPanelProps {
  candidates: ResourceCandidate[];
}

const RecommendationsPanel: React.FC<RecommendationsPanelProps> = ({ candidates }) => {
  const [copyFeedback, setCopyFeedback] = useState<string>('');
  const [expandedProcesses, setExpandedProcesses] = useState<Set<number>>(new Set());

  const toggleProcessExpanded = (index: number) => {
    const newExpanded = new Set(expandedProcesses);
    if (newExpanded.has(index)) {
      newExpanded.delete(index);
    } else {
      newExpanded.add(index);
    }
    setExpandedProcesses(newExpanded);
  };

  const copyToClipboard = async (text: string, type: string) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopyFeedback(`${type} copied to clipboard!`);
      setTimeout(() => setCopyFeedback(''), 2000);
    } catch (error) {
      console.error('Failed to copy to clipboard:', error);
      setCopyFeedback('Failed to copy');
      setTimeout(() => setCopyFeedback(''), 2000);
    }
  };

  const generateExclusionInstructions = (candidate: ResourceCandidate) => {
    const processName = candidate.name || 'Unknown Process';
    const processPath = (candidate.details?.path as string) || candidate.name || 'Path not available';
    const scanCount = parseInt(candidate.count) || 0;
    
    // Extract directory from full path
    const directory = processPath.includes('\\') 
      ? processPath.substring(0, processPath.lastIndexOf('\\'))
      : 'C:\\Program Files\\YourApp';
    
    const exclusionSyntax = {
      directory: `${directory}\\**`,
      file: processPath,
      processAndDirectory: `Process: ${processName}\nDirectory: ${directory}\\**`
    };

    return {
      processName,
      processPath,
      scanCount,
      exclusionSyntax
    };
  };

  if (!candidates || candidates.length === 0) {
    return (
      <div className="bg-white/5 rounded-xl border border-white/10 p-6">
        <div className="text-center py-8">
          <span className="text-4xl mb-4 block">✅</span>
          <h3 className="text-lg font-semibold text-gray-400 mb-2">No Exclusions Needed</h3>
          <p className="text-gray-500 text-sm">
            Your system is running optimally with no processes requiring Deep Security exclusions.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white/5 rounded-xl border border-white/10 p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center space-x-3">
          <span className="text-2xl">🤖</span>
          <h3 className="text-lg font-semibold text-white">AI-Powered Technical Support Assistant</h3>
        </div>
        <div className="text-xs text-gray-400 bg-white/5 px-3 py-1 rounded-full border border-white/10">
          Exclusion Instructions
        </div>
      </div>

      {/* Copy Feedback */}
      {copyFeedback && (
        <div className="mb-4 p-3 bg-green-900/20 border border-green-400/30 rounded-lg">
          <p className="text-green-400 text-sm">✅ {copyFeedback}</p>
        </div>
      )}

      {/* Exclusion Instructions for Each Process */}
      <div className="space-y-4">
        {candidates.map((candidate, index) => {
          const instructions = generateExclusionInstructions(candidate);
          const isExpanded = expandedProcesses.has(index);

          return (
            <div key={index} className="bg-white/5 rounded-lg border border-white/10 overflow-hidden">
              {/* Process Header - Clickable to toggle */}
              <div 
                className="p-4 cursor-pointer hover:bg-white/10 transition-colors"
                onClick={() => toggleProcessExpanded(index)}
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center space-x-3 mb-2">
                      <span className="text-lg">📋</span>
                      <h4 className="text-white font-medium">Process: {instructions.processName}</h4>
                    </div>
                    <p className="text-gray-400 text-xs mb-1">{instructions.processPath}</p>
                    <p className="text-sm text-gray-300">
                      Process with {instructions.scanCount.toLocaleString()} scan events detected.
                    </p>
                  </div>
                  <div className="ml-4 flex items-center space-x-2 text-blue-400 text-sm">
                    <span>{isExpanded ? 'Hide Instructions' : 'Show Instructions'}</span>
                    <span className="text-xs">{isExpanded ? '⬆️' : '⬇️'}</span>
                  </div>
                </div>
              </div>

              {/* Collapsible Instructions Content */}
              {isExpanded && (
                <div className="px-4 pb-4 border-t border-white/10">
                  {/* Step-by-Step Instructions */}
                  <div className="mb-6 mt-4">
                    <h5 className="text-white font-medium mb-3 flex items-center space-x-2">
                      <span>📋</span>
                      <span>Exclusion Instructions</span>
                    </h5>
                    <div className="space-y-2">
                      <div className="flex items-start space-x-2">
                        <span className="text-blue-400 text-xs mt-1 font-mono">1.</span>
                        <span className="text-sm text-gray-300 flex-1">Open Deep Security Manager console and navigate to your policy</span>
                      </div>
                      <div className="flex items-start space-x-2">
                        <span className="text-blue-400 text-xs mt-1 font-mono">2.</span>
                        <span className="text-sm text-gray-300 flex-1">Go to &apos;Anti-Malware&apos; → &apos;Advanced&apos; → &apos;Exclusions&apos; tab</span>
                      </div>
                      <div className="flex items-start space-x-2">
                        <span className="text-blue-400 text-xs mt-1 font-mono">3.</span>
                        <span className="text-sm text-gray-300 flex-1">Click &apos;New...&apos; to create a new exclusion rule</span>
                      </div>
                      <div className="flex items-start space-x-2">
                        <span className="text-blue-400 text-xs mt-1 font-mono">4.</span>
                        <span className="text-sm text-gray-300 flex-1">Choose exclusion type: &apos;Directory, file, or file extension&apos; or &apos;Process&apos;</span>
                      </div>
                      <div className="flex items-start space-x-2">
                        <span className="text-blue-400 text-xs mt-1 font-mono">5.</span>
                        <span className="text-sm text-gray-300 flex-1">Enter the exclusion path (see syntax options below)</span>
                      </div>
                      <div className="flex items-start space-x-2">
                        <span className="text-blue-400 text-xs mt-1 font-mono">6.</span>
                        <span className="text-sm text-gray-300 flex-1">Apply the exclusion to your policy and test</span>
                      </div>
                    </div>
                  </div>

                  {/* Exclusion Syntax Options */}
                  <div>
                    <h5 className="text-white font-medium mb-3 flex items-center space-x-2">
                      <span>📝</span>
                      <span>Exclusion Syntax Options</span>
                    </h5>
                    
                    <div className="space-y-3">
                      <div className="bg-gray-900/50 rounded-lg p-3">
                        <div className="flex items-center justify-between mb-2">
                          <span className="text-xs text-gray-400">Directory Exclusion (Recommended)</span>
                          <button
                            onClick={() => copyToClipboard(instructions.exclusionSyntax.directory, 'Directory path')}
                            className="text-xs text-blue-400 hover:text-blue-300"
                          >
                            📋 Copy
                          </button>
                        </div>
                        <code className="text-green-400 text-sm block break-all">
                          {instructions.exclusionSyntax.directory}
                        </code>
                      </div>

                      <div className="bg-gray-900/50 rounded-lg p-3">
                        <div className="flex items-center justify-between mb-2">
                          <span className="text-xs text-gray-400">File Exclusion</span>
                          <button
                            onClick={() => copyToClipboard(instructions.exclusionSyntax.file, 'File path')}
                            className="text-xs text-blue-400 hover:text-blue-300"
                          >
                            📋 Copy
                          </button>
                        </div>
                        <code className="text-green-400 text-sm block break-all">
                          {instructions.exclusionSyntax.file}
                        </code>
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Summary Footer */}
      <div className="mt-6 pt-4 border-t border-white/10">
        <div className="flex items-center justify-between mb-3">
          <div className="text-sm text-gray-400">
            {candidates.length} process{candidates.length > 1 ? 'es' : ''} found • {expandedProcesses.size} expanded
          </div>
          <div className="flex space-x-2">
            <button
              onClick={() => setExpandedProcesses(new Set(candidates.map((_, i) => i)))}
              className="text-xs text-blue-400 hover:text-blue-300"
            >
              Expand All
            </button>
            <span className="text-gray-600">|</span>
            <button
              onClick={() => setExpandedProcesses(new Set())}
              className="text-xs text-blue-400 hover:text-blue-300"
            >
              Collapse All
            </button>
          </div>
        </div>
        
        <div className="p-3 bg-blue-900/20 border border-blue-400/30 rounded-lg">
          <p className="text-blue-400 text-xs">
            🤖 <strong>AI Technical Support:</strong> These exclusion instructions are generated for the {candidates.length} process{candidates.length > 1 ? 'es' : ''} found in your scan analysis. Click on any process to view detailed exclusion instructions.
          </p>
        </div>
      </div>
    </div>
  );
};

export default RecommendationsPanel;