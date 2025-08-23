'use client';

import { useState, useEffect, useCallback, useRef, useMemo } from 'react';
import { useBackend } from '@/contexts/BackendContext';

interface AnalysisResult {
  type: string;
  summary: string;
  details: string[];
  recommendations: string[];
  severity: 'low' | 'medium' | 'high' | 'critical';
  analysisData?: Record<string, unknown>;
  sessionId?: string;
}

interface BackendResponse {
  success: boolean;
  session_id?: string;
  analysis_complete?: boolean;
  results?: Record<string, unknown>;
  error?: string;
}

interface ProgressStage {
  id: string;
  name: string;
  icon: string;
  duration: number;
  messages: string[];
}

interface LogEntry {
  timestamp: string;
  message: string;
  type: 'info' | 'success' | 'warning' | 'error';
}

export default function CSDAIv2Integration() {
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [uploadedFiles, setUploadedFiles] = useState<File[]>([]);
  const [analysisType, setAnalysisType] = useState('ds_logs');
  const [results, setResults] = useState<AnalysisResult | null>(null);
  const [isDragOver, setIsDragOver] = useState(false);
  const [sessionId, setSessionId] = useState<string>('');
  
  // Use global backend status from context
  const { backendStatus, checkBackendStatus } = useBackend();
  
  // Progress bar state variables
  const [overallProgress, setOverallProgress] = useState(0);
  const [currentStageIndex, setCurrentStageIndex] = useState(0);
  const [logEntries, setLogEntries] = useState<LogEntry[]>([]);
  
  // Use ref to track if component is mounted to prevent memory leaks
  const isComponentMountedRef = useRef(true);
  
  // Progress stages configuration (matching CSDAIv2)
  const progressStages: ProgressStage[] = useMemo(() => [
    { 
      id: 'stage-1', 
      name: 'File Parsing', 
      icon: '📁',
      duration: 3000,
      messages: [
        'Reading uploaded files...',
        'Validating file format...',
        'Extracting log entries...',
        'File parsing completed ✓'
      ]
    },
    { 
      id: 'stage-2', 
      name: 'Dynamic RAG Analysis', 
      icon: '🧠',
      duration: 28000,
      messages: [
        'Initializing Dynamic RAG system...',
        'Loading Claude AI analysis engine...',
        'Extracting log context and components...',
        'Generating intelligent prompts dynamically...',
        'Processing with Claude-4 Sonnet AI...',
        'Analyzing Deep Security patterns...',
        'Detecting anomalies and security issues...',
        'Generating expert-level recommendations...',
        'Dynamic RAG analysis completed ✓'
      ]
    },
    { 
      id: 'stage-3', 
      name: 'ML & Security Analysis', 
      icon: '🔬',
      duration: 10000,
      messages: [
        'Loading ML pattern recognition models...',
        'Running behavioral analysis algorithms...',
        'Processing component health metrics...',
        'Validating Dynamic RAG insights...',
        'Cross-referencing security knowledge base...',
        'Enhancing analysis with best practices...',
        'ML analysis enhancement completed ✓'
      ]
    },
    { 
      id: 'stage-4', 
      name: 'Report Generation', 
      icon: '📊',
      duration: 5000,
      messages: [
        'Compiling analysis results...',
        'Generating HTML report...',
        'Formatting recommendations...',
        'Finalizing security assessments...',
        'Report generation completed ✓'
      ]
    }
  ], []);
  
  // Initialize mounted state with StrictMode protection
  useEffect(() => {
    // Set to true on mount (handles StrictMode remounting)
    isComponentMountedRef.current = true;
    console.log('🔧 isComponentMountedRef set to true on mount/remount');
    
    return () => {
      console.log('🧹 Component unmounting, setting isComponentMountedRef to false');
      isComponentMountedRef.current = false;
    };
  }, []);

  // Debug component lifecycle (reduced frequency to avoid spam)
  useEffect(() => {
    console.log('🔧 CSDAIv2Integration mounted, isComponentMountedRef:', isComponentMountedRef.current);
    
    // Single check after mounting to handle StrictMode
    const timeoutId = setTimeout(() => {
      if (!isComponentMountedRef.current) {
        console.log('⚠️ isComponentMountedRef was false - fixing StrictMode issue');
        isComponentMountedRef.current = true;
        console.log('🔧 Reset isComponentMountedRef to true');
      }
    }, 1000);
    
    return () => {
      clearTimeout(timeoutId);
    };
  }, []);

  // Debug uploadedFiles changes
  useEffect(() => {
    console.log('📋 uploadedFiles state changed:', {
      count: uploadedFiles.length,
      files: uploadedFiles.map(f => ({ name: f.name, size: f.size }))
    });
  }, [uploadedFiles]);

  // Debug backend status changes
  useEffect(() => {
    console.log('🔗 backendStatus changed:', backendStatus);
  }, [backendStatus]);

  // Debug component renders (reduced frequency)
  useEffect(() => {
    console.log('🔄 CSDAIv2Integration rendered - uploadedFiles:', uploadedFiles.length, 'isAnalyzing:', isAnalyzing);
  });

  // Add CSS styles for CSDAIv2 HTML content
  useEffect(() => {
    const style = document.createElement('style');
    style.textContent = `
      .csdaiv2-results {
        font-family: 'Inter', 'Segoe UI', 'Roboto', sans-serif !important;
      }
      
      .csdaiv2-results .card {
        background-color: #fff;
        border: 1px solid #dee2e6;
        border-radius: 0.375rem;
        margin-bottom: 1rem;
      }
      
      .csdaiv2-results .card-header {
        background-color: #f8f9fa;
        border-bottom: 1px solid #dee2e6;
        padding: 0.75rem 1rem;
        font-weight: bold;
      }
      
      .csdaiv2-results .card-body {
        padding: 1rem;
      }
      
      .csdaiv2-results .table {
        width: 100%;
        margin-bottom: 1rem;
        border-collapse: collapse;
      }
      
      .csdaiv2-results .table th,
      .csdaiv2-results .table td {
        padding: 0.5rem;
        border: 1px solid #dee2e6;
        text-align: left;
      }
      
      .csdaiv2-results .table th {
        background-color: #f8f9fa;
        font-weight: bold;
      }
      
      .csdaiv2-results .table-striped tbody tr:nth-of-type(odd) {
        background-color: rgba(0, 0, 0, 0.05);
      }
      
      .csdaiv2-results .badge {
        display: inline-block;
        padding: 0.25em 0.4em;
        font-size: 75%;
        font-weight: 700;
        line-height: 1;
        text-align: center;
        white-space: nowrap;
        vertical-align: baseline;
        border-radius: 0.25rem;
        margin-right: 0.25rem;
        margin-bottom: 0.25rem;
      }
      
      .csdaiv2-results .bg-primary { background-color: #007bff !important; color: white; }
      .csdaiv2-results .bg-success { background-color: #28a745 !important; color: white; }
      .csdaiv2-results .bg-warning { background-color: #ffc107 !important; color: black; }
      .csdaiv2-results .bg-danger { background-color: #dc3545 !important; color: white; }
      .csdaiv2-results .bg-info { background-color: #17a2b8 !important; color: white; }
      .csdaiv2-results .bg-secondary { background-color: #6c757d !important; color: white; }
      
      .csdaiv2-results .text-success { color: #28a745 !important; }
      .csdaiv2-results .text-warning { color: #ffc107 !important; }
      .csdaiv2-results .text-danger { color: #dc3545 !important; }
      .csdaiv2-results .text-info { color: #17a2b8 !important; }
      .csdaiv2-results .text-muted { color: #6c757d !important; }
      
      .csdaiv2-results .alert {
        padding: 0.75rem 1.25rem;
        margin-bottom: 1rem;
        border: 1px solid transparent;
        border-radius: 0.25rem;
      }
      
      .csdaiv2-results .alert-success {
        color: #155724;
        background-color: #d4edda;
        border-color: #c3e6cb;
      }
      
      .csdaiv2-results .alert-warning {
        color: #856404;
        background-color: #fff3cd;
        border-color: #ffeaa7;
      }
      
      .csdaiv2-results .alert-danger {
        color: #721c24;
        background-color: #f8d7da;
        border-color: #f5c6cb;
      }
      
      .csdaiv2-results .alert-info {
        color: #0c5460;
        background-color: #d1ecf1;
        border-color: #bee5eb;
      }
      
      .csdaiv2-results .row {
        display: flex;
        flex-wrap: wrap;
        margin-right: -15px;
        margin-left: -15px;
      }
      
      .csdaiv2-results .col-md-6,
      .csdaiv2-results .col-md-4,
      .csdaiv2-results .col-md-8,
      .csdaiv2-results .col-12 {
        flex-basis: 0;
        flex-grow: 1;
        max-width: 100%;
        position: relative;
        width: 100%;
        padding-right: 15px;
        padding-left: 15px;
      }
      
      @media (min-width: 768px) {
        .csdaiv2-results .col-md-4 {
          flex: 0 0 33.333333%;
          max-width: 33.333333%;
        }
        .csdaiv2-results .col-md-6 {
          flex: 0 0 50%;
          max-width: 50%;
        }
        .csdaiv2-results .col-md-8 {
          flex: 0 0 66.666667%;
          max-width: 66.666667%;
        }
      }
      
      .csdaiv2-results h4, .csdaiv2-results h5, .csdaiv2-results h6 {
        margin-top: 0.5rem;
        margin-bottom: 0.5rem;
        font-weight: 600;
      }
      
      .csdaiv2-results p {
        margin-bottom: 0.5rem;
      }
      
      .csdaiv2-results .list-group {
        display: flex;
        flex-direction: column;
        padding-left: 0;
        margin-bottom: 0;
      }
      
      .csdaiv2-results .list-group-item {
        position: relative;
        display: block;
        padding: 0.75rem 1.25rem;
        margin-bottom: -1px;
        background-color: #fff;
        border: 1px solid rgba(0, 0, 0, 0.125);
      }
      
      .csdaiv2-results .border-primary { border-color: #007bff !important; }
      .csdaiv2-results .border-success { border-color: #28a745 !important; }
      .csdaiv2-results .border-warning { border-color: #ffc107 !important; }
      .csdaiv2-results .border-danger { border-color: #dc3545 !important; }
      .csdaiv2-results .border-info { border-color: #17a2b8 !important; }
      
      /* Progress bar specific animations */
      @keyframes shimmer {
        0% { transform: translateX(-100%); }
        100% { transform: translateX(100%); }
      }
      
      .animate-shimmer {
        animation: shimmer 2s infinite;
      }
      
      @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
      }
      
      .animate-fadeIn {
        animation: fadeIn 0.3s ease-in;
      }
    `;
    document.head.appendChild(style);
    
    return () => {
      document.head.removeChild(style);
    };
  }, []);

  // Progress bar functions
  const addLogEntry = useCallback((message: string, type: 'info' | 'success' | 'warning' | 'error' = 'info') => {
    if (!isComponentMountedRef.current) return;
    
    const timestamp = new Date().toLocaleTimeString();
    const newEntry: LogEntry = { timestamp, message, type };
    
    setLogEntries(prev => [...prev, newEntry]);
  }, []);

  const activateStage = useCallback((stageIndex: number) => {
    if (!isComponentMountedRef.current || stageIndex >= progressStages.length) return;
    
    const stage = progressStages[stageIndex];
    addLogEntry(`Starting ${stage.name}...`, 'info');
    
    setCurrentStageIndex(stageIndex);
    
    // Process stage messages with timing
    const messageInterval = stage.duration / stage.messages.length;
    
    stage.messages.forEach((message, index) => {
      setTimeout(() => {
        if (isComponentMountedRef.current) {
          addLogEntry(message, index === stage.messages.length - 1 ? 'success' : 'info');
        }
      }, messageInterval * index);
    });
    
    // Move to next stage after duration
    setTimeout(() => {
      if (isComponentMountedRef.current) {
        setCurrentStageIndex(prev => prev + 1);
        if (stageIndex + 1 < progressStages.length) {
          activateStage(stageIndex + 1);
        }
      }
    }, stage.duration);
  }, [progressStages, addLogEntry]);

  const updateOverallProgress = useCallback(() => {
    if (!isComponentMountedRef.current) return;
    
    const totalDuration = progressStages.reduce((sum, stage) => sum + stage.duration, 0);
    const completedDuration = progressStages.slice(0, currentStageIndex)
      .reduce((sum, stage) => sum + stage.duration, 0);
    
    const progress = Math.min((completedDuration / totalDuration) * 100, 95);
    setOverallProgress(progress);
  }, [progressStages, currentStageIndex]);

  // Update progress when stage changes
  useEffect(() => {
    updateOverallProgress();
  }, [currentStageIndex, updateOverallProgress]);

  // Reset progress bar state when starting new analysis
  const resetProgressBar = useCallback(() => {
    setOverallProgress(0);
    setCurrentStageIndex(0);
    setLogEntries([]);
  }, []);
  
  const API_BASE = '/api/csdai'; // Use Next.js API routes instead of direct backend calls

  // Analyzer descriptions for educational purposes
  const analyzerDescriptions = {
    'ds-agent-log': {
      title: 'DS Agent Log Analyzer',
      description: 'Analyzes Deep Security Agent logs to identify performance issues, connectivity problems, and security events. This analyzer helps diagnose agent behavior and troubleshoot deployment issues.',
      features: ['Agent Performance Analysis', 'Connectivity Diagnostics', 'Security Event Detection', 'Error Pattern Recognition'],
      icon: '🔍',
      estimatedTime: '2-3 minutes'
    },
    'av-conflicts': {
      title: 'Anti-Virus Conflict Analyzer', 
      description: 'Detects conflicts between Deep Security and other anti-virus solutions. Identifies performance impacts, compatibility issues, and provides recommendations for optimal configuration.',
      features: ['Conflict Detection', 'Performance Impact Analysis', 'Configuration Recommendations', 'Compatibility Assessment'],
      icon: '⚔️',
      estimatedTime: '1-2 minutes'
    },
    'resource-analysis': {
      title: 'Resource Analysis Engine',
      description: 'Comprehensive analysis of system resource usage including CPU, memory, disk I/O, and network patterns. Identifies bottlenecks and optimization opportunities.',
      features: ['CPU Usage Analysis', 'Memory Pattern Detection', 'I/O Performance Review', 'Resource Optimization'],
      icon: '📊',
      estimatedTime: '3-4 minutes'
    },
    'amsp': {
      title: 'AMSP (Anti-Malware Scan Performance)',
      description: 'Advanced analysis of anti-malware scanning performance and efficiency. Provides insights into scan patterns, false positives, and performance optimization recommendations.',
      features: ['Scan Performance Metrics', 'False Positive Analysis', 'Pattern Recognition', 'Optimization Insights'],
      icon: '🛡️',
      estimatedTime: '2-4 minutes'
    }
  };

  const uploadFilesToBackend = useCallback(async (files: File[]): Promise<string | null> => {
    console.log('📤 uploadFilesToBackend called with:', {
      fileCount: files.length,
      analysisType,
      fileNames: files.map(f => f.name),
      fileSizes: files.map(f => f.size)
    });

    const formData = new FormData();
    files.forEach((file, index) => {
      formData.append(`file_${index}`, file);
      console.log(`📎 Added file_${index}:`, file.name, `(${file.size} bytes)`);
    });
    formData.append('analysis_type', analysisType);
    console.log('📋 Analysis type set to:', analysisType);

    try {
      console.log('🔄 Uploading files to backend...', files.length, 'files');
      const response = await fetch(`${API_BASE}/upload`, {
        method: 'POST',
        body: formData,
      });

      console.log('📡 Upload response status:', response.status);
      
      if (response.ok) {
        const data: BackendResponse = await response.json();
        console.log('✅ Upload successful, session ID:', data.session_id);
        console.log('📊 Full upload response:', data);
        return data.session_id || null;
      } else {
        const errorData = await response.text();
        console.error('❌ Upload failed with status:', response.status, errorData);
      }
    } catch (error) {
      console.error('❌ Upload failed:', error);
    }
    return null;
  }, [analysisType]);

  const pollAnalysisStatus = useCallback(async (sessionId: string): Promise<BackendResponse | null> => {
    try {
      console.log('🔍 Polling status for session:', sessionId);
      const response = await fetch(`${API_BASE}/status/${sessionId}`);
      if (response.ok) {
        const data: BackendResponse = await response.json();
        console.log('📊 Status response:', data);
        return data;
      } else {
        console.error('❌ Status check failed with status:', response.status);
      }
    } catch (error) {
      console.error('❌ Status check failed:', error);
    }
    return null;
  }, []);

  const getAnalysisResults = useCallback(async (sessionId: string): Promise<Record<string, unknown> | null> => {
    try {
      console.log('📋 Fetching results for session:', sessionId);
      const response = await fetch(`${API_BASE}/results/${sessionId}`);
      if (response.ok) {
        const data = await response.json();
        console.log('✅ Results fetched successfully:', data);
        return data;
      } else {
        const errorText = await response.text();
        console.error('❌ Results fetch failed with status:', response.status, errorText);
      }
    } catch (error) {
      console.error('❌ Results fetch failed:', error);
    }
    return null;
  }, []);

  const analysisTypes = [
    { 
      id: 'ds_logs', 
      name: 'DS Agent Logs', 
      description: 'Analyze Deep Security Agent logs',
      fullDescription: 'Deep Security Agent has lost communication with the manager or experiencing connectivity issues.',
      icon: '🛡️',
      severity: 'high',
      estimatedTime: '15-45 minutes',
      issueType: 'Connection Issue',
      commonCauses: [
        'Network connectivity problems',
        'Firewall blocking communication',
        'Certificate issues',
        'Agent service status'
      ]
    },
    { 
      id: 'amsp_logs', 
      name: 'AMSP Analysis', 
      description: 'Anti-Malware scan performance analysis',
      fullDescription: 'Anti-malware engine is not running or has gone offline, affecting real-time protection.',
      icon: '🦠',
      severity: 'critical',
      estimatedTime: '30-60 minutes',
      issueType: 'Protection Issue',
      commonCauses: [
        'Service startup failure',
        'Component corruption',
        'Memory issues',
        'Configuration errors'
      ]
    },
    { 
      id: 'av_conflicts', 
      name: 'AV Conflicts', 
      description: 'Detect antivirus software conflicts',
      fullDescription: 'Deep Security components are consuming excessive CPU or memory resources.',
      icon: '⚠️',
      severity: 'medium',
      estimatedTime: '60-120 minutes',
      issueType: 'Performance Issue',
      commonCauses: [
        'Inefficient scan exclusions',
        'Large file scanning',
        'System resource constraints',
        'Configuration optimization needed'
      ]
    },
    { 
      id: 'resource_analysis', 
      name: 'Resource Analysis', 
      description: 'System resource utilization analysis',
      fullDescription: 'Verify compatibility with existing software and environment configuration.',
      icon: '📈',
      severity: 'medium',
      estimatedTime: '45-90 minutes',
      issueType: 'Compatibility Check',
      commonCauses: [
        'Conflicting security software',
        'Incompatible OS version',
        'Third-party software conflicts',
        'System requirements not met'
      ]
    }
  ];

  const handleFileUpload = (files: FileList | null) => {
    console.log('📁 handleFileUpload called with:', files ? files.length : 0, 'files');
    
    if (!files) {
      console.log('❌ No files provided');
      return;
    }
    
    const validFiles = Array.from(files).filter(file => {
      const validExtensions = ['.log', '.txt', '.xml', '.csv'];
      const fileExtension = '.' + file.name.split('.').pop()?.toLowerCase();
      const isValidExtension = validExtensions.includes(fileExtension);
      const isValidSize = file.size <= 50 * 1024 * 1024; // 50MB limit
      
      console.log(`📄 File: ${file.name}`, {
        extension: fileExtension,
        isValidExtension,
        size: file.size,
        isValidSize
      });
      
      return isValidExtension && isValidSize;
    });

    console.log(`✅ Valid files: ${validFiles.length} out of ${files.length}`);
    
    setUploadedFiles(prev => {
      const newFiles = [...prev, ...validFiles];
      console.log('📋 Updated uploadedFiles:', newFiles.map(f => f.name));
      return newFiles;
    });
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
    handleFileUpload(e.dataTransfer.files);
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
  };

  const startAnalysis = async () => {
    // Force ensure component is mounted before starting
    if (!isComponentMountedRef.current) {
      console.log('� Component was unmounted, resetting to mounted state');
      isComponentMountedRef.current = true;
    }

    console.log('�🚀 startAnalysis called with:', {
      uploadedFiles: uploadedFiles.length,
      analysisType,
      backendStatus,
      isMounted: isComponentMountedRef.current
    });

    if (uploadedFiles.length === 0) {
      console.log('❌ Early return: no files uploaded');
      alert('Please upload at least one file before starting analysis.');
      return;
    }

    // Verify component is still mounted
    if (!isComponentMountedRef.current) {
      console.log('❌ Early return: component unmounted during start');
      return;
    }

    // Check if backend is connected before starting
    if (backendStatus !== 'connected') {
      console.log('❌ Backend not connected:', backendStatus);
      alert('CSDAIv2 backend is not available. Please ensure the backend is running on localhost:5003');
      return;
    }

    console.log('✅ Starting analysis process...');

    if (isComponentMountedRef.current) {
      setIsAnalyzing(true);
      setResults(null);
      resetProgressBar();
      
      // Start the progress bar animation
      setTimeout(() => {
        activateStage(0);
      }, 500);
    }

    try {
      // Upload files to backend
      const uploadedSessionId = await uploadFilesToBackend(uploadedFiles);
      if (!uploadedSessionId) {
        throw new Error('File upload failed');
      }

      if (isComponentMountedRef.current) {
        setSessionId(uploadedSessionId);
      }

      // Poll for analysis completion with improved logic
      let analysisComplete = false;
      let currentStep = 2;
      let pollAttempts = 0;
      const maxPollAttempts = 30; // Maximum 60 seconds of polling

      while (!analysisComplete && currentStep <= 5 && pollAttempts < maxPollAttempts && isComponentMountedRef.current) {
        await new Promise(resolve => setTimeout(resolve, 2000));
        pollAttempts++;
        
        if (!isComponentMountedRef.current) break; // Stop polling if component unmounted
        
        const status = await pollAnalysisStatus(uploadedSessionId);
        
        // Check if analysis is complete
        if (status?.analysis_complete) {
          analysisComplete = true;
          break;
        }

        // Check if there's an error
        if (status && !status.success) {
          throw new Error(status.error || 'Analysis failed');
        }

        // Update progress only if we're not at the last step and haven't been stuck too long
        if (currentStep < 5 && pollAttempts % 3 === 0 && isComponentMountedRef.current) { // Update every 3 polls (6 seconds)
          currentStep++;
          // Progress is now handled by the enhanced progress bar
        }
      }

      if (!isComponentMountedRef.current) return; // Exit if component unmounted

      // Check if polling timed out
      if (!analysisComplete && pollAttempts >= maxPollAttempts) {
        throw new Error('Analysis timed out. Please try again or check the backend logs.');
      }

      // Get final results
      const analysisResults = await getAnalysisResults(uploadedSessionId);
      if (analysisResults && isComponentMountedRef.current) {
        const formattedResults = formatBackendResults(analysisResults, analysisType);
        setResults(formattedResults);
      } else if (!analysisResults) {
        throw new Error('Failed to retrieve analysis results');
      }

      if (isComponentMountedRef.current) {
        // Analysis completed - progress bar will handle completion
      }

    } catch (error) {
      console.error('Backend analysis failed:', error);
      if (isComponentMountedRef.current) {
        alert(`Analysis failed: ${error instanceof Error ? error.message : 'Unknown error'}. Please check the CSDAIv2 backend connection.`);
      }
    } finally {
      if (isComponentMountedRef.current) {
        setIsAnalyzing(false);
      }
    }
  };

  const formatBackendResults = (backendData: Record<string, unknown>, type: string): AnalysisResult => {
    console.log('🔍 Raw backend data:', backendData);
    console.log('🔍 Backend data results field:', backendData.results);
    console.log('🔍 Backend data results type:', typeof backendData.results);
    console.log('🔍 Is HTML content?:', typeof backendData.results === 'string' && (
      (backendData.results as string).includes('<div') ||
      (backendData.results as string).includes('<h') ||
      (backendData.results as string).includes('<p') ||
      (backendData.results as string).includes('<table') ||
      (backendData.results as string).includes('class=') ||
      (backendData.results as string).includes('font-consistent')
    ));
    
    // First 200 characters of results for debugging
    if (typeof backendData.results === 'string') {
      console.log('🔍 Results preview:', (backendData.results as string).substring(0, 200));
    }
    
    // Safely convert details to string array
    const formatDetails = (data: unknown): string[] => {
      console.log('🔄 Formatting details:', data);
      if (Array.isArray(data)) {
        return data.map(item => {
          const formatted = typeof item === 'string' ? item : JSON.stringify(item);
          console.log('🔄 Detail item formatted:', formatted);
          return formatted;
        });
      }
      if (typeof data === 'object' && data !== null) {
        return Object.entries(data).map(([key, value]) => {
          const formatted = `${key}: ${typeof value === 'string' ? value : JSON.stringify(value)}`;
          console.log('🔄 Detail object formatted:', formatted);
          return formatted;
        });
      }
      const formatted = [typeof data === 'string' ? data : JSON.stringify(data)];
      console.log('🔄 Detail fallback formatted:', formatted);
      return formatted;
    };

    // Safely convert recommendations to string array
    const formatRecommendations = (data: unknown): string[] => {
      console.log('🔄 Formatting recommendations:', data);
      if (Array.isArray(data)) {
        return data.map(item => {
          const formatted = typeof item === 'string' ? item : JSON.stringify(item);
          console.log('🔄 Recommendation item formatted:', formatted);
          return formatted;
        });
      }
      if (typeof data === 'object' && data !== null) {
        return Object.entries(data).map(([key, value]) => {
          const formatted = `${key}: ${typeof value === 'string' ? value : JSON.stringify(value)}`;
          console.log('🔄 Recommendation object formatted:', formatted);
          return formatted;
        });
      }
      const formatted = [typeof data === 'string' ? data : JSON.stringify(data)];
      console.log('🔄 Recommendation fallback formatted:', formatted);
      return formatted;
    };

    // Format the backend response to match our interface
    const result = {
      type: analysisTypes.find(t => t.id === type)?.name || 'Analysis',
      summary: typeof backendData.summary === 'string' 
        ? backendData.summary 
        : typeof backendData.summary === 'object' && backendData.summary !== null
          ? JSON.stringify(backendData.summary, null, 2)
          : 'Analysis completed successfully',
      details: formatDetails(backendData.details),
      recommendations: formatRecommendations(backendData.recommendations),
      severity: (backendData.severity as AnalysisResult['severity']) || 'medium',
      analysisData: backendData,
      sessionId: sessionId
    };
    
    console.log('✅ Final formatted result:', result);
    return result;
  };

  const removeFile = (index: number) => {
    setUploadedFiles(prev => prev.filter((_, i) => i !== index));
  };

  const resetAnalysis = () => {
    setUploadedFiles([]);
    setResults(null);
    setIsAnalyzing(false);
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical': return 'text-red-400 bg-red-500/20 border-red-500/30';
      case 'high': return 'text-orange-400 bg-orange-500/20 border-orange-500/30';
      case 'medium': return 'text-yellow-400 bg-yellow-500/20 border-yellow-500/30';
      case 'low': return 'text-green-400 bg-green-500/20 border-green-500/30';
      default: return 'text-gray-400 bg-gray-500/20 border-gray-500/30';
    }
  };

  return (
    <div className="bg-gradient-to-br from-slate-800/90 to-slate-900/90 backdrop-blur-sm rounded-3xl shadow-2xl p-8 border border-red-500/30">
      <div className="flex items-center justify-between mb-8">
        <div className="flex items-center space-x-4">
          <div className="w-16 h-16 bg-gradient-to-br from-red-500 to-red-700 rounded-2xl flex items-center justify-center">
            <span className="text-white font-bold text-2xl">🔬</span>
          </div>
          <div>
            <h2 className="text-3xl font-bold text-white">Deep Security Unified Analyzer</h2>
            <div className="flex items-center space-x-3">
              <p className="text-gray-300">AI-powered log analysis and diagnostics</p>
              <div className={`flex items-center space-x-2 px-4 py-2 rounded-lg text-sm font-medium border transition-all duration-300 ${
                backendStatus === 'connected' ? 'bg-green-500/20 text-green-400 border-green-500/30' :
                backendStatus === 'checking' ? 'bg-blue-500/20 text-blue-400 border-blue-500/30 animate-pulse' :
                'bg-red-500/20 text-red-400 border-red-500/30'
              }`}>
                {backendStatus === 'connected' && (
                  <>
                    <div className="w-3 h-3 bg-green-400 rounded-full animate-pulse"></div>
                    <span>Backend Connected</span>
                  </>
                )}
                {backendStatus === 'checking' && (
                  <>
                    <div className="w-3 h-3 bg-blue-400 rounded-full animate-bounce"></div>
                    <span>Connecting...</span>
                  </>
                )}
                {backendStatus === 'error' && (
                  <>
                    <div className="w-3 h-3 bg-red-400 rounded-full animate-ping"></div>
                    <span>Offline - Auto-retrying every 10s</span>
                  </>
                )}
              </div>
            </div>
          </div>
        </div>
        {results && (
          <button
            onClick={resetAnalysis}
            className="bg-red-500/20 text-red-300 px-6 py-2 rounded-xl hover:bg-red-500/30 transition-all duration-300 border border-red-500/30"
          >
            New Analysis
          </button>
        )}
      </div>

      {!results ? (
        <div className="space-y-8">
          {/* Backend Connection Error Message */}
          {backendStatus === 'error' && (
            <div className="bg-red-500/20 border border-red-500/30 rounded-xl p-6 mb-6">
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center space-x-3">
                  <span className="text-red-400 text-2xl">⚠️</span>
                  <h3 className="text-xl font-bold text-red-400">Backend Connection Required</h3>
                </div>
                <div className="flex items-center space-x-2 text-xs text-red-300">
                  <div className="w-2 h-2 bg-red-400 rounded-full animate-ping"></div>
                  <span>Auto-retrying every 10s</span>
                </div>
              </div>
              <p className="text-red-300 mb-2">
                CSDAIv2 backend is not available. The system will automatically retry the connection.
                Please ensure the Flask application is running on localhost:5003.
              </p>
              <p className="text-red-400 text-xs mb-4">
                ℹ️ Open browser developer tools (F12) → Console tab to see detailed connection logs
              </p>
              <div className="bg-black/30 rounded-lg p-4 border border-red-500/20">
                <p className="text-red-200 text-sm font-mono">
                  To start the backend:<br/>
                  cd path/to/CSDAIv2<br/>
                  python app.py
                </p>
              </div>
              <button
                onClick={() => {
                  console.log('Manual retry triggered');
                  checkBackendStatus();
                }}
                className="mt-4 bg-red-500/20 text-red-300 px-4 py-2 rounded-lg hover:bg-red-500/30 transition-all duration-300 border border-red-500/30 flex items-center space-x-2"
              >
                <span>🔄</span>
                <span>Retry Now</span>
              </button>
            </div>
          )}

          {/* Analysis Type Selection */}
          <div>
            <h3 className="text-3xl font-bold text-white mb-2 text-center">Select Your Issue</h3>
            <p className="text-gray-400 mb-8 text-center">Choose the specific issue you&apos;re experiencing with Deep Security</p>
            <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
              {analysisTypes.map((type) => {
                const getSeverityColor = (severity: string) => {
                  switch (severity) {
                    case 'critical': return 'bg-red-500/20 text-red-300 border-red-500/50';
                    case 'high': return 'bg-orange-500/20 text-orange-300 border-orange-500/50';
                    case 'medium': return 'bg-yellow-500/20 text-yellow-300 border-yellow-500/50';
                    default: return 'bg-blue-500/20 text-blue-300 border-blue-500/50';
                  }
                };

                const getSeverityIcon = (severity: string) => {
                  switch (severity) {
                    case 'critical': return '🔴';
                    case 'high': return '🟠';
                    case 'medium': return '🟡';
                    default: return '🔵';
                  }
                };

                return (
                  <button
                    key={type.id}
                    onClick={() => setAnalysisType(type.id)}
                    className={`relative p-6 rounded-2xl border transition-all duration-300 text-left group hover:scale-105 ${
                      analysisType === type.id
                        ? 'bg-red-500/20 border-red-500/50 shadow-2xl shadow-red-500/20'
                        : 'bg-white/5 border-white/20 hover:border-red-500/30 hover:bg-red-500/10'
                    }`}
                  >
                    {/* Severity and Issue Type Badges */}
                    <div className="flex justify-between items-start mb-4">
                      <span className={`px-3 py-1 rounded-full text-xs font-medium border ${getSeverityColor(type.severity)}`}>
                        {getSeverityIcon(type.severity)} {type.severity.toUpperCase()}
                      </span>
                      <span className="px-3 py-1 rounded-full text-xs font-medium bg-blue-500/20 text-blue-300 border border-blue-500/50">
                        {type.issueType}
                      </span>
                    </div>

                    {/* Main Icon and Title */}
                    <div className="flex items-center space-x-4 mb-4">
                      <div className="w-16 h-16 bg-gradient-to-br from-red-500/20 to-red-700/20 rounded-2xl flex items-center justify-center border border-red-500/30">
                        <span className="text-3xl">{type.icon}</span>
                      </div>
                      <div>
                        <h4 className="text-xl font-bold text-white group-hover:text-red-300 transition-colors">
                          {type.name}
                        </h4>
                        <p className="text-sm text-gray-400">{type.description}</p>
                      </div>
                    </div>

                    {/* Issue Description */}
                    <p className="text-gray-300 text-sm mb-4 leading-relaxed">
                      {type.fullDescription}
                    </p>

                    {/* Time Estimate and Difficulty */}
                    <div className="flex items-center justify-between mb-4">
                      <div className="flex items-center space-x-2 text-gray-400">
                        <span className="text-lg">⏱️</span>
                        <span className="text-sm">{type.estimatedTime}</span>
                      </div>
                      <div className="flex items-center space-x-2 text-gray-400">
                        <span className="text-lg">🔧</span>
                        <span className="text-sm">Common Issue</span>
                      </div>
                    </div>

                    {/* Common Causes */}
                    <div className="space-y-2">
                      <h5 className="text-xs font-semibold text-gray-400 uppercase tracking-wider">Common Causes</h5>
                      <div className="space-y-1">
                        {type.commonCauses.slice(0, 3).map((cause, index) => (
                          <div key={index} className="flex items-start space-x-2">
                            <div className="w-1 h-1 bg-red-400 rounded-full mt-2 flex-shrink-0"></div>
                            <span className="text-xs text-gray-400">{cause}</span>
                          </div>
                        ))}
                        {type.commonCauses.length > 3 && (
                          <div className="flex items-start space-x-2">
                            <div className="w-1 h-1 bg-red-400 rounded-full mt-2 flex-shrink-0"></div>
                            <span className="text-xs text-gray-500">+{type.commonCauses.length - 3} more causes</span>
                          </div>
                        )}
                      </div>
                    </div>

                    {/* Action Button */}
                    <div className="mt-6 pt-4 border-t border-white/10">
                      <div className={`w-full py-3 px-4 rounded-xl text-center font-medium transition-all duration-300 ${
                        analysisType === type.id
                          ? 'bg-red-500 text-white shadow-lg'
                          : 'bg-red-500/20 text-red-300 group-hover:bg-red-500/30'
                      }`}>
                        {analysisType === type.id ? '✓ Selected' : 'Create Support Ticket'}
                      </div>
                    </div>
                  </button>
                );
              })}
            </div>
          </div>

          {/* File Upload Area */}
          <div>
            <h3 className="text-xl font-bold text-white mb-4">Upload Log Files</h3>
            <div
              onDrop={handleDrop}
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              className={`border-2 border-dashed rounded-2xl p-8 text-center transition-all duration-300 ${
                isDragOver
                  ? 'border-red-500 bg-red-500/10'
                  : 'border-gray-500 hover:border-red-500/50 hover:bg-red-500/5'
              }`}
            >
              <div className="w-16 h-16 bg-gradient-to-br from-red-500 to-red-700 rounded-2xl mx-auto mb-4 flex items-center justify-center">
                <span className="text-white text-2xl">📁</span>
              </div>
              <h4 className="text-lg font-semibold text-white mb-2">
                Drop log files here or click to browse
              </h4>
              <p className="text-gray-400 mb-4">
                Supports .log, .txt, .xml, .csv files up to 50MB
              </p>
              <input
                type="file"
                multiple
                accept=".log,.txt,.xml,.csv"
                onChange={(e) => handleFileUpload(e.target.files)}
                className="hidden"
                id="file-upload"
              />
              <label
                htmlFor="file-upload"
                className="bg-red-500/20 text-red-300 px-6 py-2 rounded-xl hover:bg-red-500/30 transition-all duration-300 border border-red-500/30 cursor-pointer inline-block"
              >
                Choose Files
              </label>
            </div>

            {/* Uploaded Files List */}
            {uploadedFiles.length > 0 && (
              <div className="mt-6 space-y-3">
                <h4 className="text-lg font-semibold text-white">Uploaded Files</h4>
                {uploadedFiles.map((file, index) => (
                  <div key={index} className="flex items-center justify-between bg-white/5 rounded-xl p-4 border border-white/20">
                    <div className="flex items-center space-x-3">
                      <span className="text-2xl">📄</span>
                      <div>
                        <p className="text-white font-semibold">{file.name}</p>
                        <p className="text-gray-400 text-sm">{(file.size / 1024 / 1024).toFixed(2)} MB</p>
                      </div>
                    </div>
                    <button
                      onClick={() => removeFile(index)}
                      className="text-red-400 hover:text-red-300 transition-colors"
                    >
                      ✕
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Analysis Progress with CSDAIv2-style Progress Bar */}
          {(uploadedFiles.length > 0 || isAnalyzing) && (
            <div>
              <h3 className="text-xl font-bold text-white mb-4">Analysis Progress</h3>
              
              {isAnalyzing ? (
                /* Enhanced Progress Bar - CSDAIv2 Style */
                <div className="analysis-progress-container bg-gradient-to-br from-slate-100/10 to-slate-200/10 rounded-2xl p-8 border border-white/20">
                  <div className="analysis-progress-header flex justify-between items-center mb-6">
                    <div>
                      <h4 className="text-2xl font-bold text-white mb-2">🧠 AI Analysis in Progress</h4>
                      <p className="text-gray-300">Our advanced AI systems are analyzing your files. Please wait while we generate comprehensive insights.</p>
                    </div>
                    <div className="progress-percentage text-4xl font-bold text-blue-400" id="progress-text">
                      {Math.round(overallProgress)}%
                    </div>
                  </div>
                  
                  {/* Main Progress Bar */}
                  <div className="main-progress-bar mb-8">
                    <div className="h-5 bg-gray-600/30 rounded-full overflow-hidden shadow-inner">
                      <div 
                        className="h-full bg-gradient-to-r from-blue-500 via-green-500 to-emerald-400 rounded-full transition-all duration-500 ease-out relative overflow-hidden"
                        style={{ width: `${overallProgress}%` }}
                        id="main-progress"
                      >
                        <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent animate-shimmer"></div>
                      </div>
                    </div>
                  </div>
                  
                  {/* Analysis Stages Grid */}
                  <div className="analysis-stages grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
                    {progressStages.map((stage, index) => (
                      <div 
                        key={stage.id}
                        id={stage.id}
                        className={`stage-card bg-white/5 rounded-xl p-6 border-2 transition-all duration-300 min-h-[140px] flex flex-col items-center justify-center ${
                          index < currentStageIndex ? 'border-green-500 bg-green-500/10 completed' :
                          index === currentStageIndex ? 'border-blue-500 bg-blue-500/10 active transform -translate-y-1 shadow-lg shadow-blue-500/20' :
                          'border-gray-500/30'
                        }`}
                      >
                        <div className={`stage-icon text-4xl mb-3 transition-colors duration-300 ${
                          index < currentStageIndex ? 'text-green-400' :
                          index === currentStageIndex ? 'text-blue-400' :
                          'text-gray-400'
                        }`}>
                          {stage.icon}
                        </div>
                        <h5 className="stage-title font-semibold text-white text-center mb-3">{stage.name}</h5>
                        <div className="stage-status">
                          {index < currentStageIndex ? (
                            <i className="fa-solid fa-check text-green-400 text-xl"></i>
                          ) : index === currentStageIndex ? (
                            <div className="flex items-center space-x-2">
                              <div className="w-4 h-4 border-2 border-blue-400 border-t-transparent rounded-full animate-spin"></div>
                            </div>
                          ) : (
                            <div className="w-6 h-6 bg-gray-500/30 rounded-full flex items-center justify-center text-gray-400 text-sm font-bold">
                              {index + 1}
                            </div>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                  
                  {/* Analysis Log Feed */}
                  <div className="analysis-feed">
                    <div className="bg-gray-800/50 rounded-xl border border-gray-600/30 overflow-hidden">
                      <div className="bg-gradient-to-r from-gray-700 to-gray-800 px-4 py-3 border-b border-gray-600/30">
                        <h6 className="text-white font-semibold flex items-center">
                          <span className="mr-2">📋</span>
                          Analysis Log
                        </h6>
                      </div>
                      <div 
                        id="analysis-log"
                        className="h-48 overflow-y-auto p-4 bg-gray-900/30 font-mono text-sm space-y-1"
                      >
                        {logEntries.map((entry, index) => (
                          <div key={index} className={`log-entry animate-fadeIn ${entry.type}`}>
                            <span className="text-gray-400 mr-3">[{entry.timestamp}]</span>
                            <span className={`${
                              entry.type === 'success' ? 'text-green-400' :
                              entry.type === 'warning' ? 'text-yellow-400' :
                              entry.type === 'error' ? 'text-red-400' :
                              'text-gray-300'
                            }`}>
                              {entry.message}
                            </span>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                  
                  {/* Estimated Time */}
                  <div className="estimated-time mt-6">
                    <div className="bg-blue-500/10 border border-blue-500/30 rounded-lg p-4">
                      <div className="flex items-center">
                        <span className="text-blue-400 mr-2">ℹ️</span>
                        <span className="text-blue-300 font-semibold">Estimated Time: 2-3 minutes</span>
                      </div>
                      <p className="text-blue-200 text-sm mt-1">
                        Analysis time depends on file size and selected enhancement options.
                      </p>
                    </div>
                  </div>
                  
                  <div className="mt-6 text-center">
                    <p className="text-gray-400 text-sm">
                      <span className="mr-2">⚠️</span>
                      You will be automatically redirected to the results page when analysis is complete.
                    </p>
                  </div>
                </div>
              ) : (
                /* Analyzer Information Display (when not analyzing) */
                <div className="space-y-6">
                  {/* Current Analyzer Info */}
                  {analyzerDescriptions[analysisType as keyof typeof analyzerDescriptions] && (
                    <div className="bg-gradient-to-br from-blue-500/10 to-purple-500/10 rounded-2xl p-6 border border-blue-500/30">
                      <div className="flex items-start space-x-4">
                        <div className="text-4xl">
                          {analyzerDescriptions[analysisType as keyof typeof analyzerDescriptions].icon}
                        </div>
                        <div className="flex-1">
                          <h4 className="text-xl font-bold text-white mb-2">
                            {analyzerDescriptions[analysisType as keyof typeof analyzerDescriptions].title}
                          </h4>
                          <p className="text-gray-300 leading-relaxed mb-4">
                            {analyzerDescriptions[analysisType as keyof typeof analyzerDescriptions].description}
                          </p>
                          <div className="grid grid-cols-2 gap-3 mb-4">
                            {analyzerDescriptions[analysisType as keyof typeof analyzerDescriptions].features.map((feature, index) => (
                              <div key={index} className="flex items-center space-x-2">
                                <span className="w-2 h-2 bg-blue-400 rounded-full"></span>
                                <span className="text-sm text-gray-400">{feature}</span>
                              </div>
                            ))}
                          </div>
                          <div className="flex items-center space-x-2 text-sm">
                            <span className="text-yellow-400">⏱️</span>
                            <span className="text-yellow-300 font-semibold">
                              Estimated Time: {analyzerDescriptions[analysisType as keyof typeof analyzerDescriptions].estimatedTime}
                            </span>
                          </div>
                        </div>
                      </div>
                    </div>
                  )}

                  {/* Analysis Process Overview */}
                  <div className="bg-white/5 rounded-xl p-4 border border-white/10">
                    <h5 className="text-white font-semibold mb-3 flex items-center">
                      <span className="mr-2">🔄</span>
                      Analysis Process
                    </h5>
                    <div className="text-sm text-gray-400 space-y-2">
                      <p>• Files will be securely uploaded and processed</p>
                      <p>• AI engine will analyze patterns and anomalies</p>
                      <p>• Machine learning algorithms will enhance detection</p>
                      <p>• Comprehensive report will be generated</p>
                    </div>
                  </div>
                </div>
              )}

              {!isAnalyzing && uploadedFiles.length > 0 && !results && (
                <button
                  onClick={() => {
                    console.log('🖱️ Start Analysis button clicked!', {
                      isAnalyzing,
                      uploadedFilesCount: uploadedFiles.length,
                      hasResults: !!results,
                      backendStatus,
                      analysisType,
                      isMounted: isComponentMountedRef.current
                    });
                    startAnalysis();
                  }}
                  disabled={backendStatus !== 'connected'}
                  className={`w-full mt-6 py-4 rounded-xl font-semibold text-lg transition-all duration-300 ${
                    backendStatus === 'connected' 
                      ? 'bg-gradient-to-r from-red-500 to-red-600 text-white hover:from-red-600 hover:to-red-700 transform hover:scale-105' 
                      : 'bg-gray-500/20 text-gray-400 cursor-not-allowed border border-gray-500/30'
                  }`}
                >
                  {backendStatus === 'connected' ? 'Start Analysis' : 'Backend Required for Analysis'}
                </button>
              )}

              {/* Debug: Log button visibility conditions */}
              {(() => {
                console.log('🔍 Button visibility conditions:', {
                  isAnalyzing,
                  uploadedFilesLength: uploadedFiles.length,
                  hasResults: !!results,
                  showButton: !isAnalyzing && uploadedFiles.length > 0 && !results
                });
                return null;
              })()}
            </div>
          )}
        </div>
      ) : (
        /* Analysis Results */
        <div className="space-y-8">
          <div className="bg-white/5 rounded-2xl p-6 border border-white/20">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-2xl font-bold text-white">Analysis Results</h3>
              <span className={`px-3 py-1 rounded-lg text-sm font-semibold border ${getSeverityColor(results.severity)}`}>
                {results.severity.toUpperCase()}
              </span>
            </div>
            <h4 className="text-lg font-semibold text-white mb-2">{results.type}</h4>
            <p className="text-gray-300 leading-relaxed">
              {typeof results.summary === 'string' 
                ? results.summary 
                : JSON.stringify(results.summary, null, 2)
              }
            </p>
          </div>

          {/* Check if we have HTML results from CSDAIv2 backend for ANY analysis type */}
          {results.analysisData && typeof results.analysisData.results === 'string' && (
            results.analysisData.results.includes('<div') || 
            results.analysisData.results.includes('<h') || 
            results.analysisData.results.includes('<p') ||
            results.analysisData.results.includes('<table') ||
            results.analysisData.results.includes('class=') ||
            results.analysisData.results.includes('font-consistent')
          ) ? (
            <div className="bg-white/5 rounded-2xl p-6 border border-white/20">
              <div className="flex items-center justify-between mb-4">
                <h4 className="text-xl font-bold text-white flex items-center">
                  <span className="mr-3">📋</span>
                  Complete Analysis Results
                </h4>
                {results.sessionId && (
                  <span className="text-xs bg-blue-500/20 text-blue-400 px-2 py-1 rounded-lg">
                    Session: {results.sessionId.slice(-8)}
                  </span>
                )}
              </div>
              <div className="bg-blue-50/5 border border-blue-500/20 rounded-lg p-1">
                <p className="text-blue-300 text-sm mb-3 px-3 pt-2">
                  ℹ️ Analysis Complete: Use the navigation tabs below to explore specific sections of your {results.type} results.
                </p>
                
                {/* Render the HTML results directly for all analysis types */}
                <div 
                  className="csdaiv2-results"
                  dangerouslySetInnerHTML={{ 
                    __html: results.analysisData.results as string 
                  }}
                  style={{
                    backgroundColor: '#f8f9fa',
                    color: '#333',
                    borderRadius: '8px',
                    padding: '16px',
                    maxHeight: '80vh',
                    overflowY: 'auto',
                    fontSize: '14px',
                    lineHeight: '1.6'
                  }}
                />
              </div>
            </div>
          ) : (
            // Fallback to original layout for non-HTML results
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
              <div className="bg-white/5 rounded-2xl p-6 border border-white/20">
                <h4 className="text-xl font-bold text-white mb-4 flex items-center">
                  <span className="mr-3">🔍</span>
                  Analysis Details
                  {results.sessionId && (
                    <span className="ml-auto text-xs bg-blue-500/20 text-blue-400 px-2 py-1 rounded-lg">
                      Session: {results.sessionId.slice(-8)}
                    </span>
                  )}
                </h4>
                <ul className="space-y-3">
                  {results.details && Array.isArray(results.details) ? results.details.map((detail, index) => (
                    <li key={index} className="flex items-start space-x-3">
                      <span className="text-green-400 mt-1">•</span>
                      <span className="text-gray-300">
                        {typeof detail === 'string' ? detail : JSON.stringify(detail)}
                      </span>
                    </li>
                  )) : (
                    <li className="flex items-start space-x-3">
                      <span className="text-green-400 mt-1">•</span>
                      <span className="text-gray-300">No details available</span>
                    </li>
                  )}
                </ul>
                
                {results.analysisData && (
                  <div className="mt-4 p-3 bg-black/30 rounded-lg border border-gray-600">
                    <h5 className="text-sm font-semibold text-gray-400 mb-2">Raw Analysis Data</h5>
                    <pre className="text-xs text-gray-500 overflow-auto max-h-32">
                      {JSON.stringify(results.analysisData, null, 2)}
                    </pre>
                  </div>
                )}
              </div>

              <div className="bg-white/5 rounded-2xl p-6 border border-white/20">
                <h4 className="text-xl font-bold text-white mb-4 flex items-center">
                  <span className="mr-3">💡</span>
                  Recommendations
                </h4>
                <ul className="space-y-3">
                  {results.recommendations && Array.isArray(results.recommendations) ? results.recommendations.map((rec, index) => (
                    <li key={index} className="flex items-start space-x-3">
                      <span className="text-yellow-400 mt-1">→</span>
                      <span className="text-gray-300">
                        {typeof rec === 'string' ? rec : JSON.stringify(rec)}
                      </span>
                    </li>
                  )) : (
                    <li className="flex items-start space-x-3">
                      <span className="text-yellow-400 mt-1">→</span>
                      <span className="text-gray-300">No recommendations available</span>
                    </li>
                  )}
                </ul>
              </div>

              {/* Enhanced RAG Insights Display */}
              {results.analysisData && ((results.analysisData as any).dynamic_rag_analysis || (results.analysisData as any).intelligent_rag_insights || (results.analysisData as any).rag_insights) && (
                <div className="bg-white/5 rounded-2xl p-6 border border-white/20">
                  <h4 className="text-xl font-bold text-white mb-4 flex items-center">
                    <span className="mr-3">🧠</span>
                    AI Knowledge Insights
                    {(results.analysisData as any).dynamic_rag_analysis && (
                      <span className="ml-2 text-xs bg-gradient-to-r from-purple-500 to-blue-500 text-white px-2 py-1 rounded-lg">
                        Dynamic Intelligence
                      </span>
                    )}
                    {(results.analysisData as any).intelligent_rag_insights && !((results.analysisData as any).dynamic_rag_analysis) && (
                      <span className="ml-2 text-xs bg-purple-500/20 text-purple-400 px-2 py-1 rounded-lg">
                        Enhanced Intelligence
                      </span>
                    )}
                  </h4>
                  
                  {(() => {
                    // Priority: dynamic_rag_analysis > intelligent_rag_insights > rag_insights
                    const dynamicRag = (results.analysisData as any).dynamic_rag_analysis;
                    const ragInsights = (results.analysisData as any).intelligent_rag_insights || (results.analysisData as any).rag_insights;
                    
                    // Use dynamic RAG data if available
                    if (dynamicRag && !dynamicRag.error) {
                      const knowledgeSources = dynamicRag?.analysis_metadata?.knowledge_sources_used || 0;
                      const componentsAnalyzed = dynamicRag?.log_context?.components?.length || 0;
                      const errorTypesFound = dynamicRag?.log_context?.error_types?.length || 0;
                      const intelligenceLevel = 'dynamic';
                      const promptGenerated = dynamicRag?.dynamic_prompt ? 'Yes' : 'No';
                      const aiResponseAvailable = dynamicRag?.ai_response ? 'Yes' : 'No';
                      
                      return (
                        <div className="space-y-4">
                          {/* Dynamic Intelligence Dashboard */}
                          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                            <div className="bg-blue-500/10 border border-blue-500/20 rounded-lg p-3">
                              <div className="text-blue-400 text-lg font-bold">{knowledgeSources}</div>
                              <div className="text-blue-300 text-sm">Knowledge Sources</div>
                            </div>
                            <div className="bg-green-500/10 border border-green-500/20 rounded-lg p-3">
                              <div className="text-green-400 text-lg font-bold">{componentsAnalyzed}</div>
                              <div className="text-green-300 text-sm">Components Analyzed</div>
                            </div>
                            <div className="bg-yellow-500/10 border border-yellow-500/20 rounded-lg p-3">
                              <div className="text-yellow-400 text-lg font-bold">{errorTypesFound}</div>
                              <div className="text-yellow-300 text-sm">Error Types Found</div>
                            </div>
                            <div className="bg-purple-500/10 border border-purple-500/20 rounded-lg p-3">
                              <div className="text-purple-400 text-lg font-bold capitalize">{intelligenceLevel}</div>
                              <div className="text-purple-300 text-sm">Intelligence Level</div>
                            </div>
                          </div>

                          {/* Dynamic Analysis Features */}
                          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div className="bg-black/30 rounded-lg p-4">
                              <h5 className="text-lg font-semibold text-white mb-3 flex items-center">
                                <span className="mr-2">🎯</span>
                                Dynamic Prompt Generation
                              </h5>
                              <div className="space-y-2">
                                <div className="flex justify-between">
                                  <span className="text-gray-300">Intelligent Prompt:</span>
                                  <span className={promptGenerated === 'Yes' ? 'text-green-400' : 'text-red-400'}>
                                    {promptGenerated}
                                  </span>
                                </div>
                                <div className="flex justify-between">
                                  <span className="text-gray-300">AI Response:</span>
                                  <span className={aiResponseAvailable === 'Yes' ? 'text-green-400' : 'text-red-400'}>
                                    {aiResponseAvailable}
                                  </span>
                                </div>
                                {dynamicRag?.dynamic_prompt && (
                                  <div className="mt-3 p-3 bg-gray-800/50 rounded text-xs text-gray-300">
                                    <div className="font-medium mb-1">Prompt Preview:</div>
                                    {dynamicRag.dynamic_prompt.substring(0, 200)}...
                                  </div>
                                )}
                              </div>
                            </div>

                            {/* Components & Error Types */}
                            <div className="bg-black/30 rounded-lg p-4">
                              <h5 className="text-lg font-semibold text-white mb-3 flex items-center">
                                <span className="mr-2">🔍</span>
                                Analysis Scope
                              </h5>
                              <div className="space-y-3">
                                {dynamicRag?.log_context?.components && dynamicRag.log_context.components.length > 0 && (
                                  <div>
                                    <div className="text-gray-300 text-sm mb-1">Components:</div>
                                    <div className="flex flex-wrap gap-1">
                                      {dynamicRag.log_context.components.map((component: string, index: number) => (
                                        <span key={index} className="text-xs bg-blue-500/20 text-blue-300 px-2 py-1 rounded">
                                          {component.toUpperCase()}
                                        </span>
                                      ))}
                                    </div>
                                  </div>
                                )}
                                {dynamicRag?.log_context?.error_types && dynamicRag.log_context.error_types.length > 0 && (
                                  <div>
                                    <div className="text-gray-300 text-sm mb-1">Error Types:</div>
                                    <div className="flex flex-wrap gap-1">
                                      {dynamicRag.log_context.error_types.map((errorType: string, index: number) => (
                                        <span key={index} className="text-xs bg-red-500/20 text-red-300 px-2 py-1 rounded">
                                          {errorType.replace('_', ' ').toUpperCase()}
                                        </span>
                                      ))}
                                    </div>
                                  </div>
                                )}
                              </div>
                            </div>
                          </div>

                          {/* Knowledge Sources */}
                          {dynamicRag?.knowledge_sources && dynamicRag.knowledge_sources.length > 0 && (
                            <div className="bg-black/30 rounded-lg p-4">
                              <h5 className="text-lg font-semibold text-white mb-3 flex items-center">
                                <span className="mr-2">📚</span>
                                Expert Knowledge Sources
                              </h5>
                              <div className="space-y-3">
                                {dynamicRag.knowledge_sources.slice(0, 3).map((knowledge: any, index: number) => (
                                  <div key={index} className="border border-gray-600 rounded-lg p-3">
                                    <div className="flex items-center justify-between mb-2">
                                      <span className="text-white font-medium">{knowledge.metadata?.title || 'Expert Knowledge'}</span>
                                      <span className="text-xs bg-green-500/20 text-green-300 px-2 py-1 rounded">
                                        {Math.round((knowledge.relevance_score || 0) * 100)}% relevant
                                      </span>
                                    </div>
                                    <p className="text-gray-300 text-sm">
                                      {knowledge.content ? knowledge.content.substring(0, 150) + '...' : 'No preview available'}
                                    </p>
                                    {knowledge.metadata?.category && (
                                      <span className="text-xs text-blue-400 mt-2 inline-block">
                                        Category: {knowledge.metadata.category}
                                      </span>
                                    )}
                                  </div>
                                ))}
                              </div>
                            </div>
                          )}

                          {/* AI Response Display */}
                          {dynamicRag?.ai_response && (
                            <div className="bg-black/30 rounded-lg p-4">
                              <h5 className="text-lg font-semibold text-white mb-3 flex items-center">
                                <span className="mr-2">🤖</span>
                                AI Analysis & Recommendations
                              </h5>
                              <div className="text-gray-300 text-sm whitespace-pre-wrap max-h-96 overflow-y-auto">
                                {dynamicRag.ai_response.substring(0, 2000)}
                                {dynamicRag.ai_response.length > 2000 && '... (view full analysis in console)'}
                              </div>
                            </div>
                          )}
                        </div>
                      );
                    }
                    
                    // Fallback to standard RAG display
                    const knowledgeSources = ragInsights?.knowledge_sources_used || 0;
                    const patternMatches = ragInsights?.patterns_matched || 0;
                    const intelligenceLevel = ragInsights?.intelligence_level || 'standard';
                    
                    return (
                      <div className="space-y-4">
                        {/* Intelligence Dashboard */}
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                          <div className="bg-blue-500/10 border border-blue-500/20 rounded-lg p-3">
                            <div className="text-blue-400 text-lg font-bold">{knowledgeSources}</div>
                            <div className="text-blue-300 text-sm">Knowledge Sources</div>
                          </div>
                          <div className="bg-green-500/10 border border-green-500/20 rounded-lg p-3">
                            <div className="text-green-400 text-lg font-bold">{patternMatches}</div>
                            <div className="text-green-300 text-sm">Pattern Matches</div>
                          </div>
                          <div className="bg-purple-500/10 border border-purple-500/20 rounded-lg p-3">
                            <div className="text-purple-400 text-lg font-bold capitalize">{intelligenceLevel}</div>
                            <div className="text-purple-300 text-sm">Intelligence Level</div>
                          </div>
                        </div>

                        {/* Pattern Matches */}
                        {ragInsights?.pattern_matches && Array.isArray(ragInsights.pattern_matches) && ragInsights.pattern_matches.length > 0 && (
                          <div className="bg-black/30 rounded-lg p-4">
                            <h5 className="text-lg font-semibold text-white mb-3 flex items-center">
                              <span className="mr-2">🎯</span>
                              Detected Patterns
                            </h5>
                            <div className="space-y-3">
                              {ragInsights.pattern_matches.map((pattern: any, index: number) => (
                                <div key={index} className="border border-gray-600 rounded-lg p-3">
                                  <div className="flex items-center justify-between mb-2">
                                    <span className="text-white font-medium">{pattern.pattern_name}</span>
                                    <span className={`text-xs px-2 py-1 rounded-lg ${
                                      pattern.severity === 'critical' ? 'bg-red-500/20 text-red-400' :
                                      pattern.severity === 'high' ? 'bg-orange-500/20 text-orange-400' :
                                      pattern.severity === 'warning' ? 'bg-yellow-500/20 text-yellow-400' :
                                      'bg-blue-500/20 text-blue-400'
                                    }`}>
                                      {pattern.severity}
                                    </span>
                                  </div>
                                  <p className="text-gray-300 text-sm mb-2">{pattern.description}</p>
                                  {pattern.resolution && (
                                    <p className="text-green-300 text-sm">
                                      <span className="font-medium">Resolution:</span> {pattern.resolution}
                                    </p>
                                  )}
                                  {pattern.match_count && (
                                    <p className="text-gray-400 text-xs mt-1">
                                      Found {pattern.match_count} occurrences
                                    </p>
                                  )}
                                </div>
                              ))}
                            </div>
                          </div>
                        )}

                        {/* Knowledge Sources */}
                        {ragInsights?.relevant_knowledge && Array.isArray(ragInsights.relevant_knowledge) && ragInsights.relevant_knowledge.length > 0 && (
                          <div className="bg-black/30 rounded-lg p-4">
                            <h5 className="text-lg font-semibold text-white mb-3 flex items-center">
                              <span className="mr-2">📚</span>
                              Expert Knowledge Applied
                            </h5>
                            <div className="space-y-3">
                              {ragInsights.relevant_knowledge.slice(0, 3).map((knowledge: any, index: number) => (
                                <div key={index} className="border border-gray-600 rounded-lg p-3">
                                  <div className="flex items-center justify-between mb-2">
                                    <span className="text-white font-medium">{knowledge.metadata?.title || 'Expert Knowledge'}</span>
                                    <span className="text-xs bg-blue-500/20 text-blue-400 px-2 py-1 rounded-lg">
                                      {Math.round((knowledge.relevance_score || 0) * 100)}% relevance
                                    </span>
                                  </div>
                                  <p className="text-gray-300 text-sm">
                                    {knowledge.content?.substring(0, 200)}...
                                  </p>
                                  {knowledge.metadata?.category && (
                                    <span className="inline-block mt-2 text-xs bg-gray-600/50 text-gray-300 px-2 py-1 rounded">
                                      {knowledge.metadata.category}
                                    </span>
                                  )}
                                </div>
                              ))}
                            </div>
                          </div>
                        )}

                        {/* Smart Queries Used */}
                        {ragInsights?.smart_queries_used && Array.isArray(ragInsights.smart_queries_used) && ragInsights.smart_queries_used.length > 0 && (
                          <div className="bg-black/30 rounded-lg p-4">
                            <h5 className="text-lg font-semibold text-white mb-3 flex items-center">
                              <span className="mr-2">🔍</span>
                              Intelligent Queries Applied
                            </h5>
                            <div className="flex flex-wrap gap-2">
                              {ragInsights.smart_queries_used.map((query: string, index: number) => (
                                <span key={index} className="text-xs bg-indigo-500/20 text-indigo-300 px-3 py-1 rounded-full">
                                  {query.length > 50 ? query.substring(0, 50) + '...' : query}
                                </span>
                              ))}
                            </div>
                          </div>
                        )}
                      </div>
                    );
                  })()}
                </div>
              )}
            </div>
          )}

          <div className="flex space-x-4">
            <button 
              onClick={() => {
                if (results.sessionId && backendStatus === 'connected') {
                  // Export from backend via API route
                  window.open(`${API_BASE}/export/${results.sessionId}`, '_blank');
                } else {
                  // Export current results as JSON
                  const dataStr = JSON.stringify(results, null, 2);
                  const dataBlob = new Blob([dataStr], {type: 'application/json'});
                  const url = URL.createObjectURL(dataBlob);
                  const link = document.createElement('a');
                  link.href = url;
                  link.download = `analysis-results-${Date.now()}.json`;
                  link.click();
                }
              }}
              className="flex-1 bg-gradient-to-r from-green-500 to-green-600 text-white py-3 rounded-xl hover:from-green-600 hover:to-green-700 transition-all duration-300 transform hover:scale-105"
            >
              Export Report
            </button>
            <button 
              onClick={() => {
                if (navigator.share) {
                  navigator.share({
                    title: 'Deep Security Analysis Results',
                    text: results.summary,
                    url: window.location.href
                  });
                } else {
                  navigator.clipboard.writeText(results.summary);
                  alert('Results copied to clipboard!');
                }
              }}
              className="flex-1 bg-gradient-to-r from-blue-500 to-blue-600 text-white py-3 rounded-xl hover:from-blue-600 hover:to-blue-700 transition-all duration-300 transform hover:scale-105"
            >
              Share Results
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
