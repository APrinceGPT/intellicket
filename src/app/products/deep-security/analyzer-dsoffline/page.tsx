'use client';

import { useState, useCallback, useRef } from 'react';
import { useRouter } from 'next/navigation';
import Image from 'next/image';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { 
  Upload, 
  FileText, 
  Brain, 
  Database, 
  Zap, 
  CheckCircle, 
  Info as InfoIcon, 
  AlertCircle,
  BookOpen,
  AlertTriangle,
  BarChart3,
  Code
} from 'lucide-react';

const products = [
  { 
    id: 'deep-security', 
    name: 'Deep Security',
    description: 'Server & Cloud Protection',
    fullDescription: 'Comprehensive security for physical, virtual, and cloud servers with advanced threat protection.',
    icon: '🛡️',
    gradient: 'from-red-600 to-red-800',
    hoverGradient: 'hover:from-red-700 hover:to-red-900',
    features: ['Multi-layered server security', 'Virtual patching and IPS', 'Anti-malware and web reputation', 'Application control and integrity monitoring']
  },
  { 
    id: 'apex-one', 
    name: 'Apex One',
    description: 'Endpoint Security',
    fullDescription: 'Advanced threat detection and response for endpoints with AI-powered protection.',
    icon: '🔒',
    gradient: 'from-blue-600 to-blue-800',
    hoverGradient: 'hover:from-blue-700 hover:to-blue-900',
    features: ['Next-gen antivirus', 'Behavioral analysis', 'Advanced threat detection', 'Endpoint detection and response']
  },
  { 
    id: 'vision-one', 
    name: 'Vision One',
    description: 'XDR Platform',
    fullDescription: 'Extended Detection and Response (XDR) for comprehensive security visibility and response.',
    icon: '👁️',
    gradient: 'from-purple-600 to-purple-800',
    hoverGradient: 'hover:from-purple-700 hover:to-purple-900',
    features: ['Cross-layer visibility', 'Advanced threat hunting', 'Automated response', 'Risk assessment and prioritization']
  },
  { 
    id: 'service-gateway', 
    name: 'Service Gateway',
    description: 'Secure Connectivity',
    fullDescription: 'Secure service delivery platform with enterprise-grade performance and reliability.',
    icon: '🌐',
    gradient: 'from-green-600 to-green-800',
    hoverGradient: 'hover:from-green-700 hover:to-green-900',
    features: ['Secure service delivery', 'Advanced access control', 'Performance monitoring', 'Centralized configuration management']
  },
];

interface AnalysisResults {
  status: string;
  summary: string;
  data: {
    // Core analysis data (direct level)
    summary?: string;
    statistics?: Record<string, unknown>;
    metadata?: {
      analysis_type?: string;
      files_processed?: number;
      zip_files_extracted?: number;
      extracted_files?: number;
      log_entries_processed?: number;
      offline_issues?: number;
      critical_issues?: number;
      errors_found?: number;
      warnings_found?: number;
    };
    
    // Backend wrapper structure
    analysis_result?: {
      // Enhanced AI analysis
      ai_analysis?: {
        confidence_score?: number;
        classification?: string;
        intelligent_insights?: string[];
        anomaly_detection?: {
          anomalies_found?: number;
          pattern_analysis?: string;
          severity_distribution?: string;
        };
        communication_issues?: CommunicationIssue[];
      };
      
      // Dynamic RAG insights
      rag_insights?: {
        ai_response?: string;
        analysis_metadata?: {
          components_analyzed?: number;
          error_types_found?: number;
          knowledge_sources_used?: number;
          ai_available?: boolean;
        };
      };
      
      // Raw data with communication analysis
      raw_data?: {
        ai_communication_analysis?: {
          communication_health_score?: number;
          ai_detected_issues?: CommunicationIssue[];
        };
      };
    };
    
    // Legacy direct structure (for backwards compatibility)
    ai_analysis?: {
      confidence_score?: number;
      classification?: string;
      intelligent_insights?: string[];
      anomaly_detection?: {
        anomalies_found?: number;
        pattern_analysis?: string;
        severity_distribution?: string;
      };
      communication_issues?: CommunicationIssue[];
    };
    
    rag_insights?: {
      ai_response?: string;
      analysis_metadata?: {
        components_analyzed?: number;
        error_types_found?: number;
        knowledge_sources_used?: number;
        ai_available?: boolean;
      };
    };
    
    raw_data?: {
      ai_communication_analysis?: {
        communication_health_score?: number;
        ai_detected_issues?: CommunicationIssue[];
      };
    };
  };
  metadata?: {
    analysis_type?: string;
    files_processed?: number;
    zip_files_extracted?: number;
    extracted_files?: number;
    log_entries_processed?: number;
    offline_issues?: number;
    critical_issues?: number;
  };
  extractedFiles?: Array<{
    name: string;
    size: number;
    type: string;
  }>;
  // AI Communication Analysis Results
  ai_communication_analysis?: {
    communication_health_score: number;
    ai_detected_issues: Array<{
      category: string;
      severity: string;
      ports_affected: number[];
      communication_direction: string;
      ai_context: string;
      confidence_score: number;
      issue_count: number;
      matches: Array<{
        line_number: number;
        content: string;
        pattern_matched: string;
      }>;
    }>;
    network_architecture_analysis: {
      affected_communication_flows: string[];
      port_health_analysis: Record<string, {
        port: number;
        health_status: string;
        services: string[];
        ai_recommendations: string[];
      }>;
      ai_network_recommendations: Array<{
        priority: string;
        category: string;
        recommendation: string;
        actions: string[];
      }>;
    };
    intelligent_diagnostics: {
      priority_issues: Array<{
        category: string;
        severity: string;
        confidence_score: number;
      }>;
      ai_troubleshooting_steps: Array<{
        step: string;
        category: string;
        priority: number;
        actions: string[];
        expected_resolution_time: string;
        automation_available: boolean;
      }>;
      automated_commands: {
        windows: string[];
        linux: string[];
      };
      confidence_analysis: {
        overall_confidence: number;
        high_confidence_issues: number;
        ai_recommendation_reliability: string;
      };
    };
  };
  // AI Enhanced Root Cause Analysis
  ai_enhanced_root_cause?: {
    ai_primary_causes: Array<{
      cause: string;
      confidence: number;
      description: string;
      impact_level: string;
      affected_communications: string;
    }>;
    resolution_confidence: number;
    correlation_analysis: Record<string, unknown>;
  };
  // Dynamic RAG Analysis
  dynamic_rag_analysis?: {
    ai_response: string;
    analysis_metadata: {
      knowledge_sources_used: number;
      confidence_score: number;
    };
  };
  // ML Analysis
  ml_insights?: {
    confidence_score: number;
    pattern_analysis: Record<string, unknown>;
  };
}

interface CommunicationIssueMatch {
  ai_context: string;
  content: string;
  line_number: number;
  ml_indicators: string[];
  pattern_matched: string;
}

interface CommunicationIssue {
  ai_context: string;
  category: string;
  communication_direction: string;
  confidence_score: number;
  issue_count: number;
  matches: CommunicationIssueMatch[];
  ml_indicators: string[];
  ports_affected: number[];
  severity: string;
}

export default function DSAgentOfflineAnalyzer() {
  const router = useRouter();
  const [uploadedFiles, setUploadedFiles] = useState<File[]>([]);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [results, setResults] = useState<AnalysisResults | null>(null);
  const [dragActive, setDragActive] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleProductSelection = (productId: string) => {
    router.push(`/products/${productId}`);
  };

  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const files = Array.from(e.dataTransfer.files);
      setUploadedFiles(prev => [...prev, ...files]);
    }
  }, []);

  const handleFileSelect = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      const files = Array.from(e.target.files);
      setUploadedFiles(prev => [...prev, ...files]);
    }
  }, []);

  const removeFile = useCallback((index: number) => {
    setUploadedFiles(prev => prev.filter((_, i) => i !== index));
  }, []);

  const startAnalysis = async () => {
    if (uploadedFiles.length === 0) return;
    
    setIsAnalyzing(true);
    setResults(null);
    
    try {
      // Step 1: Upload files to dedicated DS Agent Offline endpoint
      const formData = new FormData();
      uploadedFiles.forEach((file, index) => {
        formData.append(`file_${index}`, file);
      });
      
      console.log('🎯 DS Agent Offline: Starting upload...');
      const uploadResponse = await fetch('/api/csdai/ds-agent-offline/upload', {
        method: 'POST',
        body: formData,
      });
      
      if (!uploadResponse.ok) {
        throw new Error('Upload failed');
      }
      
      const uploadData = await uploadResponse.json();
      const sessionId = uploadData.session_id;
      
      if (!sessionId) {
        throw new Error('No session ID received');
      }
      
      console.log(`✅ DS Agent Offline: Upload successful, session: ${sessionId}`);
      
      // Step 2: Poll for analysis completion
      let analysisComplete = false;
      let attempts = 0;
      const maxAttempts = 60; // 2 minutes max
      
      while (!analysisComplete && attempts < maxAttempts) {
        await new Promise(resolve => setTimeout(resolve, 2000)); // Wait 2 seconds
        attempts++;
        
        const statusResponse = await fetch(`/api/csdai/ds-agent-offline/status/${sessionId}`);
        if (statusResponse.ok) {
          const statusData = await statusResponse.json();
          
          if (statusData.analysis_complete) {
            analysisComplete = true;
            console.log('✅ DS Agent Offline: Analysis completed');
            break;
          }
        }
      }
      
      // Step 3: Fetch results
      if (analysisComplete) {
        const resultsResponse = await fetch(`/api/csdai/ds-agent-offline/results/${sessionId}`);
        if (resultsResponse.ok) {
          const resultsData = await resultsResponse.json();
          
          // Extract metadata and analysis results
          const analysisResult = resultsData.analysis_result || resultsData;
          const metadata = analysisResult.metadata || {};
          const offlineAnalysis = analysisResult.offline_analysis || {};
          
          console.log('📊 DS Agent Offline Results:', {
            metadata,
            hasOfflineAnalysis: !!offlineAnalysis,
            keys: Object.keys(analysisResult)
          });
          
          // Determine if ZIP extraction occurred
          const zipExtracted = metadata.zip_files_extracted > 0;
          const extractedFilesCount = metadata.extracted_files || 0;
          
          let summary = 'DS Agent Offline analysis completed successfully!';
          if (zipExtracted) {
            summary = `ZIP extraction successful! Analyzed ${extractedFilesCount} DS Agent log files from ${metadata.zip_files_extracted} ZIP archive(s).`;
          }
          
          setResults({
            status: 'completed',
            summary,
            data: resultsData,
            metadata,
            extractedFiles: zipExtracted ? Array(extractedFilesCount).fill(null).map((_, i) => ({
              name: `ds_agent_log_${i + 1}.log`,
              size: 0,
              type: 'DS Agent Log'
            })) : undefined
          });
        } else {
          throw new Error('Failed to fetch results');
        }
      } else {
        throw new Error('Analysis timed out');
      }
      
    } catch (error) {
      console.error('❌ DS Agent Offline analysis failed:', error);
      setResults({
        status: 'error',
        summary: error instanceof Error ? error.message : 'Analysis failed',
        data: {}
      });
    } finally {
      setIsAnalyzing(false);
    }
  };

  return (
    <div className="min-h-screen flex flex-col" style={{
      background: 'radial-gradient(ellipse at center, rgba(80, 0, 0, 0.4) 0%, rgba(40, 0, 0, 0.8) 25%, rgba(20, 0, 0, 0.95) 50%, rgba(0, 0, 0, 1) 100%)'
    }}>
      {/* Header */}
      <header className="relative z-50 border-b border-white/10 backdrop-blur-sm bg-black/30">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <button 
              onClick={() => router.push('/')}
              className="flex items-center space-x-4 hover:opacity-80 transition-opacity cursor-pointer"
            >
              <Image 
                src="/trendlogo.png" 
                alt="Trend Micro Logo" 
                width={40}
                height={40}
                className="h-10 w-auto"
              />
              <div className="border-l border-white/30 pl-4">
                <h1 className="text-2xl font-bold text-white">Intellicket</h1>
                <p className="text-xs text-red-400 font-medium">AI Support Platform</p>
              </div>
            </button>
            <div className="flex items-center space-x-4">
              <Button
                onClick={() => router.push('/products/deep-security')}
                variant="ghost"
                className="text-white hover:bg-white/10"
              >
                Back to Deep Security
              </Button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1 relative overflow-hidden py-8">
        {/* Dark Red Bokeh Effects - Multiple layers for depth */}
        <div className="absolute inset-0">
          {/* Large dark red bokeh effects */}
          <div className="absolute top-10 left-10 w-80 h-80 bg-red-900/25 rounded-full filter blur-3xl"></div>
          <div className="absolute top-32 right-20 w-96 h-96 bg-red-800/20 rounded-full filter blur-3xl"></div>
          <div className="absolute bottom-20 left-32 w-72 h-72 bg-red-900/30 rounded-full filter blur-3xl"></div>
          <div className="absolute bottom-40 right-40 w-64 h-64 bg-red-800/25 rounded-full filter blur-3xl"></div>
          
          {/* Medium dark red bokeh effects */}
          <div className="absolute top-1/3 left-1/4 w-48 h-48 bg-red-900/35 rounded-full filter blur-2xl"></div>
          <div className="absolute top-2/3 right-1/3 w-56 h-56 bg-red-800/30 rounded-full filter blur-2xl"></div>
          <div className="absolute top-1/2 left-2/3 w-40 h-40 bg-red-900/40 rounded-full filter blur-2xl"></div>
          
          {/* Small dark red accent bokeh */}
          <div className="absolute top-20 right-1/2 w-32 h-32 bg-red-800/45 rounded-full filter blur-xl"></div>
          <div className="absolute bottom-32 left-1/2 w-36 h-36 bg-red-900/35 rounded-full filter blur-xl"></div>
          
          {/* Animated dark red bokeh elements */}
          <div className="absolute top-1/4 right-1/4 w-44 h-44 bg-red-800/25 rounded-full filter blur-2xl animate-pulse"></div>
          <div className="absolute bottom-1/3 left-1/3 w-52 h-52 bg-red-900/20 rounded-full filter blur-3xl animate-pulse" style={{ animationDelay: '2s' }}></div>
        </div>
        
        <div className="relative z-10 max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        
        {/* Header Section */}
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-white mb-4">
            DS Agent Offline Analyzer
          </h1>
          <p className="text-xl text-gray-300 mb-6">
            AI-Powered Deep Security Agent Offline Diagnosis & Recovery Solution
          </p>
          <div className="flex justify-center space-x-2">
            <Badge variant="secondary" className="bg-red-900/30 text-red-300 border border-red-700/40">
              <Brain className="w-4 h-4 mr-1" />
              AI-Enhanced
            </Badge>
            <Badge variant="secondary" className="bg-red-800/30 text-red-400 border border-red-600/40">
              <Zap className="w-4 h-4 mr-1" />
              Real-time Analysis
            </Badge>
            <Badge variant="secondary" className="bg-black/60 text-red-300 border border-red-800/40">
              <Database className="w-4 h-4 mr-1" />
              RAG-Powered
            </Badge>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          
          {/* Left Column - Information */}
          <div className="lg:col-span-1 space-y-6">
            
            {/* AI Capabilities */}
            <Card className="border-red-800/30 hover:border-red-600/50 transition-all duration-300" style={{ backgroundColor: 'rgba(0, 0, 0, 0.8)', backdropFilter: 'blur(4px)' }}>
              <CardHeader>
                <CardTitle className="flex items-center text-white">
                  <Brain className="w-5 h-5 mr-2 text-red-400" />
                  AI Analysis Engines
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-start space-x-3">
                  <Database className="w-5 h-5 text-red-400 mt-1" />
                  <div>
                    <h4 className="font-semibold text-white">RAG System</h4>
                    <p className="text-sm text-gray-300">Retrieval-Augmented Generation for contextual analysis</p>
                  </div>
                </div>
                <div className="flex items-start space-x-3">
                  <Brain className="w-5 h-5 text-red-300 mt-1" />
                  <div>
                    <h4 className="font-semibold text-white">ML Engine</h4>
                    <p className="text-sm text-gray-300">Machine Learning pattern recognition and anomaly detection</p>
                  </div>
                </div>
                <div className="flex items-start space-x-3">
                  <Zap className="w-5 h-5 text-red-500 mt-1" />
                  <div>
                    <h4 className="font-semibold text-white">AI Insights</h4>
                    <p className="text-sm text-gray-300">Intelligent recommendations and root cause analysis</p>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Required Files */}
            <Card className="border-red-800/30 hover:border-red-600/50 transition-all duration-300" style={{ backgroundColor: 'rgba(0, 0, 0, 0.8)', backdropFilter: 'blur(4px)' }}>
              <CardHeader>
                <CardTitle className="flex items-center text-white">
                  <FileText className="w-5 h-5 mr-2 text-red-400" />
                  Required Files
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="flex items-center space-x-2">
                  <CheckCircle className="w-4 h-4 text-red-400" />
                  <span className="font-medium text-white">ds_agent.log</span>
                  <Badge variant="destructive" className="text-xs bg-red-800 text-white border-red-600">Required</Badge>
                </div>
                <div className="flex items-center space-x-2">
                  <InfoIcon className="w-4 h-4 text-red-300" />
                  <span className="font-medium text-white">ds_agent-err.log</span>
                  <Badge variant="secondary" className="text-xs bg-black/60 text-gray-300 border-red-800/50">Optional</Badge>
                </div>
                <div className="flex items-center space-x-2">
                  <InfoIcon className="w-4 h-4 text-red-300" />
                  <span className="font-medium text-white">ds_agent-connect.log</span>
                  <Badge variant="secondary" className="text-xs bg-black/60 text-gray-300 border-red-800/50">Optional</Badge>
                </div>
              </CardContent>
            </Card>

            {/* Instructions */}
            <Card className="border-red-800/30 hover:border-red-600/50 transition-all duration-300" style={{ backgroundColor: 'rgba(0, 0, 0, 0.8)', backdropFilter: 'blur(4px)' }}>
              <CardHeader>
                <CardTitle className="flex items-center text-white">
                  <AlertCircle className="w-5 h-5 mr-2 text-red-400" />
                  How to Use
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3 text-sm">
                <div className="flex items-start space-x-2">
                  <span className="bg-red-800/30 text-red-300 rounded-full w-5 h-5 flex items-center justify-center text-xs font-bold border border-red-600/40">1</span>
                  <p className="text-gray-300">Upload your DS Agent log files using the upload area</p>
                </div>
                <div className="flex items-start space-x-2">
                  <span className="bg-red-800/30 text-red-300 rounded-full w-5 h-5 flex items-center justify-center text-xs font-bold border border-red-600/40">2</span>
                  <p className="text-gray-300">Ensure ds_agent.log is included (required for analysis)</p>
                </div>
                <div className="flex items-start space-x-2">
                  <span className="bg-red-800/30 text-red-300 rounded-full w-5 h-5 flex items-center justify-center text-xs font-bold border border-red-600/40">3</span>
                  <p className="text-gray-300">Click &quot;Start Analysis&quot; to begin AI-powered diagnosis</p>
                </div>
                <div className="flex items-start space-x-2">
                  <span className="bg-red-800/30 text-red-300 rounded-full w-5 h-5 flex items-center justify-center text-xs font-bold border border-red-600/40">4</span>
                  <p className="text-gray-300">Review detailed offline analysis and recommendations</p>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Right Column - Upload Interface */}
          <div className="lg:col-span-2">
            <Card className="h-fit border-red-800/30" style={{ backgroundColor: 'rgba(0, 0, 0, 0.8)', backdropFilter: 'blur(4px)' }}>
              <CardHeader>
                <CardTitle className="text-white">Upload Log Files</CardTitle>
              </CardHeader>
              <CardContent>
                
                {/* Upload Area - Matching the provided image */}
                <div 
                  className={`border-2 border-dashed rounded-lg p-12 text-center transition-colors ${
                    dragActive 
                      ? 'border-red-400 bg-red-900/30' 
                      : 'border-red-800/40 bg-black/30'
                  }`}
                  onDragEnter={handleDrag}
                  onDragLeave={handleDrag}
                  onDragOver={handleDrag}
                  onDrop={handleDrop}
                >
                  <div className="flex flex-col items-center space-y-4">
                    <div className="w-16 h-16 bg-gradient-to-br from-red-500 to-red-700 rounded-2xl text-white flex items-center justify-center shadow-2xl">
                      <Upload className="w-8 h-8" />
                    </div>
                    <div>
                      <h3 className="text-lg font-semibold text-white mb-2">
                        Drop log files here or click to browse
                      </h3>
                      <p className="text-sm text-gray-300">
                        Supports .log, .txt, .xml, .csv, .zip files up to 100MB
                      </p>
                    </div>
                    <Button 
                      onClick={() => fileInputRef.current?.click()}
                      className="bg-gradient-to-r from-red-500 to-red-600 hover:from-red-600 hover:to-red-700 text-white transform hover:scale-105 transition-all duration-300"
                    >
                      Choose Files
                    </Button>
                  </div>
                  
                  <input
                    ref={fileInputRef}
                    type="file"
                    multiple
                    accept=".log,.txt,.xml,.csv,.zip"
                    onChange={handleFileSelect}
                    className="hidden"
                  />
                </div>

                {/* Uploaded Files List */}
                {uploadedFiles.length > 0 && (
                  <div className="mt-6 space-y-2">
                    <h4 className="font-semibold text-white">Uploaded Files ({uploadedFiles.length})</h4>
                    {uploadedFiles.map((file, index) => (
                      <div key={index} className="flex items-center justify-between bg-black/60 backdrop-blur-sm p-3 rounded border border-red-800/30">
                        <div className="flex items-center space-x-3">
                          <FileText className="w-5 h-5 text-red-400" />
                          <div>
                            <p className="font-medium text-white">{file.name}</p>
                            <p className="text-sm text-gray-300">{(file.size / 1024 / 1024).toFixed(2)} MB</p>
                          </div>
                        </div>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => removeFile(index)}
                          className="text-red-400 hover:text-red-300 hover:bg-red-800/30"
                        >
                          Remove
                        </Button>
                      </div>
                    ))}
                  </div>
                )}

                {/* Start Analysis Button */}
                <div className="mt-8 flex justify-center">
                  <Button
                    onClick={startAnalysis}
                    disabled={uploadedFiles.length === 0 || isAnalyzing}
                    className="bg-gradient-to-r from-red-700 to-red-800 hover:from-red-800 hover:to-red-900 text-white px-8 py-3 text-lg transform hover:scale-105 transition-all duration-300 shadow-lg"
                    size="lg"
                  >
                    {isAnalyzing ? (
                      <>
                        <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
                        Analyzing...
                      </>
                    ) : (
                      <>
                        <Brain className="w-5 h-5 mr-2" />
                        Start AI Analysis
                      </>
                    )}
                  </Button>
                </div>

                {/* Results Section */}
                {results && (
                  <div className="mt-8 space-y-6">
                    
                    {/* Analysis Summary */}
                    <Card className="bg-black/60 backdrop-blur-sm border border-red-600/40">
                      <CardHeader>
                        <CardTitle className="flex items-center space-x-2 text-red-400">
                          <CheckCircle className="w-5 h-5" />
                          <span>Analysis Complete</span>
                        </CardTitle>
                      </CardHeader>
                      <CardContent>
                        <p className="text-red-300 mb-4">{results.summary}</p>
                        
                        {/* Metadata Display */}
                        {results.metadata && (
                          <div className="grid grid-cols-2 md:grid-cols-3 gap-4 mt-4">
                            <div className="bg-red-900/20 p-3 rounded border border-red-800/30">
                              <div className="text-red-400 text-sm font-medium">Files Processed</div>
                              <div className="text-white text-lg font-bold">{results.metadata.files_processed || 0}</div>
                            </div>
                            
                            {results.metadata.zip_files_extracted && results.metadata.zip_files_extracted > 0 && (
                              <>
                                <div className="bg-red-900/20 p-3 rounded border border-red-800/30">
                                  <div className="text-red-400 text-sm font-medium">ZIP Files Extracted</div>
                                  <div className="text-white text-lg font-bold">{results.metadata.zip_files_extracted}</div>
                                </div>
                                <div className="bg-red-900/20 p-3 rounded border border-red-800/30">
                                  <div className="text-red-400 text-sm font-medium">Extracted Files</div>
                                  <div className="text-white text-lg font-bold">{results.metadata.extracted_files}</div>
                                </div>
                              </>
                            )}
                            
                            <div className="bg-red-900/20 p-3 rounded border border-red-800/30">
                              <div className="text-red-400 text-sm font-medium">Log Entries</div>
                              <div className="text-white text-lg font-bold">{results.metadata.log_entries_processed || 0}</div>
                            </div>
                            
                            <div className="bg-red-900/20 p-3 rounded border border-red-800/30">
                              <div className="text-red-400 text-sm font-medium">Offline Issues</div>
                              <div className="text-white text-lg font-bold">{results.metadata.offline_issues || 0}</div>
                            </div>
                            
                            <div className="bg-red-900/20 p-3 rounded border border-red-800/30">
                              <div className="text-red-400 text-sm font-medium">Critical Issues</div>
                              <div className="text-white text-lg font-bold">{results.metadata.critical_issues || 0}</div>
                            </div>
                          </div>
                        )}
                      </CardContent>
                    </Card>

                    {/* AI Communication Analysis Results */}
                    {results.ai_communication_analysis && (
                      <Card className="bg-gradient-to-br from-blue-950/30 to-purple-950/30 backdrop-blur-sm border border-blue-600/40">
                        <CardHeader>
                          <CardTitle className="flex items-center space-x-2 text-blue-300">
                            <Brain className="w-5 h-5" />
                            <span>AI Communication Analysis</span>
                            <Badge variant="secondary" className="bg-blue-900/30 text-blue-300 border border-blue-700/40 ml-2">
                              AI-Powered
                            </Badge>
                          </CardTitle>
                        </CardHeader>
                        <CardContent className="space-y-6">
                          {/* Communication Health Score */}
                          <div className="bg-blue-950/30 p-4 rounded border border-blue-800/30">
                            <div className="flex items-center justify-between mb-3">
                              <h3 className="text-lg font-semibold text-blue-300">Communication Health Score</h3>
                              <div className="flex items-center space-x-2">
                                <div className={`w-3 h-3 rounded-full ${
                                  results.ai_communication_analysis.communication_health_score > 0.7 ? 'bg-green-500' :
                                  results.ai_communication_analysis.communication_health_score > 0.4 ? 'bg-yellow-500' : 'bg-red-500'
                                }`}></div>
                                <span className="text-white font-bold text-xl">
                                  {(results.ai_communication_analysis.communication_health_score * 100).toFixed(1)}%
                                </span>
                              </div>
                            </div>
                            <div className="w-full bg-gray-700 rounded-full h-3">
                              <div 
                                className={`h-3 rounded-full transition-all duration-500 ${
                                  results.ai_communication_analysis.communication_health_score > 0.7 ? 'bg-green-500' :
                                  results.ai_communication_analysis.communication_health_score > 0.4 ? 'bg-yellow-500' : 'bg-red-500'
                                }`}
                                style={{ width: `${results.ai_communication_analysis.communication_health_score * 100}%` }}
                              ></div>
                            </div>
                          </div>

                          {/* AI Detected Issues */}
                          {results.ai_communication_analysis.ai_detected_issues && results.ai_communication_analysis.ai_detected_issues.length > 0 && (
                            <div className="space-y-4">
                              <h3 className="text-lg font-semibold text-blue-300 flex items-center">
                                <AlertCircle className="w-5 h-5 mr-2" />
                                AI-Detected Communication Issues ({results.ai_communication_analysis.ai_detected_issues.length})
                              </h3>
                              <div className="grid gap-4">
                                {results.ai_communication_analysis.ai_detected_issues.map((issue, index) => (
                                  <Card key={index} className="bg-gray-900/50 border-gray-700/50">
                                    <CardContent className="p-4">
                                      <div className="flex items-start justify-between mb-3">
                                        <div className="flex items-center space-x-2">
                                          <Badge 
                                            variant="secondary" 
                                            className={`${
                                              issue.severity === 'critical' ? 'bg-red-900/30 text-red-300 border-red-700/40' :
                                              issue.severity === 'high' ? 'bg-orange-900/30 text-orange-300 border-orange-700/40' :
                                              'bg-yellow-900/30 text-yellow-300 border-yellow-700/40'
                                            }`}
                                          >
                                            {issue.severity.toUpperCase()}
                                          </Badge>
                                          <span className="text-white font-medium">{issue.category.replace(/_/g, ' ').toUpperCase()}</span>
                                        </div>
                                        <div className="flex items-center space-x-2">
                                          <span className="text-sm text-gray-400">Confidence:</span>
                                          <span className="text-blue-300 font-bold">{(issue.confidence_score * 100).toFixed(0)}%</span>
                                        </div>
                                      </div>
                                      
                                      <p className="text-gray-300 text-sm mb-3">{issue.ai_context}</p>
                                      
                                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-3">
                                        <div>
                                          <span className="text-gray-400 text-sm">Affected Ports:</span>
                                          <div className="flex flex-wrap gap-1 mt-1">
                                            {issue.ports_affected.map((port, portIndex) => (
                                              <Badge key={portIndex} variant="outline" className="text-xs text-blue-300 border-blue-600/40">
                                                {port}
                                              </Badge>
                                            ))}
                                          </div>
                                        </div>
                                        <div>
                                          <span className="text-gray-400 text-sm">Communication Direction:</span>
                                          <p className="text-white text-sm mt-1">{issue.communication_direction.replace(/_/g, ' ')}</p>
                                        </div>
                                      </div>
                                      
                                      {issue.matches && issue.matches.length > 0 && (
                                        <div className="mt-3">
                                          <span className="text-gray-400 text-sm">Sample Matches ({issue.issue_count} total):</span>
                                          <div className="mt-1 space-y-1 max-h-20 overflow-y-auto">
                                            {issue.matches.slice(0, 2).map((match, matchIndex) => (
                                              <div key={matchIndex} className="text-xs text-gray-300 bg-gray-800/50 p-2 rounded">
                                                Line {match.line_number}: {match.content}
                                              </div>
                                            ))}
                                          </div>
                                        </div>
                                      )}
                                    </CardContent>
                                  </Card>
                                ))}
                              </div>
                            </div>
                          )}

                          {/* Network Architecture Analysis */}
                          {results.ai_communication_analysis.network_architecture_analysis && (
                            <div className="space-y-4">
                              <h3 className="text-lg font-semibold text-blue-300 flex items-center">
                                <Database className="w-5 h-5 mr-2" />
                                Network Architecture Analysis
                              </h3>
                              
                              {/* Port Health Analysis */}
                              {Object.keys(results.ai_communication_analysis.network_architecture_analysis.port_health_analysis || {}).length > 0 && (
                                <Card className="bg-gray-900/50 border-gray-700/50">
                                  <CardHeader>
                                    <CardTitle className="text-blue-300 text-base">Port Health Status</CardTitle>
                                  </CardHeader>
                                  <CardContent>
                                    <div className="grid gap-3">
                                      {Object.values(results.ai_communication_analysis.network_architecture_analysis.port_health_analysis).map((portInfo, index) => (
                                        <div key={index} className="flex items-center justify-between p-3 bg-gray-800/50 rounded">
                                          <div className="flex items-center space-x-3">
                                            <Badge variant="outline" className="text-blue-300 border-blue-600/40">
                                              Port {(portInfo as Record<string, unknown>).port as number}
                                            </Badge>
                                            <div>
                                              <div className="flex items-center space-x-2">
                                                <div className={`w-2 h-2 rounded-full ${
                                                  (portInfo as Record<string, unknown>).health_status === 'critical' ? 'bg-red-500' :
                                                  (portInfo as Record<string, unknown>).health_status === 'degraded' ? 'bg-yellow-500' : 'bg-green-500'
                                                }`}></div>
                                                <span className="text-white text-sm font-medium">{(portInfo as Record<string, unknown>).health_status as string}</span>
                                              </div>
                                              <div className="text-xs text-gray-400 mt-1">
                                                Services: {Array.isArray((portInfo as Record<string, unknown>).services) ? 
                                                  ((portInfo as Record<string, unknown>).services as string[]).join(', ') : 'N/A'}
                                              </div>
                                            </div>
                                          </div>
                                        </div>
                                      ))}
                                    </div>
                                  </CardContent>
                                </Card>
                              )}

                              {/* AI Network Recommendations */}
                              {results.ai_communication_analysis.network_architecture_analysis.ai_network_recommendations && 
                               results.ai_communication_analysis.network_architecture_analysis.ai_network_recommendations.length > 0 && (
                                <Card className="bg-gray-900/50 border-gray-700/50">
                                  <CardHeader>
                                    <CardTitle className="text-blue-300 text-base">AI Network Recommendations</CardTitle>
                                  </CardHeader>
                                  <CardContent>
                                    <div className="space-y-3">
                                      {results.ai_communication_analysis.network_architecture_analysis.ai_network_recommendations.map((rec, index) => (
                                        <div key={index} className="p-3 rounded bg-gray-800/50 border border-gray-700/50">
                                          <div className="flex items-start justify-between mb-2">
                                            <Badge 
                                              variant="secondary" 
                                              className={`${
                                                rec.priority === 'critical' ? 'bg-red-900/30 text-red-300 border-red-700/40' :
                                                rec.priority === 'high' ? 'bg-orange-900/30 text-orange-300 border-orange-700/40' :
                                                'bg-blue-900/30 text-blue-300 border-blue-700/40'
                                              }`}
                                            >
                                              {rec.priority.toUpperCase()}
                                            </Badge>
                                            <span className="text-xs text-gray-400">{rec.category}</span>
                                          </div>
                                          <p className="text-white text-sm mb-2">{rec.recommendation}</p>
                                          <div className="text-xs text-gray-300">
                                            <span className="font-medium">Actions:</span>
                                            <ul className="list-disc list-inside mt-1 space-y-1">
                                              {rec.actions.map((action, actionIndex) => (
                                                <li key={actionIndex}>{action}</li>
                                              ))}
                                            </ul>
                                          </div>
                                        </div>
                                      ))}
                                    </div>
                                  </CardContent>
                                </Card>
                              )}
                            </div>
                          )}

                          {/* Intelligent Diagnostics */}
                          {results.ai_communication_analysis.intelligent_diagnostics && (
                            <div className="space-y-4">
                              <h3 className="text-lg font-semibold text-blue-300 flex items-center">
                                <Zap className="w-5 h-5 mr-2" />
                                AI Intelligent Diagnostics
                              </h3>

                              {/* AI Troubleshooting Steps */}
                              {results.ai_communication_analysis.intelligent_diagnostics.ai_troubleshooting_steps && 
                               results.ai_communication_analysis.intelligent_diagnostics.ai_troubleshooting_steps.length > 0 && (
                                <Card className="bg-gray-900/50 border-gray-700/50">
                                  <CardHeader>
                                    <CardTitle className="text-blue-300 text-base">AI-Powered Troubleshooting Steps</CardTitle>
                                  </CardHeader>
                                  <CardContent>
                                    <div className="space-y-4">
                                      {results.ai_communication_analysis.intelligent_diagnostics.ai_troubleshooting_steps.map((step, index) => (
                                        <div key={index} className="p-4 rounded bg-gray-800/50 border border-gray-700/50">
                                          <div className="flex items-start justify-between mb-3">
                                            <div className="flex items-center space-x-2">
                                              <Badge variant="outline" className="text-blue-300 border-blue-600/40">
                                                Step {step.priority}
                                              </Badge>
                                              <span className="text-white font-medium">{step.step}</span>
                                            </div>
                                            <div className="text-right">
                                              <div className="text-xs text-gray-400">ETA: {step.expected_resolution_time}</div>
                                              {step.automation_available && (
                                                <Badge variant="secondary" className="bg-green-900/30 text-green-300 border-green-700/40 text-xs mt-1">
                                                  Automatable
                                                </Badge>
                                              )}
                                            </div>
                                          </div>
                                          <div className="space-y-2">
                                            {step.actions.map((action, actionIndex) => (
                                              <div key={actionIndex} className="flex items-start space-x-2">
                                                <CheckCircle className="w-4 h-4 text-blue-400 mt-0.5 flex-shrink-0" />
                                                <span className="text-gray-300 text-sm">{action}</span>
                                              </div>
                                            ))}
                                          </div>
                                        </div>
                                      ))}
                                    </div>
                                  </CardContent>
                                </Card>
                              )}

                              {/* Automated Commands */}
                              {results.ai_communication_analysis.intelligent_diagnostics.automated_commands && (
                                <Card className="bg-gray-900/50 border-gray-700/50">
                                  <CardHeader>
                                    <CardTitle className="text-blue-300 text-base">Platform-Specific Automated Commands</CardTitle>
                                  </CardHeader>
                                  <CardContent>
                                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                      {/* Windows Commands */}
                                      {results.ai_communication_analysis.intelligent_diagnostics.automated_commands.windows && (
                                        <div>
                                          <h4 className="text-white font-medium mb-2 flex items-center">
                                            <span className="w-4 h-4 mr-2">🪟</span>
                                            Windows Commands
                                          </h4>
                                          <div className="space-y-2">
                                            {results.ai_communication_analysis.intelligent_diagnostics.automated_commands.windows.map((cmd, index) => (
                                              <div key={index} className="p-2 bg-gray-800/50 rounded border border-gray-700/50 font-mono text-xs text-gray-300">
                                                {cmd}
                                              </div>
                                            ))}
                                          </div>
                                        </div>
                                      )}
                                      
                                      {/* Linux Commands */}
                                      {results.ai_communication_analysis.intelligent_diagnostics.automated_commands.linux && (
                                        <div>
                                          <h4 className="text-white font-medium mb-2 flex items-center">
                                            <span className="w-4 h-4 mr-2">🐧</span>
                                            Linux Commands
                                          </h4>
                                          <div className="space-y-2">
                                            {results.ai_communication_analysis.intelligent_diagnostics.automated_commands.linux.map((cmd, index) => (
                                              <div key={index} className="p-2 bg-gray-800/50 rounded border border-gray-700/50 font-mono text-xs text-gray-300">
                                                {cmd}
                                              </div>
                                            ))}
                                          </div>
                                        </div>
                                      )}
                                    </div>
                                  </CardContent>
                                </Card>
                              )}

                              {/* Confidence Analysis */}
                              {results.ai_communication_analysis.intelligent_diagnostics.confidence_analysis && (
                                <Card className="bg-gray-900/50 border-gray-700/50">
                                  <CardHeader>
                                    <CardTitle className="text-blue-300 text-base">AI Confidence Analysis</CardTitle>
                                  </CardHeader>
                                  <CardContent>
                                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                                      <div className="text-center p-3 bg-gray-800/50 rounded">
                                        <div className="text-2xl font-bold text-blue-300">
                                          {(results.ai_communication_analysis.intelligent_diagnostics.confidence_analysis.overall_confidence * 100).toFixed(0)}%
                                        </div>
                                        <div className="text-xs text-gray-400 mt-1">Overall Confidence</div>
                                      </div>
                                      <div className="text-center p-3 bg-gray-800/50 rounded">
                                        <div className="text-2xl font-bold text-green-300">
                                          {results.ai_communication_analysis.intelligent_diagnostics.confidence_analysis.high_confidence_issues}
                                        </div>
                                        <div className="text-xs text-gray-400 mt-1">High Confidence Issues</div>
                                      </div>
                                      <div className="text-center p-3 bg-gray-800/50 rounded">
                                        <div className={`text-2xl font-bold ${
                                          results.ai_communication_analysis.intelligent_diagnostics.confidence_analysis.ai_recommendation_reliability === 'high' ? 'text-green-300' :
                                          results.ai_communication_analysis.intelligent_diagnostics.confidence_analysis.ai_recommendation_reliability === 'medium' ? 'text-yellow-300' : 'text-red-300'
                                        }`}>
                                          {results.ai_communication_analysis.intelligent_diagnostics.confidence_analysis.ai_recommendation_reliability.toUpperCase()}
                                        </div>
                                        <div className="text-xs text-gray-400 mt-1">Recommendation Reliability</div>
                                      </div>
                                    </div>
                                  </CardContent>
                                </Card>
                              )}
                            </div>
                          )}
                        </CardContent>
                      </Card>
                    )}

                    {/* AI Enhanced Root Cause Analysis */}
                    {results.ai_enhanced_root_cause && (
                      <Card className="bg-gradient-to-br from-purple-950/30 to-pink-950/30 backdrop-blur-sm border border-purple-600/40">
                        <CardHeader>
                          <CardTitle className="flex items-center space-x-2 text-purple-300">
                            <Brain className="w-5 h-5" />
                            <span>AI Enhanced Root Cause Analysis</span>
                            <Badge variant="secondary" className="bg-purple-900/30 text-purple-300 border border-purple-700/40 ml-2">
                              Advanced AI
                            </Badge>
                          </CardTitle>
                        </CardHeader>
                        <CardContent className="space-y-4">
                          {/* Resolution Confidence */}
                          <div className="bg-purple-950/30 p-4 rounded border border-purple-800/30">
                            <div className="flex items-center justify-between">
                              <h3 className="text-lg font-semibold text-purple-300">Resolution Confidence</h3>
                              <div className="text-right">
                                <div className="text-2xl font-bold text-white">
                                  {(results.ai_enhanced_root_cause.resolution_confidence * 100).toFixed(0)}%
                                </div>
                                <div className="text-xs text-gray-400">AI Prediction</div>
                              </div>
                            </div>
                            <div className="w-full bg-gray-700 rounded-full h-2 mt-3">
                              <div 
                                className="h-2 rounded-full bg-gradient-to-r from-purple-500 to-pink-500 transition-all duration-500"
                                style={{ width: `${results.ai_enhanced_root_cause.resolution_confidence * 100}%` }}
                              ></div>
                            </div>
                          </div>

                          {/* Primary Causes */}
                          {results.ai_enhanced_root_cause.ai_primary_causes && results.ai_enhanced_root_cause.ai_primary_causes.length > 0 && (
                            <div>
                              <h3 className="text-lg font-semibold text-purple-300 mb-3">AI-Identified Primary Causes</h3>
                              <div className="space-y-3">
                                {results.ai_enhanced_root_cause.ai_primary_causes.map((cause, index) => (
                                  <Card key={index} className="bg-gray-900/50 border-gray-700/50">
                                    <CardContent className="p-4">
                                      <div className="flex items-start justify-between mb-3">
                                        <div className="flex items-center space-x-2">
                                          <Badge 
                                            variant="secondary" 
                                            className={`${
                                              cause.impact_level === 'critical' ? 'bg-red-900/30 text-red-300 border-red-700/40' :
                                              cause.impact_level === 'high' ? 'bg-orange-900/30 text-orange-300 border-orange-700/40' :
                                              'bg-yellow-900/30 text-yellow-300 border-yellow-700/40'
                                            }`}
                                          >
                                            {cause.impact_level.toUpperCase()}
                                          </Badge>
                                          <span className="font-medium text-white">{cause.cause.replace(/_/g, ' ').toUpperCase()}</span>
                                        </div>
                                        <div className="text-right">
                                          <div className="text-purple-300 font-bold">{(cause.confidence * 100).toFixed(0)}%</div>
                                          <div className="text-xs text-gray-400">Confidence</div>
                                        </div>
                                      </div>
                                      <p className="text-gray-300 text-sm mb-2">{cause.description}</p>
                                      <div className="text-xs text-gray-400">
                                        <span className="font-medium">Affected Communications:</span> {cause.affected_communications}
                                      </div>
                                    </CardContent>
                                  </Card>
                                ))}
                              </div>
                            </div>
                          )}
                        </CardContent>
                      </Card>
                    )}

                    {/* Dynamic RAG Analysis */}
                    {results.dynamic_rag_analysis && results.dynamic_rag_analysis.ai_response && (
                      <Card className="bg-gradient-to-br from-green-950/30 to-teal-950/30 backdrop-blur-sm border border-green-600/40">
                        <CardHeader>
                          <CardTitle className="flex items-center space-x-2 text-green-300">
                            <Database className="w-5 h-5" />
                            <span>Dynamic RAG Intelligence</span>
                            <Badge variant="secondary" className="bg-green-900/30 text-green-300 border border-green-700/40 ml-2">
                              Knowledge-Powered
                            </Badge>
                          </CardTitle>
                        </CardHeader>
                        <CardContent>
                          <div className="space-y-4">
                            {/* Knowledge Sources Metadata */}
                            {results.dynamic_rag_analysis.analysis_metadata && (
                              <div className="flex items-center justify-between p-3 bg-green-950/30 rounded border border-green-800/30">
                                <div className="flex items-center space-x-4">
                                  <div className="text-center">
                                    <div className="text-2xl font-bold text-green-300">
                                      {results.dynamic_rag_analysis.analysis_metadata.knowledge_sources_used}
                                    </div>
                                    <div className="text-xs text-gray-400">Knowledge Sources</div>
                                  </div>
                                  <div className="text-center">
                                    <div className="text-2xl font-bold text-green-300">
                                      {(results.dynamic_rag_analysis.analysis_metadata.confidence_score * 100).toFixed(0)}%
                                    </div>
                                    <div className="text-xs text-gray-400">RAG Confidence</div>
                                  </div>
                                </div>
                                <Badge variant="outline" className="text-green-300 border-green-600/40">
                                  Deep Security Expert Knowledge
                                </Badge>
                              </div>
                            )}

                            {/* AI Response */}
                            <div className="bg-gray-900/50 p-4 rounded border border-green-700/30">
                              <h3 className="text-green-300 font-medium mb-3 flex items-center">
                                <Brain className="w-4 h-4 mr-2" />
                                AI Expert Analysis
                              </h3>
                              <div className="text-gray-300 whitespace-pre-wrap text-sm leading-relaxed">
                                {results.dynamic_rag_analysis.ai_response}
                              </div>
                            </div>
                          </div>
                        </CardContent>
                      </Card>
                    )}

                    {/* ML Insights */}
                    {results.ml_insights && results.ml_insights.confidence_score && (
                      <Card className="bg-gradient-to-br from-yellow-950/30 to-orange-950/30 backdrop-blur-sm border border-yellow-600/40">
                        <CardHeader>
                          <CardTitle className="flex items-center space-x-2 text-yellow-300">
                            <Zap className="w-5 h-5" />
                            <span>Machine Learning Insights</span>
                            <Badge variant="secondary" className="bg-yellow-900/30 text-yellow-300 border border-yellow-700/40 ml-2">
                              ML-Powered
                            </Badge>
                          </CardTitle>
                        </CardHeader>
                        <CardContent>
                          <div className="space-y-4">
                            {/* ML Confidence Score */}
                            <div className="bg-yellow-950/30 p-4 rounded border border-yellow-800/30">
                              <div className="flex items-center justify-between">
                                <h3 className="text-lg font-semibold text-yellow-300">Pattern Recognition Confidence</h3>
                                <div className="text-right">
                                  <div className="text-2xl font-bold text-white">
                                    {(results.ml_insights.confidence_score * 100).toFixed(0)}%
                                  </div>
                                  <div className="text-xs text-gray-400">ML Analysis</div>
                                </div>
                              </div>
                              <div className="w-full bg-gray-700 rounded-full h-2 mt-3">
                                <div 
                                  className="h-2 rounded-full bg-gradient-to-r from-yellow-500 to-orange-500 transition-all duration-500"
                                  style={{ width: `${results.ml_insights.confidence_score * 100}%` }}
                                ></div>
                              </div>
                            </div>

                            {/* Pattern Analysis Details */}
                            {results.ml_insights.pattern_analysis && Object.keys(results.ml_insights.pattern_analysis).length > 0 && (
                              <div className="bg-gray-900/50 p-4 rounded border border-yellow-700/30">
                                <h3 className="text-yellow-300 font-medium mb-3">Pattern Analysis Details</h3>
                                <div className="text-gray-300 text-sm">
                                  <pre className="whitespace-pre-wrap">
                                    {JSON.stringify(results.ml_insights.pattern_analysis, null, 2)}
                                  </pre>
                                </div>
                              </div>
                            )}
                          </div>
                        </CardContent>
                      </Card>
                    )}

                    {/* Extracted Files Display */}
                    {results.extractedFiles && results.extractedFiles.length > 0 && (
                      <Card className="bg-black/60 backdrop-blur-sm border border-red-600/40">
                        <CardHeader>
                          <CardTitle className="flex items-center space-x-2 text-red-400">
                            <FileText className="w-5 h-5" />
                            <span>Extracted Files ({results.extractedFiles.length})</span>
                          </CardTitle>
                        </CardHeader>
                        <CardContent>
                          <div className="space-y-2">
                            {results.extractedFiles.map((file, index) => (
                              <div key={index} className="flex items-center justify-between bg-red-900/20 p-3 rounded border border-red-800/30">
                                <div className="flex items-center space-x-3">
                                  <FileText className="w-5 h-5 text-red-400" />
                                  <div>
                                    <p className="font-medium text-white">{file.name}</p>
                                    <p className="text-sm text-red-300">{file.type}</p>
                                  </div>
                                </div>
                                <Badge variant="secondary" className="bg-green-900/30 text-green-300 border border-green-700/40">
                                  <CheckCircle className="w-3 h-3 mr-1" />
                                  Analyzed
                                </Badge>
                              </div>
                            ))}
                          </div>
                        </CardContent>
                      </Card>
                    )}

                    {/* AI-Enhanced Analysis Results */}
                    {results.data && (
                      <div className="space-y-6">
                        {/* Debug Information */}
                        <Card className="bg-yellow-950/50 backdrop-blur-sm border border-yellow-500/40">
                          <CardHeader>
                            <CardTitle className="text-yellow-300 text-sm">
                              🔍 Debug: Data Structure Available
                            </CardTitle>
                          </CardHeader>
                          <CardContent>
                            <div className="text-yellow-200 text-xs">
                              <div>AI Analysis: {results.data.analysis_result?.ai_analysis ? '✅ Available' : '❌ Missing'}</div>
                              <div>RAG Insights: {results.data.analysis_result?.rag_insights ? '✅ Available' : '❌ Missing'}</div>
                              <div>Raw Data: {results.data.analysis_result?.raw_data ? '✅ Available' : '❌ Missing'}</div>
                              <div>Communication Analysis: {results.data.analysis_result?.raw_data?.ai_communication_analysis ? '✅ Available' : '❌ Missing'}</div>
                              <div>AI Issues: {results.data.analysis_result?.raw_data?.ai_communication_analysis?.ai_detected_issues ? `✅ ${Array.isArray(results.data.analysis_result.raw_data.ai_communication_analysis.ai_detected_issues) ? results.data.analysis_result.raw_data.ai_communication_analysis.ai_detected_issues.length : 'Not Array'} issues` : '❌ Missing'}</div>
                            </div>
                          </CardContent>
                        </Card>
                        
                        {/* AI Communication Analysis */}
                        {(results.data.analysis_result?.ai_analysis || results.data.summary || results.data.metadata) && (
                          <Card className="bg-gradient-to-br from-blue-950/80 to-purple-950/80 backdrop-blur-sm border border-blue-500/40">
                            <CardHeader>
                              <CardTitle className="flex items-center space-x-2 text-blue-300">
                                <Brain className="w-5 h-5" />
                                <span>AI Communication Analysis</span>
                                {results.data.analysis_result?.ai_analysis?.confidence_score && (
                                  <Badge variant="secondary" className="bg-blue-600/20 text-blue-300 border-blue-500/30">
                                    {results.data.analysis_result.ai_analysis.confidence_score}% Confidence
                                  </Badge>
                                )}
                              </CardTitle>
                            </CardHeader>
                            <CardContent className="space-y-4">
                              {results.data.analysis_result?.ai_analysis?.classification && (
                                <div className="bg-blue-950/50 p-4 rounded border border-blue-800/30">
                                  <h4 className="text-blue-200 font-medium mb-2">Analysis Classification</h4>
                                  <p className="text-blue-300">{results.data.analysis_result.ai_analysis.classification}</p>
                                </div>
                              )}
                              
                              {results.data.analysis_result?.ai_analysis?.intelligent_insights && (
                                <div className="bg-blue-950/50 p-4 rounded border border-blue-800/30">
                                  <h4 className="text-blue-200 font-medium mb-2">AI Insights</h4>
                                  <ul className="space-y-2">
                                    {results.data.analysis_result.ai_analysis.intelligent_insights.map((insight: string, idx: number) => (
                                      <li key={idx} className="flex items-start space-x-2 text-blue-300">
                                        <CheckCircle className="w-4 h-4 mt-0.5 text-blue-400" />
                                        <span>{insight}</span>
                                      </li>
                                    ))}
                                  </ul>
                                </div>
                              )}

                              {results.data.analysis_result?.ai_analysis?.anomaly_detection && (
                                <div className="bg-blue-950/50 p-4 rounded border border-blue-800/30">
                                  <h4 className="text-blue-200 font-medium mb-2">Anomaly Detection</h4>
                                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                                    <div className="text-center">
                                      <div className="text-2xl font-bold text-blue-300">
                                        {results.data.analysis_result.ai_analysis.anomaly_detection.anomalies_found || 0}
                                      </div>
                                      <div className="text-blue-400 text-sm">Anomalies Found</div>
                                    </div>
                                    <div className="text-center">
                                      <div className="text-lg text-blue-300">
                                        {results.data.analysis_result.ai_analysis.anomaly_detection.pattern_analysis || 'N/A'}
                                      </div>
                                      <div className="text-blue-400 text-sm">Pattern Analysis</div>
                                    </div>
                                    <div className="text-center">
                                      <div className="text-lg text-blue-300">
                                        {results.data.analysis_result.ai_analysis.anomaly_detection.severity_distribution || 'Normal'}
                                      </div>
                                      <div className="text-blue-400 text-sm">Severity Distribution</div>
                                    </div>
                                  </div>
                                </div>
                              )}

                              {/* Communication Health Score from raw_data */}
                              {results.data.analysis_result?.raw_data?.ai_communication_analysis?.communication_health_score !== undefined && (
                                <div className="bg-blue-950/50 p-4 rounded border border-blue-800/30">
                                  <h4 className="text-blue-200 font-medium mb-2">Communication Health Score</h4>
                                  <div className="flex items-center space-x-4">
                                    <div className="text-3xl font-bold text-blue-300">
                                      {Math.round(results.data.analysis_result.raw_data.ai_communication_analysis.communication_health_score * 100)}%
                                    </div>
                                    <div className="flex-1">
                                      <div className="w-full bg-gray-700 rounded-full h-3">
                                        <div 
                                          className={`h-3 rounded-full ${
                                            results.data.analysis_result.raw_data.ai_communication_analysis.communication_health_score > 0.7 ? 'bg-green-500' :
                                            results.data.analysis_result.raw_data.ai_communication_analysis.communication_health_score > 0.4 ? 'bg-yellow-500' : 'bg-red-500'
                                          }`}
                                          style={{ width: `${results.data.analysis_result.raw_data.ai_communication_analysis.communication_health_score * 100}%` }}
                                        />
                                      </div>
                                    </div>
                                  </div>
                                </div>
                              )}
                            </CardContent>
                          </Card>
                        )}

                        {/* Dynamic RAG Analysis */}
                        {(results.data.analysis_result?.rag_insights || results.data.summary) && (
                          <Card className="bg-gradient-to-br from-emerald-950/80 to-teal-950/80 backdrop-blur-sm border border-emerald-500/40">
                            <CardHeader>
                              <CardTitle className="flex items-center space-x-2 text-emerald-300">
                                <BookOpen className="w-5 h-5" />
                                <span>Expert Knowledge & Recommendations</span>
                                <Badge variant="secondary" className="bg-emerald-600/20 text-emerald-300 border-emerald-500/30">
                                  Dynamic RAG
                                </Badge>
                              </CardTitle>
                            </CardHeader>
                            <CardContent>
                              {results.data.analysis_result?.rag_insights?.ai_response && (
                                <div className="bg-emerald-950/50 p-4 rounded border border-emerald-800/30">
                                  <div className="prose prose-invert prose-emerald max-w-none">
                                    <div 
                                      className="text-emerald-200 leading-relaxed"
                                      dangerouslySetInnerHTML={{
                                        __html: results.data.analysis_result?.rag_insights?.ai_response || ''
                                          .replace(/\n/g, '<br/>')
                                          .replace(/### (.*?)(?=\n|$)/g, '<h3 class="text-emerald-300 font-bold text-lg mt-4 mb-2">$1</h3>')
                                          .replace(/## (.*?)(?=\n|$)/g, '<h2 class="text-emerald-200 font-bold text-xl mt-6 mb-3">$1</h2>')
                                          .replace(/# (.*?)(?=\n|$)/g, '<h1 class="text-emerald-100 font-bold text-2xl mt-8 mb-4">$1</h1>')
                                          .replace(/\*\*(.*?)\*\*/g, '<strong class="text-emerald-100">$1</strong>')
                                          .replace(/```bash([\s\S]*?)```/g, '<pre class="bg-black/50 p-3 rounded border border-emerald-700/30 text-green-300 text-sm overflow-x-auto"><code>$1</code></pre>')
                                          .replace(/```([\s\S]*?)```/g, '<pre class="bg-black/50 p-3 rounded border border-emerald-700/30 text-emerald-300 text-sm overflow-x-auto"><code>$1</code></pre>')
                                          .replace(/• (.*?)(?=<br|$)/g, '<div class="flex items-start space-x-2 my-1"><span class="text-emerald-400 mt-0.5">•</span><span>$1</span></div>')
                                      }}
                                    />
                                  </div>
                                </div>
                              )}
                              
                              {results.data.analysis_result?.rag_insights?.analysis_metadata && (
                                <div className="mt-4 grid grid-cols-2 md:grid-cols-4 gap-4">
                                  <div className="text-center">
                                    <div className="text-lg font-bold text-emerald-300">
                                      {results.data.analysis_result?.rag_insights?.analysis_metadata?.components_analyzed || 0}
                                    </div>
                                    <div className="text-emerald-400 text-sm">Components Analyzed</div>
                                  </div>
                                  <div className="text-center">
                                    <div className="text-lg font-bold text-emerald-300">
                                      {results.data.analysis_result?.rag_insights?.analysis_metadata?.error_types_found || 0}
                                    </div>
                                    <div className="text-emerald-400 text-sm">Error Types Found</div>
                                  </div>
                                  <div className="text-center">
                                    <div className="text-lg font-bold text-emerald-300">
                                      {results.data.analysis_result?.rag_insights?.analysis_metadata?.knowledge_sources_used || 0}
                                    </div>
                                    <div className="text-emerald-400 text-sm">Knowledge Sources</div>
                                  </div>
                                  <div className="text-center">
                                    <div className="text-lg font-bold text-emerald-300">
                                      {results.data.analysis_result?.rag_insights?.analysis_metadata?.ai_available ? '✅' : '❌'}
                                    </div>
                                    <div className="text-emerald-400 text-sm">AI Available</div>
                                  </div>
                                </div>
                              )}
                            </CardContent>
                          </Card>
                        )}

                        {/* Communication Issues Analysis */}
                        {(results.data.analysis_result?.raw_data?.ai_communication_analysis?.ai_detected_issues || 
                          (results.data.metadata?.errors_found || 0) > 0 ||
                          (results.data.metadata?.critical_issues || 0) > 0) && (
                          <Card className="bg-gradient-to-br from-red-950/80 to-orange-950/80 backdrop-blur-sm border border-red-500/40">
                            <CardHeader>
                              <CardTitle className="flex items-center space-x-2 text-red-300">
                                <AlertTriangle className="w-5 h-5" />
                                <span>Communication Issues Detected</span>
                                <Badge variant="destructive" className="bg-red-600/20 text-red-300 border-red-500/30">
                                  {results.data.analysis_result?.raw_data?.ai_communication_analysis?.ai_detected_issues?.length || 0} Issues
                                </Badge>
                              </CardTitle>
                            </CardHeader>
                            <CardContent className="space-y-4">
                              {results.data.analysis_result?.raw_data?.ai_communication_analysis?.ai_detected_issues && 
                               Array.isArray(results.data.analysis_result.raw_data.ai_communication_analysis.ai_detected_issues) ? 
                               results.data.analysis_result.raw_data.ai_communication_analysis.ai_detected_issues.map((issue: CommunicationIssue, idx: number) => (
                                <div key={idx} className="bg-red-950/50 p-4 rounded border border-red-800/30">
                                  <div className="flex items-start justify-between mb-3">
                                    <h4 className="text-red-200 font-medium capitalize">
                                      {issue.category?.replace(/_/g, ' ') || 'Communication Issue'}
                                    </h4>
                                    <div className="flex items-center space-x-2">
                                      <Badge 
                                        variant={issue.severity === 'critical' ? 'destructive' : 'secondary'}
                                        className={`${
                                          issue.severity === 'critical' ? 'bg-red-600/20 text-red-300 border-red-500/30' :
                                          issue.severity === 'high' ? 'bg-orange-600/20 text-orange-300 border-orange-500/30' :
                                          'bg-yellow-600/20 text-yellow-300 border-yellow-500/30'
                                        }`}
                                      >
                                        {issue.severity?.toUpperCase() || 'MEDIUM'}
                                      </Badge>
                                      {issue.confidence_score && (
                                        <Badge variant="outline" className="text-red-400 border-red-500/30">
                                          {Math.round(issue.confidence_score * 100)}% Confidence
                                        </Badge>
                                      )}
                                    </div>
                                  </div>
                                  
                                  {issue.ai_context && (
                                    <p className="text-red-300 text-sm mb-3 italic">{issue.ai_context}</p>
                                  )}
                                  
                                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                    <div>
                                      <h5 className="text-red-200 font-medium mb-2">Issue Count & Direction</h5>
                                      <div className="space-y-1">
                                        <div className="text-red-300 text-sm">
                                          Issues Found: <span className="font-bold">{issue.issue_count || 0}</span>
                                        </div>
                                        <div className="text-red-300 text-sm">
                                          Direction: <span className="font-bold capitalize">{issue.communication_direction?.replace(/_/g, ' ') || 'Unknown'}</span>
                                        </div>
                                      </div>
                                    </div>
                                    
                                    {issue.ports_affected && issue.ports_affected.length > 0 && (
                                      <div>
                                        <h5 className="text-red-200 font-medium mb-2">Affected Ports</h5>
                                        <div className="flex flex-wrap gap-2">
                                          {issue.ports_affected.map((port: number, portIdx: number) => (
                                            <Badge key={portIdx} variant="outline" className="text-red-400 border-red-500/30">
                                              Port {port}
                                            </Badge>
                                          ))}
                                        </div>
                                      </div>
                                    )}
                                  </div>
                                  
                                  {issue.matches && issue.matches.length > 0 && (
                                    <div className="mt-4">
                                      <h5 className="text-red-200 font-medium mb-2">Log Entries ({issue.matches.length})</h5>
                                      <div className="space-y-2 max-h-40 overflow-y-auto">
                                        {issue.matches.slice(0, 3).map((match: CommunicationIssueMatch, matchIdx: number) => (
                                          <div key={matchIdx} className="bg-black/30 p-2 rounded text-xs">
                                            <div className="text-red-400 font-mono">Line {match.line_number}:</div>
                                            <div className="text-red-300 mt-1">{match.content}</div>
                                          </div>
                                        ))}
                                        {issue.matches.length > 3 && (
                                          <div className="text-red-400 text-xs text-center">
                                            ... and {issue.matches.length - 3} more entries
                                          </div>
                                        )}
                                      </div>
                                    </div>
                                  )}
                                </div>
                              )) : null}
                            </CardContent>
                          </Card>
                        )}

                        {/* Analysis Summary & Statistics */}
                        {(results.data.summary || results.data.statistics) && (
                          <Card className="bg-gradient-to-br from-gray-950/80 to-slate-950/80 backdrop-blur-sm border border-gray-500/40">
                            <CardHeader>
                              <CardTitle className="flex items-center space-x-2 text-gray-300">
                                <BarChart3 className="w-5 h-5" />
                                <span>Analysis Summary & Statistics</span>
                              </CardTitle>
                            </CardHeader>
                            <CardContent className="space-y-4">
                              {results.data.summary && (
                                <div className="bg-gray-950/50 p-4 rounded border border-gray-800/30">
                                  <h4 className="text-gray-200 font-medium mb-2">Summary</h4>
                                  <p className="text-gray-300">{results.data.summary}</p>
                                </div>
                              )}
                              
                              {results.data.statistics && (
                                <div className="bg-gray-950/50 p-4 rounded border border-gray-800/30">
                                  <h4 className="text-gray-200 font-medium mb-3">Analysis Statistics</h4>
                                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                                    {Object.entries(results.data.statistics).map(([key, value]) => (
                                      <div key={key} className="text-center">
                                        <div className="text-lg font-bold text-gray-300">
                                          {typeof value === 'number' ? value : (value as string)?.toString() || 'N/A'}
                                        </div>
                                        <div className="text-gray-400 text-sm capitalize">
                                          {key.replace(/_/g, ' ')}
                                        </div>
                                      </div>
                                    ))}
                                  </div>
                                </div>
                              )}

                              {results.data.metadata && (
                                <div className="bg-gray-950/50 p-4 rounded border border-gray-800/30">
                                  <h4 className="text-gray-200 font-medium mb-3">Analysis Metadata</h4>
                                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                                    <div className="text-center">
                                      <div className="text-lg font-bold text-gray-300">
                                        {results.data.metadata.files_processed || 0}
                                      </div>
                                      <div className="text-gray-400 text-sm">Files Processed</div>
                                    </div>
                                    <div className="text-center">
                                      <div className="text-lg font-bold text-gray-300">
                                        {results.data.metadata.log_entries_processed || 0}
                                      </div>
                                      <div className="text-gray-400 text-sm">Log Entries</div>
                                    </div>
                                    <div className="text-center">
                                      <div className="text-lg font-bold text-gray-300">
                                        {results.data.metadata.errors_found || 0}
                                      </div>
                                      <div className="text-gray-400 text-sm">Errors Found</div>
                                    </div>
                                    <div className="text-center">
                                      <div className="text-lg font-bold text-gray-300">
                                        {results.data.metadata.warnings_found || 0}
                                      </div>
                                      <div className="text-gray-400 text-sm">Warnings Found</div>
                                    </div>
                                  </div>
                                </div>
                              )}
                            </CardContent>
                          </Card>
                        )}

                        {/* Raw Data Expandable Section (for debugging) */}
                        <Card className="bg-black/40 backdrop-blur-sm border border-gray-600/30">
                          <CardHeader>
                            <CardTitle className="flex items-center space-x-2 text-gray-400">
                              <Code className="w-5 h-5" />
                              <span>Technical Details</span>
                              <Badge variant="outline" className="text-gray-500 border-gray-600/30">
                                Advanced
                              </Badge>
                            </CardTitle>
                          </CardHeader>
                          <CardContent>
                            <details className="group">
                              <summary className="cursor-pointer text-gray-400 hover:text-gray-300 transition-colors">
                                <span className="group-open:hidden">Show raw analysis data</span>
                                <span className="hidden group-open:inline">Hide raw analysis data</span>
                              </summary>
                              <div className="mt-4 bg-gray-950/50 p-4 rounded border border-gray-800/30 overflow-auto max-h-96">
                                <pre className="text-gray-400 text-xs whitespace-pre-wrap">
                                  {JSON.stringify(results.data, null, 2)}
                                </pre>
                              </div>
                            </details>
                          </CardContent>
                        </Card>
                      </div>
                    )}

                  </div>
                )}

              </CardContent>
            </Card>
          </div>
        </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="relative z-50 bg-black/70 border-t border-white/10 text-white py-16">
        <div className="max-w-7xl mx-auto px-4">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
            <div className="md:col-span-2">
              <div className="flex items-center space-x-4 mb-4">
                <Image 
                  src="/trendlogo.png" 
                  alt="Trend Micro Logo" 
                  width={32}
                  height={32}
                  className="h-8 w-auto"
                />
                <div className="border-l border-white/30 pl-4">
                  <h3 className="text-xl font-bold text-white">Intellicket</h3>
                  <p className="text-xs text-red-400 font-medium">AI Support Platform</p>
                </div>
              </div>
              <p className="text-gray-300 mb-4 max-w-md">
                Intelligent support system for Trend Micro products. Secure your digital world with AI-powered cybersecurity solutions.
              </p>
              <div className="flex space-x-4">
                <a href="#" className="text-gray-400 hover:text-red-400 transition-colors">
                  <span className="sr-only">Twitter</span>
                  <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                    <path d="M6.29 18.251c7.547 0 11.675-6.253 11.675-11.675 0-.178 0-.355-.012-.53A8.348 8.348 0 0020 3.92a8.19 8.19 0 01-2.357.646 4.118 4.118 0 001.804-2.27 8.224 8.224 0 01-2.605.996 4.107 4.107 0 00-6.993 3.743 11.65 11.65 0 01-8.457-4.287 4.106 4.106 0 001.27 5.477A4.073 4.073 0 01.8 7.713v.052a4.105 4.105 0 003.292 4.022 4.095 4.095 0 01-1.853.07 4.108 4.108 0 003.834 2.85A8.233 8.233 0 010 16.407a11.616 11.616 0 006.29 1.84" />
                  </svg>
                </a>
                <a href="#" className="text-gray-400 hover:text-red-400 transition-colors">
                  <span className="sr-only">LinkedIn</span>
                  <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M16.338 16.338H13.67V12.16c0-.995-.017-2.277-1.387-2.277-1.39 0-1.601 1.086-1.601 2.207v4.248H8.014v-8.59h2.559v1.174h.037c.356-.675 1.227-1.387 2.526-1.387 2.703 0 3.203 1.778 3.203 4.092v4.711zM5.005 6.575a1.548 1.548 0 11-.003-3.096 1.548 1.548 0 01.003 3.096zm-1.337 9.763H6.34v-8.59H3.667v8.59zM17.668 1H2.328C1.595 1 1 1.581 1 2.298v15.403C1 18.418 1.595 19 2.328 19h15.34c.734 0 1.332-.582 1.332-1.299V2.298C19 1.581 18.402 1 17.668 1z" clipRule="evenodd" />
                  </svg>
                </a>
              </div>
            </div>
            <div>
              <h3 className="text-lg font-semibold mb-4 text-red-400">Quick Links</h3>
              <ul className="space-y-3 text-gray-300">
                <li><a href="#" className="hover:text-white transition-colors duration-300 flex items-center"><span className="w-1 h-1 bg-red-500 rounded-full mr-2"></span>Support Center</a></li>
                <li><a href="#" className="hover:text-white transition-colors duration-300 flex items-center"><span className="w-1 h-1 bg-red-500 rounded-full mr-2"></span>Documentation</a></li>
                <li><a href="#" className="hover:text-white transition-colors duration-300 flex items-center"><span className="w-1 h-1 bg-red-500 rounded-full mr-2"></span>Contact Us</a></li>
                <li><a href="#" className="hover:text-white transition-colors duration-300 flex items-center"><span className="w-1 h-1 bg-red-500 rounded-full mr-2"></span>Security Blog</a></li>
              </ul>
            </div>
            <div>
              <h3 className="text-lg font-semibold mb-4 text-red-400">Products</h3>
              <ul className="space-y-3 text-gray-300">
                {products.map((product) => (
                  <li key={product.id}>
                    <button 
                      onClick={() => handleProductSelection(product.id)}
                      className="hover:text-white transition-colors duration-300 text-left flex items-center"
                    >
                      <span className="text-lg mr-2">{product.icon}</span>
                      {product.name}
                    </button>
                  </li>
                ))}
              </ul>
            </div>
          </div>
          <div className="border-t border-white/20 mt-12 pt-8">
            <div className="flex flex-col md:flex-row justify-between items-center">
              <p className="text-gray-400 text-sm">
                &copy; 2025 Intellicket - AI-Powered Cybersecurity Platform. All rights reserved. | Securing your digital transformation.
              </p>
              <div className="flex space-x-6 mt-4 md:mt-0">
                <a href="#" className="text-gray-400 hover:text-white text-sm transition-colors">Privacy Policy</a>
                <a href="#" className="text-gray-400 hover:text-white text-sm transition-colors">Terms of Service</a>
                <a href="#" className="text-gray-400 hover:text-white text-sm transition-colors">Security</a>
              </div>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}