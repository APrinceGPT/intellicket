import React from 'react';

interface ConflictingSoftware {
  name: string;
  description: string;
  process_found?: string;
  av_main_process?: string;
  av_parent_process?: string;
  av_sub_processes?: string;
  conflict_assessment?: string;
  installation_risk?: string;
  policy_exclusions?: string[];
  resolution_steps?: string[];
}

interface ConflictAnalysisData {
  conflicts_detected?: boolean;
  processes_analyzed?: number;
  analysis_html?: string;
  analysis_text?: string;
  conflicting_software?: ConflictingSoftware[];
  analysis_summary?: string;
  [key: string]: unknown;
}

interface ConflictAnalysisParserProps {
  analysisData: ConflictAnalysisData;
}

const ConflictAnalysisParser: React.FC<ConflictAnalysisParserProps> = ({ analysisData }) => {
  // Parse HTML content to extract structured information with Deep Security policy details
  const parseHtmlContent = (htmlContent: string) => {
    const parser = new DOMParser();
    const doc = parser.parseFromString(htmlContent, 'text/html');
    
    const extractedData = {
      status: 'unknown',
      conflictingSoftware: [] as Array<{
        name: string, 
        description: string,
        process_found?: string,
        av_main_process?: string,
        av_parent_process?: string,
        av_sub_processes?: string,
        conflict_assessment?: string,
        installation_risk?: string,
        policy_exclusions?: string[],
        resolution_steps?: string[]
      }>,
      processCount: 0,
      summary: '',
      conflictCount: 0
    };

    // Extract status from HTML headers
    const statusElements = doc.querySelectorAll('h4, h3, h2');
    statusElements.forEach(el => {
      const text = el.textContent || '';
      if (text.includes('CONFLICTS DETECTED')) {
        extractedData.status = 'conflicts_detected';
      } else if (text.includes('NO CONFLICTS DETECTED')) {
        extractedData.status = 'no_conflicts';
      } else if (text.includes('ANALYSIS ERROR')) {
        extractedData.status = 'error';
      }
    });

    // Extract conflict count and process count from cards/paragraphs
    const allText = doc.body.textContent || htmlContent;
    
    // Look for "Conflicts Found: X" pattern
    const conflictMatch = allText.match(/Conflicts Found:\s*(\d+)/i);
    if (conflictMatch) {
      extractedData.conflictCount = parseInt(conflictMatch[1]);
    }
    
    // Look for "Processes Analyzed: X" pattern  
    const processMatch = allText.match(/Processes Analyzed:\s*(\d+)/i);
    if (processMatch) {
      extractedData.processCount = parseInt(processMatch[1]);
    }
    
    // Look for process count in other formats like "214 total"
    if (extractedData.processCount === 0) {
      const altProcessMatch = allText.match(/(\d+)\s+total/i);
      if (altProcessMatch) {
        extractedData.processCount = parseInt(altProcessMatch[1]);
      }
    }

    // Extract Enhanced Deep Security policy exclusion data
    const conflictingSoftware: Array<{
      name: string,
      description: string,
      process_found?: string,
      av_main_process?: string,
      av_parent_process?: string,
      av_sub_processes?: string,
      conflict_assessment?: string,
      installation_risk?: string,
      policy_exclusions?: string[],
      resolution_steps?: string[]
    }> = [];
    
    // Look for Deep Security policy exclusion sections
    const policyCards = doc.querySelectorAll('.mb-4.p-3');
    policyCards.forEach(card => {
      const cardContent = card.textContent || '';
      const headerElement = card.querySelector('h5');
      
      if (headerElement && (headerElement.textContent?.includes('�️') || headerElement.textContent?.includes('virus') || cardContent.includes('AV Process Hierarchy'))) {
        const nameMatch = headerElement?.textContent?.match(/\d+\.\s*(.+)/);
        const softwareName = nameMatch ? nameMatch[1].trim() : 'Unknown Anti-Virus Software';
        
        // Extract AV-specific process information
        const avMainProcessMatch = cardContent.match(/Main Process:\s*([^\n]+)/);
        const avMainProcess = avMainProcessMatch ? avMainProcessMatch[1].trim() : undefined;
        
        const avParentProcessMatch = cardContent.match(/Parent Process:\s*([^\n]+)/);
        const avParentProcess = avParentProcessMatch ? avParentProcessMatch[1].trim() : undefined;
        
        const avSubProcessesMatch = cardContent.match(/Sub-Processes:\s*([^\n]+)/);
        const avSubProcesses = avSubProcessesMatch ? avSubProcessesMatch[1].trim() : undefined;
        
        const conflictAssessmentMatch = cardContent.match(/Conflict Details:\s*([^\n]+)/);
        const conflictAssessment = conflictAssessmentMatch ? conflictAssessmentMatch[1].trim() : undefined;
        
        const installationRiskMatch = cardContent.match(/Installation Risk:\s*([^\n]+)/);
        const installationRisk = installationRiskMatch ? installationRiskMatch[1].trim() : undefined;
        
        // Extract legacy process found for backward compatibility
        const processMatch = cardContent.match(/Process Found:\s*([^\n]+)/);
        const processFound = processMatch ? processMatch[1].trim() : undefined;
        
        // Extract policy exclusions
        const exclusionsSection = card.querySelector('.alert-info');
        const exclusions: string[] = [];
        if (exclusionsSection) {
          const exclusionElements = exclusionsSection.querySelectorAll('div code, code');
          exclusionElements.forEach(el => {
            const exclusion = el.textContent?.trim();
            if (exclusion) {
              exclusions.push(exclusion);
            }
          });
        }
        
        // Extract resolution steps
        const stepsList = card.querySelector('ol');
        const steps: string[] = [];
        if (stepsList) {
          stepsList.querySelectorAll('li').forEach(li => {
            const step = li.textContent?.trim();
            if (step) {
              steps.push(step);
            }
          });
        }
        
        // Extract description
        const descParagraphs = card.querySelectorAll('div:not(.alert-info) p, div:not(.alert-info) div');
        let description = '';
        descParagraphs.forEach(p => {
          const text = p.textContent?.trim();
          if (text && !text.includes('Process Found:') && !text.includes('Main Process:') && !text.includes('Required Policy Exclusions:') && !text.includes('Resolution Steps:')) {
            description += (description ? ' ' : '') + text;
          }
        });
        
        conflictingSoftware.push({
          name: softwareName,
          description: description || 'Anti-virus software detected that may conflict with Deep Security',
          process_found: processFound,
          av_main_process: avMainProcess,
          av_parent_process: avParentProcess,
          av_sub_processes: avSubProcesses,
          conflict_assessment: conflictAssessment,
          installation_risk: installationRisk,
          policy_exclusions: exclusions.length > 0 ? exclusions : undefined,
          resolution_steps: steps.length > 0 ? steps : undefined
        });
      }
    });
    
    // Fallback: Extract from traditional format if no policy cards found
    if (conflictingSoftware.length === 0) {
      const softwareElements = doc.querySelectorAll('li, p');
      const conflicts: Array<{name: string, description: string}> = [];
      
      softwareElements.forEach(el => {
        const text = el.textContent || '';
        // Look for common antivirus software names
        const antivirusPatterns = [
          /norton/i, /mcafee/i, /kaspersky/i, /avast/i, /avg/i, /bitdefender/i,
          /eset/i, /sophos/i, /trend micro/i, /symantec/i, /malwarebytes/i,
          /windows defender/i, /defender/i, /avira/i, /comodo/i, /f-secure/i
        ];
        
        antivirusPatterns.forEach(pattern => {
          if (pattern.test(text) && !conflicts.some(c => pattern.test(c.name))) {
            const match = text.match(pattern);
            if (match) {
              conflicts.push({
                name: match[0].charAt(0).toUpperCase() + match[0].slice(1).toLowerCase(),
                description: text.length > 100 ? text.substring(0, 100) + '...' : text
              });
            }
          }
        });
      });
      
      conflictingSoftware.push(...conflicts);
    }
    
    extractedData.conflictingSoftware = conflictingSoftware;

    // Generate summary based on findings
    if (extractedData.status === 'conflicts_detected') {
      extractedData.summary = `Analysis detected ${extractedData.conflictCount || conflictingSoftware.length} potential antivirus conflicts among ${extractedData.processCount} running processes. Multiple security solutions may cause performance issues.`;
    } else if (extractedData.status === 'no_conflicts') {
      extractedData.summary = `No antivirus conflicts detected among ${extractedData.processCount} running processes. System appears to be free of conflicting security software.`;
    } else {
      extractedData.summary = allText.substring(0, 200) + (allText.length > 200 ? '...' : '');
    }

    return extractedData;
  };

  // Parse JSON content to extract structured information  
  const parseJsonContent = (jsonData: ConflictAnalysisData) => {
    const conflictingSoftware = jsonData.conflicting_software || [];
    return {
      status: jsonData.conflicts_detected ? 'conflicts_detected' : 'no_conflicts',
      conflictingSoftware,
      processCount: jsonData.processes_analyzed || 0,
      conflictCount: conflictingSoftware.length,
      summary: jsonData.analysis_summary || 'Analysis completed'
    };
  };

  // Determine the type of data and parse accordingly
  const getParsedData = () => {
    // First check for enhanced metadata (new format)
    if (analysisData.metadata && typeof analysisData.metadata === 'object') {
      const metadata = analysisData.metadata as Record<string, unknown>;
      const conflictsList = (metadata.conflicts_list as ConflictingSoftware[]) || [];
      const conflictsCount = (metadata.conflicts_count as number) || conflictsList.length;
      const processesAnalyzed = (metadata.processes_analyzed as number) || 0;
      const conflictsDetected = (metadata.conflicts_detected as boolean) || false;
      
      return {
        status: conflictsDetected ? 'conflicts_detected' : 'no_conflicts',
        conflictingSoftware: conflictsList,
        processCount: processesAnalyzed,
        conflictCount: conflictsCount,
        summary: conflictsDetected 
          ? `Analysis detected ${conflictsCount} potential antivirus conflicts among ${processesAnalyzed} running processes. Multiple security solutions may cause performance issues.`
          : `No antivirus conflicts detected among ${processesAnalyzed} running processes. System appears to be free of conflicting security software.`
      };
    }
    
    // Fallback to HTML parsing
    if (analysisData.analysis_html && typeof analysisData.analysis_html === 'string') {
      return parseHtmlContent(analysisData.analysis_html);
    } else if (analysisData.analysis_text) {
      return parseJsonContent(analysisData);
    } else {
      return parseJsonContent(analysisData);
    }
  };

  const parsedData = getParsedData();

  const getStatusConfig = (status: string) => {
    switch (status) {
      case 'conflicts_detected':
        return {
          icon: '⚠️',
          color: 'text-red-400',
          bgColor: 'bg-red-900/20',
          borderColor: 'border-red-400/30',
          title: 'Conflicts Detected'
        };
      case 'no_conflicts':
        return {
          icon: '✅',
          color: 'text-green-400',
          bgColor: 'bg-green-900/20',
          borderColor: 'border-green-400/30',
          title: 'No Conflicts Found'
        };
      case 'error':
        return {
          icon: '❌',
          color: 'text-red-400',
          bgColor: 'bg-red-900/20',
          borderColor: 'border-red-400/30',
          title: 'Analysis Error'
        };
      default:
        return {
          icon: 'ℹ️',
          color: 'text-blue-400',
          bgColor: 'bg-blue-900/20',
          borderColor: 'border-blue-400/30',
          title: 'Analysis Complete'
        };
    }
  };

  const statusConfig = getStatusConfig(parsedData.status);

  return (
    <div className="space-y-6">
      {/* Enhanced Status Overview with Action Items */}
      <div className={`${statusConfig.bgColor} ${statusConfig.borderColor} border rounded-xl p-6 relative overflow-hidden`}>
        {/* Background Pattern */}
        <div className="absolute inset-0 opacity-5">
          <div className="h-full w-full" style={{
            backgroundImage: `url("data:image/svg+xml,%3Csvg width='20' height='20' viewBox='0 0 20 20' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='%23ffffff' fill-opacity='0.1' fill-rule='evenodd'%3E%3Ccircle cx='3' cy='3' r='3'/%3E%3Ccircle cx='13' cy='13' r='3'/%3E%3C/g%3E%3C/svg%3E")`,
            backgroundSize: '20px 20px'
          }} />
        </div>
        
        <div className="relative">
          <div className="flex items-start justify-between mb-4">
            <div className="flex items-center space-x-4">
              <div className="flex-shrink-0">
                <div className={`w-12 h-12 rounded-full ${statusConfig.bgColor} ${statusConfig.borderColor} border-2 flex items-center justify-center`}>
                  <span className="text-2xl">{statusConfig.icon}</span>
                </div>
              </div>
              <div>
                <h4 className={`text-xl font-bold ${statusConfig.color} mb-1`}>
                  {statusConfig.title}
                </h4>
                <p className="text-gray-400 text-sm">
                  Antivirus Conflict Analysis • {new Date().toLocaleDateString()}
                </p>
              </div>
            </div>
            
            {/* Severity Badge */}
            <div className={`px-3 py-1 rounded-full text-xs font-medium ${
              parsedData.status === 'conflicts_detected' 
                ? 'bg-red-900/50 text-red-300 border border-red-400/30' 
                : 'bg-green-900/50 text-green-300 border border-green-400/30'
            }`}>
              {parsedData.status === 'conflicts_detected' ? 'Action Required' : 'System Healthy'}
            </div>
          </div>
          
          <p className="text-gray-300 text-base leading-relaxed mb-4">
            {parsedData.summary}
          </p>
          
          {/* Quick Action Buttons */}
          {parsedData.status === 'conflicts_detected' && (
            <div className="flex flex-wrap gap-2 mt-4">
              <button className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white text-sm font-medium rounded-lg transition-colors duration-200 flex items-center space-x-2">
                <span>🔧</span>
                <span>View Resolution Steps</span>
              </button>
              <button className="px-4 py-2 bg-gray-700 hover:bg-gray-600 text-gray-300 text-sm font-medium rounded-lg transition-colors duration-200 flex items-center space-x-2">
                <span>📋</span>
                <span>Export Report</span>
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Enhanced Statistics Grid with Visual Indicators */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-gradient-to-br from-blue-900/20 to-blue-800/10 rounded-xl p-5 border border-blue-400/20 hover:border-blue-400/40 transition-colors duration-200">
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-blue-500/20 rounded-lg flex items-center justify-center">
                <span className="text-blue-400 text-lg">📊</span>
              </div>
              <div>
                <h5 className="text-sm font-medium text-blue-300">Processes Analyzed</h5>
                <p className="text-xs text-gray-400">Total system processes scanned</p>
              </div>
            </div>
          </div>
          <p className="text-3xl font-bold text-white mb-1">{parsedData.processCount.toLocaleString()}</p>
          <div className="flex items-center space-x-1 text-xs text-gray-400">
            <span className="w-2 h-2 bg-blue-400 rounded-full"></span>
            <span>Comprehensive scan completed</span>
          </div>
        </div>

        <div className={`${
          parsedData.conflictCount > 0 
            ? 'bg-gradient-to-br from-red-900/20 to-red-800/10 border-red-400/20' 
            : 'bg-gradient-to-br from-green-900/20 to-green-800/10 border-green-400/20'
        } rounded-xl p-5 border hover:border-opacity-60 transition-colors duration-200`}>
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center space-x-3">
              <div className={`w-10 h-10 ${
                parsedData.conflictCount > 0 ? 'bg-red-500/20' : 'bg-green-500/20'
              } rounded-lg flex items-center justify-center`}>
                <span className={`${
                  parsedData.conflictCount > 0 ? 'text-red-400' : 'text-green-400'
                } text-lg`}>
                  {parsedData.conflictCount > 0 ? '⚡' : '✅'}
                </span>
              </div>
              <div>
                <h5 className={`text-sm font-medium ${
                  parsedData.conflictCount > 0 ? 'text-red-300' : 'text-green-300'
                }`}>
                  Conflicts Found
                </h5>
                <p className="text-xs text-gray-400">Detected security conflicts</p>
              </div>
            </div>
          </div>
          <p className="text-3xl font-bold text-white mb-1">
            {parsedData.conflictCount || parsedData.conflictingSoftware.length}
          </p>
          <div className="flex items-center space-x-1 text-xs text-gray-400">
            <span className={`w-2 h-2 ${
              parsedData.conflictCount > 0 ? 'bg-red-400' : 'bg-green-400'
            } rounded-full`}></span>
            <span>
              {parsedData.conflictCount > 0 ? 'Requires attention' : 'All clear'}
            </span>
          </div>
        </div>

        <div className="bg-gradient-to-br from-purple-900/20 to-purple-800/10 rounded-xl p-5 border border-purple-400/20 hover:border-purple-400/40 transition-colors duration-200">
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-purple-500/20 rounded-lg flex items-center justify-center">
                <span className="text-purple-400 text-lg">🛡️</span>
              </div>
              <div>
                <h5 className="text-sm font-medium text-purple-300">Security Status</h5>
                <p className="text-xs text-gray-400">Overall system protection</p>
              </div>
            </div>
          </div>
          <p className="text-lg font-bold text-white mb-1">
            {parsedData.conflictCount > 0 ? 'At Risk' : 'Protected'}
          </p>
          <div className="flex items-center space-x-1 text-xs text-gray-400">
            <span className={`w-2 h-2 ${
              parsedData.conflictCount > 0 ? 'bg-orange-400' : 'bg-purple-400'
            } rounded-full`}></span>
            <span>
              {parsedData.conflictCount > 0 ? 'Performance may be affected' : 'Optimal configuration'}
            </span>
          </div>
        </div>
      </div>

      {/* Enhanced Conflicting Software Details with Deep Security Policy Exclusions */}
      {parsedData.conflictingSoftware.length > 0 && (
        <div className="bg-white/5 rounded-xl p-6 border border-white/10">
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center space-x-3">
              <div className="w-12 h-12 bg-gradient-to-br from-red-500/30 to-orange-500/20 rounded-xl flex items-center justify-center">
                <span className="text-red-400 text-xl">🛡️</span>
              </div>
              <div>
                <h5 className="text-xl font-bold text-white">Deep Security Policy Exclusions Required</h5>
                <p className="text-sm text-gray-400">
                  {parsedData.conflictingSoftware.length} security solution{parsedData.conflictingSoftware.length > 1 ? 's' : ''} requiring immediate policy exclusions
                </p>
              </div>
            </div>
            <div className="text-right">
              <div className="px-3 py-1 bg-red-900/50 text-red-300 text-xs font-bold rounded-full border border-red-400/30">
                ACTION REQUIRED
              </div>
            </div>
          </div>
          
          <div className="space-y-6">
            {parsedData.conflictingSoftware.map((software: ConflictingSoftware, index: number) => (
              <div key={index} className="bg-gradient-to-r from-amber-900/20 to-orange-900/10 rounded-xl p-6 border border-amber-400/30 hover:border-amber-400/50 transition-colors duration-200">
                <div className="flex items-start justify-between mb-4">
                  <div className="flex items-start space-x-4 flex-grow">
                    <div className="w-10 h-10 bg-amber-500/30 rounded-full flex items-center justify-center flex-shrink-0">
                      <span className="text-amber-300 text-sm font-bold">{index + 1}</span>
                    </div>
                    <div className="flex-grow">
                      <h6 className="text-white font-bold mb-2 text-lg flex items-center space-x-2">
                        <span>{software.name}</span>
                        <span className="px-2 py-1 bg-red-900/50 text-red-300 text-xs rounded border border-red-400/30">
                          CONFLICT DETECTED
                        </span>
                      </h6>
                      
                      {software.process_found && (
                        <div className="mb-3 p-3 bg-black/30 rounded-lg border border-gray-600/30">
                          <p className="text-xs font-medium text-gray-400 mb-1">PROCESS DETECTED:</p>
                          <p className="text-white font-mono text-sm bg-black/50 px-2 py-1 rounded">
                            {software.process_found}
                          </p>
                        </div>
                      )}
                      
                      <p className="text-gray-300 text-sm leading-relaxed mb-4">{software.description}</p>
                      
                      {/* Deep Security Policy Exclusions */}
                      {software.policy_exclusions && software.policy_exclusions.length > 0 && (
                        <div className="mb-4">
                          <h6 className="text-blue-300 font-semibold mb-3 flex items-center space-x-2">
                            <span className="text-blue-400">⚙️</span>
                            <span>Required Deep Security Policy Exclusions:</span>
                          </h6>
                          <div className="bg-blue-900/20 border border-blue-400/30 rounded-lg p-4">
                            <div className="space-y-2">
                              {software.policy_exclusions.map((exclusion, idx) => (
                                <div key={idx} className="flex items-center space-x-3">
                                  <div className="w-2 h-2 bg-blue-400 rounded-full flex-shrink-0"></div>
                                  <code className="text-blue-300 bg-black/40 px-2 py-1 rounded text-sm flex-grow">
                                    {exclusion}
                                  </code>
                                  <button 
                                    className="text-blue-400 hover:text-blue-300 text-xs px-2 py-1 bg-blue-900/50 rounded transition-colors"
                                    onClick={() => navigator.clipboard.writeText(exclusion)}
                                  >
                                    Copy
                                  </button>
                                </div>
                              ))}
                            </div>
                          </div>
                        </div>
                      )}
                      
                      {/* Resolution Steps */}
                      {software.resolution_steps && software.resolution_steps.length > 0 && (
                        <div className="mb-4">
                          <h6 className="text-green-300 font-semibold mb-3 flex items-center space-x-2">
                            <span className="text-green-400">✅</span>
                            <span>Step-by-Step Resolution:</span>
                          </h6>
                          <div className="bg-green-900/20 border border-green-400/30 rounded-lg p-4">
                            <ol className="space-y-3">
                              {software.resolution_steps.map((step, idx) => (
                                <li key={idx} className="flex items-start space-x-3">
                                  <div className="w-6 h-6 bg-green-500/30 rounded-full flex items-center justify-center flex-shrink-0 mt-1">
                                    <span className="text-green-300 text-xs font-bold">{idx + 1}</span>
                                  </div>
                                  <span className="text-green-100 text-sm leading-relaxed">{step}</span>
                                </li>
                              ))}
                            </ol>
                          </div>
                        </div>
                      )}
                      
                      {/* Quick Action Buttons */}
                      <div className="flex flex-wrap gap-3 mt-4">
                        <button className="px-4 py-2 bg-blue-600/80 hover:bg-blue-600 text-white text-sm font-medium rounded-lg transition-colors duration-200 flex items-center space-x-2">
                          <span>🔧</span>
                          <span>Open Deep Security Manager</span>
                        </button>
                        <button className="px-4 py-2 bg-green-600/80 hover:bg-green-600 text-white text-sm font-medium rounded-lg transition-colors duration-200 flex items-center space-x-2">
                          <span>📋</span>
                          <span>Copy All Exclusions</span>
                        </button>
                        <button className="px-4 py-2 bg-gray-700/80 hover:bg-gray-700 text-gray-300 text-sm font-medium rounded-lg transition-colors duration-200 flex items-center space-x-2">
                          <span>📄</span>
                          <span>Export Instructions</span>
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
          
          {/* Deep Security Manager Quick Access */}
          <div className="mt-6 p-5 bg-gradient-to-r from-blue-900/30 to-indigo-900/20 border border-blue-400/30 rounded-xl">
            <div className="flex items-start space-x-4">
              <div className="w-12 h-12 bg-blue-500/30 rounded-xl flex items-center justify-center flex-shrink-0">
                <span className="text-blue-400 text-xl">💡</span>
              </div>
              <div className="flex-grow">
                <h6 className="text-blue-300 font-bold mb-3 text-lg">Quick Access to Deep Security Manager</h6>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                  <div className="space-y-2">
                    <div className="flex items-center space-x-2">
                      <span className="text-blue-400 font-medium">Web Console:</span>
                      <code className="text-white bg-black/40 px-2 py-1 rounded">https://[DSM-Server]:4119</code>
                    </div>
                    <div className="flex items-center space-x-2">
                      <span className="text-blue-400 font-medium">Policy Path:</span>
                      <span className="text-gray-300">Policies → [Your Policy] → Anti-Malware → Exclusions</span>
                    </div>
                  </div>
                  <div className="space-y-2">
                    <div className="flex items-center space-x-2">
                      <span className="text-blue-400 font-medium">Exclusion Types:</span>
                      <span className="text-gray-300">Real-time, Manual, Scheduled</span>
                    </div>
                    <div className="flex items-center space-x-2">
                      <span className="text-blue-400 font-medium">Apply Changes:</span>
                      <span className="text-gray-300">Don&apos;t forget to apply the policy</span>
                    </div>
                  </div>
                </div>
                <div className="mt-4 flex flex-wrap gap-2">
                  <button className="px-3 py-1 bg-blue-600/80 hover:bg-blue-600 text-white text-xs font-medium rounded transition-colors duration-200">
                    Open DSM Console
                  </button>
                  <button className="px-3 py-1 bg-gray-700/80 hover:bg-gray-700 text-gray-300 text-xs font-medium rounded transition-colors duration-200">
                    View Documentation
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Enhanced Analysis Insights */}
      <div className="bg-white/5 rounded-xl p-6 border border-white/10">
        <div className="flex items-center space-x-3 mb-4">
          <div className="w-10 h-10 bg-purple-500/20 rounded-lg flex items-center justify-center">
            <span className="text-purple-400 text-lg">🔍</span>
          </div>
          <div>
            <h5 className="text-lg font-semibold text-white">Analysis Insights</h5>
            <p className="text-sm text-gray-400">Key findings from the conflict analysis</p>
          </div>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="space-y-3">
            <div className="flex items-start space-x-3 p-3 bg-black/20 rounded-lg">
              <span className="text-green-400 text-lg flex-shrink-0">✓</span>
              <div>
                <span className="text-sm text-gray-300 block">
                  Scanned {parsedData.processCount} running processes for security conflicts
                </span>
                <span className="text-xs text-gray-500">Comprehensive system analysis completed</span>
              </div>
            </div>
            
            {parsedData.status === 'conflicts_detected' && (
              <div className="flex items-start space-x-3 p-3 bg-black/20 rounded-lg">
                <span className="text-red-400 text-lg flex-shrink-0">⚠</span>
                <div>
                  <span className="text-sm text-gray-300 block">
                    Multiple security solutions may impact system performance
                  </span>
                  <span className="text-xs text-gray-500">Resource conflicts and scanning overlap detected</span>
                </div>
              </div>
            )}
            
            {parsedData.status === 'no_conflicts' && (
              <div className="flex items-start space-x-3 p-3 bg-black/20 rounded-lg">
                <span className="text-green-400 text-lg flex-shrink-0">🛡️</span>
                <div>
                  <span className="text-sm text-gray-300 block">
                    System is optimally configured with no security conflicts
                  </span>
                  <span className="text-xs text-gray-500">Recommended security configuration maintained</span>
                </div>
              </div>
            )}
          </div>
          
          <div className="space-y-3">
            <div className="flex items-start space-x-3 p-3 bg-black/20 rounded-lg">
              <span className="text-blue-400 text-lg flex-shrink-0">📊</span>
              <div>
                <span className="text-sm text-gray-300 block">
                  Analysis completed in real-time with current system state
                </span>
                <span className="text-xs text-gray-500">Live process monitoring and conflict detection</span>
              </div>
            </div>
            
            <div className="flex items-start space-x-3 p-3 bg-black/20 rounded-lg">
              <span className="text-purple-400 text-lg flex-shrink-0">🔧</span>
              <div>
                <span className="text-sm text-gray-300 block">
                  Detailed recommendations available for conflict resolution
                </span>
                <span className="text-xs text-gray-500">Step-by-step guidance for optimal security setup</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Raw Data Toggle (for debugging) */}
      <details className="bg-black/20 rounded-xl border border-gray-600 overflow-hidden">
        <summary className="p-4 cursor-pointer text-gray-400 hover:text-gray-300 text-sm font-medium bg-black/10 hover:bg-black/20 transition-colors duration-200 flex items-center space-x-2">
          <span>🔧</span>
          <span>View Raw Analysis Data</span>
          <span className="ml-auto text-xs text-gray-500">(Developer Debug Information)</span>
        </summary>
        <div className="p-4 border-t border-gray-600">
          <pre className="text-xs text-gray-500 overflow-auto max-h-60 bg-black/30 p-3 rounded-lg font-mono">
            {JSON.stringify(analysisData, null, 2)}
          </pre>
        </div>
      </details>
    </div>
  );
};

export default ConflictAnalysisParser;
