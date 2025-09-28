'use client';

import { useState, useEffect, useCallback, useRef, useMemo } from 'react';
import { useBackend } from '@/contexts/BackendContext';
import AnalysisDataParser from './AnalysisDataParser';

interface AnalysisResult {
  type: string;
  analysisType?: string; // Original analyzer type ID
  summary: string;
  details: string[];
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
  progress_percentage?: number;
  progress_message?: string;
  analysis_stage?: string;
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

interface CSDAIv2IntegrationProps {
  initialAnalyzer?: string;
  caseContext?: {
    caseTitle?: string;
    description?: string;
    product?: string;
    severity?: string;
    attachments?: {
      name: string;
      size: number;
      type: string;
    }[];
    extractedFiles?: {
      name: string;
      size: number;
    }[];
    autoUploaded?: boolean;
    uploadResult?: Record<string, unknown>;
    extractionError?: string;
    requiredFiles?: string[];
    fromPortal?: boolean;
    requiresReupload?: boolean;
  };
}

export default function CSDAIv2Integration({ initialAnalyzer, caseContext }: CSDAIv2IntegrationProps = {}) {
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [uploadedFiles, setUploadedFiles] = useState<File[]>([]);
  const [analysisType, setAnalysisType] = useState(initialAnalyzer || 'amsp_logs');
  const [results, setResults] = useState<AnalysisResult | null>(null);
  const [isDragOver, setIsDragOver] = useState(false);
  const [sessionId, setSessionId] = useState<string>('');
  
  // Intelligent extraction state
  const [extractionInfo, setExtractionInfo] = useState<{
    sessionId: string;
    filesExtracted: number;
    filesInfo: Array<{name: string; size: number; required: boolean; zipPath: string}>;
    extractionSummary?: {
      totalFilesInZip: number;
      filesMatched: number;
      requiredFilesFound: number;
      missingRequired: string[];
      description: string;
    };
  } | null>(null);
  
  const caseInfo = caseContext;
  
  // Use global backend status from context
  const { backendStatus } = useBackend();
  
  // Progress bar state variables
  const [overallProgress, setOverallProgress] = useState(0);
  const [currentStageIndex, setCurrentStageIndex] = useState(0);
  const [logEntries, setLogEntries] = useState<LogEntry[]>([]);
  
  // Auto-scroll state management
  const [autoScrollEnabled, setAutoScrollEnabled] = useState(true);
  const [userScrollTimer, setUserScrollTimer] = useState<NodeJS.Timeout | null>(null);
  const logContainerRef = useRef<HTMLDivElement>(null);
  
  // New analysis confirmation modal state
  const [showNewAnalysisModal, setShowNewAnalysisModal] = useState(false);
  
  // Analyzer availability state
  const [analyzerAvailability, setAnalyzerAvailability] = useState<Record<string, { status: string; health: string }>>({});
  const [previousAnalyzerAvailability, setPreviousAnalyzerAvailability] = useState<Record<string, { status: string; health: string }>>({});
  
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
    
    return () => {
      isComponentMountedRef.current = false;
    };
  }, []);

  // Handle StrictMode component lifecycle
  useEffect(() => {
    // Single check after mounting to handle StrictMode
    const timeoutId = setTimeout(() => {
      if (!isComponentMountedRef.current) {
        isComponentMountedRef.current = true;
      }
    }, 1000);
    
    return () => {
      clearTimeout(timeoutId);
    };
  }, []);

  // Add CSS styles for CSDAIv2 HTML content and enhanced progress animations
  useEffect(() => {
    const style = document.createElement('style');
    style.textContent = `
      .csdaiv2-results {
        font-family: 'Inter', 'Segoe UI', 'Roboto', sans-serif !important;
      }
      
      /* Enhanced Progress Bar Animations */
      @keyframes shimmer {
        0% { transform: translateX(-100%); }
        100% { transform: translateX(200%); }
      }
      
      @keyframes pulse-glow {
        0%, 100% { box-shadow: 0 0 5px rgba(59, 130, 246, 0.5); }
        50% { box-shadow: 0 0 20px rgba(59, 130, 246, 0.8), 0 0 30px rgba(59, 130, 246, 0.4); }
      }
      
      @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
      }
      
      @keyframes bounce-in {
        0% { transform: scale(0.3) rotate(45deg); opacity: 0; }
        50% { transform: scale(1.05) rotate(45deg); }
        70% { transform: scale(0.9) rotate(45deg); }
        100% { transform: scale(1) rotate(45deg); opacity: 1; }
      }
      
      .animate-shimmer {
        animation: shimmer 2s infinite;
      }
      
      .animate-pulse-glow {
        animation: pulse-glow 2s infinite;
      }
      
      .animate-fadeIn {
        animation: fadeIn 0.5s ease-out;
      }
      
      .animate-bounce-in {
        animation: bounce-in 0.6s cubic-bezier(0.68, -0.55, 0.265, 1.55);
      }
      
      /* Stage Cards Enhanced Animations */
      .stage-card.active {
        animation: pulse-glow 3s infinite;
      }
      
      .stage-card.completed .stage-icon {
        animation: bounce-in 0.6s ease-out;
      }
      
      /* Progress Bar Enhancements */
      .main-progress-bar .h-full {
        transition: width 0.8s cubic-bezier(0.4, 0, 0.2, 1);
      }
      
      /* Log Entry Animations */
      .log-entry {
        animation: fadeIn 0.3s ease-out;
      }
      
      .log-entry.success {
        border-left: 3px solid #10b981;
        padding-left: 8px;
        background: rgba(16, 185, 129, 0.1);
        margin: 2px 0;
        border-radius: 4px;
      }
      
      .log-entry.warning {
        border-left: 3px solid #f59e0b;
        padding-left: 8px;
        background: rgba(245, 158, 11, 0.1);
        margin: 2px 0;
        border-radius: 4px;
      }
      
      .log-entry.error {
        border-left: 3px solid #ef4444;
        padding-left: 8px;
        background: rgba(239, 68, 68, 0.1);
        margin: 2px 0;
        border-radius: 4px;
      }
      
      /* Smooth scroll for log container */
      .scroll-smooth {
        scroll-behavior: smooth;
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
      
      /* Enhanced scrollbar for analysis log */
      #analysis-log::-webkit-scrollbar {
        width: 8px;
      }
      
      #analysis-log::-webkit-scrollbar-track {
        background: rgba(55, 65, 81, 0.3);
        border-radius: 4px;
      }
      
      #analysis-log::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #3b82f6, #1d4ed8);
        border-radius: 4px;
        transition: background 0.3s ease;
      }
      
      #analysis-log::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(135deg, #1d4ed8, #1e40af);
      }
      
      /* Smooth scroll behavior */
      .scroll-smooth {
        scroll-behavior: smooth;
      }
      
      /* New log entry highlight effect */
      .log-entry {
        transition: background-color 0.3s ease;
      }
      
      .log-entry.new-entry {
        background-color: rgba(59, 130, 246, 0.1);
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
    
    // Auto-scroll if enabled
    if (autoScrollEnabled) {
      setTimeout(() => {
        const logContainer = logContainerRef.current;
        if (logContainer) {
          logContainer.scrollTo({
            top: logContainer.scrollHeight,
            behavior: 'smooth'
          });
        }
      }, 100);
    }
  }, [autoScrollEnabled]);

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
  
  // Auto-scroll setup function
  const setupAutoScroll = useCallback(() => {
    const logContainer = logContainerRef.current;
    if (!logContainer) return;
    
    const handleScroll = () => {
      const isAtBottom = logContainer.scrollTop + logContainer.clientHeight >= logContainer.scrollHeight - 10;
      
      if (!isAtBottom) {
        // User scrolled up, disable auto-scroll temporarily
        setAutoScrollEnabled(false);
        
        // Clear existing timer
        if (userScrollTimer) {
          clearTimeout(userScrollTimer);
        }
        
        // Re-enable auto-scroll after 3 seconds of no scrolling
        const timer = setTimeout(() => {
          setAutoScrollEnabled(true);
        }, 3000);
        
        setUserScrollTimer(timer);
      } else {
        // User is at bottom, re-enable auto-scroll
        setAutoScrollEnabled(true);
      }
    };
    
    logContainer.addEventListener('scroll', handleScroll);
    
    return () => {
      logContainer.removeEventListener('scroll', handleScroll);
    };
  }, [userScrollTimer, setAutoScrollEnabled, setUserScrollTimer]);
  
  // Setup auto-scroll when component mounts
  useEffect(() => {
    const cleanup = setupAutoScroll();
    return cleanup;
  }, [setupAutoScroll]);

  // Handle auto-uploaded files from portal
  useEffect(() => {
    if (caseContext?.autoUploaded && caseContext.extractedFiles?.length) {
      // Create File objects from the extracted file info with proper size information
      // Note: We can't reconstruct the actual file content here since it's already uploaded to backend
      // Instead, we'll show a status message indicating files were auto-uploaded with correct sizes
      const mockFiles = caseContext.extractedFiles.map(fileInfo => {
        // Create a proper File-like object with the correct size
        const mockFile = new File([''], fileInfo.name, { type: 'text/plain' });
        // Override the size property to match the actual extracted file size
        Object.defineProperty(mockFile, 'size', {
          value: fileInfo.size || 0,
          writable: false
        });
        return mockFile;
      });
      
      // Set the files in state to show them in UI
      setUploadedFiles(mockFiles);
      
      // If there's a session ID from the upload result, use it
      if (caseContext.uploadResult?.session_id && typeof caseContext.uploadResult.session_id === 'string') {
        setSessionId(caseContext.uploadResult.session_id);
      }
    } else if (caseContext?.extractionError) {
      // Handle extraction errors silently for production
      if (caseContext.requiredFiles) {
        // Required files information available for debugging if needed
      }
    }
  }, [caseContext]);
  
  const API_BASE = '/api/csdai'; // Use Next.js API routes instead of direct backend calls

  // Analyzer descriptions for educational purposes
  const analyzerDescriptions = {
    'ds_agent_offline': {
      title: 'DS Agent Offline Analyzer',
      description: 'Specialized analyzer for diagnosing Deep Security Agent offline issues. Identifies root causes when agents appear offline in the Deep Security Manager and provides targeted resolution steps.',
      features: ['Offline Cause Detection', 'Communication Analysis', 'Service Status Diagnostics', 'Network Troubleshooting'],
      icon: '🔴',
      estimatedTime: '1-3 minutes'
    },
    'amsp_logs': {
      title: 'AMSP (Anti-Malware Scan Performance)',
      description: 'Advanced analysis of anti-malware scanning performance and efficiency. Provides insights into scan patterns, false positives, and performance optimization recommendations.',
      features: ['Scan Performance Metrics', 'False Positive Analysis', 'Pattern Recognition', 'Optimization Insights'],
      icon: '🛡️',
      estimatedTime: '2-4 minutes'
    },
    'av_conflicts': {
      title: 'Anti-Virus Conflict Analyzer', 
      description: 'Detects conflicts between Deep Security and other anti-virus solutions. Identifies performance impacts, compatibility issues, and provides recommendations for optimal configuration.',
      features: ['Conflict Detection', 'Performance Impact Analysis', 'Configuration Recommendations', 'Compatibility Assessment'],
      icon: '⚔️',
      estimatedTime: '1-2 minutes'
    },
    'resource_analysis': {
      title: 'Resource Analysis Engine',
      description: 'Comprehensive analysis of system resource usage including CPU, memory, disk I/O, and network patterns. Identifies bottlenecks and optimization opportunities.',
      features: ['CPU Usage Analysis', 'Memory Pattern Detection', 'I/O Performance Review', 'Resource Optimization'],
      icon: '📊',
      estimatedTime: '3-4 minutes'
    },
    'diagnostic_package': {
      title: 'Diagnostic Package Analyzer',
      description: 'Comprehensive analysis of complete diagnostic packages containing multiple log files. Provides cross-correlation analysis, ML-enhanced insights, and executive summaries for complex multi-component issues.',
      features: ['Multi-Log Correlation', 'Advanced Component Analysis', 'ML Pattern Recognition', 'Executive Summary Generation', 'ZIP Package Processing'],
      icon: '📦',
      estimatedTime: '5-8 minutes'
    }
  };

  const uploadFilesToBackend = useCallback(async (files: File[]): Promise<string | null> => {
    // Check if these are mock files from auto-upload (they would have size but no actual content)
    const isAutoUploaded = caseContext?.autoUploaded && sessionId;
    if (isAutoUploaded) {
      // Don't try to upload mock files, just return the existing session ID
      console.log('📄 Skipping upload for auto-uploaded files, using existing session:', sessionId);
      return sessionId;
    }

    const formData = new FormData();
    files.forEach((file, index) => {
      formData.append(`file_${index}`, file);
    });
    formData.append('analysis_type', analysisType);

    try {
      const response = await fetch(`${API_BASE}/upload`, {
        method: 'POST',
        body: formData,
      });
      
      if (response.ok) {
        const data: BackendResponse = await response.json();
        return data.session_id || null;
      } else {
        const errorData = await response.text();
        console.error('❌ Upload failed with status:', response.status, errorData);
      }
    } catch (error) {
      console.error('❌ Upload failed:', error);
    }
    return null;
  }, [analysisType, caseContext?.autoUploaded, sessionId]);

  const pollAnalysisStatus = useCallback(async (sessionId: string): Promise<BackendResponse | null> => {
    try {
      console.log(`🔍 Polling status for session: ${sessionId} at ${API_BASE}/status/${sessionId}`);
      const response = await fetch(`${API_BASE}/status/${sessionId}`);
      if (response.ok) {
        const data: BackendResponse = await response.json();
        console.log(`✅ Status response:`, data);
        return data;
      } else {
        console.error('❌ Status check failed with status:', response.status);
        const errorText = await response.text();
        console.error('❌ Error details:', errorText);
      }
    } catch (error) {
      console.error('❌ Status check failed:', error);
    }
    return null;
  }, []);

  const getAnalysisResults = useCallback(async (sessionId: string): Promise<Record<string, unknown> | null> => {
    try {
      console.log(`🔄 Fetching analysis results for session ${sessionId}`);
      
      const response = await fetch(`${API_BASE}/results/${sessionId}`);
      if (response.ok) {
        const data = await response.json();
        console.log('✅ Analysis results fetched successfully');
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

  // Intelligent file extraction and analysis functions
  const extractAndFilterFiles = useCallback(async (zipFile: File, analyzerType: string): Promise<{
    success: boolean;
    sessionId?: string;
    filesExtracted?: number;
    filesInfo?: Array<{name: string; size: number; required: boolean; zipPath: string}>;
    extractionSummary?: {
      totalFilesInZip: number;
      filesMatched: number;
      requiredFilesFound: number;
      missingRequired: string[];
      description: string;
    };
    error?: string;
  }> => {
    console.log(`🎯 Starting intelligent extraction for analyzer: ${analyzerType}`);
    
    const formData = new FormData();
    formData.append('file_0', zipFile);
    formData.append('analyzer_type', analyzerType);

    try {
      const response = await fetch(`${API_BASE}/extract-and-filter`, {
        method: 'POST',
        body: formData,
      });
      
      const data = await response.json();
      
      if (response.ok && data.success) {
        console.log(`✅ Extraction successful: ${data.files_extracted} files found`);
        return {
          success: true,
          sessionId: data.session_id,
          filesExtracted: data.files_extracted,
          filesInfo: data.files_info,
          extractionSummary: data.extraction_summary
        };
      } else {
        console.error('❌ Extraction failed:', data.error);
        return {
          success: false,
          error: data.error || 'Unknown extraction error'
        };
      }
    } catch (error) {
      console.error('❌ Extraction request failed:', error);
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Network error during extraction'
      };
    }
  }, []);

  const analyzeExtractedFiles = useCallback(async (sessionId: string): Promise<{
    success: boolean;
    status?: string;
    analysisType?: string;
    filesProcessed?: number;
    error?: string;
  }> => {
    console.log(`🚀 Starting analysis for extracted session: ${sessionId}`);
    
    try {
      const response = await fetch(`${API_BASE}/analyze-extracted/${sessionId}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });
      
      const data = await response.json();
      
      if (response.ok && data.success) {
        console.log(`✅ Analysis started successfully: ${data.analysis_type}`);
        return {
          success: true,
          status: data.status,
          analysisType: data.analysis_type,
          filesProcessed: data.files_processed
        };
      } else {
        console.error('❌ Analysis start failed:', data.error);
        return {
          success: false,
          error: data.error || 'Unknown analysis error'
        };
      }
    } catch (error) {
      console.error('❌ Analysis request failed:', error);
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Network error during analysis'
      };
    }
  }, []);

  // New Analysis function - Clean session and reset state
  const handleNewAnalysis = useCallback(async () => {
    try {
      // Clean up current session if exists
      if (sessionId && backendStatus === 'connected') {
        try {
          await fetch(`${API_BASE}/cleanup/${sessionId}`, {
            method: 'DELETE',
            headers: {
              'Content-Type': 'application/json',
            },
          });
          addLogEntry(`🧹 Session ${sessionId.slice(-8)} cleaned up successfully`, 'success');
        } catch (cleanupError) {
          console.warn('Session cleanup failed:', cleanupError);
          addLogEntry('⚠️ Session cleanup failed, but continuing with new analysis', 'warning');
        }
      }

      // Reset all state variables to initial values
      setIsAnalyzing(false);
      setUploadedFiles([]);
      setAnalysisType(initialAnalyzer || 'amsp_logs');
      setResults(null);
      setIsDragOver(false);
      setSessionId('');
      setExtractionInfo(null);
      
      // Reset progress bar and logs
      resetProgressBar();
      
      // Add success message
      addLogEntry('🎯 Ready for new analysis! Upload files to begin.', 'success');
      
    } catch (error) {
      console.error('Error during new analysis setup:', error);
      addLogEntry('❌ Error preparing new analysis, but state has been reset', 'error');
      
      // Reset state anyway
      setIsAnalyzing(false);
      setUploadedFiles([]);
      setAnalysisType(initialAnalyzer || 'amsp_logs');
      setResults(null);
      setIsDragOver(false);
      setSessionId('');
      setExtractionInfo(null);
      resetProgressBar();
    }
  }, [sessionId, backendStatus, API_BASE, addLogEntry, resetProgressBar, initialAnalyzer]);

  // Fetch analyzer availability from admin API
  const fetchAnalyzerAvailability = useCallback(async () => {
    if (backendStatus !== 'connected') return;
    
    try {
      const response = await fetch('http://localhost:5003/admin/analyzers');
      if (response.ok) {
        const data = await response.json();
        const availability: Record<string, { status: string; health: string }> = {};
        
        // Map analyzer IDs to analysis type IDs
        const analyzerMapping = {
          'amsp_analyzer': 'amsp_logs',
          'conflict_analyzer': 'av_conflicts', 
          'ds_agent_offline_analyzer': 'ds_agent_offline',
          'resource_analyzer': 'resource_analysis',
          'diagnostic_package_analyzer': 'diagnostic_package'
        };
        
        if (data.success && data.data) {
          data.data.forEach((analyzer: { id: string; status: string; health: string }) => {
            const analysisTypeId = analyzerMapping[analyzer.id as keyof typeof analyzerMapping];
            if (analysisTypeId) {
              availability[analysisTypeId] = {
                status: analyzer.status,
                health: analyzer.health
              };
            }
          });
        }
        
        // Check for changes and notify user
        setAnalyzerAvailability(prev => {
          // Detect changes in analyzer status
          Object.keys(availability).forEach(analyzerId => {
            const newStatus = availability[analyzerId]?.status;
            const oldStatus = prev[analyzerId]?.status;
            
            if (oldStatus && newStatus !== oldStatus) {
              if (newStatus === 'disabled') {
                addLogEntry(`⚠️ Analyzer "${analyzerId}" has been disabled by admin`, 'warning');
                
                // If currently selected analyzer becomes disabled, show notification
                if (analysisType === analyzerId) {
                  addLogEntry(`🚫 Currently selected analyzer "${analyzerId}" is now unavailable`, 'error');
                }
              } else if (newStatus === 'enabled') {
                addLogEntry(`✅ Analyzer "${analyzerId}" has been re-enabled by admin`, 'success');
              }
            }
          });
          
          return availability;
        });
        
        console.log('🔄 Updated analyzer availability:', availability);
      }
    } catch (error) {
      console.warn('Failed to fetch analyzer availability:', error);
    }
  }, [backendStatus, addLogEntry, analysisType]);

  // Real-time analyzer availability polling
  useEffect(() => {
    if (backendStatus !== 'connected') return;

    // Initial fetch
    fetchAnalyzerAvailability();

    // Set up polling every 5 seconds for real-time admin changes
    const availabilityPollingInterval = setInterval(() => {
      fetchAnalyzerAvailability();
    }, 5000);

    console.log('🔄 Started real-time analyzer availability polling');

    return () => {
      clearInterval(availabilityPollingInterval);
      console.log('⏹️ Stopped analyzer availability polling');
    };
  }, [fetchAnalyzerAvailability, backendStatus]);

  // File upload and processing handlers

  const analysisTypes = [
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
      id: 'ds_agent_offline', 
      name: 'DS Agent Offline', 
      description: 'Diagnose Deep Security Agent offline issues',
      fullDescription: 'Deep Security Agent appears offline in the manager or has intermittent connectivity issues.',
      icon: '🔴',
      severity: 'critical',
      estimatedTime: '10-30 minutes',
      issueType: 'Connectivity Issue',
      commonCauses: [
        'Agent service not running',
        'Network communication failures',
        'Manager connectivity issues',
        'Port blocking or firewall rules'
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
    },
    { 
      id: 'diagnostic_package', 
      name: 'Diagnostic Package', 
      description: 'Comprehensive diagnostic package analysis',
      fullDescription: 'Analyze complete diagnostic packages containing multiple log files with cross-correlation analysis.',
      icon: '📦',
      severity: 'high',
      estimatedTime: '60-180 minutes',
      issueType: 'Comprehensive Analysis',
      commonCauses: [
        'Multiple component failures',
        'Complex system issues',
        'Performance degradation',
        'Service correlation problems'
      ]
    }
  ];

  const handleFileUpload = async (files: FileList | null) => {
    console.log(`🚀 DEBUG: handleFileUpload called with files:`, files);
    console.log(`🎯 DEBUG: Current analysisType:`, analysisType);
    
    if (!files) {
      console.log(`❌ DEBUG: No files provided, returning early`);
      return;
    }
    
    const validFiles = Array.from(files).filter(file => {
      // ALL analyzers now accept ZIP files for intelligent extraction
      const validExtensions = ['.log', '.txt', '.xml', '.csv', '.zip'];
      const maxFileSize = 100 * 1024 * 1024; // 100MB limit for all analyzers to support ZIP files
      
      const fileExtension = '.' + file.name.split('.').pop()?.toLowerCase();
      const isValidExtension = validExtensions.includes(fileExtension);
      const isValidSize = file.size <= maxFileSize;
      
      return isValidExtension && isValidSize;
    });

    // Check if we have ZIP files that could benefit from intelligent extraction
    const zipFiles = validFiles.filter(file => file.name.toLowerCase().endsWith('.zip'));
    
    // CRITICAL FIX: Always use intelligent extraction for ZIP files except when explicitly using diagnostic_package
    // This ensures Resource Analyzer and other specific analyzers work correctly with ZIP files
    const shouldUseIntelligentExtraction = zipFiles.length > 0 && analysisType !== 'diagnostic_package';
      
    console.log(`🔍 DEBUG: ZIP files found: ${zipFiles.length}, analysisType: ${analysisType}, shouldUseIntelligentExtraction: ${shouldUseIntelligentExtraction}`);
    
    if (shouldUseIntelligentExtraction) {
      console.log(`🎯 Detected ZIP files with ${analysisType} analyzer - attempting intelligent extraction`);
      
      // For each ZIP file, try intelligent extraction
      for (const zipFile of zipFiles) {
        try {
          const extractionResult = await extractAndFilterFiles(zipFile, analysisType);
          
          if (extractionResult.success && extractionResult.sessionId) {
            console.log(`✅ Intelligent extraction completed: ${extractionResult.filesExtracted} files filtered for ${analysisType}`);
            
            // Store extraction information for later use (simplified without recommendations)
            setExtractionInfo({
              sessionId: extractionResult.sessionId,
              filesExtracted: extractionResult.filesExtracted || 0,
              filesInfo: extractionResult.filesInfo || [],
              extractionSummary: extractionResult.extractionSummary
            });
            
            console.log(`📋 Extracted files:`, extractionResult.filesInfo);
            
            // Replace ZIP file with extracted files info in the display
            const extractedFileDisplay = extractionResult.filesInfo?.map(fileInfo => {
              console.log(`📄 Creating display file: ${fileInfo.name} (${fileInfo.size} bytes)`);
              // Create a mock File object for display purposes
              const mockFile = new File([''], fileInfo.name, { type: 'text/plain' });
              Object.defineProperty(mockFile, 'size', { value: fileInfo.size });
              return mockFile;
            }) || [];
            
            console.log(`📂 Setting ${extractedFileDisplay.length} extracted files for display`);
            
            setUploadedFiles(prev => {
              // Remove the ZIP file and add extracted files
              const withoutZip = prev.filter(f => f !== zipFile);
              const newFiles = [...withoutZip, ...extractedFileDisplay];
              console.log(`📊 Total files after extraction: ${newFiles.length}`);
              return newFiles;
            });
            
            return; // Successfully processed ZIP file
          } else {
            console.log(`⚠️ Intelligent extraction failed for ${zipFile.name}: ${extractionResult.error}`);
            
            // Check if this is a missing required files error
            if (extractionResult.error?.includes('Missing required files')) {
              alert(`❌ INTELLIGENT EXTRACTION ERROR

Unable to extract required files for ${analysisType} analysis from ${zipFile.name}.

${extractionResult.error}

SUGGESTION:
Try using the Diagnostic Package analyzer for comprehensive analysis, or ensure your ZIP file contains the necessary log files for this specific analyzer.`);
              
              setIsAnalyzing(false);
              return; // Don't continue with this file
            }
            
            // For other extraction errors, fall back to regular file handling
            console.log(`🔄 Falling back to regular file handling for ${zipFile.name}`);
          }
        } catch (error) {
          console.error(`❌ Error during intelligent extraction for ${zipFile.name}:`, error);
          // Fall back to regular file handling
        }
      }
    }

    // Regular file handling (for non-ZIP files or if extraction failed)
    setUploadedFiles(prev => {
      const newFiles = [...prev, ...validFiles];
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

  // Resource Analyzer file validation and warning system
  const validateResourceAnalyzerFiles = (): { isValid: boolean; shouldProceed: boolean } => {
    if (analysisType !== 'resource' && analysisType !== 'resource_analysis') {
      return { isValid: true, shouldProceed: true };
    }

    const hasXmlFile = uploadedFiles.some(file => 
      file.name.toLowerCase().includes('runningprocess') && 
      file.name.toLowerCase().endsWith('.xml')
    );
    
    const hasTxtFile = uploadedFiles.some(file => 
      file.name.toLowerCase().includes('topnbusyprocess') && 
      file.name.toLowerCase().endsWith('.txt')
    );

    // If both files are present, no warning needed
    if (hasXmlFile && hasTxtFile) {
      return { isValid: true, shouldProceed: true };
    }

    // Single file scenarios - show warning dialog
    let warningMessage = '';
    
    if (hasXmlFile && !hasTxtFile) {
      warningMessage = `⚠️ INCOMPLETE RESOURCE ANALYSIS

You have uploaded only the RunningProcesses.xml file.

LIMITATIONS OF XML-ONLY ANALYSIS:
• No scan count data available
• Cannot prioritize processes by performance impact
• Limited optimization recommendations
• No quantitative resource usage metrics

MISSING FILE:
• TopNBusyProcess.txt (contains scan count and performance data)

RECOMMENDATION:
For comprehensive resource conflict analysis, please upload both RunningProcesses.xml AND TopNBusyProcess.txt files.

Do you want to proceed with limited analysis anyway?`;
    } else if (hasTxtFile && !hasXmlFile) {
      warningMessage = `⚠️ INCOMPLETE RESOURCE ANALYSIS

You have uploaded only the TopNBusyProcess.txt file.

LIMITATIONS OF TXT-ONLY ANALYSIS:
• No correlation with running processes
• Cannot verify process legitimacy
• Limited security context
• No process enumeration data

MISSING FILE:
• RunningProcesses.xml (contains running process information)

RECOMMENDATION:
For comprehensive resource conflict analysis, please upload both RunningProcesses.xml AND TopNBusyProcess.txt files.

Do you want to proceed with limited analysis anyway?`;
    } else {
      // No relevant files found
      alert(`❌ RESOURCE ANALYZER FILE ERROR

No valid Resource Analyzer files detected.

REQUIRED FILES:
• RunningProcesses.xml (running processes data)
• TopNBusyProcess.txt (scan count and performance data)

Please upload at least one of these files to proceed with Resource Analysis.`);
      return { isValid: false, shouldProceed: false };
    }

    // Show confirmation dialog for single-file analysis
    const userConfirmed = confirm(warningMessage);
    return { isValid: true, shouldProceed: userConfirmed };
  };

  const startAnalysis = async () => {
    // Force ensure component is mounted before starting
    if (!isComponentMountedRef.current) {
      isComponentMountedRef.current = true;
    }

    if (uploadedFiles.length === 0) {
      addLogEntry('Please upload at least one file before starting analysis.', 'error');
      return;
    }

    // Check if selected analyzer is available
    const availability = analyzerAvailability[analysisType];
    if (availability?.status === 'disabled') {
      addLogEntry(`Cannot start analysis: ${analysisType} analyzer is currently disabled. Please select a different analyzer or contact the administrator.`, 'error');
      return;
    }

    // Verify component is still mounted
    if (!isComponentMountedRef.current) {
      return;
    }

    // Check if backend is connected before starting
    if (backendStatus !== 'connected') {
      addLogEntry('CSDAIv2 backend is not available. Please ensure the backend is running on localhost:5003', 'error');
      return;
    }

    // Validate Resource Analyzer files and show warning if needed
    const validation = validateResourceAnalyzerFiles();
    if (!validation.isValid || !validation.shouldProceed) {
      // User cancelled or files are invalid
      if (!validation.isValid) {
        addLogEntry('Please upload valid Resource Analyzer files to proceed.', 'error');
      } else {
        addLogEntry('Analysis cancelled by user due to incomplete file set.', 'warning');
      }
      return;
    }

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
      let currentSessionId: string | null;
      
      // Check if we have extraction info from intelligent file processing
      if (extractionInfo && extractionInfo.sessionId) {
        console.log('🎯 Using intelligent extraction session:', extractionInfo.sessionId);
        addLogEntry('Using intelligently extracted files...', 'info');
        
        // Start analysis using extracted files directly (no analyzer switching)
        addLogEntry('Starting analysis with extracted files...', 'info');
        const analysisStartResult = await analyzeExtractedFiles(extractionInfo.sessionId);
        
        if (!analysisStartResult.success) {
          throw new Error(`Analysis start failed: ${analysisStartResult.error}`);
        }
        
        currentSessionId = extractionInfo.sessionId;
        if (isComponentMountedRef.current) {
          setSessionId(currentSessionId);
          addLogEntry(`Analysis started successfully for ${analysisStartResult.filesProcessed} files`, 'success');
        }
        
        // Continue with polling logic for extracted files analysis
        let analysisComplete = false;
        let currentStep = 2;
        let pollAttempts = 0;
        const maxPollAttempts = 30;

        console.log(`🔄 Starting polling for session: ${currentSessionId}, maxAttempts: ${maxPollAttempts}`);

        while (!analysisComplete && currentStep <= 5 && pollAttempts < maxPollAttempts && isComponentMountedRef.current) {
          await new Promise(resolve => setTimeout(resolve, 2000));
          pollAttempts++;
          
          console.log(`📊 Poll attempt ${pollAttempts}/${maxPollAttempts} for session ${currentSessionId}`);
          
          if (!isComponentMountedRef.current) {
            console.log('❌ Component unmounted, stopping polling');
            break;
          }
          
          const status = await pollAnalysisStatus(currentSessionId);
          console.log(`📈 Poll result for attempt ${pollAttempts}:`, status);
          
          if (status) {
            if (status.progress_percentage && status.progress_percentage > overallProgress) {
              setOverallProgress(Math.min(status.progress_percentage, 95));
              console.log(`📊 Progress updated to: ${status.progress_percentage}%`);
            }
            
            if (status.progress_message && status.progress_message !== 'Processing...') {
              addLogEntry(status.progress_message, 'info');
            }
            
            if (status.analysis_stage && status.analysis_stage !== 'Unknown') {
              addLogEntry(`Stage: ${status.analysis_stage}`, 'info');
            }
          }
          
          if (status?.analysis_complete) {
            console.log('✅ Analysis marked as complete, ending polling');
            analysisComplete = true;
            setOverallProgress(100);
            addLogEntry('Intelligent analysis completed!', 'success');
            break;
          }
          
          if (currentStep <= 5) {
            currentStep++;
            activateStage(currentStep - 1);
          }
        }

        console.log(`🏁 Polling ended: complete=${analysisComplete}, step=${currentStep}, attempts=${pollAttempts}, mounted=${isComponentMountedRef.current}`);
        
        // Fetch and display results after successful analysis
        if (analysisComplete && isComponentMountedRef.current) {
          console.log('🎯 Fetching analysis results...');
          const analysisResults = await getAnalysisResults(currentSessionId);
          if (analysisResults && isComponentMountedRef.current) {
            console.log('✅ Analysis results received, processing...');
            const processedResults = formatBackendResults(analysisResults, analysisType);
            setResults(processedResults);
            addLogEntry('Analysis completed successfully!', 'success');
            setOverallProgress(100);
            setIsAnalyzing(false); // Stop the analyzing state
          } else {
            console.error('❌ Failed to fetch analysis results');
            addLogEntry('Warning: Analysis completed but results could not be retrieved', 'warning');
            setIsAnalyzing(false); // Stop analyzing even on error
          }
        } else if (pollAttempts >= maxPollAttempts) {
          console.error('❌ Polling timed out');
          addLogEntry('Analysis timed out - please try again', 'error');
          setIsAnalyzing(false); // Stop analyzing on timeout
        }
        
      } else {
        // Regular file upload process
        addLogEntry('Preparing analysis...', 'info');
        currentSessionId = await uploadFilesToBackend(uploadedFiles);
        if (!currentSessionId) {
          throw new Error('File upload failed or session not available');
        }

        if (isComponentMountedRef.current) {
          setSessionId(currentSessionId);
          addLogEntry(`Using session: ${currentSessionId}`, 'info');
        }

        // Poll for analysis completion with improved real-time logic
        let analysisComplete = false;
        let currentStep = 2;
        let pollAttempts = 0;
        let consecutiveNoProgress = 0;
        const maxPollAttempts = 60; // Maximum 2 minutes of polling
        const maxNoProgressAttempts = 10; // Max attempts without progress before fallback

        while (!analysisComplete && currentStep <= 5 && pollAttempts < maxPollAttempts && isComponentMountedRef.current) {
          await new Promise(resolve => setTimeout(resolve, 2000));
          pollAttempts++;
          
          if (!isComponentMountedRef.current) break; // Stop polling if component unmounted
          
          const status = await pollAnalysisStatus(currentSessionId);
          
          // Handle backend progress updates
          if (status) {
            // Update progress from backend if available and higher than current
            if (status.progress_percentage && status.progress_percentage > overallProgress) {
              setOverallProgress(Math.min(status.progress_percentage, 95));
              consecutiveNoProgress = 0; // Reset no-progress counter
              addLogEntry(`Progress: ${status.progress_percentage}%`, 'info');
            } else if (status.progress_percentage === overallProgress) {
              consecutiveNoProgress++;
            }
            
            // Add backend progress messages to log (avoid duplicates with simple check)
            if (status.progress_message && 
                status.progress_message !== 'Processing...') {
              addLogEntry(status.progress_message, 'info');
            }
            
            // Update current stage from backend if available
            if (status.analysis_stage && 
                status.analysis_stage !== 'Unknown') {
              addLogEntry(`Stage: ${status.analysis_stage}`, 'info');
              
              // Auto-advance stage based on backend stage updates
              if (status.analysis_stage.includes('File') && currentStep < 2) {
                currentStep = 2;
                activateStage(1);
              } else if (status.analysis_stage.includes('Pattern') && currentStep < 3) {
                currentStep = 3;
                activateStage(2);
              } else if (status.analysis_stage.includes('Output') && currentStep < 4) {
                currentStep = 4;
                activateStage(3);
              }
            }
          }
          
          // Check if analysis is complete
          if (status?.analysis_complete) {
            analysisComplete = true;
            setOverallProgress(100);
            addLogEntry('Backend analysis confirmed complete!', 'success');
            break;
          }

          // Check if there's an error
          if (status && !status.success) {
            throw new Error(status.error || 'Analysis failed');
          }

          // Improved fallback logic: Only advance if we haven't had progress for a while
          if (consecutiveNoProgress >= maxNoProgressAttempts && currentStep < 5 && !status?.progress_percentage) {
            currentStep++;
            const fallbackProgress = Math.min((currentStep / 5) * 85, 85);
            setOverallProgress(fallbackProgress);
            addLogEntry(`Advancing to step ${currentStep} (no backend progress)`, 'warning');
            consecutiveNoProgress = 0; // Reset counter after manual advance
          }
        }

        // Handle timeout case
        if (pollAttempts >= maxPollAttempts && !analysisComplete) {
          addLogEntry('Analysis taking longer than expected, checking results...', 'warning');
          // Still try to get results even if polling timed out
        }

      // Get final results using the current session
      const analysisResults = await getAnalysisResults(currentSessionId);
      if (analysisResults && isComponentMountedRef.current) {
        const formattedResults = formatBackendResults(analysisResults, analysisType);
        setResults(formattedResults);
      } else if (!analysisResults) {
        throw new Error('Failed to retrieve analysis results');
      }

      if (isComponentMountedRef.current) {
        // Analysis completed - progress bar will handle completion
      }
      }

    } catch (error) {
      console.error('Backend analysis failed:', error);
      if (isComponentMountedRef.current) {
        addLogEntry(`Analysis failed: ${error instanceof Error ? error.message : 'Unknown error'}. Please check the CSDAIv2 backend connection.`, 'error');
      }
    } finally {
      if (isComponentMountedRef.current) {
        setIsAnalyzing(false);
      }
    }
  };

  const formatBackendResults = (backendData: Record<string, unknown>, type: string): AnalysisResult => {
    // CRITICAL FIX: Check for new standardized format from backend API first
    const hasStandardizedFormat = backendData.analysis_result && typeof backendData.analysis_result === 'object';
    const hasLegacyFormat = backendData.results && typeof backendData.results === 'string';
    const formatVersion = backendData.format_version as string;
    
    console.log('🔍 Backend response format detected:', {
      hasStandardizedFormat,
      hasLegacyFormat,
      formatVersion,
      keys: Object.keys(backendData),
      analysisType: type
    });
    
    // Prioritize standardized format (new API response structure) for other analyzers
    if (hasStandardizedFormat) {
      const standardizedData = backendData.analysis_result as Record<string, unknown>;
      console.log('✅ Using standardized format from backend API');
      
      // Check for single-file analysis warnings
      const hasWarning = standardizedData.warning && typeof standardizedData.warning === 'string';
      const analysisStatus = standardizedData.status as string;
      const isPartialAnalysis = analysisStatus?.includes('partial_');
      
      let warningMessage = '';
      if (hasWarning) {
        warningMessage = standardizedData.warning as string;
      } else if (isPartialAnalysis) {
        if (analysisStatus === 'partial_xml_only') {
          warningMessage = 'Analysis performed with only RunningProcesses.xml. Results may be incomplete without TopNBusyProcess.txt scan data.';
        } else if (analysisStatus === 'partial_txt_only') {
          warningMessage = 'Analysis performed with only TopNBusyProcess.txt. Results may be incomplete without RunningProcesses.xml process data.';
        }
      }
      
      const result = {
        type: analysisTypes.find(t => t.id === type)?.name || 'Analysis',
        analysisType: type, // Store original analyzer type
        summary: typeof standardizedData.summary === 'string' 
          ? standardizedData.summary 
          : 'Analysis completed successfully',
        details: [
          ...(Array.isArray(standardizedData.details) 
            ? standardizedData.details.map(item => typeof item === 'string' ? item : JSON.stringify(item))
            : ['No details available']),
          ...(warningMessage ? [`⚠️ Warning: ${warningMessage}`] : [])
        ],
        severity: (standardizedData.severity as AnalysisResult['severity']) || (isPartialAnalysis ? 'medium' : 'medium'),
        analysisData: {
          ...standardizedData,
          correlations: standardizedData.correlations,
          statistics: standardizedData.statistics,
          ml_insights: standardizedData.ml_insights,
          // Include warning information
          hasWarning: hasWarning || isPartialAnalysis,
          warningMessage: warningMessage,
          analysisMode: isPartialAnalysis ? analysisStatus : 'complete',
          // Include original backend response for debugging
          _backendResponse: backendData,
          formatVersion: 'standardized_v2'
        },
        sessionId: sessionId
      };
      
      console.log('📊 Standardized result processed:', {
        type: result.type,
        summaryLength: result.summary?.length || 0,
        detailsCount: result.details?.length || 0,
        severity: result.severity
      });
      
      return result;
    }
    
    // Check if this is legacy standardized analyzer output (direct from analyzer)
    const isDirectStandardized = backendData.analysis_type && backendData.status && backendData.summary && backendData.details;
    
    if (isDirectStandardized) {
      console.log('✅ Using direct standardized format from analyzer');
      // Direct mapping from standardized structure
      const result = {
        type: analysisTypes.find(t => t.id === type)?.name || 'Analysis',
        analysisType: type, // Store original analyzer type
        summary: typeof backendData.summary === 'string' 
          ? backendData.summary 
          : 'Analysis completed successfully',
        details: Array.isArray(backendData.details) 
          ? backendData.details.map(item => typeof item === 'string' ? item : JSON.stringify(item))
          : ['No details available'],
        severity: (backendData.severity as AnalysisResult['severity']) || 'medium',
        analysisData: {
          ...backendData,
          correlations: backendData.correlations,
          statistics: backendData.statistics,
          ml_insights: backendData.ml_insights,
          formatVersion: 'direct_standardized'
        },
        sessionId: sessionId
      };
      
      return result;
    }
    
    // NEW: Check for rich raw_results format (enhanced parsing)
    const hasRawResults = backendData.raw_results && typeof backendData.raw_results === 'string';
    
    if (hasRawResults) {
      console.log('✅ Parsing enhanced raw_results format');
      const rawText = backendData.raw_results as string;
      
      // Extract structured data from raw_results
      const totalLinesMatch = rawText.match(/Total Lines:\s*(\d+)/i);
      const errorsMatch = rawText.match(/Errors Found:\s*(\d+)/i);
      const warningsMatch = rawText.match(/Warnings Found:\s*(\d+)/i);
      const criticalMatch = rawText.match(/Critical Issues:\s*(\d+)/i);
      
      const totalLines = totalLinesMatch ? parseInt(totalLinesMatch[1]) : 0;
      const errors = errorsMatch ? parseInt(errorsMatch[1]) : 0;
      const warnings = warningsMatch ? parseInt(warningsMatch[1]) : 0;
      const critical = criticalMatch ? parseInt(criticalMatch[1]) : 0;
      
      // Extract details from raw text
      const detailsSection = rawText.match(/Details \((\d+) items\):([\s\S]*?)(?=\n\nRecommendations|\n\nDebug|$)/);
      const detailsList: string[] = [];
      if (detailsSection && detailsSection[2]) {
        const issueLines = detailsSection[2].split('\n').filter(line => line.trim().startsWith('- '));
        issueLines.forEach((line) => {
          const cleanLine = line.replace(/^- /, '').trim();
          if (cleanLine) {
            detailsList.push(cleanLine);
          }
        });
      }
      
      // Create enhanced summary
      const healthScore = Math.max(10, 100 - (critical * 25) - (errors * 10) - Math.floor(warnings / 10));
      const status = critical > 0 ? 'critical' : errors > 0 ? 'error' : warnings > 50 ? 'warning' : 'success';
      
      const summary = `Analysis completed: ${totalLines.toLocaleString()} lines processed, ` +
        `${critical} critical issues, ${errors} errors, ${warnings} warnings found. ` +
        `Health Score: ${healthScore}/100 (${status.toUpperCase()})`;
      
      const result = {
        type: analysisTypes.find(t => t.id === type)?.name || 'Enhanced Analysis',
        analysisType: type, // Store original analyzer type
        summary,
        details: detailsList.length > 0 ? detailsList : ['No specific issues identified'],
        severity: (critical > 0 ? 'critical' : errors > 0 ? 'high' : warnings > 100 ? 'medium' : 'low') as AnalysisResult['severity'],
        analysisData: {
          ...backendData,
          enhancedMetrics: {
            totalLines,
            errors,
            warnings,
            critical,
            healthScore,
            status
          },
          correlations: backendData.correlations,
          statistics: backendData.statistics,
          ml_insights: backendData.ml_insights,
          formatVersion: 'enhanced_raw_results'
        },
        sessionId: sessionId
      };
      
      console.log('📊 Enhanced raw_results parsed:', {
        totalLines,
        errors,
        warnings,
        critical,
        healthScore,
        detailsCount: detailsList.length
      });
      
      return result;
    }

    // Legacy formatting for backward compatibility
    console.log('⚠️ Falling back to legacy format processing');
    
    // Check if results field contains HTML
    const isHTML = typeof backendData.results === 'string' && (
      (backendData.results as string).includes('<div') ||
      (backendData.results as string).includes('<h') ||
      (backendData.results as string).includes('<p') ||
      (backendData.results as string).includes('<table') ||
      (backendData.results as string).includes('class=') ||
      (backendData.results as string).includes('font-consistent')
    );
    
    if (isHTML) {
      console.log('📄 Processing legacy HTML format');
      // For HTML content, extract meaningful text
      const htmlContent = backendData.results as string;
      const result = {
        type: analysisTypes.find(t => t.id === type)?.name || 'Analysis',
        analysisType: type, // Store original analyzer type
        summary: 'Analysis completed - view formatted results below',
        details: ['HTML analysis results available in formatted view'],
        severity: 'medium' as AnalysisResult['severity'],
        analysisData: { 
          ...backendData,
          formattedHTML: htmlContent,
          isLegacyFormat: true,
          formatVersion: 'legacy_html'
        },
        sessionId: sessionId
      };
      
      console.log('📊 Legacy HTML result processed');
      return result;
    }

    // Safely convert details to string array
    const formatDetails = (data: unknown): string[] => {
      if (Array.isArray(data)) {
        return data.map(item => typeof item === 'string' ? item : JSON.stringify(item));
      }
      if (typeof data === 'object' && data !== null) {
        return Object.entries(data).map(([key, value]) => 
          `${key}: ${typeof value === 'string' ? value : JSON.stringify(value)}`
        );
      }
      return [typeof data === 'string' ? data : JSON.stringify(data)];
    };

    // Format the backend response to match our interface (final fallback)
    console.log('⚠️ Using final fallback format processing');
    const result = {
      type: analysisTypes.find(t => t.id === type)?.name || 'Analysis',
      analysisType: type, // Store original analyzer type
      summary: typeof backendData.summary === 'string' 
        ? backendData.summary 
        : typeof backendData.summary === 'object' && backendData.summary !== null
          ? JSON.stringify(backendData.summary, null, 2)
          : 'Analysis completed successfully',
      details: formatDetails(backendData.details),
      severity: (backendData.severity as AnalysisResult['severity']) || 'medium',
      analysisData: {
        ...backendData,
        formatVersion: 'final_fallback'
      },
      sessionId: sessionId
    };
    
    console.log('📊 Final fallback result processed:', {
      type: result.type,
      summaryLength: result.summary?.length || 0,
      detailsCount: result.details?.length || 0,
      severity: result.severity,
      originalKeys: Object.keys(backendData)
    });
    return result;
  };

  const removeFile = (index: number) => {
    setUploadedFiles(prev => prev.filter((_, i) => i !== index));
  };

  return (
    <div className="bg-gradient-to-br from-slate-800/90 to-slate-900/90 backdrop-blur-sm rounded-3xl shadow-2xl p-8 border border-red-500/30">
      {/* Case Context Display */}
      {caseInfo && (
        <div className="mb-8 bg-gradient-to-r from-purple-900/20 to-blue-900/20 border border-purple-500/30 rounded-2xl p-6">
          <div className="flex items-start space-x-4">
            <div className="w-12 h-12 bg-gradient-to-br from-purple-500 to-blue-600 rounded-xl flex items-center justify-center flex-shrink-0">
              <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </div>
            <div className="flex-1">
              <div className="flex items-center space-x-2 mb-3">
                <h3 className="text-xl font-semibold text-white">Case Context from Portal</h3>
                <span className="px-3 py-1 bg-purple-500/20 text-purple-300 rounded-full text-sm font-medium">
                  AI Recommended: {analysisTypes.find(at => at.id === analysisType)?.name || 'Unknown'}
                </span>
              </div>
              
              {caseInfo.caseTitle && (
                <div className="mb-3">
                  <span className="text-gray-400 text-sm font-medium">Case Title:</span>
                  <p className="text-white mt-1">{caseInfo.caseTitle}</p>
                </div>
              )}
              
              {caseInfo.description && (
                <div className="mb-3">
                  <span className="text-gray-400 text-sm font-medium">Description:</span>
                  <p className="text-gray-300 mt-1 leading-relaxed">{caseInfo.description}</p>
                </div>
              )}
              
              <div className="flex items-center space-x-4 text-sm">
                {caseInfo.product && (
                  <span className="bg-slate-700/50 px-3 py-1 rounded-lg text-gray-300">
                    Product: {caseInfo.product}
                  </span>
                )}
                {caseInfo.severity && (
                  <span className={`px-3 py-1 rounded-lg font-medium ${
                    caseInfo.severity === 'Critical' ? 'bg-red-500/20 text-red-300' :
                    caseInfo.severity === 'High' ? 'bg-orange-500/20 text-orange-300' :
                    caseInfo.severity === 'Medium' ? 'bg-yellow-500/20 text-yellow-300' :
                    'bg-green-500/20 text-green-300'
                  }`}>
                    {caseInfo.severity} Priority
                  </span>
                )}
                {caseInfo.attachments && caseInfo.attachments.length > 0 && (
                  <span className="bg-blue-500/20 text-blue-300 px-3 py-1 rounded-lg">
                    {caseInfo.attachments.length} Attachment{caseInfo.attachments.length > 1 ? 's' : ''}
                  </span>
                )}
              </div>
            </div>
          </div>
        </div>
      )}

      {!results ? (
        <div className="space-y-8">

          {/* Analysis Type Selection */}
          <div>
            <h3 className="text-3xl font-bold text-white mb-8 text-center">Select Your Issue</h3>
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

                // Check if analyzer is available
                const availability = analyzerAvailability[type.id];
                const isDisabled = availability?.status === 'disabled';
                const isAvailable = availability?.status === 'enabled' || !availability; // Default to enabled if unknown

                return (
                  <button
                    key={type.id}
                    onClick={() => isAvailable ? setAnalysisType(type.id) : null}
                    disabled={isDisabled}
                    className={`relative p-6 rounded-2xl border transition-all duration-300 text-left group ${
                      isDisabled 
                        ? 'opacity-50 cursor-not-allowed bg-gray-500/10 border-gray-500/30' 
                        : 'hover:scale-105'
                    } ${
                      analysisType === type.id && isAvailable
                        ? 'bg-red-500/20 border-red-500/50 shadow-2xl shadow-red-500/20'
                        : 'bg-white/5 border-white/20 hover:border-red-500/30 hover:bg-red-500/10'
                    }`}
                  >
                    {/* Severity and Issue Type Badges */}
                    <div className="flex justify-between items-start mb-4">
                      <div className="flex space-x-2">
                        <span className={`px-3 py-1 rounded-full text-xs font-medium border ${getSeverityColor(type.severity)}`}>
                          {getSeverityIcon(type.severity)} {type.severity.toUpperCase()}
                        </span>
                        {isDisabled && (
                          <span className="px-3 py-1 rounded-full text-xs font-medium bg-gray-500/20 text-gray-300 border border-gray-500/50">
                            🚫 DISABLED
                          </span>
                        )}
                      </div>
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
            
            {/* Auto-upload status indicator */}
            {caseContext?.autoUploaded && (
              <div className="mb-4 p-4 bg-gradient-to-r from-green-600 to-blue-600 rounded-xl border border-green-500/30">
                <div className="flex items-center space-x-3">
                  <div className="w-8 h-8 bg-green-400 rounded-full flex items-center justify-center">
                    <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                  </div>
                  <div className="flex-1">
                    <h4 className="text-white font-semibold">Files Auto-Uploaded from Portal</h4>
                    <p className="text-green-100 text-sm">
                      {caseContext.extractedFiles?.length || 0} files were automatically extracted and uploaded from your diagnostic package
                    </p>
                    {caseContext.extractedFiles && (
                      <div className="mt-2 text-xs text-green-200">
                        Files: {caseContext.extractedFiles.map(f => f.name).join(', ')}
                      </div>
                    )}
                  </div>
                </div>
              </div>
            )}

            {/* Extraction error indicator */}
            {caseContext?.extractionError && (
              <div className="mb-4 p-4 bg-gradient-to-r from-yellow-600 to-orange-600 rounded-xl border border-yellow-500/30">
                <div className="flex items-center space-x-3">
                  <div className="w-8 h-8 bg-yellow-400 rounded-full flex items-center justify-center">
                    <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.732-.833-2.5 0L4.732 15.5c-.77.833.192 2.5 1.732 2.5z" />
                    </svg>
                  </div>
                  <div className="flex-1">
                    <h4 className="text-white font-semibold">Auto-Upload Failed</h4>
                    <p className="text-yellow-100 text-sm">{caseContext.extractionError}</p>
                    {caseContext.requiredFiles && (
                      <div className="mt-2 text-xs text-yellow-200">
                        Please upload these files manually: {caseContext.requiredFiles.join(', ')}
                      </div>
                    )}
                  </div>
                </div>
              </div>
            )}

            {/* Portal redirect with re-upload notification */}
            {caseContext?.fromPortal && caseContext?.requiresReupload && (
              <div className="mb-4 p-4 bg-gradient-to-r from-blue-600 to-purple-600 rounded-xl border border-blue-500/30">
                <div className="flex items-center space-x-3">
                  <div className="w-8 h-8 bg-blue-400 rounded-full flex items-center justify-center">
                    <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                  </div>
                  <div className="flex-1">
                    <h4 className="text-white font-semibold">Different Analyzer Selected</h4>
                    <p className="text-blue-100 text-sm">
                      You chose a different analyzer from the portal. Please re-upload your files to continue with the analysis.
                    </p>
                    <div className="mt-2 text-xs text-blue-200">
                      Case: {caseContext.caseTitle || 'Untitled'} | Severity: {caseContext.severity || 'Not specified'}
                    </div>
                  </div>
                </div>
              </div>
            )}
            
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
                Supports .log, .txt, .xml, .csv, .zip files up to 100MB
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

            {/* Intelligent Extraction Results */}
            {extractionInfo && (
              <div className="mt-6 p-6 bg-blue-900/20 border border-blue-500/30 rounded-2xl">
                <div className="flex items-center mb-4">
                  <span className="text-2xl mr-3">📂</span>
                  <h4 className="text-lg font-semibold text-white">Intelligent File Extraction</h4>
                </div>
                
                <div className="mb-4">
                  <p className="text-sm text-gray-400">Files Extracted</p>
                  <p className="text-white font-semibold">{extractionInfo.filesExtracted || 0} files</p>
                </div>
                
                <div className="mb-4">
                  <p className="text-sm text-gray-400 mb-2">Extracted Files:</p>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                    {extractionInfo.filesInfo.map((file, index) => (
                      <div key={index} className="flex items-center justify-between p-2 bg-gray-800/50 rounded-lg">
                        <div className="flex items-center">
                          <span className={`w-2 h-2 rounded-full mr-2 ${
                            file.required ? 'bg-green-500' : 'bg-blue-500'
                          }`}></span>
                          <span className="text-white text-sm">{file.name}</span>
                        </div>
                        <span className="text-gray-400 text-xs">
                          {(file.size / 1024 / 1024).toFixed(2)} MB
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
                
                {extractionInfo.extractionSummary && (
                  <div className="text-xs text-gray-400">
                    Summary: {extractionInfo.extractionSummary.filesMatched || 0} of {extractionInfo.extractionSummary.totalFilesInZip || 0} files matched patterns
                    {extractionInfo.extractionSummary.missingRequired?.length > 0 && (
                      <span className="text-yellow-400 ml-2">
                        • Missing: {extractionInfo.extractionSummary.missingRequired.join(', ')}
                      </span>
                    )}
                  </div>
                )}
              </div>
            )}

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
                        <h6 className="text-white font-semibold flex items-center justify-between">
                          <span className="flex items-center">
                            <span className="mr-2">📋</span>
                            Analysis Log
                          </span>
                          {!autoScrollEnabled && (
                            <span className="text-xs bg-red-500/20 text-red-300 px-2 py-1 rounded">
                              Auto-scroll paused
                            </span>
                          )}
                        </h6>
                      </div>
                      <div className="relative">
                        <div 
                          ref={logContainerRef}
                          id="analysis-log"
                          className="h-48 overflow-y-auto p-4 bg-gray-900/30 font-mono text-sm space-y-1 scroll-smooth"
                          style={{ scrollBehavior: 'smooth' }}
                        >
                          {logEntries.map((entry, index) => (
                            <div key={index} className={`log-entry animate-fadeIn ${entry.type} transition-colors duration-300`}>
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
                        
                        {/* Auto-scroll Indicator */}
                        {autoScrollEnabled && logEntries.length > 0 && (
                          <div className="absolute bottom-2 right-2 bg-blue-500/80 text-white text-xs px-2 py-1 rounded opacity-50 transition-opacity duration-300 pointer-events-none">
                            Auto-scrolling
                          </div>
                        )}
                        
                        {/* Scroll to Bottom Button */}
                        {!autoScrollEnabled && (
                          <button
                            onClick={() => {
                              setAutoScrollEnabled(true);
                              const logContainer = logContainerRef.current;
                              if (logContainer) {
                                logContainer.scrollTo({
                                  top: logContainer.scrollHeight,
                                  behavior: 'smooth'
                                });
                              }
                            }}
                            className="absolute bottom-2 right-2 bg-blue-500 hover:bg-blue-600 text-white p-2 rounded-full transition-all duration-300 transform hover:scale-110 shadow-lg"
                            title="Scroll to bottom and re-enable auto-scroll"
                          >
                            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 14l-7 7m0 0l-7-7m7 7V3" />
                            </svg>
                          </button>
                        )}
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
                  disabled={backendStatus !== 'connected' || analyzerAvailability[analysisType]?.status === 'disabled'}
                  className={`w-full mt-6 py-4 rounded-xl font-semibold text-lg transition-all duration-300 ${
                    backendStatus === 'connected' && analyzerAvailability[analysisType]?.status !== 'disabled'
                      ? 'bg-gradient-to-r from-red-500 to-red-600 text-white hover:from-red-600 hover:to-red-700 transform hover:scale-105' 
                      : 'bg-gray-500/20 text-gray-400 cursor-not-allowed border border-gray-500/30'
                  }`}
                >
                  {analyzerAvailability[analysisType]?.status === 'disabled' ? (
                    <>
                      <span className="mr-2">🚫</span>
                      Analyzer Disabled by Admin
                    </>
                  ) : (
                    'Start Analysis'
                  )}
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
          {/* Check if we have HTML results OR structured data from CSDAIv2 backend for ANY analysis type */}
          {Boolean(
            // Case 1: HTML results (legacy format)
            (results.analysisData && 
             typeof results.analysisData.results === 'string' && 
             (results.analysisData.results.includes('<div') || 
              results.analysisData.results.includes('<h') || 
              results.analysisData.results.includes('<p') ||
              results.analysisData.results.includes('<table') ||
              results.analysisData.results.includes('class=') ||
              results.analysisData.results.includes('font-consistent'))) ||
            // Case 2: Structured data (v2 format)
            (results.analysisData && results.analysisData.structured_data)
          ) ? (
            <>
              {/* Legacy HTML Results (standard analysis display) */}
              <div className="bg-white/5 rounded-2xl p-6 border border-white/20">
                <div className="flex items-center justify-between mb-4">
                  <h4 className="text-xl font-bold text-white flex items-center">
                    <span className="mr-3">📋</span>
                    Legacy Analysis Results
                  </h4>
                  {results.sessionId && (
                    <span className="text-xs bg-blue-500/20 text-blue-400 px-2 py-1 rounded-lg">
                      Session: {results.sessionId.slice(-8)}
                    </span>
                  )}
                </div>
                <div className="bg-blue-50/5 border border-blue-500/20 rounded-lg p-1">
                  <p className="text-blue-300 text-sm mb-3 px-3 pt-2">
                    ℹ️ Legacy Format: Raw HTML output from backend analysis.
                  </p>
                  
                  {/* Render the HTML results directly for all analysis types */}
                  <div 
                    className="csdaiv2-results"
                    dangerouslySetInnerHTML={{ 
                      __html: (results.analysisData?.results as string) || '' 
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
            </>
          ) : (
            // Fallback to original layout for non-HTML results
            <div className="space-y-8">
                {results.analysisData && (
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
                    <AnalysisDataParser 
                      analysisData={results.analysisData} 
                      analysisType={results.analysisType || 'unknown'}
                    />
                  </div>
                )}

            </div>
          )}

          <div className="flex space-x-4">
            <button 
              onClick={() => setShowNewAnalysisModal(true)}
              disabled={isAnalyzing}
              className="flex-1 bg-gradient-to-r from-purple-500 to-purple-600 text-white py-3 rounded-xl hover:from-purple-600 hover:to-purple-700 transition-all duration-300 transform hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none flex items-center justify-center gap-2"
            >
              <span className="text-lg">🔄</span>
              New Analysis
            </button>
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
              className="flex-1 bg-gradient-to-r from-green-500 to-green-600 text-white py-3 rounded-xl hover:from-green-600 hover:to-green-700 transition-all duration-300 transform hover:scale-105 flex items-center justify-center gap-2"
            >
              <span className="text-lg">📄</span>
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
                  addLogEntry('Results copied to clipboard!', 'success');
                }
              }}
              className="flex-1 bg-gradient-to-r from-blue-500 to-blue-600 text-white py-3 rounded-xl hover:from-blue-600 hover:to-blue-700 transition-all duration-300 transform hover:scale-105 flex items-center justify-center gap-2"
            >
              <span className="text-lg">📤</span>
              Share Results
            </button>
          </div>
        </div>
      )}

      {/* New Analysis Confirmation Modal */}
      {showNewAnalysisModal && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center z-[9999] p-4">
          <div className="bg-gray-900/95 border border-purple-500/30 rounded-2xl p-6 max-w-md w-full mx-4 shadow-2xl backdrop-blur-md">
            <div className="text-center">
              <div className="mb-4">
                <span className="text-4xl">🔄</span>
              </div>
              <h3 className="text-xl font-bold text-white mb-2">Start New Analysis?</h3>
              <p className="text-gray-300 mb-6">
                This will clear your current analysis results and session data. Are you sure you want to continue?
              </p>
              
              {sessionId && (
                <div className="bg-blue-500/10 border border-blue-500/30 rounded-lg p-3 mb-6">
                  <p className="text-blue-300 text-sm">
                    <span className="font-semibold">Current Session:</span> {sessionId.slice(-8)}
                  </p>
                  <p className="text-blue-400 text-xs mt-1">
                    Session data will be cleaned up automatically
                  </p>
                </div>
              )}
              
              <div className="flex space-x-3">
                <button
                  onClick={() => setShowNewAnalysisModal(false)}
                  className="flex-1 bg-gray-600 hover:bg-gray-700 text-white py-3 px-4 rounded-xl transition-all duration-300"
                >
                  Cancel
                </button>
                <button
                  onClick={async () => {
                    setShowNewAnalysisModal(false);
                    await handleNewAnalysis();
                  }}
                  className="flex-1 bg-gradient-to-r from-purple-500 to-purple-600 hover:from-purple-600 hover:to-purple-700 text-white py-3 px-4 rounded-xl transition-all duration-300 transform hover:scale-105"
                >
                  Start New Analysis
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

    </div>
  );
}
