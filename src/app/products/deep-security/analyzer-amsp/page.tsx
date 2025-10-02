'use client'

import React, { useState, useCallback } from 'react'
import Link from 'next/link'
import Image from 'next/image'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'

import { 
  FileText, 
  Upload, 
  AlertTriangle, 
  CheckCircle, 
  Brain,
  Target,
  Wrench,
  Info,
  AlertCircle,
  X,
  ArrowLeft,
  Bug,
  Zap,
  Activity
} from 'lucide-react'

interface AMSPAnalysisResult {
  analysis_type: string
  status: string
  summary: string
  details: string[]
  recommendations: Array<{
    kb_id: string
    title: string
    category: string
    priority: string
    estimated_time: string
    difficulty: string
    prerequisites: string[]
    steps: Array<{
      step_number: number
      instruction: string
      command: string
      expected_result: string
    }>
    verification: string[]
    troubleshooting_tips: string[]
    related_articles: string[]
  }>
  log_interpretation?: {
    title: string
    summary: string
    entries: Array<{
      line_number: number
      timestamp: string
      level: string
      component: string
      raw_message: string
      ai_interpretation: string
      severity_indicator: string
      action_required: string
    }>
    patterns_detected: string[]
    ai_insights: string
  }
  errors?: Array<{
    line: number
    timestamp: string
    operation: string
    message: string
    level: string
  }>
  warnings?: Array<{
    line: number
    timestamp: string
    operation: string
    message: string
    level: string
  }>
  critical_errors?: Array<{
    line: number
    timestamp: string
    operation: string
    message: string
    level: string
  }>
  metadata?: {
    files_processed: number
    log_file: string
    total_lines: number
    errors_found: number
    warnings_found: number
    pattern_failures: number
    bpf_failures: number
    trendx_failures: number
  }
  dynamic_rag_analysis?: {
    ai_response: string
    analysis_metadata: {
      knowledge_sources_used: number
      confidence_score: number
    }
  }
  ml_insights?: {
    health_score: number
    anomaly_score: number
  }
}

export default function AMSPAnalyzerPage() {
  const [selectedFiles, setSelectedFiles] = useState<File[]>([])
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [analysisResult, setAnalysisResult] = useState<AMSPAnalysisResult | null>(null)
  const [error, setError] = useState<string | null>(null)

  // Products array for footer
  const products = [
    { id: 'deep-security', name: 'Deep Security', icon: '🛡️' },
    { id: 'apex-one', name: 'Apex One', icon: '🔒' },
    { id: 'vision-one', name: 'Vision One', icon: '👁️' },
    { id: 'service-gateway', name: 'Service Gateway', icon: '🌐' },
  ];

  const handleFileSelect = useCallback((files: FileList | null) => {
    if (files) {
      const fileArray = Array.from(files)
      // Filter for log files that might be AMSP-related
      const logFiles = fileArray.filter(file => 
        file.name.toLowerCase().includes('ds_am') || 
        file.name.toLowerCase().includes('amsp') ||
        file.name.toLowerCase().includes('.log')
      )
      setSelectedFiles(logFiles.length > 0 ? logFiles : fileArray)
    }
  }, [])

  const removeFile = useCallback((index: number) => {
    setSelectedFiles(prev => prev.filter((_, i) => i !== index))
  }, [])

  const handleAnalysis = async () => {
    if (selectedFiles.length === 0) return
    
    setIsAnalyzing(true)
    setError(null)
    
    try {
      const formData = new FormData()
      selectedFiles.forEach((file, index) => {
        formData.append(`file${index}`, file)
      })
      formData.append('analysis_type', 'amsp')
      
      // Upload files to dedicated AMSP endpoint
      const uploadResponse = await fetch('/api/csdai/amsp/upload', {
        method: 'POST',
        body: formData,
      })
      
      if (!uploadResponse.ok) {
        throw new Error('Upload failed')
      }
      
      const uploadResult = await uploadResponse.json()
      const sessionId = uploadResult.session_id
      
      // Poll for results
      const pollResults = async () => {
        let attempts = 0
        const maxAttempts = 60 // 2 minutes timeout
        
        while (attempts < maxAttempts) {
          try {
            // Check status
            const statusResponse = await fetch(`/api/csdai/amsp/status/${sessionId}`)
            if (statusResponse.ok) {
              const statusResult = await statusResponse.json()
              
              if (statusResult.status === 'completed') {
                // Get results
                const resultsResponse = await fetch(`/api/csdai/amsp/results/${sessionId}`)
                if (resultsResponse.ok) {
                  const results = await resultsResponse.json()
                  setAnalysisResult(results)
                  setIsAnalyzing(false)
                  return
                }
              } else if (statusResult.status === 'error') {
                throw new Error(statusResult.error || 'Analysis failed')
              }
            }
            
            // Wait 2 seconds before next poll
            await new Promise(resolve => setTimeout(resolve, 2000))
            attempts++
          } catch (err) {
            console.error('Polling error:', err)
            attempts++
            await new Promise(resolve => setTimeout(resolve, 2000))
          }
        }
        
        throw new Error('Analysis timeout - please try again')
      }
      
      pollResults()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Analysis failed')
      setIsAnalyzing(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-red-950/10 to-gray-950 relative overflow-hidden">
      {/* Animated Background Elements */}
      <div className="absolute inset-0 opacity-15">
        <div className="absolute top-20 left-20 w-96 h-96 bg-red-500 rounded-full mix-blend-multiply filter blur-3xl animate-pulse"></div>
        <div className="absolute bottom-20 right-20 w-96 h-96 bg-orange-500 rounded-full mix-blend-multiply filter blur-3xl animate-pulse animation-delay-2000"></div>
      </div>

      {/* Header */}
      <header className="relative z-10 bg-black/40 backdrop-blur-sm border-b border-red-500/30">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <Link 
                href="/"
                className="flex items-center space-x-3 hover:opacity-80 transition-opacity"
              >
                <Image 
                  src="/trendlogo.png" 
                  alt="Trend Micro Logo" 
                  width={40}
                  height={40}
                  className="h-10 w-auto"
                />
                <div className="border-l border-white/30 pl-3">
                  <div className="text-xl font-bold text-red-400">Intellicket</div>
                  <div className="text-xs text-gray-400">AI Support Platform</div>
                </div>
              </Link>
              <span className="text-gray-500">→</span>
              <div className="flex items-center space-x-2">
                <span className="text-2xl">🛡️</span>
                <span className="text-white font-semibold">Deep Security</span>
              </div>
              <span className="text-gray-500">→</span>
              <div className="flex items-center space-x-2">
                <Bug className="h-5 w-5 text-orange-400" />
                <span className="text-gray-300 font-medium">AMSP Analyzer</span>
              </div>
            </div>
            <Link
              href="/products/deep-security"
              className="bg-red-500/20 text-red-300 px-6 py-2 rounded-xl hover:bg-red-500/30 transition-all duration-300 border border-red-500/30 flex items-center gap-2"
            >
              <ArrowLeft className="h-4 w-4" />
              Back to Analyzers
            </Link>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="relative z-10 max-w-7xl mx-auto px-4 py-12">
        {/* Enhanced Header with AI Capabilities Showcase */}
        <div className="text-center mb-16">
          <div className="flex items-center justify-center gap-4 mb-6">
            <Link href="/products/deep-security" className="transition-transform hover:scale-105">
              <Image
                src="/trendlogo.png"
                alt="Trend Micro"
                width={60}
                height={60}
                className="drop-shadow-2xl"
              />
            </Link>
            <div className="h-12 w-px bg-gradient-to-b from-transparent via-red-500/50 to-transparent" />
            <div className="relative">
              <Bug className="h-12 w-12 text-orange-500 drop-shadow-lg" />
              <div className="absolute -top-1 -right-1 w-6 h-6 bg-gradient-to-r from-blue-500 to-purple-500 rounded-full flex items-center justify-center animate-pulse">
                <Brain className="h-3 w-3 text-white" />
              </div>
            </div>
          </div>
          
          <div className="mb-8">
            <h1 className="text-6xl font-bold bg-gradient-to-r from-white via-gray-200 to-orange-300 bg-clip-text text-transparent mb-4">
              AMSP Analyzer
            </h1>
            <div className="flex items-center justify-center gap-2 mb-4">
              <Badge className="bg-gradient-to-r from-blue-500/20 to-purple-500/20 text-blue-300 border-blue-500/30 px-3 py-1">
                <Brain className="h-3 w-3 mr-1" />
                AI-Powered
              </Badge>
              <Badge className="bg-gradient-to-r from-purple-500/20 to-pink-500/20 text-purple-300 border-purple-500/30 px-3 py-1">
                <Target className="h-3 w-3 mr-1" />
                ML-Enhanced
              </Badge>
              <Badge className="bg-gradient-to-r from-green-500/20 to-emerald-500/20 text-green-300 border-green-500/30 px-3 py-1">
                <Zap className="h-3 w-3 mr-1" />
                RAG System  
              </Badge>
            </div>
            <p className="text-xl text-gray-300 max-w-4xl mx-auto leading-relaxed">
              Advanced AI-powered analysis of Deep Security Anti-Malware Scan Platform (AMSP) logs. 
              Diagnose pattern loading failures, engine issues, and performance problems with expert-level insights.
            </p>
          </div>
        </div>

        {!analysisResult && (
          <div className="space-y-12">{/* AI Capabilities Showcase */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-16">
            <div className="bg-white/10 backdrop-blur-sm rounded-2xl shadow-2xl p-8 border border-white/20 hover:border-blue-500/40 transition-all duration-500 group transform hover:scale-105">
              <div className="relative mb-6">
                <div className="w-20 h-20 bg-gradient-to-br from-blue-500 to-blue-700 rounded-3xl mb-4 flex items-center justify-center group-hover:scale-110 transition-transform duration-500 mx-auto">
                  <Brain className="h-10 w-10 text-white" />
                </div>
                <div className="absolute -top-2 -right-2 w-8 h-8 bg-gradient-to-r from-cyan-400 to-blue-500 rounded-full flex items-center justify-center animate-bounce">
                  <span className="text-xs font-bold text-white">RAG</span>
                </div>
              </div>
              <h3 className="text-2xl font-bold text-white mb-3 group-hover:text-blue-300 transition-colors text-center">RAG System</h3>
              <p className="text-gray-300 text-center leading-relaxed">
                Dynamic Retrieval-Augmented Generation system that queries expert knowledge bases to provide 
                contextual analysis and expert recommendations for AMSP issues.
              </p>
              <div className="mt-4 flex items-center justify-center">
                <Badge variant="outline" className="border-blue-500/30 text-blue-300 bg-blue-500/10">
                  Knowledge Retrieval
                </Badge>
              </div>
            </div>

            <div className="bg-white/10 backdrop-blur-sm rounded-2xl shadow-2xl p-8 border border-white/20 hover:border-purple-500/40 transition-all duration-500 group transform hover:scale-105">
              <div className="relative mb-6">
                <div className="w-20 h-20 bg-gradient-to-br from-purple-500 to-purple-700 rounded-3xl mb-4 flex items-center justify-center group-hover:scale-110 transition-transform duration-500 mx-auto">
                  <Target className="h-10 w-10 text-white" />
                </div>
                <div className="absolute -top-2 -right-2 w-8 h-8 bg-gradient-to-r from-purple-400 to-pink-500 rounded-full flex items-center justify-center animate-bounce delay-100">
                  <span className="text-xs font-bold text-white">ML</span>
                </div>
              </div>
              <h3 className="text-2xl font-bold text-white mb-3 group-hover:text-purple-300 transition-colors text-center">ML Engine</h3>
              <p className="text-gray-300 text-center leading-relaxed">
                Machine learning algorithms analyze AMSP patterns, classify severity levels, detect anomalies, 
                and predict potential issues based on historical log data.
              </p>
              <div className="mt-4 flex items-center justify-center">
                <Badge variant="outline" className="border-purple-500/30 text-purple-300 bg-purple-500/10">
                  Pattern Recognition
                </Badge>
              </div>
            </div>

            <div className="bg-white/10 backdrop-blur-sm rounded-2xl shadow-2xl p-8 border border-white/20 hover:border-green-500/40 transition-all duration-500 group transform hover:scale-105">
              <div className="relative mb-6">
                <div className="w-20 h-20 bg-gradient-to-br from-green-500 to-green-700 rounded-3xl mb-4 flex items-center justify-center group-hover:scale-110 transition-transform duration-500 mx-auto">
                  <Activity className="h-10 w-10 text-white" />
                </div>
                <div className="absolute -top-2 -right-2 w-8 h-8 bg-gradient-to-r from-emerald-400 to-green-500 rounded-full flex items-center justify-center animate-bounce delay-200">
                  <span className="text-xs font-bold text-white">AI</span>
                </div>
              </div>
              <h3 className="text-2xl font-bold text-white mb-3 group-hover:text-green-300 transition-colors text-center">AI Insights</h3>
              <p className="text-gray-300 text-center leading-relaxed">
                Intelligent diagnostic insights with confidence scoring and automated root cause analysis. 
                Provides expert-level troubleshooting recommendations with step-by-step guidance.
              </p>
              <div className="mt-4 flex items-center justify-center">
                <Badge variant="outline" className="border-green-500/30 text-green-300 bg-green-500/10">
                  Expert Analysis
                </Badge>
              </div>
            </div>
          </div>

          {/* Core Technology Stats */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-16">
            <div className="text-center p-4 bg-white/5 rounded-xl border border-white/10">
              <div className="text-2xl font-bold text-orange-400 mb-1">95%+</div>
              <div className="text-xs text-gray-400">Pattern Detection</div>
            </div>
            <div className="text-center p-4 bg-white/5 rounded-xl border border-white/10">
              <div className="text-2xl font-bold text-purple-400 mb-1">&lt;60s</div>
              <div className="text-xs text-gray-400">Analysis Time</div>
            </div>
            <div className="text-center p-4 bg-white/5 rounded-xl border border-white/10">
              <div className="text-2xl font-bold text-green-400 mb-1">100+</div>
              <div className="text-xs text-gray-400">AMSP Patterns</div>
            </div>
            <div className="text-center p-4 bg-white/5 rounded-xl border border-white/10">
              <div className="text-2xl font-bold text-red-400 mb-1">24/7</div>
              <div className="text-xs text-gray-400">Availability</div>
            </div>
          </div>

        {/* Usage Instructions */}
        <div className="mb-16">
          <div className="bg-gradient-to-r from-orange-500/10 via-red-500/10 to-orange-500/10 backdrop-blur-sm rounded-2xl shadow-2xl p-8 border border-white/20">
            <div className="text-center mb-8">
              <div className="w-16 h-16 bg-gradient-to-br from-orange-500 to-red-500 rounded-2xl mx-auto mb-4 flex items-center justify-center">
                <Info className="h-8 w-8 text-white" />
              </div>
              <h2 className="text-3xl font-bold text-white mb-3">How to Use AMSP Analyzer</h2>
              <p className="text-gray-300 max-w-2xl mx-auto">
                Follow these simple steps to perform comprehensive diagnostic analysis of your AMSP system
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
              <div className="text-center group">
                <div className="relative mb-6">
                  <div className="w-16 h-16 bg-gradient-to-br from-orange-500 to-orange-700 rounded-2xl mx-auto flex items-center justify-center group-hover:scale-110 transition-transform duration-300">
                    <Upload className="h-8 w-8 text-white" />
                  </div>
                  <div className="absolute -top-2 -right-6 w-8 h-8 bg-orange-500 rounded-full flex items-center justify-center text-white font-bold text-sm">
                    1
                  </div>
                </div>
                <h3 className="text-xl font-bold text-white mb-3">Upload AMSP Logs</h3>
                <p className="text-gray-300 text-sm leading-relaxed">
                  Select and upload your AMSP log files. The analyzer accepts ds_am.log (required) and 
                  additional AMSP-related logs for comprehensive analysis.
                </p>
              </div>

              <div className="text-center group">
                <div className="relative mb-6">
                  <div className="w-16 h-16 bg-gradient-to-br from-purple-500 to-purple-700 rounded-2xl mx-auto flex items-center justify-center group-hover:scale-110 transition-transform duration-300">
                    <Brain className="h-8 w-8 text-white" />
                  </div>
                  <div className="absolute -top-2 -right-6 w-8 h-8 bg-purple-500 rounded-full flex items-center justify-center text-white font-bold text-sm">
                    2
                  </div>
                </div>
                <h3 className="text-xl font-bold text-white mb-3">AI Analysis</h3>
                <p className="text-gray-300 text-sm leading-relaxed">
                  Our AI engines automatically analyze your AMSP logs using RAG system, ML pattern recognition, 
                  and expert knowledge base to identify issues and root causes.
                </p>
              </div>

              <div className="text-center group">
                <div className="relative mb-6">
                  <div className="w-16 h-16 bg-gradient-to-br from-green-500 to-green-700 rounded-2xl mx-auto flex items-center justify-center group-hover:scale-110 transition-transform duration-300">
                    <Target className="h-8 w-8 text-white" />
                  </div>
                  <div className="absolute -top-2 -right-6 w-8 h-8 bg-green-500 rounded-full flex items-center justify-center text-white font-bold text-sm">
                    3
                  </div>
                </div>
                <h3 className="text-xl font-bold text-white mb-3">Get Results</h3>
                <p className="text-gray-300 text-sm leading-relaxed">
                  Receive comprehensive analysis results with pattern failures, engine diagnostics, 
                  AI insights, and step-by-step troubleshooting recommendations.
                </p>
              </div>
            </div>
          </div>
        </div>

            {/* Select Your Log Files Section */}
            <div className="max-w-4xl mx-auto mb-12">
              <div className="text-center mb-8">
                <h2 className="text-2xl font-bold text-white mb-4">Select Your Log Files</h2>
                <p className="text-gray-400">Choose the AMSP (Anti-Malware Scan Platform) log files you want to analyze</p>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                {/* ds_am.log - Required */}
                <div className="text-center p-6 bg-white/5 backdrop-blur-sm rounded-2xl border border-green-500/30 hover:border-green-500/50 transition-all duration-300">
                  <div className="w-16 h-16 bg-gradient-to-br from-green-500 to-green-700 rounded-2xl mx-auto mb-4 flex items-center justify-center">
                    <FileText className="h-8 w-8 text-white" />
                  </div>
                  <h3 className="text-lg font-semibold text-white mb-2 break-words">ds_am.log</h3>
                  <Badge className="bg-green-500/20 text-green-300 border-green-500/30 mb-3">Required</Badge>
                  <p className="text-gray-400 text-xs">Anti-malware events from Linux systems with pattern loading and engine status.</p>
                </div>

                {/* AMSP-Inst_LocalDebugLog.log - Optional */}
                <div className="text-center p-6 bg-white/5 backdrop-blur-sm rounded-2xl border border-blue-500/30 hover:border-blue-500/50 transition-all duration-300">
                  <div className="w-16 h-16 bg-gradient-to-br from-blue-500 to-blue-700 rounded-2xl mx-auto mb-4 flex items-center justify-center">
                    <Upload className="h-8 w-8 text-white" />
                  </div>
                  <h3 className="text-sm font-semibold text-white mb-2 break-words leading-tight">AMSP-Inst_LocalDebugLog.log</h3>
                  <Badge variant="outline" className="border-blue-500/30 text-blue-300 mb-3">Optional</Badge>
                  <p className="text-gray-400 text-xs">Installation logs for anti-malware module deployment and setup.</p>
                </div>

                {/* AMSP-UnInst_LocalDebugLog.log - Optional */}
                <div className="text-center p-6 bg-white/5 backdrop-blur-sm rounded-2xl border border-orange-500/30 hover:border-orange-500/50 transition-all duration-300">
                  <div className="w-16 h-16 bg-gradient-to-br from-orange-500 to-orange-700 rounded-2xl mx-auto mb-4 flex items-center justify-center">
                    <X className="h-8 w-8 text-white" />
                  </div>
                  <h3 className="text-sm font-semibold text-white mb-2 break-words leading-tight">AMSP-UnInst_LocalDebugLog.log</h3>
                  <Badge variant="outline" className="border-orange-500/30 text-orange-300 mb-3">Optional</Badge>
                  <p className="text-gray-400 text-xs">Uninstallation logs for anti-malware module removal processes.</p>
                </div>

                {/* ds_am-icrc - Optional */}
                <div className="text-center p-6 bg-white/5 backdrop-blur-sm rounded-2xl border border-purple-500/30 hover:border-purple-500/50 transition-all duration-300">
                  <div className="w-16 h-16 bg-gradient-to-br from-purple-500 to-purple-700 rounded-2xl mx-auto mb-4 flex items-center justify-center">
                    <Activity className="h-8 w-8 text-white" />
                  </div>
                  <h3 className="text-lg font-semibold text-white mb-2 break-words">ds_am-icrc.log</h3>
                  <Badge variant="outline" className="border-purple-500/30 text-purple-300 mb-3">Optional</Badge>
                  <p className="text-gray-400 text-xs">Network connection logs from anti-malware module communications.</p>
                </div>
              </div>
            </div>

            {/* Clean Upload Area */}
            <div className="max-w-2xl mx-auto">
              <div className="relative">
                <label className="block w-full cursor-pointer group">
                  <div className="relative bg-white/5 backdrop-blur-sm border-2 border-dashed border-gray-600 rounded-3xl p-12 hover:border-orange-500/50 hover:bg-orange-500/5 transition-all duration-500 group">
                    {/* Background Animation */}
                    <div className="absolute inset-0 bg-gradient-to-br from-orange-500/0 to-orange-500/0 group-hover:from-orange-500/5 group-hover:to-orange-500/10 rounded-3xl transition-all duration-500"></div>
                    
                    {/* Content */}
                    <div className="relative text-center">
                      <div className="w-20 h-20 bg-gradient-to-br from-gray-600 to-gray-700 group-hover:from-orange-500 group-hover:to-orange-600 rounded-2xl mx-auto mb-6 flex items-center justify-center transition-all duration-500 group-hover:scale-110">
                        <Upload className="h-10 w-10 text-white" />
                      </div>
                      
                      <div className="space-y-2">
                        <h3 className="text-2xl font-bold text-white group-hover:text-orange-200 transition-colors">
                          <span className="text-orange-400 group-hover:text-orange-300">Drag & Drop</span> or <span className="text-orange-400 group-hover:text-orange-300">Click to Select</span>
                        </h3>
                        <p className="text-gray-400 group-hover:text-gray-300 transition-colors">
                          AMSP log files for AI-powered analysis
                        </p>
                      </div>
                      
                      <div className="mt-6 flex items-center justify-center gap-6 text-sm text-gray-500">
                        <div className="flex items-center gap-2">
                          <div className="w-2 h-2 bg-orange-500 rounded-full"></div>
                          <span>.log</span>
                        </div>
                        <div className="flex items-center gap-2">
                          <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                          <span>.txt</span>
                        </div>
                        <div className="flex items-center gap-2">
                          <div className="w-2 h-2 bg-purple-500 rounded-full"></div>
                          <span>.zip</span>
                        </div>
                      </div>
                    </div>
                  </div>
                  
                  <input
                    type="file"
                    className="hidden"
                    multiple
                    accept=".log,.txt,.zip"
                    onChange={(e) => handleFileSelect(e.target.files)}
                    id="file-upload"
                  />
                </label>
              </div>

              {/* Selected Files Display */}
              {selectedFiles.length > 0 && (
                <div className="mt-8 max-w-2xl mx-auto">
                  <div className="bg-white/5 backdrop-blur-sm rounded-2xl p-6 border border-white/10">
                    <div className="flex items-center justify-between mb-4">
                      <h3 className="text-lg font-semibold text-white">Selected Files</h3>
                      <Badge className="bg-orange-500/20 text-orange-300 border-orange-500/30">
                        {selectedFiles.length} file{selectedFiles.length !== 1 ? 's' : ''}
                      </Badge>
                    </div>
                    
                    <div className="space-y-3">
                      {Array.from(selectedFiles).map((file, index) => (
                        <div key={index} className="flex items-center justify-between p-4 bg-white/5 rounded-xl border border-white/10 hover:border-white/20 transition-colors">
                          <div className="flex items-center gap-3">
                            <div className="w-10 h-10 bg-gradient-to-br from-orange-500 to-orange-600 rounded-lg flex items-center justify-center">
                              <FileText className="h-5 w-5 text-white" />
                            </div>
                            <div>
                              <div className="font-medium text-white">{file.name}</div>
                              <div className="text-sm text-gray-400">
                                {(file.size / 1024 / 1024).toFixed(2)} MB
                              </div>
                            </div>
                          </div>
                          <button
                            onClick={() => removeFile(index)}
                            className="p-2 hover:bg-red-500/20 rounded-lg transition-colors group"
                            title="Remove file"
                          >
                            <X className="h-4 w-4 text-gray-400 group-hover:text-red-400" />
                          </button>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              )}

              {/* Analysis Button */}
              {selectedFiles.length > 0 && (
                <div className="text-center mt-8">
                  <button
                    onClick={handleAnalysis}
                    disabled={isAnalyzing}
                    className="bg-gradient-to-r from-orange-500 to-red-600 hover:from-orange-600 hover:to-red-700 text-white px-12 py-4 rounded-2xl text-lg font-semibold transition-all duration-300 transform hover:scale-105 shadow-2xl hover:shadow-orange-500/30 disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none"
                  >
                    {isAnalyzing ? (
                      <div className="flex items-center gap-3">
                        <div className="animate-spin h-6 w-6 border-2 border-white border-t-transparent rounded-full"></div>
                        <span>Analyzing AMSP Logs...</span>
                      </div>
                    ) : (
                      <div className="flex items-center gap-3">
                        <Bug className="h-6 w-6" />
                        <span>Start AI Analysis</span>
                      </div>
                    )}
                  </button>
                  
                  {error && (
                    <div className="mt-6 bg-red-950/50 border border-red-500/30 rounded-2xl p-6">
                      <div className="flex items-center gap-3 text-red-300 mb-2">
                        <AlertCircle className="h-5 w-5" />
                        <span className="font-semibold">Analysis Error</span>
                      </div>
                      <p className="text-red-200">{error}</p>
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        )}

        {/* Analysis Results Overlay - Maintains Background Consistency */}
        {analysisResult && (
          <div className="relative">
            {/* Results Header */}
            <div className="text-center mb-12">
              <div className="flex items-center justify-center gap-3 mb-6">
                <div className="w-16 h-16 bg-gradient-to-br from-green-500 to-green-700 rounded-2xl flex items-center justify-center">
                  <CheckCircle className="h-8 w-8 text-white" />
                </div>
              </div>
              
              <h2 className="text-4xl font-bold bg-gradient-to-r from-white via-orange-200 to-orange-400 bg-clip-text text-transparent mb-4">
                AMSP Analysis Complete
              </h2>
              
              <div className="flex items-center justify-center gap-4 mb-6">
                <Badge className="bg-green-500/20 text-green-300 border-green-500/30 px-4 py-2">
                  <CheckCircle className="h-4 w-4 mr-2" />
                  Analysis Complete
                </Badge>
                {analysisResult.ml_insights?.health_score && (
                  <Badge className="bg-blue-500/20 text-blue-300 border-blue-500/30 px-4 py-2">
                    <Target className="h-4 w-4 mr-2" />
                    Health Score: {analysisResult.ml_insights.health_score}%
                  </Badge>
                )}
                {analysisResult.dynamic_rag_analysis?.analysis_metadata?.confidence_score && (
                  <Badge className="bg-purple-500/20 text-purple-300 border-purple-500/30 px-4 py-2">
                    <Brain className="h-4 w-4 mr-2" />
                    AI Confidence: {analysisResult.dynamic_rag_analysis.analysis_metadata.confidence_score}%
                  </Badge>
                )}
              </div>
              
              <p className="text-gray-300 max-w-3xl mx-auto leading-relaxed">
                Comprehensive AMSP analysis powered by AI, ML, and RAG technologies with pattern analysis, 
                engine diagnostics, and expert recommendations based on Trend Micro knowledge base.
              </p>
            </div>

            {/* Results Grid */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-12">
              {/* Card 1: Analysis Summary */}
              <Card className="bg-white/10 backdrop-blur-sm border-white/20 hover:border-orange-500/40 transition-all duration-300">
                <CardHeader className="pb-4">
                  <div className="flex items-center gap-3">
                    <div className="w-12 h-12 bg-gradient-to-br from-orange-500 to-red-600 rounded-xl flex items-center justify-center">
                      <Bug className="h-6 w-6 text-white" />
                    </div>
                    <div>
                      <CardTitle className="text-white text-xl">Analysis Summary</CardTitle>
                      <CardDescription className="text-gray-300">Overall AMSP system status and key findings</CardDescription>
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="space-y-6">
                    {/* Summary Text */}
                    <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-lg p-4">
                      <p className="text-gray-300 leading-relaxed">{analysisResult.summary}</p>
                    </div>

                    {/* Key Metrics */}
                    {analysisResult.metadata && (
                      <div className="grid grid-cols-2 gap-4">
                        <div className="text-center bg-white/5 backdrop-blur-sm p-4 rounded-lg border border-white/10">
                          <div className="text-2xl font-bold text-orange-400">{analysisResult.metadata.total_lines}</div>
                          <div className="text-xs text-orange-300">Total Lines</div>
                        </div>
                        <div className="text-center bg-white/5 backdrop-blur-sm p-4 rounded-lg border border-white/10">
                          <div className="text-2xl font-bold text-red-400">{analysisResult.metadata.errors_found}</div>
                          <div className="text-xs text-red-300">Errors Found</div>
                        </div>
                        <div className="text-center bg-white/5 backdrop-blur-sm p-4 rounded-lg border border-white/10">
                          <div className="text-2xl font-bold text-yellow-400">{analysisResult.metadata.pattern_failures}</div>
                          <div className="text-xs text-yellow-300">Pattern Failures</div>
                        </div>
                        <div className="text-center bg-white/5 backdrop-blur-sm p-4 rounded-lg border border-white/10">
                          <div className="text-2xl font-bold text-purple-400">{analysisResult.metadata.bpf_failures}</div>
                          <div className="text-xs text-purple-300">BPF Failures</div>
                        </div>
                      </div>
                    )}
                  </div>
                </CardContent>
              </Card>

              {/* Card 2: AI Analysis */}
              {analysisResult.dynamic_rag_analysis?.ai_response && (
                <Card className="bg-white/10 backdrop-blur-sm border-white/20 hover:border-blue-500/40 transition-all duration-300">
                  <CardHeader className="pb-4">
                    <div className="flex items-center gap-3">
                      <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-purple-600 rounded-xl flex items-center justify-center">
                        <Brain className="h-6 w-6 text-white" />
                      </div>
                      <div>
                        <CardTitle className="text-white text-xl">AI Expert Analysis</CardTitle>
                        <CardDescription className="text-gray-300">Dynamic knowledge retrieval and insights</CardDescription>
                      </div>
                    </div>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-lg p-4 max-h-96 overflow-y-auto">
                        <div className="text-white leading-relaxed whitespace-pre-wrap">
                          {analysisResult.dynamic_rag_analysis.ai_response}
                        </div>
                      </div>
                      
                      {analysisResult.dynamic_rag_analysis.analysis_metadata && (
                        <div className="flex items-center gap-4 text-sm">
                          <span className="text-blue-300">
                            Sources: {analysisResult.dynamic_rag_analysis.analysis_metadata.knowledge_sources_used}
                          </span>
                          <span className="text-purple-300">
                            Confidence: {analysisResult.dynamic_rag_analysis.analysis_metadata.confidence_score}%
                          </span>
                        </div>
                      )}
                    </div>
                  </CardContent>
                </Card>
              )}
            </div>

            {/* Log Interpretation Card - AI-Powered Line-by-Line Analysis */}
            {analysisResult.log_interpretation && (
              <Card className="bg-white/10 backdrop-blur-sm border-white/20 hover:border-purple-500/40 transition-all duration-300 mb-8">
                <CardHeader className="pb-4">
                  <div className="flex items-center gap-3">
                    <div className="w-12 h-12 bg-gradient-to-br from-purple-500 to-indigo-600 rounded-xl flex items-center justify-center">
                      <FileText className="h-6 w-6 text-white" />
                    </div>
                    <div>
                      <CardTitle className="text-white text-xl flex items-center gap-2">
                        🔍 Log Interpretation
                        <Badge className="bg-purple-500/20 text-purple-300 border-purple-500/30 text-xs">
                          AI-Powered
                        </Badge>
                      </CardTitle>
                      <CardDescription className="text-gray-300">
                        {analysisResult.log_interpretation.summary}
                      </CardDescription>
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  {/* AI Insights Summary */}
                  <div className="bg-gradient-to-r from-purple-500/10 to-indigo-500/10 rounded-lg p-4 mb-6 border border-purple-500/30">
                    <div className="flex items-start gap-3">
                      <Brain className="h-5 w-5 text-purple-400 mt-0.5 flex-shrink-0" />
                      <div>
                        <h4 className="text-purple-300 font-semibold mb-2">🤖 AI Analysis Overview</h4>
                        <p className="text-gray-300 text-sm leading-relaxed">{analysisResult.log_interpretation.ai_insights}</p>
                      </div>
                    </div>
                  </div>

                  {/* Patterns Detected */}
                  <div className="mb-6">
                    <h4 className="text-white font-semibold mb-3 flex items-center gap-2">
                      <Target className="h-4 w-4 text-blue-400" />
                      Detected Patterns
                    </h4>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                      {analysisResult.log_interpretation.patterns_detected.map((pattern, index) => (
                        <div key={index} className="bg-white/5 rounded-lg p-3 border border-blue-500/20">
                          <span className="text-blue-300 text-sm">{pattern}</span>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Line-by-Line Analysis */}
                  <div className="space-y-4 max-h-96 overflow-y-auto">
                    <h4 className="text-white font-semibold mb-4 flex items-center gap-2">
                      <Activity className="h-4 w-4 text-green-400" />
                      Line-by-Line AI Analysis
                    </h4>
                    {analysisResult.log_interpretation.entries.map((entry, index) => {
                      // Ensure all entry properties are safe for rendering
                      const safeEntry = {
                        line_number: String(entry?.line_number || index + 1),
                        timestamp: String(entry?.timestamp || ''),
                        severity_indicator: String(entry?.severity_indicator || entry?.level || 'INFO'),
                        component: String(entry?.component || 'AMSP'),
                        raw_message: String(entry?.raw_message || ''),
                        ai_interpretation: String(entry?.ai_interpretation || ''),
                        action_required: entry?.action_required ? String(entry.action_required) : null
                      };
                      
                      return (
                      <div key={index} className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-lg p-4 hover:border-purple-500/30 transition-colors">
                        {/* Entry Header */}
                        <div className="flex items-center justify-between mb-3">
                          <div className="flex items-center gap-3">
                            <Badge variant="outline" className="text-xs font-mono">
                              Line {safeEntry.line_number}
                            </Badge>
                            <span className="text-xs text-gray-400">{safeEntry.timestamp}</span>
                            <Badge className={`text-xs ${
                              safeEntry.severity_indicator === 'ERROR' ? 'bg-red-500/20 text-red-300 border-red-500/30' :
                              safeEntry.severity_indicator === 'WARN' ? 'bg-yellow-500/20 text-yellow-300 border-yellow-500/30' :
                              'bg-blue-500/20 text-blue-300 border-blue-500/30'
                            }`}>
                              {safeEntry.severity_indicator}
                            </Badge>
                          </div>
                          <Badge variant="outline" className="text-xs">
                            {safeEntry.component}
                          </Badge>
                        </div>

                        {/* Raw Log Message */}
                        <div className="mb-3 p-3 bg-black/30 rounded-lg border border-gray-600/30">
                          <p className="text-gray-300 text-sm font-mono leading-relaxed">{safeEntry.raw_message}</p>
                        </div>

                        {/* AI Interpretation */}
                        <div className="mb-3 p-3 bg-gradient-to-r from-purple-500/10 to-blue-500/10 rounded-lg border border-purple-500/20">
                          <div className="flex items-start gap-2">
                            <Brain className="h-4 w-4 text-purple-400 mt-0.5 flex-shrink-0" />
                            <div>
                              <h5 className="text-purple-300 font-medium text-sm mb-1">AI Interpretation</h5>
                              <p className="text-white text-sm leading-relaxed">{safeEntry.ai_interpretation}</p>
                            </div>
                          </div>
                        </div>

                        {/* Action Required */}
                        {safeEntry.action_required && (
                          <div className="flex items-start gap-2 p-3 bg-gradient-to-r from-green-500/10 to-emerald-500/10 rounded-lg border border-green-500/20">
                            <Wrench className="h-4 w-4 text-green-400 mt-0.5 flex-shrink-0" />
                            <div>
                              <h5 className="text-green-300 font-medium text-sm mb-1">Recommended Action</h5>
                              <p className="text-green-100 text-sm">{safeEntry.action_required}</p>
                            </div>
                          </div>
                        )}
                      </div>
                      );
                    })}
                  </div>
                </CardContent>
              </Card>
            )}

            {/* KB-Style Troubleshooting Guides */}
            {analysisResult.recommendations && analysisResult.recommendations.length > 0 && (
              <div className="space-y-6 mb-8">
                <div className="text-center mb-6">
                  <div className="flex items-center justify-center gap-3 mb-4">
                    <div className="w-12 h-12 bg-gradient-to-br from-emerald-500 to-green-600 rounded-xl flex items-center justify-center">
                      <Wrench className="h-6 w-6 text-white" />
                    </div>
                    <div>
                      <h3 className="text-2xl font-bold text-white">📚 Knowledge Base Articles</h3>
                      <p className="text-gray-300">Step-by-step troubleshooting guides powered by AI</p>
                    </div>
                  </div>
                </div>

                {analysisResult.recommendations.map((kbArticle, index) => {
                  // Safety check: ensure kbArticle is a proper object with expected structure
                  if (!kbArticle || typeof kbArticle !== 'object') {
                    console.error('Invalid kbArticle:', kbArticle);
                    return null;
                  }
                  
                  // Ensure all required fields are strings/arrays, not objects
                  const safeKbArticle = {
                    kb_id: String(kbArticle.kb_id || `AMSP-KB-${index + 1}`),
                    title: String(kbArticle.title || 'AMSP Issue Resolution'),
                    category: String(kbArticle.category || 'General'),
                    priority: String(kbArticle.priority || 'Medium'),
                    difficulty: String(kbArticle.difficulty || 'Intermediate'),
                    estimated_time: String(kbArticle.estimated_time || '15-30 minutes'),
                    prerequisites: Array.isArray(kbArticle.prerequisites) ? kbArticle.prerequisites.map(String) : [],
                    steps: Array.isArray(kbArticle.steps) ? kbArticle.steps : [],
                    verification: Array.isArray(kbArticle.verification) ? kbArticle.verification.map(String) : [],
                    troubleshooting_tips: Array.isArray(kbArticle.troubleshooting_tips) ? kbArticle.troubleshooting_tips.map(String) : []
                  };
                  
                  return (
                  <Card key={index} className="bg-white/10 backdrop-blur-sm border-white/20 hover:border-emerald-500/40 transition-all duration-300">
                    {/* KB Article Header */}
                    <CardHeader className="pb-4">
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="flex items-center gap-3 mb-2">
                            <Badge className="bg-emerald-500/20 text-emerald-300 border-emerald-500/30 font-mono text-xs">
                              {safeKbArticle.kb_id}
                            </Badge>
                            <Badge className={`text-xs ${
                              safeKbArticle.priority === 'Critical' || safeKbArticle.priority === 'High' 
                                ? 'bg-red-500/20 text-red-300 border-red-500/30'
                                : safeKbArticle.priority === 'Medium'
                                ? 'bg-yellow-500/20 text-yellow-300 border-yellow-500/30'
                                : 'bg-green-500/20 text-green-300 border-green-500/30'
                            }`}>
                              {safeKbArticle.priority} Priority
                            </Badge>
                            <Badge variant="outline" className="text-xs">
                              {safeKbArticle.difficulty}
                            </Badge>
                          </div>
                          <CardTitle className="text-white text-lg mb-2">{safeKbArticle.title}</CardTitle>
                          <div className="flex items-center gap-4 text-sm text-gray-400">
                            <span className="flex items-center gap-1">
                              <Target className="h-3 w-3" />
                              {safeKbArticle.category}
                            </span>
                            <span className="flex items-center gap-1">
                              ⏱️ {safeKbArticle.estimated_time}
                            </span>
                          </div>
                        </div>
                      </div>
                    </CardHeader>

                    <CardContent>
                      {/* Prerequisites */}
                      {safeKbArticle.prerequisites && safeKbArticle.prerequisites.length > 0 && (
                        <div className="mb-6 p-4 bg-blue-500/10 rounded-lg border border-blue-500/20">
                          <h4 className="text-blue-300 font-semibold mb-2 flex items-center gap-2">
                            <Info className="h-4 w-4" />
                            Prerequisites
                          </h4>
                          <ul className="space-y-1 text-blue-100 text-sm">
                            {safeKbArticle.prerequisites.map((prereq, prereqIndex) => (
                              <li key={prereqIndex} className="flex items-start gap-2">
                                <span className="text-blue-400 mt-1">•</span>
                                {prereq}
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}

                      {/* Step-by-Step Instructions */}
                      <div className="mb-6">
                        <h4 className="text-white font-semibold mb-4 flex items-center gap-2">
                          <Wrench className="h-4 w-4 text-emerald-400" />
                          Step-by-Step Instructions
                        </h4>
                        <div className="space-y-4">
                          {safeKbArticle.steps.map((step, stepIndex) => (
                            <div key={stepIndex} className="bg-white/5 rounded-lg p-4 border border-white/10">
                              <div className="flex items-start gap-4">
                                <div className="w-8 h-8 bg-emerald-500 rounded-full flex items-center justify-center text-white text-sm font-bold flex-shrink-0">
                                  {step.step_number}
                                </div>
                                <div className="flex-1">
                                  <p className="text-white text-sm mb-3 leading-relaxed">{step.instruction}</p>
                                  
                                  {step.command && (
                                    <div className="mb-3 p-3 bg-black/40 rounded-lg border border-gray-600/30">
                                      <div className="flex items-center gap-2 mb-2">
                                        <span className="text-xs text-gray-400 font-mono">Command:</span>
                                      </div>
                                      <code className="text-emerald-300 text-sm font-mono">{step.command}</code>
                                    </div>
                                  )}

                                  {step.expected_result && (
                                    <div className="p-3 bg-emerald-500/10 rounded-lg border border-emerald-500/20">
                                      <div className="flex items-center gap-2 mb-1">
                                        <CheckCircle className="h-3 w-3 text-emerald-400" />
                                        <span className="text-emerald-300 text-xs font-medium">Expected Result:</span>
                                      </div>
                                      <p className="text-emerald-100 text-xs">{step.expected_result}</p>
                                    </div>
                                  )}
                                </div>
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>

                      {/* Verification Steps */}
                      {safeKbArticle.verification && safeKbArticle.verification.length > 0 && (
                        <div className="mb-6 p-4 bg-green-500/10 rounded-lg border border-green-500/20">
                          <h4 className="text-green-300 font-semibold mb-3 flex items-center gap-2">
                            <CheckCircle className="h-4 w-4" />
                            Verification Steps
                          </h4>
                          <ul className="space-y-2 text-green-100 text-sm">
                            {safeKbArticle.verification.map((verification, verifyIndex) => (
                              <li key={verifyIndex} className="flex items-start gap-2">
                                <CheckCircle className="h-3 w-3 text-green-400 mt-1 flex-shrink-0" />
                                {verification}
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}

                      {/* Troubleshooting Tips */}
                      {safeKbArticle.troubleshooting_tips && safeKbArticle.troubleshooting_tips.length > 0 && (
                        <div className="p-4 bg-yellow-500/10 rounded-lg border border-yellow-500/20">
                          <h4 className="text-yellow-300 font-semibold mb-3 flex items-center gap-2">
                            <AlertTriangle className="h-4 w-4" />
                            Troubleshooting Tips
                          </h4>
                          <ul className="space-y-2 text-yellow-100 text-sm">
                            {safeKbArticle.troubleshooting_tips.map((tip, tipIndex) => (
                              <li key={tipIndex} className="flex items-start gap-2">
                                <span className="text-yellow-400 mt-1">💡</span>
                                {String(tip)}
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </CardContent>
                  </Card>
                  );
                })}
              </div>
            )}

            {/* New Analysis Button */}
            <div className="text-center">
              <button
                onClick={() => {
                  setAnalysisResult(null)
                  setSelectedFiles([])
                  setError(null)
                }}
                className="bg-white/10 hover:bg-white/20 border border-white/20 hover:border-white/30 text-white px-8 py-3 rounded-2xl transition-all duration-300 font-medium"
              >
                <div className="flex items-center gap-2">
                  <Upload className="h-5 w-5" />
                  <span>Analyze New Files</span>
                </div>
              </button>
            </div>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="relative z-10 bg-black/40 backdrop-blur-sm border-t border-white/10 text-white py-12">
        <div className="max-w-7xl mx-auto px-4">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
            <div className="md:col-span-2">
              <div className="flex items-center space-x-4 mb-4">
                <Image
                  src="/trendlogo.png"
                  alt="Trend Micro Logo"
                  width={40}
                  height={40}
                  className="h-10 w-auto"
                />
                <div className="border-l border-white/30 pl-4">
                  <div className="text-xl font-bold text-red-400">Intellicket</div>
                  <div className="text-sm text-gray-400">AI-Powered Cybersecurity Support</div>
                </div>
              </div>
              <p className="text-gray-400 text-sm mb-6 max-w-md">
                Advanced AI and machine learning technology providing intelligent analysis and expert-level recommendations for Deep Security products.
              </p>
              <div className="flex items-center space-x-4">
                <div className="flex items-center space-x-2">
                  <Brain className="h-4 w-4 text-blue-400" />
                  <span className="text-blue-300 text-sm">AI-Enhanced</span>
                </div>
                <div className="flex items-center space-x-2">
                  <Target className="h-4 w-4 text-purple-400" />
                  <span className="text-purple-300 text-sm">ML-Powered</span>
                </div>
                <div className="flex items-center space-x-2">
                  <Zap className="h-4 w-4 text-green-400" />
                  <span className="text-green-300 text-sm">RAG System</span>
                </div>
              </div>
            </div>
            <div>
              <h3 className="text-lg font-semibold mb-4 text-red-400">Quick Links</h3>
              <ul className="space-y-2 text-sm">
                <li><Link href="/products/deep-security" className="text-gray-400 hover:text-red-300 transition-colors">Deep Security</Link></li>
                <li><Link href="/products/deep-security/analyzer-dsoffline" className="text-gray-400 hover:text-red-300 transition-colors">DS Agent Analyzer</Link></li>
                <li><Link href="/portal" className="text-gray-400 hover:text-red-300 transition-colors">Support Portal</Link></li>
              </ul>
            </div>
            <div>
              <h3 className="text-lg font-semibold mb-4 text-red-400">Products</h3>
              <ul className="space-y-2 text-sm">
                {products.map((product) => (
                  <li key={product.id}>
                    <Link href={`/products/${product.id}`} className="text-gray-400 hover:text-red-300 transition-colors flex items-center gap-2">
                      <span>{product.icon}</span>
                      {product.name}
                    </Link>
                  </li>
                ))}
              </ul>
            </div>
          </div>
          <div className="border-t border-white/20 mt-12 pt-8">
            <div className="flex flex-col md:flex-row justify-between items-center">
              <p className="text-gray-400 text-sm">
                © 2024 Trend Micro Incorporated. All rights reserved.
              </p>
              <div className="flex items-center space-x-4 mt-4 md:mt-0">
                <span className="text-gray-400 text-sm">Powered by Advanced AI Technology</span>
              </div>
            </div>
          </div>
        </div>
      </footer>
    </div>
  )
}